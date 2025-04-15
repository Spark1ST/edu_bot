import streamlit as st
from utils.session import load_course_data, load_user_data, update_user_progress, save_user_data

def enroll_in_course(uid, course_id):
    """Enroll user in a course using Firebase"""
    user_data = load_user_data(uid)
    if "enrolled_courses" not in user_data:
        user_data["enrolled_courses"] = []
    if course_id not in user_data["enrolled_courses"]:
        user_data["enrolled_courses"].append(course_id)
        save_user_data(uid, user_data)

def show_courses(enrolled_only=False):
    """Display course catalog"""
    if "uid" not in st.session_state:
        st.error("Please log in to access courses.")
        st.session_state.page = "auth"
        st.rerun()

    st.title("My Courses" if enrolled_only else "Course Catalog")
    
    courses = load_course_data()
    user_data = load_user_data(st.session_state.uid)
    enrolled_courses = user_data.get("enrolled_courses", [])

    if enrolled_only:
        courses = [c for c in courses if c["id"] in enrolled_courses]
        if not courses:
            st.info("No enrolled courses yet.")
            if st.button("Browse All Courses"):
                st.session_state.page = "courses"
                st.rerun()
            return

    cols = st.columns(3)
    for i, course in enumerate(courses):
        with cols[i % 3]:
            with st.container(border=True):
                st.image(course.get("image_url", ""), use_container_width=True)
                st.subheader(course["title"])
                st.caption(f"Instructor: {course.get('instructor', 'Unknown')}")
                st.write(course.get("description", ""))

                is_enrolled = course["id"] in enrolled_courses

                if is_enrolled:
                    if st.button("Continue", key=f"cont_{course['id']}"):
                        st.session_state.selected_course = course["id"]
                        st.session_state.current_module = None
                        st.session_state.page = "course"
                        st.rerun()
                else:
                    if st.button("Enroll Now", key=f"enroll_{course['id']}"):
                        enroll_in_course(st.session_state.uid, course["id"])
                        st.success("Enrolled successfully!")
                        st.rerun()

def show_course_details():
    """Display selected course details and modules"""
    if "selected_course" not in st.session_state:
        st.session_state.page = "courses"
        st.rerun()

    course = load_course_data(st.session_state.selected_course)
    if not course:
        st.error("Course not found.")
        st.session_state.page = "courses"
        st.rerun()

    st.title(course["title"])
    st.caption(f"Instructor: {course.get('instructor', 'Unknown')}")
    st.write(course.get("description", ""))

    if st.button("← Back to Courses"):
        st.session_state.selected_course = None
        st.session_state.page = "courses"
        st.rerun()

    user_data = load_user_data(st.session_state.uid)
    progress = user_data.get("progress", {}).get(course['id'], {})
    current_module = st.session_state.get("current_module")

    if current_module:
        show_module_content(course, current_module, progress)
    else:
        st.subheader("Modules")
        for module in course.get("modules", []):
            col1, col2 = st.columns([4, 1])
            completed = progress.get(module['id'], {}).get('completed', False)
            with col1:
                st.write(f"{'✅' if completed else '📚'} {module['title']}")
            with col2:
                if st.button("Open", key=f"mod_{module['id']}"):
                    st.session_state.current_module = module['id']
                    st.rerun()

def show_module_content(course, module_id, course_progress):
    """Display content for a selected module"""
    module = next((m for m in course["modules"] if m["id"] == module_id), None)
    if not module:
        st.session_state.current_module = None
        st.rerun()

    st.title(module["title"])

    if st.button("← Back to Modules"):
        st.session_state.current_module = None
        st.rerun()

    if module["content_type"] == "video":
        st.video(module["content"])
        if st.button("Mark as Completed"):
            update_user_progress(
                st.session_state.uid,
                course["id"],
                module["id"],
                {"completed": True}
            )
            st.success("Progress updated!")
            st.rerun()

    elif module["content_type"] == "quiz":
        if "quiz_answers" not in st.session_state:
            st.session_state.quiz_answers = {}

        for i, question in enumerate(module["content"]):
            st.write(f"**Q{i+1}:** {question['question']}")
            st.session_state.quiz_answers[i] = st.radio(
                "Select answer:",
                question["options"],
                key=f"quiz_{module['id']}_{i}"
            )

        if st.button("Submit Quiz"):
            score = sum(
                1 for i, q in enumerate(module["content"])
                if st.session_state.quiz_answers[i] == q["options"][q["correct"]]
            )
            total = len(module["content"])
            percentage = int((score / total) * 100)

            update_user_progress(
                st.session_state.uid,
                course["id"],
                module["id"],
                {
                    "completed": True,
                    "score": score,
                    "total": total,
                    "percentage": percentage
                }
            )
            st.success(f"You scored {score}/{total} ({percentage}%)")
            del st.session_state.quiz_answers
            st.rerun()
