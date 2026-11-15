# ============================================================
# AI STUDENT CAREER & ACADEMIC ASSISTANT
# Complete app.py
# ============================================================

import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
from html import escape
from supabase import create_client, Client


# ============================================================
# IMPORT PROJECT MODULES
# ============================================================

from planner import (
    generate_plan,
    generate_weekly_plan,
    get_study_recommendations,
    generate_smart_insights
)

from resume_analyzer import (
    extract_text_from_pdf,
    analyze_resume,
    CAREER_SKILLS
)

from offline_assistant import (
    answer_from_pdf,
    CAREER_ROADMAPS,
    INTERVIEW_BANK,
    evaluate_interview_answer
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Student Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #f5f8ff;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #101d3a, #172e56);
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

.main-title {
    font-size: 34px;
    font-weight: 800;
    color: #15294b;
    margin-bottom: 5px;
}

.subtitle {
    color: #66758f;
    font-size: 15px;
    margin-bottom: 25px;
}

.hero {
    background: linear-gradient(120deg, #123b75, #1676c5, #21a6c7);
    color: white;
    padding: 35px;
    border-radius: 20px;
    margin-bottom: 25px;
}

.hero h1 {
    color: white;
    font-size: 32px;
    font-weight: 800;
}

.hero p {
    color: #e8f5ff;
    font-size: 16px;
}

.card {
    background: white;
    padding: 22px;
    border-radius: 16px;
    border: 1px solid #e4eaf4;
    box-shadow: 0 4px 15px rgba(20, 50, 90, 0.05);
    margin-bottom: 15px;
}

.card h3 {
    color: #17365f;
}

.metric-card {
    background: white;
    border-radius: 15px;
    padding: 20px;
    border: 1px solid #e1e9f5;
    text-align: center;
}

.metric-value {
    font-size: 30px;
    font-weight: 800;
    color: #1769aa;
}

.metric-label {
    font-size: 13px;
    color: #718096;
}

.section-heading {
    color: #17365f;
    font-size: 23px;
    font-weight: 750;
    margin-top: 20px;
    margin-bottom: 15px;
}

.small-muted {
    color: #718096;
    font-size: 13px;
}

div.stButton > button {
    border-radius: 9px;
    font-weight: 600;
}

.stProgress > div > div > div > div {
    background-color: #1686cb;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# SUPABASE CONNECTION
# ============================================================

@st.cache_resource
def get_supabase_client() -> Client:
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )


try:
    supabase = get_supabase_client()
except Exception as exc:
    st.error(
        "Supabase connection could not be initialized. "
        "Check SUPABASE_URL and SUPABASE_KEY in "
        "Streamlit Cloud → Settings → Secrets."
    )
    st.exception(exc)
    st.stop()


# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================

def initialize_session():

    defaults = {
        "auth_user": None,
        "auth_access_token": None,
        "auth_refresh_token": None,
        "interview_attempts": [],
        "interview_loaded_user": None,
        "study_plan_results": None,
        "study_log": {},
        "study_history_loaded_user": None,
        "study_history": [],
        "chat_messages": [],
        "pdf_text": "",
        "resume_text": "",
        "chat_history_loaded_user": None
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


initialize_session()


# ============================================================
# AUTHENTICATION HELPERS
# ============================================================

def set_logged_in(session):

    st.session_state.auth_user = session.user
    st.session_state.auth_access_token = session.access_token
    st.session_state.auth_refresh_token = session.refresh_token

    st.session_state.interview_loaded_user = None
    st.session_state.study_history_loaded_user = None
    st.session_state.chat_history_loaded_user = None


def clear_auth_state():

    st.session_state.auth_user = None
    st.session_state.auth_access_token = None
    st.session_state.auth_refresh_token = None

    st.session_state.interview_attempts = []
    st.session_state.interview_loaded_user = None

    st.session_state.study_history = []
    st.session_state.study_history_loaded_user = None

    st.session_state.chat_messages = []
    st.session_state.chat_history_loaded_user = None


def restore_supabase_session():

    access_token = st.session_state.auth_access_token
    refresh_token = st.session_state.auth_refresh_token

    if not access_token or not refresh_token:
        return False

    try:
        response = supabase.auth.set_session(
            access_token,
            refresh_token
        )

        if response and response.user:
            st.session_state.auth_user = response.user

            if response.session:
                st.session_state.auth_access_token = (
                    response.session.access_token
                )
                st.session_state.auth_refresh_token = (
                    response.session.refresh_token
                )

            return True

        return False

    except Exception:
        return False


# ============================================================
# PROFILE DATABASE HELPERS
# ============================================================

def save_profile(user_id, full_name, course, study_year):

    try:
        supabase.table("profiles").upsert({
            "id": str(user_id),
            "full_name": full_name,
            "course": course,
            "study_year": study_year
        }).execute()

        return True

    except Exception as exc:
        st.error("Could not save profile.")
        st.exception(exc)
        return False


def load_profile(user_id):

    try:
        response = (
            supabase.table("profiles")
            .select("*")
            .eq("id", str(user_id))
            .limit(1)
            .execute()
        )

        if response.data:
            return response.data[0]

    except Exception:
        pass

    return {}


# ============================================================
# AUTHENTICATION PAGE
# ============================================================

def show_auth_page():

    st.markdown("""
    <div class="hero">
        <h1>🎓 AI Student Assistant</h1>
        <p>
        Your personal workspace for academic planning,
        resume insights and career readiness.
        </p>
    </div>
    """, unsafe_allow_html=True)

    left, center, right = st.columns([1, 1.5, 1])

    with center:

        st.markdown(
            '<h2 style="text-align:center;color:#17365f;">Welcome</h2>',
            unsafe_allow_html=True
        )

        login_tab, signup_tab, resend_tab = st.tabs([
            "Log in",
            "Create account",
            "Resend verification"
        ])

        # ---------------- LOGIN ----------------

        with login_tab:

            with st.form("login_form"):

                email = st.text_input("Email address")
                password = st.text_input(
                    "Password",
                    type="password"
                )

                submitted = st.form_submit_button(
                    "Log in",
                    use_container_width=True
                )

                if submitted:

                    if not email or not password:
                        st.warning("Enter your email and password.")

                    else:
                        try:
                            response = (
                                supabase.auth.sign_in_with_password({
                                    "email": email,
                                    "password": password
                                })
                            )

                            if response.session:
                                set_logged_in(response.session)
                                st.success("Login successful!")
                                st.rerun()

                            else:
                                st.error(
                                    "Login unsuccessful. "
                                    "Check your credentials and email verification."
                                )

                        except Exception as exc:
                            st.error("Login failed.")
                            st.exception(exc)

        # ---------------- SIGNUP ----------------

        with signup_tab:

            with st.form("signup_form"):

                full_name = st.text_input("Full name")
                email = st.text_input("Email address")
                course = st.text_input(
                    "Course",
                    value="B.Tech CSE-AI"
                )

                study_year = st.selectbox(
                    "Study year",
                    ["1st Year", "2nd Year", "3rd Year", "4th Year"]
                )

                password = st.text_input(
                    "Create password",
                    type="password"
                )

                confirm_password = st.text_input(
                    "Confirm password",
                    type="password"
                )

                submitted = st.form_submit_button(
                    "Create account",
                    use_container_width=True
                )

                if submitted:

                    if not all([
                        full_name,
                        email,
                        password,
                        confirm_password
                    ]):
                        st.warning("Please complete all required fields.")

                    elif password != confirm_password:
                        st.error("Passwords do not match.")

                    elif len(password) < 6:
                        st.error(
                            "Password must contain at least 6 characters."
                        )

                    else:

                        try:
                            response = supabase.auth.sign_up({
                                "email": email,
                                "password": password,
                                "options": {
                                    "data": {
                                        "full_name": full_name,
                                        "course": course,
                                        "study_year": study_year
                                    }
                                }
                            })

                            if response.session:

                                set_logged_in(response.session)

                                save_profile(
                                    response.user.id,
                                    full_name,
                                    course,
                                    study_year
                                )

                                st.success("Account created successfully!")
                                st.rerun()

                            else:
                                st.success(
                                    "Account created. "
                                    "Please verify your email before logging in."
                                )

                        except Exception as exc:
                            st.error("Account creation failed.")
                            st.exception(exc)

        # ---------------- RESEND VERIFICATION ----------------

        with resend_tab:

            with st.form("resend_form"):

                email = st.text_input("Registered email address")

                submitted = st.form_submit_button(
                    "Resend verification email",
                    use_container_width=True
                )

                if submitted:

                    if not email:
                        st.warning("Enter your email address.")

                    else:
                        try:
                            supabase.auth.resend({
                                "type": "signup",
                                "email": email
                            })

                            st.success(
                                "Verification email request submitted."
                            )

                        except Exception as exc:
                            st.error("Could not resend verification email.")
                            st.exception(exc)


# ============================================================
# STUDY PLANNER HELPERS
# ============================================================

def rebuild_study_plan(results):

    subjects = results["subjects"]
    daily_hours = float(results["daily_hours"])
    days = int(results["days"])

    for subject in subjects:

        subject["remaining_topics"] = max(
            0,
            int(subject["total_topics"])
            - int(subject["completed_topics"])
        )

    results["plan"] = generate_plan(
        subjects,
        daily_hours
    )

    results["weekly"] = generate_weekly_plan(
        subjects,
        daily_hours,
        days=days
    )

    results["recommendations"] = get_study_recommendations(
        subjects
    )

    results["smart_insights"] = generate_smart_insights(
        subjects,
        daily_hours
    )

    st.session_state.study_plan_results = results

    return results


def initialize_study_tracker():

    if "study_log" not in st.session_state:
        st.session_state.study_log = {}

    if "study_plan_results" not in st.session_state:
        st.session_state.study_plan_results = None


# ============================================================
# STUDY LOG DATABASE HELPERS
# ============================================================

def save_study_log(
    user_id,
    study_date,
    subject_name,
    actual_hours
):

    try:

        payload = {
            "user_id": str(user_id),
            "study_date": study_date.isoformat(),
            "subject_name": subject_name,
            "actual_hours": float(actual_hours)
        }

        supabase.table("study_logs").insert(
            payload
        ).execute()

        return True

    except Exception as exc:

        st.error("Could not save study hours to Supabase.")
        st.exception(exc)

        return False


def load_study_logs(user_id):

    try:

        response = (
            supabase.table("study_logs")
            .select("*")
            .eq("user_id", str(user_id))
            .order("study_date", desc=False)
            .execute()
        )

        return response.data or []

    except Exception as exc:

        st.error("Could not load study history from Supabase.")
        st.exception(exc)

        return []


# ============================================================
# INTERVIEW HISTORY DATABASE HELPERS
# ============================================================

def load_interview_history(user_id):

    try:

        response = (
            supabase.table("interview_attempts")
            .select("*")
            .eq("user_id", str(user_id))
            .order("created_at", desc=True)
            .limit(100)
            .execute()
        )

        return response.data or []

    except Exception as exc:

        st.warning("Interview history could not be loaded.")
        return []


def save_interview_attempt(
    user_id,
    question,
    answer,
    evaluation
):

    try:

        payload = {
            "user_id": str(user_id),
            "question": question,
            "answer": answer,
            "score": evaluation.get("score", 0),
            "matched_keywords": evaluation.get(
                "matched_keywords", []
            ),
            "missing_keywords": evaluation.get(
                "missing_keywords", []
            ),
            "strengths": evaluation.get("strengths", []),
            "improvements": evaluation.get("improvements", [])
        }

        supabase.table("interview_attempts").insert(
            payload
        ).execute()

        return True

    except Exception as exc:

        st.error("Could not save interview attempt.")
        st.exception(exc)

        return False


def delete_interview_history(user_id):

    try:

        supabase.table("interview_attempts").delete().eq(
            "user_id",
            str(user_id)
        ).execute()

        st.session_state.interview_attempts = []

        return True

    except Exception as exc:

        st.error("Could not delete interview history.")
        st.exception(exc)

        return False


# ============================================================
# CHATBOT
# ============================================================

def get_student_chatbot_response(message):

    message = message.lower().strip()

    if any(word in message for word in [
        "hello", "hi", "hey", "good morning", "good evening"
    ]):
        return (
            "Hello! 👋 Welcome to your AI Student Assistant. "
            "I can help you with Python, DSA, academics, "
            "placements, resumes and career planning."
        )

    elif "python" in message:

        return """
        **Python Learning Roadmap**

        1. Variables and data types
        2. Operators and expressions
        3. Conditional statements
        4. Loops
        5. Functions
        6. Lists, tuples, sets and dictionaries
        7. File handling
        8. OOP concepts
        9. Exception handling
        10. Projects and problem-solving
        """

    elif "oops" in message or "object oriented" in message:

        return """
        **Object-Oriented Programming Concepts**

        - Class: Blueprint for creating objects.
        - Object: Instance of a class.
        - Inheritance: Reusing properties and methods.
        - Polymorphism: One interface with multiple implementations.
        - Encapsulation: Combining data and methods.
        - Abstraction: Hiding implementation details.
        """

    elif "dsa" in message or "data structure" in message:

        return """
        **DSA Preparation Roadmap**

        1. Arrays and strings
        2. Searching and sorting
        3. Hashing
        4. Two pointers
        5. Sliding window
        6. Stack and queue
        7. Linked lists
        8. Trees and binary search trees
        9. Graphs
        10. Dynamic programming

        Practise problems regularly and analyse time and space complexity.
        """

    elif "dbms" in message or "sql" in message:

        return """
        **Important DBMS Topics**

        - Database architecture
        - ER diagrams
        - Primary and foreign keys
        - Normalization
        - SQL queries
        - Joins
        - Transactions
        - ACID properties
        - Indexing
        - Concurrency control
        """

    elif "operating system" in message or "os" in message:

        return """
        **Operating System Topics**

        - Process management
        - CPU scheduling
        - Threads
        - Deadlocks
        - Memory management
        - Paging and segmentation
        - Virtual memory
        - File systems
        """

    elif "network" in message:

        return """
        **Computer Networks Topics**

        - OSI model
        - TCP/IP model
        - IP addressing
        - Routing
        - Switching
        - TCP and UDP
        - DNS
        - HTTP and HTTPS
        - Network security
        """

    elif "placement" in message or "job" in message:

        return """
        **Placement Preparation Plan**

        1. Strengthen one programming language.
        2. Practise DSA regularly.
        3. Study DBMS, OS and Computer Networks.
        4. Prepare OOP concepts.
        5. Build practical projects.
        6. Improve aptitude and reasoning.
        7. Prepare your resume.
        8. Practise technical and HR interviews.
        """

    elif "resume" in message:

        return """
        **Resume Improvement Tips**

        - Use a clear professional format.
        - Add relevant technical skills.
        - Include measurable project outcomes.
        - Mention internships and practical experience.
        - Use action verbs.
        - Avoid spelling and grammar mistakes.
        - Tailor your resume to the target job.
        """

    elif "artificial intelligence" in message or "ai/ml" in message or "machine learning" in message:

        return """
        **AI/ML Learning Roadmap**

        1. Python programming
        2. Mathematics and statistics
        3. NumPy and Pandas
        4. Data visualization
        5. Scikit-learn
        6. Supervised learning
        7. Unsupervised learning
        8. Model evaluation
        9. Deep learning
        10. Real-world AI projects
        """

    elif "project" in message:

        return """
        **Project Ideas for CSE-AI Students**

        - AI Resume Analyzer
        - AI Study Planner
        - Student Performance Prediction
        - Fake News Detection
        - Chatbot for College Enquiries
        - Personal Finance Tracker
        - Smart Attendance System
        - Career Recommendation System
        """

    elif "study" in message or "timetable" in message:

        return """
        **Effective Study Strategy**

        - Set daily learning targets.
        - Prioritize difficult subjects.
        - Divide topics into smaller tasks.
        - Practise active recall.
        - Revise regularly.
        - Solve previous-year questions.
        - Track your progress.
        """

    elif "interview" in message:

        return """
        **Interview Preparation**

        Prepare these areas:

        - Python or your preferred language
        - DSA
        - OOP
        - DBMS and SQL
        - Operating Systems
        - Computer Networks
        - Projects and internships
        - HR questions
        """

    elif "thank" in message:

        return "You're welcome! Keep learning and keep building. 🚀"

    else:

        return """
        I can help you with:

        - Python programming
        - DSA
        - DBMS and SQL
        - Operating Systems
        - Computer Networks
        - Artificial Intelligence and Machine Learning
        - Resume preparation
        - Interview preparation
        - Study planning
        - Project ideas

        Try asking me a question about one of these topics!
        """


# ============================================================
# CHAT HISTORY DATABASE HELPERS
# ============================================================

def load_chat_history(user_id):

    try:

        response = (
            supabase.table("assistant_chat_messages")
            .select("*")
            .eq("user_id", str(user_id))
            .order("created_at", desc=False)
            .limit(100)
            .execute()
        )

        return response.data or []

    except Exception:
        return []


def save_chat_message(user_id, role, content):

    try:

        supabase.table("assistant_chat_messages").insert({
            "user_id": str(user_id),
            "role": role,
            "content": content
        }).execute()

    except Exception:
        pass


# ============================================================
# SMALL DISPLAY HELPERS
# ============================================================

def show_metric(label, value):

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-value">{escape(str(value))}</div>
            <div class="metric-label">{escape(str(label))}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def show_page_title(title, subtitle=""):

    st.markdown(
        f'<div class="main-title">{title}</div>',
        unsafe_allow_html=True
    )

    if subtitle:
        st.markdown(
            f'<div class="subtitle">{subtitle}</div>',
            unsafe_allow_html=True
        )


# ============================================================
# AUTHENTICATION GATE
# ============================================================

if st.session_state.auth_user is None:

    show_auth_page()
    st.stop()


if not restore_supabase_session():

    clear_auth_state()
    st.rerun()


user = st.session_state.auth_user
user_id = user.id
user_email = getattr(user, "email", "") or ""


# ============================================================
# LOAD USER PROFILE
# ============================================================

profile = load_profile(user_id)

user_name = (
    profile.get("full_name")
    or getattr(user, "user_metadata", {}).get("full_name", "")
    or user_email.split("@")[0]
)

user_course = profile.get("course", "Not specified")
user_year = profile.get("study_year", "Not specified")


# ============================================================
# LOAD INTERVIEW HISTORY
# ============================================================

if st.session_state.interview_loaded_user != str(user_id):

    st.session_state.interview_attempts = load_interview_history(
        user_id
    )

    st.session_state.interview_loaded_user = str(user_id)


# ============================================================
# HEADER AND NAVIGATION
# ============================================================

st.markdown("""
<div class="hero">
    <h1>🎓 AI Student Career & Academic Assistant</h1>
    <p>
        Your personal workspace for academic planning,
        resume insights and career readiness.
    </p>
</div>
""", unsafe_allow_html=True)


with st.sidebar:

    st.markdown("## 🎓 Student Assistant")

    st.markdown("---")

    st.markdown(f"### Welcome, {escape(user_name)}")

    st.caption(user_email)

    st.markdown("---")

    module = st.radio(
        "Navigation",
        [
            "👤 My Profile",
            "🏠 Dashboard",
            "📚 AI Study Planner",
            "📄 AI Resume Analyzer",
            "📑 PDF Study Assistant",
            "💼 Career & Interview Coach",
            "🤖 Student Chatbot"
        ]
    )

    st.markdown("---")

    st.markdown("### Your Workspace")

    st.caption("Academic planning • Career readiness")

    if st.button("🚪 Logout", use_container_width=True):

        try:
            supabase.auth.sign_out()
        except Exception:
            pass

        clear_auth_state()
        st.rerun()


# ============================================================
# MODULE 1: MY PROFILE
# ============================================================

if module == "👤 My Profile":

    show_page_title(
        "👤 My Profile",
        "Manage your academic and personal information."
    )

    with st.form("profile_form"):

        full_name = st.text_input(
            "Full name",
            value=user_name
        )

        email = st.text_input(
            "Email address",
            value=user_email,
            disabled=True
        )

        course = st.text_input(
            "Course",
            value=user_course
        )

        study_year = st.selectbox(
            "Study year",
            [
                "1st Year",
                "2nd Year",
                "3rd Year",
                "4th Year"
            ],
            index=[
                "1st Year",
                "2nd Year",
                "3rd Year",
                "4th Year"
            ].index(user_year)
            if user_year in [
                "1st Year",
                "2nd Year",
                "3rd Year",
                "4th Year"
            ] else 2
        )

        submitted = st.form_submit_button(
            "💾 Save Profile",
            use_container_width=True
        )

        if submitted:

            if save_profile(
                user_id,
                full_name,
                course,
                study_year
            ):

                st.success("Profile updated successfully!")
                st.rerun()

    st.markdown("---")

    st.markdown("### Account Information")

    col1, col2 = st.columns(2)

    with col1:
        show_metric("Account", "Active")

    with col2:
        show_metric("Course", course)


# ============================================================
# MODULE 2: DASHBOARD
# ============================================================

elif module == "🏠 Dashboard":

    show_page_title(
        "🏠 Dashboard",
        "Your academic and career progress at a glance."
    )

    st.markdown("""
    <div class="card">
        <h3>Welcome to your Student Workspace 👋</h3>
        <p>
        Plan your studies, improve your resume, practise interviews
        and prepare for your future career using one integrated platform.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        show_metric("Available Modules", "7")

    with col2:
        show_metric(
            "Interview Attempts",
            len(st.session_state.interview_attempts)
        )

    with col3:
        show_metric(
            "Study Plan",
            "Created" if st.session_state.study_plan_results else "Not Created"
        )

    st.markdown('<div class="section-heading">Explore Features</div>',
                unsafe_allow_html=True)

    feature_data = [
        ("📚 AI Study Planner", "Create a structured study timetable."),
        ("📄 AI Resume Analyzer", "Analyse skills and improve your resume."),
        ("📑 PDF Study Assistant", "Ask questions from your study material."),
        ("💼 Career Coach", "Explore career paths and practise interviews."),
        ("🤖 Student Chatbot", "Get help with academic and technical topics."),
        ("📈 Study Analytics", "Monitor your learning progress.")
    ]

    cols = st.columns(3)

    for index, (title, description) in enumerate(feature_data):

        with cols[index % 3]:

            st.markdown(
                f"""
                <div class="card">
                    <h3>{title}</h3>
                    <p>{description}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown('<div class="section-heading">Recommended Actions</div>',
                unsafe_allow_html=True)

    st.info(
        "Start by creating a study plan, analysing your resume "
        "and practising technical interview questions."
    )


# ============================================================
# MODULE 3: AI STUDY PLANNER
# ============================================================

elif module == "📚 AI Study Planner":

    initialize_study_tracker()

    show_page_title(
        "📚 AI Study Planner",
        "Create, manage and adapt your personalized study schedule."
    )
    
    with st.expander("➕ Create a New Study Plan", expanded=True):
        # Keep subject count OUTSIDE the form
        subject_count = st.number_input(
            "Number of subjects",
            min_value=1,
            max_value=10,
            value=3,
            step=1,
            key="study_subject_count"
        )

    with st.form("study_plan_form"):

        col1, col2 = st.columns(2)

        with col1:
            daily_hours = st.number_input(
                "Daily available study hours",
                min_value=0.5,
                max_value=16.0,
                value=4.0,
                step=0.5
            )

        with col2:
            schedule_days = st.selectbox(
                "Schedule duration",
                [3, 5, 7],
                index=2
            )

        valid_subjects = []

        for i in range(int(subject_count)):

            st.markdown(f"#### Subject {i + 1}")

            col1, col2 = st.columns(2)

            with col1:

                subject_name = st.text_input(
                    "Subject name",
                    key=f"subject_name_{i}"
                )

                difficulty = st.selectbox(
                    "Difficulty",
                    ["Easy", "Medium", "Hard"],
                    key=f"difficulty_{i}"
                )

                deadline = st.date_input(
                    "Exam / completion deadline",
                    value=date.today() + timedelta(days=14),
                    min_value=date.today(),
                    key=f"deadline_{i}"
                )

            with col2:

                total_topics = st.number_input(
                    "Total topics",
                    min_value=1,
                    max_value=200,
                    value=10,
                    key=f"total_topics_{i}"
                )

                completed_topics = st.number_input(
                    "Completed topics",
                    min_value=0,
                    max_value=200,
                    value=0,
                    key=f"completed_topics_{i}"
                )

                estimated_hours = st.number_input(
                    "Estimated total study hours",
                    min_value=1.0,
                    max_value=500.0,
                    value=10.0,
                    key=f"estimated_hours_{i}"
                )

            if subject_name.strip():

                valid_subjects.append({
                    "name": subject_name.strip(),
                    "difficulty": difficulty,
                    "deadline": deadline,
                    "total_topics": int(total_topics),
                    "completed_topics": int(completed_topics),
                    "remaining_topics": max(
                        0,
                        int(total_topics) - int(completed_topics)
                    ),
                    "estimated_hours": float(estimated_hours)
                })

        submitted = st.form_submit_button(
            "🚀 Generate Study Plan",
            use_container_width=True
        )

        if submitted:

            if not valid_subjects:

                st.error("Enter at least one subject.")

            else:

                results = {
                    "subjects": valid_subjects,
                    "daily_hours": float(daily_hours),
                    "days": int(schedule_days)
                }

                results = rebuild_study_plan(results)

                st.session_state.study_plan_results = results

                st.success("Your study plan has been generated!")
                st.rerun()


                

    results = st.session_state.study_plan_results

    if results:

        subjects = results["subjects"]

        # ----------------------------------------------------
        # STUDY PLAN OVERVIEW
        # ----------------------------------------------------

        st.markdown(
            '<div class="section-heading">📊 Study Overview</div>',
            unsafe_allow_html=True
        )

        total_subjects = len(subjects)

        total_topics = sum(
            s["total_topics"] for s in subjects
        )

        completed_topics = sum(
            s["completed_topics"] for s in subjects
        )

        pending_topics = max(
            0,
            total_topics - completed_topics
        )

        progress = (
            completed_topics / total_topics * 100
            if total_topics else 0
        )

        remaining_hours = sum(
            (
                s["estimated_hours"]
                * s["remaining_topics"]
                / max(s["total_topics"], 1)
            )
            for s in subjects
        )

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            show_metric("Subjects", total_subjects)

        with c2:
            show_metric("Completed Topics", completed_topics)

        with c3:
            show_metric("Pending Topics", pending_topics)

        with c4:
            show_metric("Remaining Hours", round(remaining_hours, 1))

        st.progress(progress / 100)

        st.caption(f"Overall completion: {progress:.1f}%")

        # ----------------------------------------------------
        # STUDY PLAN TABS
        # ----------------------------------------------------

        tab1, tab2, tab3, tab4 = st.tabs([
            "📌 Priority Plan",
            "📅 Timetable",
            "💡 Recommendations",
            "🧠 Smart Insights"
        ])

        # ---------------- PRIORITY PLAN ----------------

        with tab1:

            st.markdown("### Subject Priority")

            for subject in sorted(
                subjects,
                key=lambda s: (
                    s["deadline"] - date.today()
                ).days
            ):

                days_left = (
                    subject["deadline"] - date.today()
                ).days

                subject_progress = (
                    subject["completed_topics"]
                    / max(subject["total_topics"], 1)
                )

                st.markdown(
                    f"""
                    <div class="card">
                        <h3>{escape(subject['name'])}</h3>
                        <p>
                        Difficulty: {subject['difficulty']} |
                        Deadline: {subject['deadline']} |
                        Days remaining: {days_left}
                        </p>
                        <p>
                        Completed:
                        {subject['completed_topics']}/
                        {subject['total_topics']} topics
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.progress(subject_progress)

            priority_data = []

            for subject in subjects:

                priority_data.append({
                    "Subject": subject["name"],
                    "Difficulty": subject["difficulty"],
                    "Deadline": str(subject["deadline"]),
                    "Total Topics": subject["total_topics"],
                    "Completed": subject["completed_topics"],
                    "Remaining": subject["remaining_topics"],
                    "Estimated Hours": subject["estimated_hours"]
                })

            priority_df = pd.DataFrame(priority_data)

            st.download_button(
                "⬇️ Download Priority Plan",
                priority_df.to_csv(index=False),
                file_name="study_priority_plan.csv",
                mime="text/csv"
            )

        # ---------------- TIMETABLE ----------------

        with tab2:

            st.markdown("### Generated Timetable")

            weekly = results.get("weekly")

            if isinstance(weekly, pd.DataFrame):

                st.dataframe(
                    weekly,
                    use_container_width=True,
                    hide_index=True
                )

                st.download_button(
                    "⬇️ Download Timetable",
                    weekly.to_csv(index=False),
                    file_name="study_timetable.csv",
                    mime="text/csv"
                )

            elif isinstance(weekly, list):

                if weekly:

                    weekly_df = pd.DataFrame(weekly)

                    st.dataframe(
                        weekly_df,
                        use_container_width=True,
                        hide_index=True
                    )

                    st.download_button(
                        "⬇️ Download Timetable",
                        weekly_df.to_csv(index=False),
                        file_name="study_timetable.csv",
                        mime="text/csv"
                    )

                else:
                    st.info("No timetable entries were generated.")

            else:

                st.write(weekly)

        # ---------------- RECOMMENDATIONS ----------------

        with tab3:

            st.markdown("### Personalized Recommendations")

            recommendations = results.get(
                "recommendations",
                []
            )

            if isinstance(recommendations, list):

                for recommendation in recommendations:
                    st.info(str(recommendation))

            elif recommendations:

                st.write(recommendations)

            else:

                st.info("No recommendations available.")

        # ---------------- SMART INSIGHTS ----------------

        with tab4:

            st.markdown("### Smart Study Insights")

            insights = results.get("smart_insights", [])

            if isinstance(insights, list):

                for insight in insights:
                    st.info(str(insight))

            elif insights:

                st.write(insights)

            else:

                st.info("No additional insights available.")

            st.markdown("### Subject Progress")

            for subject in subjects:

                st.write(
                    f"**{subject['name']}** — "
                    f"{subject['completed_topics']}/"
                    f"{subject['total_topics']} topics"
                )

                st.progress(
                    subject["completed_topics"]
                    / max(subject["total_topics"], 1)
                )

        # ----------------------------------------------------
        # SUBJECT PROGRESS TRACKER
        # ----------------------------------------------------

        st.markdown(
            '<div class="section-heading">📈 Subject Progress Tracker</div>',
            unsafe_allow_html=True
        )

        with st.form("progress_update_form"):

            progress_updates = {}

            for index, subject in enumerate(subjects):

                progress_updates[index] = st.number_input(
                    f"{subject['name']} — Completed topics",
                    min_value=0,
                    max_value=int(subject["total_topics"]),
                    value=int(subject["completed_topics"]),
                    key=f"progress_update_{index}"
                )

            update_progress = st.form_submit_button(
                "Update Progress",
                use_container_width=True
            )

            if update_progress:

                for index, subject in enumerate(subjects):

                    subject["completed_topics"] = int(
                        progress_updates[index]
                    )

                    subject["remaining_topics"] = max(
                        0,
                        subject["total_topics"]
                        - subject["completed_topics"]
                    )

                rebuild_study_plan(results)

                st.success("Study progress updated!")
                st.rerun()

        # ----------------------------------------------------
        # DAILY STUDY HOURS TRACKER
        # ----------------------------------------------------

        st.markdown(
            '<div class="section-heading">⏱️ Daily Study-Hours Tracker</div>',
            unsafe_allow_html=True
        )

        if st.session_state.study_history_loaded_user != str(user_id):

            st.session_state.study_history = load_study_logs(user_id)

            st.session_state.study_history_loaded_user = str(user_id)

        col1, col2 = st.columns(2)

        with col1:

            selected_date = st.date_input(
                "Study date",
                value=date.today(),
                key="daily_study_date"
            )

        with col2:

            selected_subject = st.selectbox(
                "Select subject",
                [s["name"] for s in subjects],
                key="daily_study_subject"
            )

        actual_hours = st.number_input(
            "Actual hours studied",
            min_value=0.0,
            max_value=24.0,
            value=1.0,
            step=0.5,
            key="daily_actual_hours"
        )

        if st.button(
            "➕ Record Study Hours",
            use_container_width=True
        ):

            if actual_hours <= 0:

                st.warning("Enter study hours greater than zero.")

            else:

                saved = save_study_log(
                    user_id,
                    selected_date,
                    selected_subject,
                    actual_hours
                )

                if saved:

                    st.session_state.study_history = load_study_logs(
                        user_id
                    )

                    st.success("Study hours recorded successfully!")
                    st.rerun()

        # ----------------------------------------------------
        # WEEKLY STUDY ANALYTICS
        # ----------------------------------------------------

        st.markdown(
            '<div class="section-heading">📊 Weekly Study Analytics</div>',
            unsafe_allow_html=True
        )

        history = st.session_state.study_history

        if history:

            history_df = pd.DataFrame(history)

            history_df["study_date"] = pd.to_datetime(
                history_df["study_date"]
            )

            history_df["actual_hours"] = pd.to_numeric(
                history_df["actual_hours"],
                errors="coerce"
            ).fillna(0)

            week_start = date.today() - timedelta(
                days=date.today().weekday()
            )

            week_df = history_df[
                history_df["study_date"] >= pd.Timestamp(week_start)
            ]

            if not week_df.empty:

                daily_summary = (
                    week_df.groupby("study_date")["actual_hours"]
                    .sum()
                    .reset_index()
                )

                daily_summary.columns = [
                    "Date",
                    "Actual Study Hours"
                ]

                st.dataframe(
                    daily_summary,
                    use_container_width=True,
                    hide_index=True
                )

                chart_df = daily_summary.set_index("Date")

                st.line_chart(chart_df)

                total_weekly_hours = week_df["actual_hours"].sum()

                show_metric(
                    "Study hours this week",
                    round(total_weekly_hours, 2)
                )

            else:

                st.info(
                    "No study-hour records are available for this week."
                )

            with st.expander("View Complete Study History"):

                st.dataframe(
                    history_df[
                        [
                            "study_date",
                            "subject_name",
                            "actual_hours"
                        ]
                    ],
                    use_container_width=True,
                    hide_index=True
                )

        else:

            st.info(
                "Record your daily study hours to see weekly analytics."
            )

        # ----------------------------------------------------
        # DEADLINE ALERTS
        # ----------------------------------------------------

        st.markdown(
            '<div class="section-heading">🚨 Deadline Alerts</div>',
            unsafe_allow_html=True
        )

        for subject in subjects:

            days_left = (
                subject["deadline"] - date.today()
            ).days

            if subject["remaining_topics"] == 0:

                st.success(
                    f"✅ {subject['name']}: All topics completed."
                )

            elif days_left <= 3:

                st.error(
                    f"🔴 {subject['name']}: Deadline is very close "
                    f"({days_left} days remaining)."
                )

            elif days_left <= 7:

                st.warning(
                    f"🟠 {subject['name']}: Deadline approaching "
                    f"({days_left} days remaining)."
                )

            else:

                st.info(
                    f"🟢 {subject['name']}: {days_left} days remaining."
                )

        # ----------------------------------------------------
        # ADAPTIVE TIMETABLE
        # ----------------------------------------------------

        st.markdown(
            '<div class="section-heading">🔄 Adaptive Timetable</div>',
            unsafe_allow_html=True
        )

        st.write(
            "Regenerate your timetable using your latest subject progress."
        )

        if st.button(
            "🔄 Rebuild My Study Plan",
            use_container_width=True
        ):

            rebuild_study_plan(results)

            st.success("Your timetable has been updated!")
            st.rerun()

        if st.button(
            "🗑️ Clear Study Plan",
            use_container_width=True
        ):

            st.session_state.study_plan_results = None
            st.rerun()

    else:

        st.info(
            "No study plan available. Create a new plan to get started."
        )


# ============================================================
# MODULE 4: AI RESUME ANALYZER
# ============================================================

elif module == "📄 AI Resume Analyzer":

    show_page_title(
        "📄 AI Resume Analyzer",
        "Analyse your resume and identify missing career skills."
    )

    career_goal = st.selectbox(
        "Select your target career",
        list(CAREER_SKILLS.keys())
    )

    uploaded_file = st.file_uploader(
        "Upload your resume in PDF format",
        type=["pdf"]
    )

    if uploaded_file:

        try:

            resume_text = extract_text_from_pdf(uploaded_file)

            if not resume_text:

                st.warning("Could not extract text from the PDF.")

            else:

                analysis = analyze_resume(
                    resume_text,
                    career_goal
                )

                st.session_state.resume_text = resume_text

                st.markdown("### 📊 Resume Analysis")

                score = analysis.get(
                    "score",
                    analysis.get("resume_score", 0)
                )

                col1, col2 = st.columns(2)

                with col1:
                    show_metric("Resume Score", score)

                with col2:
                    show_metric("Target Role", career_goal)

                st.progress(
                    min(max(float(score) / 100, 0), 1)
                )

                st.markdown("### ✅ Matched Skills")

                matched = analysis.get(
                    "matched_skills",
                    analysis.get("matched", [])
                )

                if matched:

                    for skill in matched:
                        st.success(str(skill))

                else:

                    st.info("No matching skills identified.")

                st.markdown("### 📌 Skills to Improve")

                missing = analysis.get(
                    "missing_skills",
                    analysis.get("missing", [])
                )

                if missing:

                    for skill in missing:
                        st.warning(str(skill))

                else:

                    st.success(
                        "Your resume covers the identified target skills."
                    )

                st.markdown("### 💡 Recommendations")

                recommendations = analysis.get(
                    "recommendations",
                    []
                )

                if isinstance(recommendations, list):

                    for recommendation in recommendations:
                        st.info(str(recommendation))

                elif recommendations:

                    st.write(recommendations)

                with st.expander("View Extracted Resume Text"):

                    st.text_area(
                        "Resume content",
                        resume_text,
                        height=300
                    )

        except Exception as exc:

            st.error("Resume analysis failed.")
            st.exception(exc)

    else:

        st.info("Upload your PDF resume to begin analysis.")


# ============================================================
# MODULE 5: PDF STUDY ASSISTANT
# ============================================================

elif module == "📑 PDF Study Assistant":

    show_page_title(
        "📑 PDF Study Assistant",
        "Ask questions and understand your study material."
    )

    uploaded_pdf = st.file_uploader(
        "Upload your study PDF",
        type=["pdf"],
        key="study_pdf"
    )

    if uploaded_pdf:

        try:

            pdf_text = extract_text_from_pdf(uploaded_pdf)

            if not pdf_text:

                st.error("No readable text found in this PDF.")

            else:

                st.session_state.pdf_text = pdf_text

                st.success("PDF uploaded and processed successfully!")

                question = st.text_area(
                    "Ask a question about your PDF",
                    placeholder="Example: Explain the main concepts in this chapter."
                )

                if st.button(
                    "🤖 Ask AI Assistant",
                    use_container_width=True
                ):

                    if not question.strip():

                        st.warning("Enter a question first.")

                    else:

                        with st.spinner("Finding the answer..."):

                            answer = answer_from_pdf(
                                question,
                                pdf_text
                            )

                        st.markdown("### Answer")

                        st.markdown(answer)

                with st.expander("Preview Extracted PDF Text"):

                    st.text_area(
                        "PDF content",
                        pdf_text[:20000],
                        height=350
                    )

                st.download_button(
                    "⬇️ Download Extracted Text",
                    pdf_text,
                    file_name="extracted_study_material.txt",
                    mime="text/plain"
                )

        except Exception as exc:

            st.error("Could not process the PDF.")
            st.exception(exc)

    else:

        st.info("Upload a PDF to start studying with the assistant.")


# ============================================================
# MODULE 6: CAREER & INTERVIEW COACH
# ============================================================

elif module == "💼 Career & Interview Coach":

    show_page_title(
        "💼 Career & Interview Coach",
        "Explore career paths and improve your interview performance."
    )

    tab1, tab2, tab3 = st.tabs([
        "🚀 Career Roadmap",
        "🎯 Interview Practice",
        "🧑‍💼 Mock Interview"
    ])

    # --------------------------------------------------------
    # CAREER ROADMAP
    # --------------------------------------------------------

    with tab1:

        st.markdown("### Explore Career Roadmaps")

        career_options = list(CAREER_ROADMAPS.keys())

        selected_career = st.selectbox(
            "Choose your career path",
            career_options
        )

        roadmap = CAREER_ROADMAPS[selected_career]

        if isinstance(roadmap, dict):

            for section, content in roadmap.items():

                st.markdown(f"#### {section}")

                if isinstance(content, list):

                    for item in content:
                        st.write(f"• {item}")

                else:

                    st.write(content)

        elif isinstance(roadmap, list):

            for item in roadmap:
                st.write(f"• {item}")

        else:

            st.write(roadmap)

    # --------------------------------------------------------
    # INTERVIEW PRACTICE
    # --------------------------------------------------------

    with tab2:

        st.markdown("### Technical Interview Practice")

        interview_categories = list(INTERVIEW_BANK.keys())

        category = st.selectbox(
            "Choose interview category",
            interview_categories
        )

        questions = INTERVIEW_BANK[category]

        if isinstance(questions, dict):

            question_options = list(questions.keys())

            question = st.selectbox(
                "Select a question",
                question_options
            )

            question_data = questions[question]

            st.markdown(f"### {question}")

            if isinstance(question_data, dict):

                reference_answer = question_data.get(
                    "answer",
                    question_data.get("reference_answer", "")
                )

                st.write(
                    question_data.get("description", "")
                )

            else:

                reference_answer = str(question_data)

            with st.expander("View Reference Answer"):

                st.write(reference_answer)

        elif isinstance(questions, list) and questions:

            selected_question = st.selectbox(
                "Select a question",
                questions
            )

            question = selected_question

            reference_answer = ""

            st.markdown(f"### {question}")

        else:

            question = ""
            reference_answer = ""

            st.info("No questions are available in this category.")

        answer = st.text_area(
            "Write your answer",
            height=180,
            key="practice_answer"
        )

        if st.button(
            "Evaluate My Answer",
            use_container_width=True
        ):

            if not question or not answer.strip():

                st.warning("Select a question and enter your answer.")

            else:

                try:

                    evaluation = evaluate_interview_answer(
                        question,
                        answer
                    )

                    st.markdown("### 📊 Evaluation")

                    score = evaluation.get("score", 0)

                    show_metric("Your Score", score)

                    st.progress(
                        min(max(float(score) / 100, 0), 1)
                    )

                    st.markdown("### ✅ Matched Keywords")

                    matched = evaluation.get(
                        "matched_keywords",
                        []
                    )

                    if matched:

                        for item in matched:
                            st.success(str(item))

                    else:

                        st.info("No matched keywords identified.")

                    st.markdown("### 📌 Missing Keywords")

                    missing = evaluation.get(
                        "missing_keywords",
                        []
                    )

                    if missing:

                        for item in missing:
                            st.warning(str(item))

                    st.markdown("### 💪 Strengths")

                    for item in evaluation.get("strengths", []):
                        st.success(str(item))

                    st.markdown("### 🔧 Areas to Improve")

                    for item in evaluation.get("improvements", []):
                        st.info(str(item))

                    saved = save_interview_attempt(
                        user_id,
                        question,
                        answer,
                        evaluation
                    )

                    if saved:

                        st.session_state.interview_attempts = (
                            load_interview_history(user_id)
                        )

                        st.success("Your interview attempt has been saved.")

                except Exception as exc:

                    st.error("Answer evaluation failed.")
                    st.exception(exc)

    # --------------------------------------------------------
    # MOCK INTERVIEW
    # --------------------------------------------------------

    with tab3:

        st.markdown("### 🧑‍💼 Mock Interview")

        mock_questions = [
            "Tell me about yourself.",
            "What are your strengths and weaknesses?",
            "Why should we hire you?",
            "Explain your final-year or academic project.",
            "Where do you see yourself in five years?",
            "Why are you interested in this role?",
            "Describe a challenging problem you solved.",
            "How do you handle working under pressure?"
        ]

        mock_question = st.selectbox(
            "Choose an HR interview question",
            mock_questions
        )

        st.info(mock_question)

        mock_answer = st.text_area(
            "Your response",
            height=180,
            key="mock_answer"
        )

        if st.button(
            "Evaluate Mock Interview Answer",
            use_container_width=True
        ):

            if not mock_answer.strip():

                st.warning("Enter your answer first.")

            else:

                try:

                    evaluation = evaluate_interview_answer(
                        mock_question,
                        mock_answer
                    )

                    st.markdown("### Your Performance")

                    score = evaluation.get("score", 0)

                    show_metric("Interview Score", score)

                    st.progress(
                        min(max(float(score) / 100, 0), 1)
                    )

                    st.markdown("### Strengths")

                    for item in evaluation.get("strengths", []):
                        st.success(str(item))

                    st.markdown("### Improvements")

                    for item in evaluation.get("improvements", []):
                        st.info(str(item))

                    if save_interview_attempt(
                        user_id,
                        mock_question,
                        mock_answer,
                        evaluation
                    ):

                        st.session_state.interview_attempts = (
                            load_interview_history(user_id)
                        )

                except Exception as exc:

                    st.error("Mock interview evaluation failed.")
                    st.exception(exc)

    # --------------------------------------------------------
    # INTERVIEW HISTORY
    # --------------------------------------------------------

    st.markdown("---")

    st.markdown("### 📚 Interview History")

    attempts = st.session_state.interview_attempts

    if attempts:

        history_data = []

        for attempt in attempts:

            history_data.append({
                "Question": attempt.get("question", ""),
                "Score": attempt.get("score", 0),
                "Date": attempt.get("created_at", "")
            })

        history_df = pd.DataFrame(history_data)

        st.dataframe(
            history_df,
            use_container_width=True,
            hide_index=True
        )

        scores = pd.to_numeric(
            history_df["Score"],
            errors="coerce"
        ).fillna(0)

        col1, col2 = st.columns(2)

        with col1:
            show_metric("Total Attempts", len(attempts))

        with col2:
            show_metric(
                "Average Score",
                round(scores.mean(), 1)
            )

        st.line_chart(scores.reset_index(drop=True))

        if st.button(
            "🗑️ Clear Interview History",
            use_container_width=True
        ):

            if delete_interview_history(user_id):

                st.success("Interview history cleared.")
                st.rerun()

    else:

        st.info("Your interview attempts will appear here.")


# ============================================================
# MODULE 7: STUDENT CHATBOT
# ============================================================

elif module == "🤖 Student Chatbot":

    show_page_title(
        "🤖 Student Chatbot",
        "Your academic and career guidance assistant."
    )

    if st.session_state.chat_history_loaded_user != str(user_id):

        saved_messages = load_chat_history(user_id)

        st.session_state.chat_messages = [
            {
                "role": item.get("role", "assistant"),
                "content": item.get("content", "")
            }
            for item in saved_messages
            if item.get("role") in ["user", "assistant"]
        ]

        st.session_state.chat_history_loaded_user = str(user_id)

    st.markdown("""
    <div class="card">
        <h3>How can I help you today? 👋</h3>
        <p>
        Ask questions about Python, DSA, DBMS, AI/ML,
        placements, resumes, projects or study planning.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Display previous messages

    for message in st.session_state.chat_messages:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

    # Chat input

    user_message = st.chat_input(
        "Ask your academic or career question..."
    )

    if user_message:

        st.session_state.chat_messages.append({
            "role": "user",
            "content": user_message
        })

        save_chat_message(
            user_id,
            "user",
            user_message
        )

        with st.chat_message("user"):
            st.markdown(user_message)

        response = get_student_chatbot_response(
            user_message
        )

        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": response
        })

        save_chat_message(
            user_id,
            "assistant",
            response
        )

        with st.chat_message("assistant"):
            st.markdown(response)

        st.rerun()

    if st.button(
        "🗑️ Clear Chat",
        use_container_width=True
    ):

        st.session_state.chat_messages = []

        try:

            supabase.table(
                "assistant_chat_messages"
            ).delete().eq(
                "user_id",
                str(user_id)
            ).execute()

        except Exception:
            pass

        st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.markdown(
    """
    <div style="text-align:center;color:#718096;padding:15px;">
        <b>AI Student Career & Academic Assistant</b><br>
        Unified Academic Planning and Career Assessment<br>
        Built with Python, Streamlit and Supabase
    </div>
    """,
    unsafe_allow_html=True
)
