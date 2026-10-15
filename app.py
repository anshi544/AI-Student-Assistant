import streamlit as st
from datetime import date
from html import escape
from supabase import create_client, Client

from planner import generate_plan, generate_weekly_plan, get_study_recommendations
from resume_analyzer import extract_text_from_pdf, analyze_resume, CAREER_SKILLS


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="AI Student Assistant",
    page_icon="🎓",
    layout="wide",
)

# --------------------------------------------------
# VISUAL DESIGN SYSTEM — MODERN AI DASHBOARD
# --------------------------------------------------
st.markdown(
    """
    <style>
    :root {
        --ink: #14213d;
        --muted: #64748b;
        --blue: #2563eb;
        --cyan: #06b6d4;
        --surface: #ffffff;
        --line: #e2e8f0;
    }
    .stApp {
        background:
            radial-gradient(circle at 95% 0%, rgba(37, 99, 235, 0.07), transparent 25rem),
            #f7f9fd;
    }
    [data-testid="stHeader"] {
        background: rgba(247, 249, 253, 0.88);
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }
    h1, h2, h3 {
        color: #14213d;
        letter-spacing: -0.025em;
    }
    h1 { font-weight: 800; }
    h2, h3 { font-weight: 750; }
    p, label, .stCaption {
        color: #475569;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #101d3a 0%, #172b50 100%);
        border-right: 1px solid rgba(255,255,255,0.08);
    }
    [data-testid="stSidebar"] * {
        color: #f8fafc;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        border-radius: 10px;
        padding: 0.35rem 0.45rem;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #dbeafe;
    }
    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.15);
    }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 18px;
        border-color: #e2e8f0;
        background: rgba(255,255,255,0.88);
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.035);
    }
    div.stButton > button,
    div[data-testid="stFormSubmitButton"] > button {
        border-radius: 10px;
        font-weight: 650;
        min-height: 2.65rem;
        transition: all 0.18s ease;
    }
    div.stButton > button[kind="primary"],
    div[data-testid="stFormSubmitButton"] > button[kind="primary"] {
        border: 0;
        background: linear-gradient(110deg, #2563eb, #0891b2);
        color: white;
    }
    div.stButton > button:hover,
    div[data-testid="stFormSubmitButton"] > button:hover {
        border-color: #2563eb;
        transform: translateY(-1px);
    }
    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea,
    [data-testid="stNumberInput"] input,
    [data-testid="stDateInput"] input,
    [data-testid="stSelectbox"] [data-baseweb="select"] > div {
        border-radius: 10px;
    }
    [data-testid="stMetric"] {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 15px;
        padding: 1rem 1.1rem;
        box-shadow: 0 5px 18px rgba(15, 23, 42, 0.035);
    }
    [data-testid="stTabs"] button {
        font-weight: 650;
    }
    .app-eyebrow {
        color: #2563eb;
        font-size: 0.76rem;
        font-weight: 800;
        letter-spacing: 0.13em;
        text-transform: uppercase;
        margin-bottom: 0.45rem;
    }
    .app-hero {
        padding: 1.7rem 1.8rem;
        border-radius: 22px;
        color: white;
        background: linear-gradient(115deg, #101d3a 0%, #1e40af 58%, #0891b2 100%);
        box-shadow: 0 16px 38px rgba(30, 64, 175, 0.18);
        margin: 0.5rem 0 1.4rem 0;
    }
    .app-hero h2 {
        color: white;
        margin: 0.25rem 0 0.45rem 0;
        font-size: clamp(1.65rem, 3vw, 2.35rem);
    }
    .app-hero p {
        color: #e0f2fe;
        margin: 0;
        max-width: 760px;
        line-height: 1.6;
    }
    .app-hero .hero-tag {
        display: inline-block;
        color: #e0f2fe;
        border: 1px solid rgba(255,255,255,0.28);
        border-radius: 999px;
        padding: 0.25rem 0.65rem;
        font-size: 0.78rem;
        margin-bottom: 0.35rem;
    }
    .feature-card {
        height: 100%;
        min-height: 185px;
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 18px;
        padding: 1.25rem;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04);
    }
    .feature-card .icon {
        display: inline-flex;
        width: 2.6rem;
        height: 2.6rem;
        align-items: center;
        justify-content: center;
        border-radius: 12px;
        background: #eff6ff;
        font-size: 1.35rem;
        margin-bottom: 0.75rem;
    }
    .feature-card h3 {
        font-size: 1.05rem;
        margin: 0 0 0.45rem 0;
        color: #14213d;
    }
    .feature-card p {
        color: #64748b;
        font-size: 0.92rem;
        line-height: 1.55;
        margin: 0;
    }
    .section-label {
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.1em;
        color: #64748b;
        text-transform: uppercase;
        margin: 1.1rem 0 0.7rem 0;
    }
    @media (max-width: 700px) {
        .block-container { padding-top: 1rem; }
        .app-hero { padding: 1.25rem; border-radius: 16px; }
        .feature-card { min-height: auto; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# SUPABASE CONNECTION
# --------------------------------------------------
@st.cache_resource
def get_supabase_client() -> Client:
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"],
    )


try:
    supabase = get_supabase_client()
except Exception:
    st.error(
        "Supabase connection could not be initialized. "
        "Check SUPABASE_URL and SUPABASE_KEY in Streamlit Cloud → Settings → Secrets."
    )
    st.stop()


# --------------------------------------------------
# SESSION HELPERS
# --------------------------------------------------
if "auth_user" not in st.session_state:
    st.session_state.auth_user = None
if "auth_access_token" not in st.session_state:
    st.session_state.auth_access_token = None
if "auth_refresh_token" not in st.session_state:
    st.session_state.auth_refresh_token = None


def set_logged_in(session):
    st.session_state.auth_user = session.user
    st.session_state.auth_access_token = session.access_token
    st.session_state.auth_refresh_token = session.refresh_token


def restore_supabase_session():
    access_token = st.session_state.get("auth_access_token")
    refresh_token = st.session_state.get("auth_refresh_token")
    if access_token and refresh_token:
        try:
            supabase.auth.set_session(access_token, refresh_token)
            return True
        except Exception:
            st.session_state.auth_user = None
            st.session_state.auth_access_token = None
            st.session_state.auth_refresh_token = None
    return False


def get_student_chatbot_response(message: str) -> str:
    """Return a topic-based response without calling an external AI API."""
    text = " ".join((message or "").lower().strip().split())
    if not text:
        return "Please type a question so I can help. You can ask about Python, DSA, placements, careers, AI/ML, or study planning."

    rules = [
        (("hello", "hi", "hey", "good morning", "good evening"),
         """Hello! 👋 I'm your Student Assistant chatbot. I can help with study planning, Python, DSA, placements, career skills, and AI/ML. What would you like to work on today?"""),
        (("python", "learn programming", "programming basics", "coding basics"),
         """🐍 **Python learning path**

1. Learn variables, data types, input/output, and operators.
2. Practise conditions, loops, and functions.
3. Learn strings, lists, tuples, sets, and dictionaries.
4. Practise file handling, exceptions, and basic modules.
5. Solve small problems daily and then move to DSA.

**Practice task:** Write a program that counts vowels in a string, then try it with different inputs."""),
        (("dsa", "data structures", "algorithms", "leetcode", "coding interview"),
         """💻 **DSA preparation path**

Start with time complexity, arrays, strings, and hashing. Then study linked lists, stacks, queues, binary search, sorting, recursion, trees, heaps, graphs, and dynamic programming.

A useful daily routine is 20 minutes of concept revision, 45–60 minutes solving 1–2 problems, and 10 minutes reviewing mistakes. Focus on understanding the approach before memorizing code."""),
        (("placement", "interview", "job preparation", "campus drive", "aptitude"),
         """🚀 **Placement preparation plan**

- **Technical:** Python fundamentals, OOP, DSA, DBMS, SQL, operating systems, and computer networks.
- **Aptitude:** percentages, ratios, averages, time and work, logical reasoning, and verbal ability.
- **Projects:** explain the problem, your contribution, tools used, workflow, limitations, and future improvements.
- **HR:** prepare a concise introduction, project explanation, strengths, and examples of teamwork.

Practise a few aptitude questions and one coding problem each day, and revise your resume before the drive."""),
        (("career", "career path", "which field", "job role", "career goal"),
         """💼 **Choosing a career path**

- **Software development:** Python or Java, DSA, OOP, Git, APIs, and databases.
- **Data analytics:** Excel, SQL, statistics, Python, and Power BI/Tableau.
- **AI/ML:** Python, statistics, linear algebra basics, data preparation, model evaluation, and projects.
- **Web development:** HTML, CSS, JavaScript, a frontend framework, APIs, and databases.

Choose one target role first, review several job descriptions, identify repeated skills, and build a small project that demonstrates them."""),
        (("machine learning", " ai/ml", "ai ml", "artificial intelligence", "deep learning", "neural network"),
         """🤖 **AI/ML learning path**

1. Strengthen Python and core libraries such as NumPy and pandas.
2. Learn descriptive statistics, probability, and basic linear algebra.
3. Study supervised learning: linear/logistic regression, decision trees, random forests, and SVM.
4. Learn model evaluation, overfitting, train/test splits, and data leakage.
5. Build projects, document your results, and explain limitations.

Start with a small, well-understood dataset before moving to deep learning."""),
        (("resume", "cv", "skills", "skill gap", "resume analyzer"),
         """📄 **Improve your resume**

- Tailor the skills and project descriptions to the role you're applying for.
- Describe projects with the problem, tools, your actions, and measurable results where you can support them.
- Include only skills you can explain and demonstrate.
- Keep formatting consistent and proofread carefully.

You can use the **AI Resume Analyzer** module in this app to compare detected resume skills with a selected role checklist. Its coverage score is a checklist match, not a hiring prediction."""),
        (("study plan", "study schedule", "timetable", "manage time", "exam preparation", "study"),
         """📚 **Build a practical study routine**

1. List subjects, exam dates, and difficult topics.
2. Prioritize urgent and challenging subjects.
3. Divide available time into focused blocks of 25–50 minutes, with short breaks.
4. Reserve time for active recall, practice questions, and revision.
5. Review progress daily and adjust the next day's plan.

Open **AI Study Planner** in this app to generate a deadline- and difficulty-based schedule."""),
        (("project", "minor project", "github", "streamlit", "portfolio"),
         """🛠️ **Project development checklist**

- Define the problem and intended users.
- Break the app into small modules and test each module.
- Keep secrets such as API keys and passwords out of GitHub.
- Document setup, features, limitations, and future scope in the README.
- Test the deployed app with valid inputs, empty inputs, and error cases.

For your project explanation, be ready to describe the architecture, technologies, your own contribution, and what you would improve next."""),
        (("sql", "database", "dbms", "normalization", "joins"),
         """🗄️ **DBMS and SQL preparation**

Study keys, constraints, ER diagrams, normalization, transactions, ACID properties, indexing, and relational algebra basics. Practise SQL SELECT, WHERE, GROUP BY, HAVING, joins, subqueries, and aggregate functions.

**Practice task:** Given Students and Marks tables, write a query to list each student with their average marks."""),
        (("thank", "thanks", "thank you"),
         """You're welcome! 😊 Ask me another question about studies, programming, careers, placements, resumes, or AI/ML whenever you're ready."""),
    ]
    for keywords, response in rules:
        if any(keyword in text for keyword in keywords):
            return response

    return ("I don't have a tailored response for that topic in my current offline knowledge base yet. "
            "I can currently help with **Python, DSA, placement preparation, career paths, AI/ML, resumes, "
            "study planning, projects, and DBMS/SQL**. Try asking a more specific question in one of these areas. "
            "This version works without an external AI API, so it uses topic-based responses rather than generating "
            "open-ended answers like a large language model.")


def show_auth_page():
    st.markdown(
        """
        <div class="app-hero">
            <span class="hero-tag">STUDENT SUCCESS • POWERED BY AI</span>
            <h2>AI Student Career &amp; Academic Assistant</h2>
            <p>Your personal workspace for academic planning, resume insights, and career readiness.
            Sign in or create an account to continue.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    login_tab, signup_tab, resend_tab = st.tabs(
        ["🔐 Log in", "📝 Create account", "✉️ Resend verification"]
    )

    with login_tab:
        with st.form("login_form"):
            email = st.text_input("Email address", key="login_email").strip().lower()
            password = st.text_input("Password", type="password", key="login_password")
            submitted = st.form_submit_button("Log in", use_container_width=True)

        if submitted:
            if not email or not password:
                st.warning("Enter both your email address and password.")
            else:
                try:
                    response = supabase.auth.sign_in_with_password(
                        {"email": email, "password": password}
                    )
                    if response.session is None:
                        st.error("Login did not return a session. Verify your email and try again.")
                    else:
                        set_logged_in(response.session)
                        st.success("Login successful.")
                        st.rerun()
                except Exception as exc:
                    st.error(
                        "Login failed. Check your email and password, and confirm your email "
                        "address if email confirmation is enabled."
                    )

    with signup_tab:
        with st.form("signup_form"):
            full_name = st.text_input("Full name")
            email = st.text_input("Email address", key="signup_email").strip().lower()
            password = st.text_input(
                "Create password",
                type="password",
                help="Use at least 8 characters and avoid reusing an important password.",
            )
            confirm_password = st.text_input("Confirm password", type="password")
            course = st.text_input("Course", placeholder="e.g., B.Tech CSE-AI")
            study_year = st.selectbox(
                "Current study year",
                ["1st year", "2nd year", "3rd year", "4th year", "Other"],
            )
            submitted = st.form_submit_button("Create account", use_container_width=True)

        if submitted:
            if not all([full_name.strip(), email, password, confirm_password, course.strip()]):
                st.warning("Please complete all fields.")
            elif password != confirm_password:
                st.warning("The passwords do not match.")
            elif len(password) < 8:
                st.warning("Choose a password with at least 8 characters.")
            else:
                try:
                    response = supabase.auth.sign_up(
                        {
                            "email": email,
                            "password": password,
                            "options": {
                                "data": {
                                    "full_name": full_name.strip(),
                                    "course": course.strip(),
                                    "study_year": study_year,
                                }
                            },
                        }
                    )
                    if response.session is not None and response.user is not None:
                        set_logged_in(response.session)
                        user_id = response.user.id
                        try:
                            supabase.table("profiles").upsert(
                                {
                                    "id": user_id,
                                    "full_name": full_name.strip(),
                                    "course": course.strip(),
                                    "study_year": study_year,
                                }
                            ).execute()
                        except Exception:
                            st.warning(
                                "Your account was created, but the profile could not be saved yet. "
                                "You can complete it from your dashboard after logging in."
                            )
                        st.success("Account created. Opening your dashboard…")
                        st.rerun()
                    else:
                        st.success(
                            "Registration started! Check your inbox for the verification email. "
                            "After verifying, return here and log in."
                        )
                except Exception as exc:
                    # Show the Supabase error details to help diagnose registration failures.
                    # Do not display credentials, access tokens, or request headers.
                    error_text = str(exc).strip()
                    st.error("Registration failed.")
                    if error_text:
                        st.code(f"{type(exc).__name__}: {error_text[:1200]}")
                    else:
                        st.info(
                            "Supabase returned an empty error message. Check the Auth logs "
                            "in your Supabase dashboard."
                        )

    with resend_tab:
        st.write("If you registered but did not receive a verification email, request another.")
        with st.form("resend_form"):
            resend_email = st.text_input("Registration email").strip().lower()
            resend_submit = st.form_submit_button("Resend verification email")
        if resend_submit:
            if not resend_email:
                st.warning("Enter your registration email.")
            else:
                try:
                    supabase.auth.resend(
                        {"type": "signup", "email": resend_email}
                    )
                    st.success(
                        "If the address is eligible, Supabase will send a verification email. "
                        "Check your spam folder too."
                    )
                except Exception:
                    st.error(
                        "Could not resend the email. Check your Supabase email settings and try again."
                    )


# --------------------------------------------------
# AUTH GATE
# --------------------------------------------------
if st.session_state.auth_user is None:
    show_auth_page()
    st.stop()

restore_supabase_session()

user = st.session_state.auth_user
user_id = user.id
user_email = getattr(user, "email", "") or ""

# --------------------------------------------------
# LOAD / SAVE PROFILE
# --------------------------------------------------
profile = {
    "full_name": (getattr(user, "user_metadata", None) or {}).get("full_name", ""),
    "course": (getattr(user, "user_metadata", None) or {}).get("course", ""),
    "study_year": (getattr(user, "user_metadata", None) or {}).get("study_year", "Other"),
}
try:
    profile_result = (
        supabase.table("profiles")
        .select("full_name, course, study_year")
        .eq("id", user_id)
        .maybe_single()
        .execute()
    )
    if profile_result.data:
        profile.update(profile_result.data)
except Exception:
    pass


# --------------------------------------------------
# HEADER / NAVIGATION
# --------------------------------------------------
st.markdown('<div class="app-eyebrow">AI-POWERED STUDENT WORKSPACE</div>', unsafe_allow_html=True)
st.title("AI Student Career & Academic Assistant")
st.caption("One workspace to plan your studies, strengthen your resume, and prepare for your career.")

with st.sidebar:
    st.markdown("## 🎓 Student Hub")
    st.caption("LEARN • PLAN • GROW")
    st.divider()
    st.write(f"**Signed in as**")
    st.caption(user_email)
    module = st.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "👤 My Profile",
            "📚 AI Study Planner",
            "📄 AI Resume Analyzer",
            "🤖 Student Chatbot",
        ],
    )
    if st.button("Log out", use_container_width=True):
        try:
            supabase.auth.sign_out()
        except Exception:
            pass
        for key in [
            "auth_user",
            "auth_access_token",
            "auth_refresh_token",
        ]:
            st.session_state[key] = None
        st.rerun()


# ==================================================
# DASHBOARD
# ==================================================
if module == "🏠 Dashboard":
    student_name = escape((profile.get("full_name") or "").strip().split(" ")[0] or "Student")
    st.markdown(
        f"""
        <div class="app-hero">
            <span class="hero-tag">YOUR PERSONAL LEARNING SPACE</span>
            <h2>Welcome back, {student_name}! 👋</h2>
            <p>Build better study habits, understand your skills, and take the next step
            toward your academic and career goals.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-label">YOUR WORKSPACE</div>', unsafe_allow_html=True)
    card1, card2, card3, card4 = st.columns(4)
    with card1:
        st.markdown(
            """
            <div class="feature-card">
                <div class="icon">📚</div>
                <h3>AI Study Planner</h3>
                <p>Organize subjects by deadlines and difficulty, then generate a study plan
                around the time you have available.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with card2:
        st.markdown(
            """
            <div class="feature-card">
                <div class="icon">📄</div>
                <h3>AI Resume Analyzer</h3>
                <p>Review detected skills, explore skill coverage, and identify areas to
                consider developing for your career goals.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with card3:
        st.markdown(
            """
            <div class="feature-card">
                <div class="icon">👤</div>
                <h3>Student Profile</h3>
                <p>Keep your name, course, and current study year up to date in your
                personal student workspace.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with card4:
        st.markdown(
            """
            <div class="feature-card">
                <div class="icon">🤖</div>
                <h3>Student Chatbot</h3>
                <p>Get instant topic-based guidance for programming, placements, careers,
                AI/ML, and study habits—without an API key.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-label">QUICK OVERVIEW</div>', unsafe_allow_html=True)
    metric1, metric2, metric3 = st.columns(3)
    with metric1:
        st.metric("Learning tools", "02", help="Study Planner and Resume Analyzer")
    with metric2:
        st.metric("Account status", "Verified login", help="You are signed in to your workspace")
    with metric3:
        st.metric("Profile", "Personalized", help="Update your details from My Profile")

    st.info("Choose a module from the sidebar to get started. Your existing tools are ready to use.")


# ==================================================
# PROFILE
# ==================================================
elif module == "👤 My Profile":
    st.markdown('<div class="app-eyebrow">YOUR ACCOUNT</div>', unsafe_allow_html=True)
    st.header("👤 My Student Profile")
    st.write("Manage the details associated with your student workspace.")

    with st.form("profile_form"):
        full_name = st.text_input("Full name", value=profile.get("full_name") or "")
        course = st.text_input("Course", value=profile.get("course") or "")
        year_options = ["1st year", "2nd year", "3rd year", "4th year", "Other"]
        saved_year = profile.get("study_year") or "Other"
        study_year_index = year_options.index(saved_year) if saved_year in year_options else 4
        study_year = st.selectbox("Current study year", year_options, index=study_year_index)
        save_profile = st.form_submit_button("Save profile")

    if save_profile:
        if not full_name.strip() or not course.strip():
            st.warning("Please enter your name and course.")
        else:
            try:
                supabase.table("profiles").upsert(
                    {
                        "id": user_id,
                        "full_name": full_name.strip(),
                        "course": course.strip(),
                        "study_year": study_year,
                    }
                ).execute()
                st.success("Profile saved successfully.")
                st.rerun()
            except Exception:
                    st.error(
                        "Could not save your profile. Confirm that the profiles table and its "
                        "Row Level Security policies are configured correctly."
                    )


# ==================================================
# STUDY PLANNER (ENHANCED DAILY + WEEKLY PLANNING)
# ==================================================
elif module == "📚 AI Study Planner":
    st.markdown('<div class="app-eyebrow">PLAN WITH PURPOSE</div>', unsafe_allow_html=True)
    st.header("📚 AI Study Planner")
    st.write(
        "Build a practical study plan using subject deadlines and difficulty. "
        "Review daily priorities, a weekly timetable, and study recommendations."
    )
    st.info(
        "For useful results, enter each subject's actual deadline and difficulty. "
        "The planner uses these details to prioritize study time."
    )

    daily_hours = st.number_input(
        "Available study hours per day",
        min_value=0.5,
        max_value=16.0,
        value=4.0,
        step=0.5,
        help="Enter focused study time, excluding meals and long breaks.",
        key="planner_daily_hours",
    )
    schedule_days = st.selectbox(
        "Schedule length",
        options=[3, 5, 7],
        index=2,
        format_func=lambda value: f"{value} days",
        key="planner_schedule_days",
    )

    st.subheader("📝 Subject Details")
    number_of_subjects = st.number_input(
        "Number of subjects", min_value=1, max_value=10, value=3, step=1,
        key="planner_subject_count",
    )

    subjects = []
    for i in range(int(number_of_subjects)):
        with st.container(border=True):
            st.markdown(f"**Subject {i + 1}**")
            col1, col2, col3 = st.columns([1.4, 1, 1])
            with col1:
                name = st.text_input("Subject name", key=f"name_{i}")
            with col2:
                deadline = st.date_input(
                    "Deadline", value=date.today(), key=f"deadline_{i}"
                )
            with col3:
                difficulty = st.selectbox(
                    "Difficulty", ["Easy", "Medium", "Hard"], key=f"difficulty_{i}"
                )
            subjects.append({
                "name": name.strip(),
                "deadline": deadline,
                "difficulty": difficulty,
            })

    if st.button("🚀 Generate Study Schedule", type="primary", use_container_width=True):
        valid_subjects = [subject for subject in subjects if subject["name"]]
        if not valid_subjects:
            st.warning("Please enter at least one subject name.")
            st.session_state.pop("study_plan_results", None)
        else:
            try:
                st.session_state.study_plan_results = {
                    "subjects": valid_subjects,
                    "daily_hours": float(daily_hours),
                    "days": int(schedule_days),
                    "plan": generate_plan(valid_subjects, float(daily_hours)),
                    "weekly": generate_weekly_plan(
                        valid_subjects, float(daily_hours), days=int(schedule_days)
                    ),
                    "recommendations": get_study_recommendations(valid_subjects),
                }
            except Exception as exc:
                st.error("We couldn't generate the schedule. Check your subject details and try again.")
                with st.expander("Technical details"):
                    st.code(str(exc))

    results = st.session_state.get("study_plan_results")
    if results:
        st.divider()
        st.subheader("📊 Your Study Overview")
        total_subjects = len(results["subjects"])
        urgent_subjects = sum(
            1 for item in results["subjects"] if item["deadline"] <= date.today()
        )
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Subjects", total_subjects)
        with m2:
            st.metric("Daily Study Time", f"{results['daily_hours']:g} hrs")
        with m3:
            st.metric("Deadlines Today or Passed", urgent_subjects)

        plan_tab, week_tab, tips_tab = st.tabs(
            ["🎯 Priority Plan", "🗓️ Timetable", "💡 Recommendations"]
        )

        with plan_tab:
            st.markdown("#### Recommended Study Allocation")
            st.caption(
                "Subjects are ranked by deadline urgency and difficulty. Recommended hours "
                "are proportional to the priority score."
            )
            display_plan = []
            for item in results["plan"]:
                display_plan.append({
                    "Subject": item["Subject"],
                    "Deadline": item["Deadline"],
                    "Difficulty": item["Difficulty"],
                    "Priority Score": item["Priority Score"],
                    "Recommended Hours/Day": item["Recommended Hours"],
                })
            st.dataframe(display_plan, use_container_width=True, hide_index=True)
            st.download_button(
                "⬇️ Download priority plan (CSV)",
                data=__import__("pandas").DataFrame(display_plan).to_csv(index=False).encode("utf-8"),
                file_name="study_priority_plan.csv",
                mime="text/csv",
                use_container_width=True,
            )

        with week_tab:
            st.markdown(f"#### Your {results['days']}-Day Study Timetable")
            st.caption(
                "The schedule rotates subjects, limits each day to up to three subjects, "
                "and labels periodic sessions as revision. Use the plan as a starting point "
                "and adjust it to your actual class timetable."
            )
            weekly_rows = []
            for item in results["weekly"]:
                weekly_rows.append({
                    "Day": item["Day"],
                    "Date": item["Date"],
                    "Subject": item["Subject"],
                    "Study Hours": item["Study Hours"],
                    "Session Length (min)": item["Session Length (minutes)"],
                    "Session Type": item["Session Type"],
                })
            if weekly_rows:
                st.dataframe(weekly_rows, use_container_width=True, hide_index=True)
                st.download_button(
                    "⬇️ Download timetable (CSV)",
                    data=__import__("pandas").DataFrame(weekly_rows).to_csv(index=False).encode("utf-8"),
                    file_name="weekly_study_timetable.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
            else:
                st.info("Enter a positive daily study time to create a timetable.")

            st.markdown("#### Suggested Study Rhythm")
            st.markdown(
                "- **Focused block:** study for 25–50 minutes.\\n"
                "- **Short break:** take 5–10 minutes between focused blocks.\\n"
                "- **Revision:** test yourself or solve practice questions instead of only rereading notes."
            )

        with tips_tab:
            st.markdown("#### Next Best Actions")
            for index, recommendation in enumerate(results["recommendations"], start=1):
                st.markdown(f"{index}. {recommendation}")

        if st.button("🧹 Clear generated schedule", key="clear_study_schedule"):
            st.session_state.pop("study_plan_results", None)
            st.rerun()


# ==================================================
# RESUME ANALYZER (EXISTING FUNCTIONALITY PRESERVED)
# ==================================================
elif module == "📄 AI Resume Analyzer":
    st.markdown('<div class="app-eyebrow">CAREER READINESS</div>', unsafe_allow_html=True)
    st.header("📄 AI Resume Analyzer")
    st.write("Review skills detected in your resume and compare them with a checklist for your target role.")
    st.info(
        "The skill coverage percentage measures matches against the selected role's checklist. "
        "It is not an overall resume-quality score or a prediction of hiring outcomes."
    )

    career_goal = st.selectbox(
        "Choose your target career",
        options=list(CAREER_SKILLS.keys()),
        key="resume_career_goal",
    )
    uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"], key="resume_pdf_upload")

    if uploaded_file is not None and st.button("🔍 Analyze Resume", type="primary"):
        try:
            with st.spinner("Analyzing resume skills..."):
                text = extract_text_from_pdf(uploaded_file)
                if not text.strip():
                    st.warning(
                        "No selectable text was found in this PDF. If it is a scanned resume, "
                        "try exporting it as a text-based PDF and upload it again."
                    )
                    st.stop()
                result = analyze_resume(text, career_goal=career_goal)

            st.success("Resume analysis completed!")
            st.markdown(f"### 🎯 Target role: {result['career_goal']}")
            metric1, metric2, metric3 = st.columns(3)
            with metric1:
                st.metric("Role Skill Coverage", f"{result['score']}%")
            with metric2:
                st.metric("Matched Skills", len(result["matched_skills"]))
            with metric3:
                st.metric("Skills to Explore", len(result["missing_skills"]))

            st.progress(result["score"] / 100)

            matched_col, gap_col = st.columns(2)
            with matched_col:
                st.subheader("✅ Skills Found for This Role")
                if result["matched_skills"]:
                    for skill in result["matched_skills"]:
                        st.markdown(f"- {skill}")
                else:
                    st.write("No skills from this role checklist were detected yet.")
            with gap_col:
                st.subheader("🧭 Skills to Consider Developing")
                if result["missing_skills"]:
                    for skill in result["missing_skills"]:
                        st.markdown(f"- {skill}")
                else:
                    st.write("All skills in this role checklist were detected.")

            st.subheader("💡 Skill Development Suggestions")
            if result["recommendations"]:
                for item in result["recommendations"]:
                    with st.expander(item["skill"]):
                        st.write(item["suggestion"])
            else:
                st.success("No additional skills from this checklist to recommend.")

            with st.expander("View All Detected Resume Skills"):
                if result["skills"]:
                    st.write(", ".join(result["skills"]))
                else:
                    st.write("No predefined skills were detected in the resume text.")

            with st.expander("View Extracted Resume Text"):
                st.text(text)

        except Exception as exc:
            st.error("We couldn't analyze this PDF. Please try another text-based PDF resume.")
            with st.expander("Technical details"):
                st.code(str(exc))


# ==================================================
# STUDENT CHATBOT (OFFLINE RULE-BASED; NO API KEY)
# ==================================================
elif module == "🤖 Student Chatbot":
    st.markdown('<div class="app-eyebrow">YOUR STUDY & CAREER COMPANION</div>', unsafe_allow_html=True)
    st.header("🤖 Student Chatbot")
    st.write(
        "Ask about programming, study planning, placements, career skills, resumes, AI/ML, "
        "projects, or DBMS/SQL. This chatbot uses a local rule-based knowledge base and does not call an external AI service."
    )
    st.info("Offline chatbot • No API key • No API usage charges • Responses are topic-based, not generated by a large AI model.")

    if "student_chat_history" not in st.session_state:
        st.session_state.student_chat_history = [
            {"role": "assistant", "content": "Hi! 👋 I'm your Student Assistant. What would you like help with today? Try asking about Python, DSA, placements, career options, AI/ML, resumes, or study planning."}
        ]

    st.markdown("#### 💡 Try a suggested question")
    suggested_questions = [
        "How do I start learning Python?",
        "Give me a placement preparation plan",
        "How should I prepare DSA?",
        "Explain the AI/ML learning path",
    ]
    suggestion_cols = st.columns(2)
    for index, question in enumerate(suggested_questions):
        with suggestion_cols[index % 2]:
            if st.button(question, key=f"chat_suggestion_{index}", use_container_width=True):
                st.session_state.student_chat_history.append({"role": "user", "content": question})
                st.session_state.student_chat_history.append({"role": "assistant", "content": get_student_chatbot_response(question)})
                st.rerun()

    st.divider()
    for message in st.session_state.student_chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_prompt = st.chat_input("Ask a study or career question...")
    if user_prompt:
        st.session_state.student_chat_history.append({"role": "user", "content": user_prompt})
        reply = get_student_chatbot_response(user_prompt)
        st.session_state.student_chat_history.append({"role": "assistant", "content": reply})
        st.rerun()

    if st.button("🧹 Clear chat history", key="clear_student_chat"):
        st.session_state.student_chat_history = [
            {"role": "assistant", "content": "Chat cleared. 👋 Ask me about Python, DSA, placements, careers, AI/ML, resumes, projects, or study planning."}
        ]
        st.rerun()
