import pandas as pd
import re
import string
import spacy
from sentence_transformers import SentenceTransformer
import faiss
import qdrant_client 
import numpy as np
import google.generativeai as genai
import os
from qdrant_client.http import models
from qdrant_client import QdrantClient
from langchain.chains import ConversationChain
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentExecutor
from langchain.prompts import PromptTemplate
from langchain_community.llms import OpenAI
#from agentops import AgentOpsLogger    
#from langchain_core.language_models import LLM
from typing import Optional, List
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from crewai import Agent, Crew, Task
from crewai.llm import LLM
import agentops
from qdrant_client.models import VectorParams, Distance,PointStruct
import yaml

# Connect to Qdrant
qdrant_client = QdrantClient(
    url="https://d2934d30-6e01-45c7-b516-4ed5ac3f1b8f.us-east4-0.gcp.cloud.qdrant.io:6333", 
    api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.P8MJV_2LFjXA_ytBZ1-9UFb5ysDzfJhPHHRp8qicLMQ",
    timeout=60.0
)
# Try to list collections (this will test the connection)
try:
    collections = qdrant_client.get_collections()
    print("✅ Connected to Qdrant!")
    for col in collections.collections:
        print(f" - {col.name}")
except Exception as e:
    print("❌ Failed to connect to Qdrant:")
    print(e)
# # Set Gemini API key
genai.configure(api_key="AIzaSyBdA7Qsj2JbgJtixDWhG3YxtocfaOCmAGI")

#Set AgentOps Key
os.environ["AGENTOPS_API_KEY"] = "bf2253c4-893f-48f4-81ef-55a983fffd49"
# os.environ["AGENTOPS_LOG_LEVEL"] = "DEBUG"
agentops.init(api_key=os.environ["AGENTOPS_API_KEY"])

# Load Spacy model for NLP tasks
nlp = spacy.load("en_core_web_sm")

# Load dataset (replace with actual dataset path)
df = pd.read_csv("udemy_course_data.csv")

# Data Cleaning and Normalization
def clean_text(text):
    text = text.lower()  # Convert to lowercase
    text = re.sub(f"[{string.punctuation}]", "", text)  # Remove punctuation
    text = re.sub(r"\s+", " ", text).strip()  # Remove extra spaces
    return text

df['course_title'] = df['course_title'].apply(clean_text)


# Tokenization and Lemmatization
def lemmatize_text(text):
    doc = nlp(text)
    return " ".join([token.lemma_ for token in doc if not token.is_stop])

df['course_title'] = df['course_title'].apply(lemmatize_text)

# Named Entity Recognition (NER)
def extract_entities(text):
    doc = nlp(text)
    entities = {ent.label_: ent.text for ent in doc.ents}
    return entities

df['entities'] = df['course_title'].apply(extract_entities)

# Vectorization using Sentence Transformers
model = SentenceTransformer("all-MiniLM-L6-v2")
df['embedding'] = df['course_title'].apply(lambda x: model.encode(x))

# Indexing using FAISS
d = len(df['embedding'][0])  # Dimension of vectors
index = faiss.IndexFlatL2(d)
index.add(np.array(df['embedding'].tolist()))


qdrant_client.recreate_collection(
    collection_name="course_embeddings",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
)

# Insert vectors into Qdrant

points = [PointStruct(id=i, vector=df['embedding'][i], payload={"title": df['course_title'][i]}) for i in range(len(df))]
print(len(df['embedding'][0]))  # Should be consistent and reasonable



batch_size = 100  # Start with 100, adjust as needed
for i in range(0, len(df), batch_size):
    batch_points = [
        PointStruct(
            id=j, 
            vector=df['embedding'][j], 
            payload={"title": df['course_title'][j]}
        ) 
        for j in range(i, min(i + batch_size, len(df)))
    ]
    qdrant_client.upsert(collection_name="course_embeddings", points=batch_points)
    print(f"Processed batch {i//batch_size + 1}")

API_CONFIG = """
GEMINI_API_KEY: "AIzaSyBUAQsQ_KVLeeJRqHP_e9qX5zmV1pw6ejE"
"""
config = yaml.safe_load(API_CONFIG)

llm = LLM(model="gemini/gemini-1.5-flash", api_key=config["GEMINI_API_KEY"])

def retrieve_similar_courses(query, top_k=5):
    query_vector = model.encode(query)
    search_result = qdrant_client.search(
        collection_name="course_embeddings",
        query_vector=query_vector,
        limit=top_k,
        with_payload=True
    )
    results = [hit.payload["title"] for hit in search_result]
    return results

def generate_response(context, user_query):
    prompt = f"Given the following course titles: {context}, answer the user's question: {user_query}"
    gemini_model = genai.GenerativeModel("gemini-1.5-flash")
    response = gemini_model.generate_content(prompt)
    return response.text

def career_coaching_tool_func(course_name):
    prompt = f"What career paths are available after completing the course '{course_name}'?"
    gemini_model = genai.GenerativeModel("gemini-1.5-flash")
    response = gemini_model.generate_content(prompt)
    return response.text

# Define tools (above the handle_with_crewai function)
course_recommendation_tool = Tool(
    name="CourseRecommendation",
    func=retrieve_similar_courses,
    description="Retrieve a list of courses similar to the user's query"
)

qa_tool = Tool(
    name="CourseQA",
    func=generate_response,
    description="Answer a user's question based on course descriptions"
)

career_tool = Tool(
    name="CareerCoaching",
    func=career_coaching_tool_func,
    description="Provide career guidance based on a completed course"
)

tools = [course_recommendation_tool, qa_tool, career_tool]


# Define CrewAI Agents
intent_agent = Agent(
    role="Intent Classifier",
    goal="Understand the user's question and choose the correct pipeline",
    backstory="You're responsible for routing the user's query to the right service.",
    verbose=True,
    allow_delegation=False,
    llm=llm
)

context_agent = Agent(
    role="Context Reviewer",
    goal="Review any generated response and ensure it's appropriate",
    backstory="You're in charge of quality assurance and making sure responses are accurate and relevant.",
    verbose=True,
    allow_delegation=False,
    llm=llm
)

def handle_intent_agent(user_input):
    intent_task = Task(
        description=f"Classify the user's intent and return one of: 'recommendation', 'Q&A', or 'career advice'. The user's question is: {user_input}",
        agent=intent_agent,
        expected_output="intent",
        output_key="intent_response"
    )

    crew = Crew(
        agents=[intent_agent,],
        tasks=[intent_task],
        verbose=True
    )

    # Get intent
    result = crew.kickoff(inputs={"input": user_input})
    intent = result.tasks_output[0].raw


    if "recommendation" in intent:
        response = course_recommendation_tool.func(user_input)
    elif "Q&A" in intent or "qa" in intent:
        context = retrieve_similar_courses(user_input)  # or preloaded context
        response = qa_tool.func(context, user_input)
    elif "career advice" in intent:
        response = career_tool.func(user_input)
    else:
        response = "Sorry, I couldn't determine the intent."
    return response

def handle_context_agent(initial_response, user_input):
    context_task = Task(
        description=(
            f"Review the following initial response to determine if it correctly answers the user's input.\n\n"
            f"User Input: {user_input}\n"
            f"Initial Response: {initial_response}\n\n"
            "If the response is correct and relevant, return it directly.\n"
            "If the response recommends courses that do not match the user's topic of interest (e.g., suggesting web development courses for a machine learning query), respond with the following:\n\n"
            "- Politely inform the user that there are no matching courses on the platform.\n"
            "- Then, recommend external or general resources relevant to the user's topic.\n"
            "- Ensure the response is user-friendly and helpful.\n\n"
            "Return only the final user-facing response."
        ),
        agent=context_agent,
        expected_output="final_response"
    )

    crew = Crew(
        agents=[context_agent],
        tasks=[context_task],
        verbose=True
    )

    result = crew.kickoff(inputs={"input": initial_response})

    # Extract and normalize initial_response if it's a list
    if isinstance(initial_response, list):
        initial_response_str = initial_response[0]
    else:
        initial_response_str = initial_response

    # Extract and normalize final_response
    final_response_raw = result.tasks_output[0].raw
    if isinstance(final_response_raw, list):
        final_response = final_response_raw[0]
    else:
        final_response = final_response_raw

    # Compare
    was_modified = final_response.strip() != initial_response_str.strip()

    return final_response, was_modified

def get_response(user_input: str):
    initial = handle_intent_agent(user_input)
    final, _ = handle_context_agent(initial, user_input)
    return final
print("ready")
# user_input = "What should I study to learn python?"
# result = handle_intent_agent(user_input)
# print("\nFinal Answer:", result)
# resonse,modefide = handle_context_agent(result,user_input)
# print("\nFinal Answer:", resonse)
# print("\nmodefide:", modefide)