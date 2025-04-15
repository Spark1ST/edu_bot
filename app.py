import streamlit as st
import os
from pathlib import Path
from pages.authentication import show_authentication
from pages.courses import show_courses, show_course_details
from pages.dashboard import show_dashboard
from pages.admin import show_admin
from pages.chat import show_chat_page
from utils.session import check_session_state, initialize_session_state

# Set page configuration
st.set_page_config(
    page_title="QuestCourse Forge",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide Streamlit default controls
st.markdown("""
<style>
    [data-testid="collapsedControl"] { display: none !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

def setup_directories():
    directories = [
        "data",
        "data/users",
        "data/courses",
        "data/progress",
        "data/knowledge"
    ]
    for directory in directories:
        try:
            Path(directory).mkdir(parents=True, exist_ok=True)
            os.chmod(directory, 0o700)
        except Exception as e:
            st.error(f"Failed to create directory {directory}: {str(e)}")
            raise

def show_sidebar():
    with st.sidebar:
        st.markdown("""
        <style>
            .sidebar-button { width: 100%; margin: 4px 0; }
        </style>
        """, unsafe_allow_html=True)

        if st.session_state.logged_in:
            st.markdown(f"""
            <div style='margin-bottom: 20px;'>
                <h2 style='margin-bottom: 5px;'>QuestCourse Forge</h2>
                <p>👤 Logged in as: <strong>{st.session_state.username}</strong></p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("### Navigation")
            nav_actions = {
                "🏠 Dashboard": "dashboard",
                "📚 Course Catalog": "courses",
                "🎓 My Courses": "my_learning",
                "💬 AI Assistant": "chat"
            }

            for label, page in nav_actions.items():
                if st.button(label, key=f"nav_{page}", use_container_width=True,
                             type="primary" if st.session_state.page == page else "secondary"):
                    st.session_state.page = page
                    st.rerun()

            st.markdown("---")
            if st.button("🔒 Logout", key="logout", use_container_width=True, type="primary"):
                for key in list(st.session_state.keys()):
                    if key != "pages_initialized":
                        del st.session_state[key]
                initialize_session_state()
                st.rerun()

            if st.session_state.get("is_admin", False):
                st.markdown("---")
                st.markdown("### Admin Controls")
                if st.button("🛠️ Admin Panel", key="admin_panel", use_container_width=True):
                    st.session_state.page = "admin"
                    st.rerun()
        else:
            st.markdown("""
            <div style='text-align: center; margin-top: 20px;'>
                <h2>QuestCourse Forge</h2>
                <p>Please log in to continue</p>
            </div>
            """, unsafe_allow_html=True)

def main():
    try:
        setup_directories()
        initialize_session_state()
        check_session_state()

        if not st.session_state.logged_in:
            show_authentication()
            return

        current_page = st.session_state.page
        show_sidebar()

        if current_page == "admin":
            show_admin()
        elif current_page == "dashboard":
            show_dashboard()
        elif current_page in ["courses", "my_learning"]:
            if st.session_state.get("selected_course"):
                show_course_details()
            else:
                show_courses(enrolled_only=(current_page == "my_learning"))
        elif current_page == "chat":
            show_chat_page()
        else:
            st.session_state.page = "dashboard"
            st.rerun()

    except Exception as e:
        st.error("An unexpected error occurred. Please try again.")
        st.error(f"Error details: {str(e)}")
        if st.button("Reload Application"):
            st.rerun()

if __name__ == "__main__":
    main()
