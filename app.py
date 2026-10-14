import streamlit as st
from datetime import date

from planner import generate_plan
from resume_analyzer import (
    extract_text_from_pdf,
    analyze_resume
)


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="AI Student Assistant",
    page_icon="🎓",
    layout="wide"
)


# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title("🎓 AI Student Career & Academic Assistant")

st.write(
    "An AI-based platform that supports students in "
    "academic planning and career readiness."
)

st.divider()


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.title("Navigation")

module = st.sidebar.radio(
    "Select a module:",
    [
        "🏠 Home",
        "📚 AI Study Planner",
        "📄 AI Resume Analyzer"
    ]
)


# ==================================================
# HOME
# ==================================================

if module == "🏠 Home":

    st.header("Welcome!")

    st.write(
        "This platform integrates two student-focused "
        "modules into a single application."
    )

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("📚 AI Study Planner")

        st.write(
            "Creates a prioritized study plan based on "
            "subject difficulty, deadlines and available "
            "study time."
        )

    with col2:

        st.subheader("📄 AI Resume Analyzer")

        st.write(
            "Analyzes a student's resume, identifies "
            "skills and provides basic resume insights."
        )

    st.info(
        "Select a module from the sidebar to begin."
    )


# ==================================================
# STUDY PLANNER
# ==================================================

elif module == "📚 AI Study Planner":

    st.header("📚 AI Study Planner")

    st.write(
        "Create a personalized study plan based on "
        "your subjects, deadlines and difficulty levels."
    )

    daily_hours = st.number_input(
        "Available study hours per day",
        min_value=1.0,
        max_value=24.0,
        value=4.0,
        step=0.5
    )

    st.subheader("Enter Subject Details")

    number_of_subjects = st.number_input(
        "Number of subjects",
        min_value=1,
        max_value=10,
        value=3,
        step=1
    )

    subjects = []

    for i in range(int(number_of_subjects)):

        st.markdown(f"### Subject {i + 1}")

        col1, col2, col3 = st.columns(3)

        with col1:

            name = st.text_input(
                "Subject name",
                key=f"name_{i}"
            )

        with col2:

            deadline = st.date_input(
                "Deadline",
                value=date.today(),
                key=f"deadline_{i}"
            )

        with col3:

            difficulty = st.selectbox(
                "Difficulty",
                ["Easy", "Medium", "Hard"],
                key=f"difficulty_{i}"
            )

        subjects.append({
            "name": name,
            "deadline": deadline,
            "difficulty": difficulty
        })

    if st.button("🚀 Generate Study Plan"):

        valid_subjects = [
            subject
            for subject in subjects
            if subject["name"].strip()
        ]

        if not valid_subjects:

            st.warning(
                "Please enter at least one subject."
            )

        else:

            plan = generate_plan(
                valid_subjects,
                daily_hours
            )

            st.success("Study plan generated successfully!")

            st.subheader("📋 Recommended Study Plan")

            st.dataframe(
                plan,
                use_container_width=True
            )


# ==================================================
# RESUME ANALYZER
# ==================================================

elif module == "📄 AI Resume Analyzer":

    st.header("📄 AI Resume Analyzer")

    st.write(
        "Upload your resume to identify skills and "
        "receive a basic resume analysis."
    )

    uploaded_file = st.file_uploader(
        "Upload your resume (PDF)",
        type=["pdf"]
    )

    if uploaded_file is not None:

        if st.button("🔍 Analyze Resume"):

            with st.spinner("Analyzing resume..."):

                text = extract_text_from_pdf(
                    uploaded_file
                )

                result = analyze_resume(text)

            st.success("Resume analysis completed!")

            # Score
            st.subheader("📊 Resume Score")

            st.metric(
                "Skill Coverage",
                f"{result['score']}%"
            )

            # Skills found
            st.subheader("✅ Detected Skills")

            if result["skills"]:

                st.write(
                    ", ".join(result["skills"])
                )

            else:

                st.write(
                    "No predefined skills detected."
                )

            # Missing skills
            st.subheader("⚠️ Skills Not Detected")

            if result["missing_skills"]:

                st.write(
                    ", ".join(result["missing_skills"])
                )

            else:

                st.write(
                    "All listed skills were detected."
                )

            # Extracted text
            with st.expander(
                "View Extracted Resume Text"
            ):

                st.text(text)
