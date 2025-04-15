import streamlit as st
import pandas as pd
from fastpi.crud import create_user, get_user, get_all_users, delete_user, create_course, get_course, get_all_courses, delete_course, enroll_user_in_course
from datetime import datetime

def show_admin():
    """Display admin panel for managing users and courses"""
    # Check if user is admin
    if not st.session_state.get("is_admin", False):
        st.error("You do not have permission to access this page.")
        return
    
    st.title("Admin Panel")
    
    # Back button
    if st.button("← Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()
    
    # Create tabs for different admin functions
    tab1, tab2 = st.tabs(["Manage Users", "Manage Courses"])
    
    # Manage Users tab
    with tab1:
        show_manage_users()
        
    # Manage Courses tab
    with tab2:
        show_manage_courses()

def show_manage_users():
    """Admin interface for managing users"""
    st.header("Manage Users")
    
    # Get all users
    users = get_all_users()
    
    # Display users in a table
    if users:
        users_df = pd.DataFrame([{
            "username": user.username,
            "email": user.email,
            "is_admin": user.is_admin,
            "enrolled_courses": len(user.enrolled_courses)
        } for user in users])
        st.dataframe(users_df, use_container_width=True)
        
        # Add user section
        st.subheader("Add New User")
        
        col1, col2 = st.columns(2)
        with col1:
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
        
        with col2:
            new_email = st.text_input("Email")
            is_admin = st.checkbox("Admin privileges")
        
        if st.button("Add User"):
            if new_username and new_email and new_password:
                try:
                    user_uid = create_user({
                        "username": new_username,
                        "email": new_email,
                        "password": new_password,
                        "is_admin": is_admin
                    })
                    st.success(f"User '{new_username}' created successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error creating user: {e}")
            else:
                st.error("Please fill all required fields")
        
        # Delete user section
        st.subheader("Delete User")
        delete_username = st.selectbox("Select user to delete", [user.username for user in users])
        
        if delete_username and st.button("Delete User", key="delete_user"):
            # Don't allow deleting the admin user who's logged in
            if delete_username == st.session_state.username:
                st.error("You cannot delete your own account while logged in.")
            else:
                # Find the user UID
                user_to_delete = next((user for user in users if user.username == delete_username), None)
                if user_to_delete:
                    try:
                        delete_user(user_to_delete.uid)
                        st.success(f"User '{delete_username}' deleted successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error deleting user: {e}")
                else:
                    st.error("User not found.")

    else:
        st.info("No users found.")

def show_manage_courses():
    """Admin interface for managing courses"""
    st.header("Manage Courses")
    
    # Get all courses
    courses = get_all_courses()
    
    # Display courses in a table
    if courses:
        courses_df = pd.DataFrame([{
            "id": course.id,
            "title": course.title,
            "instructor": course.instructor,
            "modules": len(course.modules)
        } for course in courses])
        st.dataframe(courses_df, use_container_width=True)
        
        # Add course section
        st.subheader("Add New Course")
        
        with st.expander("Create New Course"):
            col1, col2 = st.columns(2)
            with col1:
                course_id = st.text_input("Course ID (no spaces, lowercase)")
                course_title = st.text_input("Course Title")
                course_instructor = st.text_input("Instructor")
                
            with col2:
                course_description = st.text_area("Course Description")
                course_image = st.text_input("Image URL", value="https://i.imgur.com/JUTeU6G.jpg")
            
            if st.button("Create Course"):
                if course_id and course_title and course_description:
                    try:
                        course_id = create_course({
                            "id": course_id,
                            "title": course_title,
                            "description": course_description,
                            "instructor": course_instructor,
                            "image_url": course_image,
                            "modules": []
                        })
                        st.success(f"Course '{course_title}' created successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error creating course: {e}")
                else:
                    st.error("Please fill all required fields")
        
        # Delete course section
        st.subheader("Delete Course")
        delete_course_title = st.selectbox("Select course to delete", [course.title for course in courses])
        delete_course_id = next((course.id for course in courses if course.title == delete_course_title), None)
        
        if delete_course_title and delete_course_id and st.button("Delete Course", key="delete_course"):
            try:
                delete_course(delete_course_id)
                st.success(f"Course '{delete_course_title}' deleted successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error deleting course: {e}")
    else:
        st.info("No courses found.")
