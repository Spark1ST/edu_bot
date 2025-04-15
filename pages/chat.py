import streamlit as st
from utils.session import load_user_data
import requests
def show_chat_page():
    """Display the AI chat interface without file upload"""
    st.title("AI Learning Assistant")
    st.write(f"Hello {st.session_state.username}! How can I help you with your learning today?")
    
    # Initialize chat history if not exists
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi! I'm your AI learning assistant. How can I help you with your courses today?"}
        ]
    
    # Display chat messages from history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Accept user input
    if prompt := st.chat_input("Ask me anything about your courses..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Display assistant response
        with st.chat_message("assistant"):
            response = generate_ai_response(prompt)
            st.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Back to dashboard button
    # if st.button("Back to Dashboard"):
    #     st.session_state.page = "dashboard"
    #     st.rerun()

def generate_ai_response(prompt):
    try:
        response = requests.post(
            "http://127.0.0.1:8000/generate",  # or your deployed URL
            json={"prompt": prompt, "username": st.session_state.username},
            timeout=30
        )
        return response.json().get("response", "No answer received.")
    except Exception as e:
        return f"Error: {e}"
