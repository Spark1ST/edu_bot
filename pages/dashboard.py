import streamlit as st
import datetime
import pandas as pd
import altair as alt
from utils.session import load_user_data, load_course_data
from pages.chat import show_chat_page
def show_dashboard():
    """Display user dashboard with progress info"""
    if not st.session_state.logged_in:
        st.session_state.page = "auth"
        st.rerun()

    st.title(f"Welcome, {st.session_state.username}!")
    st.write(f"Today is {datetime.datetime.now().strftime('%A, %B %d, %Y')}")

    # Load user data
    user_data = load_user_data(st.session_state.uid)
    enrolled_courses = user_data.get("enrolled_courses", [])
    progress_data = user_data.get("progress", {})

    # Create dashboard layout
    col1, col2 = st.columns([2, 1])

    with col1:
        if not enrolled_courses:
            st.info("You haven't enrolled in any courses yet.")
            if st.button("Browse Courses"):
                st.session_state.page = "courses"
                st.rerun()
        else:
            show_progress_overview(enrolled_courses, progress_data)



    # Show detailed progress by course
    if enrolled_courses:
        st.subheader("Course Progress")
        show_course_progress(enrolled_courses, progress_data)


def show_progress_overview(enrolled_courses, progress_data):
    st.subheader("Your Learning Progress")

    total_modules = 0
    completed_modules = 0
    courses_data = []

    for course_id in enrolled_courses:
        course = load_course_data(course_id)
        if course:
            course_modules = len(course["modules"])
            total_modules += course_modules

            course_progress = progress_data.get(course_id, {})
            completed_in_course = sum(1 for m in course_progress.values() if m.get("completed", False))
            completed_modules += completed_in_course

            completion_percentage = (completed_in_course / course_modules * 100) if course_modules > 0 else 0
            courses_data.append({
                "course": course["title"],
                "completion": completion_percentage
            })

    overall_completion = (completed_modules / total_modules * 100) if total_modules > 0 else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Enrolled Courses", len(enrolled_courses))
    col2.metric("Completed Modules", f"{completed_modules}/{total_modules}")
    col3.metric("Overall Completion", f"{overall_completion:.1f}%")

    if courses_data:
        chart_data = pd.DataFrame(courses_data)
        chart = alt.Chart(chart_data).mark_bar().encode(
            x=alt.X('completion:Q', title='Completion (%)'),
            y=alt.Y('course:N', title='Course'),
            color=alt.Color('completion:Q', scale=alt.Scale(scheme='blues'), legend=None)
        ).properties(
            title='Course Completion'
        )
        st.altair_chart(chart, use_container_width=True)


def show_course_progress(enrolled_courses, progress_data):
    tabs = st.tabs([load_course_data(course_id)["title"] for course_id in enrolled_courses])

    for i, course_id in enumerate(enrolled_courses):
        with tabs[i]:
            course = load_course_data(course_id)
            course_progress = progress_data.get(course_id, {})

            st.write(f"**Instructor:** {course['description']}")

            for module in course["modules"]:
                module_progress = course_progress.get(module["id"], {})
                completed = module_progress.get("completed", False)

                col1, col2 = st.columns([3, 1])

                with col1:
                    status_icon = "✅" if completed else "⏱️"
                    st.write(f"{status_icon} **{module['title']}** ({module['content_type'].capitalize()})")

                with col2:
                    if module["content_type"] == "quiz" and completed:
                        score = module_progress.get("score", 0)
                        total = module_progress.get("total", 1)
                        percentage = module_progress.get("percentage", 0)
                        st.write(f"Score: {score}/{total} ({percentage}%)")

            if st.button("Continue Course", key=f"dashboard_continue_{course_id}"):
                st.session_state.selected_course = course_id
                st.session_state.page = "course"
                st.rerun()
