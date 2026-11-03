import streamlit as st
import pandas as pd
from datetime import date
from html import escape
from supabase import create_client, Client

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


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="AI Student Assistant",
    page_icon="🎓",
    layout="wide"
)


# ==================================================
# VISUAL DESIGN SYSTEM
# ==================================================

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
            radial-gradient(
                circle at 95% 0%,
                rgba(37, 99, 235, 0.07),
                transparent 25rem
            ),
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

    h1 {
        font-weight: 800;
    }

    h2, h3 {
        font-weight: 750;
    }

    p, label, .stCaption {
        color: #475569;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(
            180deg,
            #101d3a 0%,
            #172b50 100%
        );
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
        background: linear-gradient(
            115deg,
            #101d3a 0%,
            #1e40af 58%,
            #0891b2 100%
        );
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

    [data-testid="stChatMessage"] {
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 0.9rem 1rem;
        background: rgba(255,255,255,0.92);
        box-shadow: 0 5px 16px rgba(15, 23, 42, 0.035);
        margin-bottom: 0.75rem;
    }

    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p {
        color: #334155;
        line-height: 1.7;
    }

    [data-testid="stChatInput"] {
        border-radius: 16px;
    }

    [data-testid="stChatInput"] textarea {
        border-radius: 14px;
    }

    [data-testid="stAlert"] {
        border-radius: 14px;
    }

    [data-testid="stExpander"] {
        border-radius: 14px;
        border-color: #e2e8f0;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        overflow: hidden;
    }

    .module-intro {
        border: 1px solid #dbeafe;
        border-radius: 16px;
        padding: 1rem 1.15rem;
        background: linear-gradient(
            110deg,
            #eff6ff 0%,
            #ecfeff 100%
        );
        color: #334155;
        margin: 0.4rem 0 1rem 0;
        line-height: 1.65;
    }

    .topic-pill {
        display: inline-block;
        background: #ffffff;
        color: #1d4ed8;
        border: 1px solid #bfdbfe;
        border-radius: 999px;
        padding: 0.3rem 0.65rem;
        font-size: 0.78rem;
        font-weight: 700;
        margin: 0.15rem 0.2rem 0.15rem 0;
    }

    @media (max-width: 700px) {
        .block-container {
            padding-top: 1rem;
        }

        .app-hero {
            padding: 1.25rem;
            border-radius: 16px;
        }

        .feature-card {
            min-height: auto;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==================================================
# SUPABASE CONNECTION
# ==================================================

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
        "Check SUPABASE_URL and SUPABASE_KEY in "
        "Streamlit Cloud → Settings → Secrets."
    )
    st.stop()


# ==================================================
# SESSION HELPERS
# ==================================================

if "auth_user" not in st.session_state:
    st.session_state.auth_user = None

if "auth_access_token" not in st.session_state:
    st.session_state.auth_access_token = None

if "auth_refresh_token" not in st.session_state:
    st.session_state.auth_refresh_token = None

if "interview_attempts" not in st.session_state:
    st.session_state.interview_attempts = []


def set_logged_in(session):
    st.session_state.auth_user = session.user
    st.session_state.auth_access_token = session.access_token
    st.session_state.auth_refresh_token = session.refresh_token


def restore_supabase_session():
    access_token = st.session_state.get("auth_access_token")
    refresh_token = st.session_state.get("auth_refresh_token")

    if access_token and refresh_token:
        try:
            supabase.auth.set_session(
                access_token,
                refresh_token
            )
            return True

        except Exception:
            st.session_state.auth_user = None
            st.session_state.auth_access_token = None
            st.session_state.auth_refresh_token = None

    return False


# ==================================================
# SUPABASE INTERVIEW HISTORY
# ==================================================

def load_interview_history(user_id):
    """Load the logged-in user's interview attempts from Supabase."""

    try:
        response = (
            supabase.table("interview_attempts")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=False)
            .execute()
        )

        attempts = []

        for row in response.data or []:
            answer = row.get("answer") or ""

            attempts.append({
                "id": row.get("id"),
                "question": row.get("question", ""),
                "answer": answer,
                "score": int(row.get("score", 0)),
                "word_count": len(answer.split()),
                "matched": row.get("matched_keywords") or [],
                "missing": row.get("missing_keywords") or [],
                "strengths": row.get("strengths") or [],
                "improvements": row.get("improvements") or [],
                "created_at": row.get("created_at")
            })

        return attempts

    except Exception as exc:
        st.error("Could not load interview history from Supabase.")

        with st.expander("Technical details"):
            st.code(str(exc))

        return None


def save_interview_attempt(user_id, question, answer, evaluation):
    try:
        payload = {
            "user_id": str(user_id),
            "question": question,
            "answer": answer,
            "score": int(evaluation["score"]),
            "matched_keywords": evaluation["matched_keywords"],
            "missing_keywords": evaluation["missing_keywords"],
            "strengths": evaluation["strengths"],
            "improvements": evaluation["improvements"]
        }

        response = (
            supabase
            .table("interview_attempts")
            .insert(payload)
            .select("*")
            .execute()
        )

        if response.data and len(response.data) > 0:
            return response.data[0]

        st.error("Supabase did not return the inserted interview record.")
        return None

    except Exception as exc:
        st.error("Your interview result could not be saved.")
        st.exception(exc)
        return None
    except Exception as exc:
        st.error("Your interview result could not be saved.")

        with st.expander("Technical details"):
            st.code(str(exc))

        return None


def delete_interview_history(user_id):
    """Delete only the logged-in user's interview attempts."""

    try:
        (
            supabase.table("interview_attempts")
            .delete()
            .eq("user_id", user_id)
            .execute()
        )

        return True

    except Exception as exc:
        st.error("Could not delete interview history.")

        with st.expander("Technical details"):
            st.code(str(exc))

        return False


# ==================================================
# OFFLINE STUDENT CHATBOT
# ==================================================

def get_student_chatbot_response(message: str) -> str:
    """Return topic-based guidance without an external AI API."""

    import re

    text = " ".join(
        (message or "").lower().strip().split()
    )

    if not text:
        return (
            "Please type a question. I can help with Python, DSA, "
            "DBMS/SQL, core CS subjects, placements, career paths, "
            "AI/ML, resumes, projects, and study techniques."
        )

    def matches(phrases):
        for phrase in phrases:
            phrase = phrase.lower()

            if " " in phrase:
                if phrase in text:
                    return True
            elif re.search(
                r"\b" + re.escape(phrase) + r"\b",
                text
            ):
                return True

        return False

    if matches([
        "hello", "hi", "hey",
        "good morning", "good afternoon", "good evening"
    ]):
        return """Hello! 👋 I'm your Student Assistant.

I can guide you through **Python, DSA, DBMS/SQL, core CS subjects, AI/ML, resumes, projects, and placements**.

Ask me a specific question to get started."""

    if matches([
        "oops", "object oriented", "object-oriented",
        "class and object", "inheritance",
        "polymorphism", "encapsulation", "abstraction"
    ]):
        return """🧩 **OOP interview revision**

The four commonly discussed OOP principles are:

- **Encapsulation:** Keep data and related methods together.
- **Abstraction:** Expose essential behavior while hiding implementation details.
- **Inheritance:** Create a class that reuses or extends another class.
- **Polymorphism:** Use a common interface with different implementations.

**Practice:** Explain each principle with a real-world example."""

    if matches([
        "python", "learn programming",
        "programming basics", "coding basics", "python roadmap"
    ]):
        return """🐍 **Python learning roadmap**

1. Fundamentals: variables, data types, input/output and operators.
2. Control flow: conditions, loops and functions.
3. Collections: strings, lists, tuples, sets and dictionaries.
4. Problem solving: searching, sorting and frequency maps.
5. Practical Python: files, exceptions, modules and OOP.
6. Projects: calculator, quiz app, expense tracker or student record tool.

**Try today:** Write a function that counts vowels in a string."""

    if matches([
        "dsa", "data structures", "algorithms",
        "leetcode", "coding interview", "time complexity",
        "big o", "binary search", "linked list",
        "stack", "queue", "tree", "graph",
        "dynamic programming"
    ]):
        return """💻 **DSA preparation roadmap**

1. Time and space complexity (Big-O).
2. Arrays, strings, hashing and two-pointer patterns.
3. Searching and sorting.
4. Linked lists, stacks, queues and recursion.
5. Trees, heaps and graphs.
6. Greedy algorithms and dynamic programming.

**Daily routine:** Revise a concept, solve one or two problems, and record mistakes."""

    if matches([
        "sql", "dbms", "database", "normalization",
        "joins", "primary key", "foreign key",
        "acid properties", "transaction"
    ]):
        return """🗄️ **DBMS and SQL revision**

**DBMS topics:** Keys, constraints, ER diagrams, normalization, ACID properties, indexing and concurrency.

**SQL practice order:**
SELECT → WHERE → GROUP BY → HAVING → JOIN → Subqueries → Views.

**Practice:** Calculate each student's average marks using JOIN, GROUP BY and AVG()."""

    if matches([
        "operating system", "operating systems",
        "process", "thread", "deadlock",
        "cpu scheduling", "memory management"
    ]):
        return """🖥️ **Operating Systems interview checklist**

Review process vs thread, process states, CPU scheduling, context switching, synchronization, semaphores, deadlocks, paging and virtual memory.

For each topic prepare:
**Definition → Diagram/example → Advantages/limitations → Comparison.**"""

    if matches([
        "computer network", "computer networks",
        "networking", "osi model", "tcp/ip",
        "tcp", "udp", "dns", "http", "https",
        "ip address"
    ]):
        return """🌐 **Computer Networks revision**

Focus on:
- OSI and TCP/IP models
- IP addressing
- TCP vs UDP
- DNS
- HTTP vs HTTPS
- Routing and network devices

Practise explaining what happens after entering a website address in a browser."""

    if matches([
        "aptitude", "quantitative", "logical reasoning",
        "verbal ability", "percentages", "ratio",
        "time and work", "placement", "campus drive",
        "job preparation", "interview preparation",
        "technical interview"
    ]):
        return """🚀 **Placement preparation plan**

- Coding: Python and DSA.
- Core CS: OOP, DBMS/SQL, OS and networks.
- Aptitude: Percentages, ratios, averages and logical reasoning.
- Projects: Explain architecture, contribution and testing.
- HR: Practise self-introduction and behavioural questions.

Prioritize skills mentioned in your target job description."""

    if matches([
        "hr interview", "tell me about yourself",
        "self introduction", "strengths and weaknesses",
        "why should we hire you"
    ]):
        return """🗣️ **HR interview practice**

Structure your introduction around:

1. Your degree and area of study.
2. Relevant technical skills.
3. One or two projects.
4. Your target role.

Keep it around 45–60 seconds.

For behavioural questions, use STAR:
Situation, Task, Action and Result."""

    if matches([
        "career", "career path", "which field",
        "job role", "career goal", "data analyst",
        "data analytics", "software developer",
        "web development", "frontend", "backend"
    ]):
        return """💼 **Career path guide**

- Software development: Programming, DSA, OOP, Git and APIs.
- Data analytics: Excel, SQL, statistics and visualization.
- AI/ML: Python, statistics, data preparation and evaluation.
- Web development: HTML, CSS, JavaScript and APIs.

Choose one target role and build a project demonstrating its recurring job requirements."""

    if matches([
        "machine learning", "ai/ml", "ai ml",
        "artificial intelligence", "deep learning",
        "neural network", "supervised learning",
        "overfitting", "random forest", "svm"
    ]):
        return """🤖 **AI/ML learning roadmap**

1. Python, NumPy, pandas and visualization.
2. Probability, statistics and linear algebra.
3. Supervised learning algorithms.
4. Train/test splits and evaluation metrics.
5. Feature engineering and cross-validation.
6. End-to-end machine learning projects.

Always explain your evaluation methodology and check for data leakage."""

    if matches([
        "resume", "cv", "resume analyzer",
        "skill gap", "resume skills", "project description"
    ]):
        return """📄 **Resume improvement checklist**

- Tailor skills and project bullets to the target role.
- Describe the problem, tools and your contribution.
- Quantify outcomes only when supported by evidence.
- Keep dates and formatting consistent.
- Include skills you can explain in an interview.

Use the Resume Analyzer to compare detected skills with your target role."""

    if matches([
        "study plan", "study schedule", "timetable",
        "manage time", "exam preparation",
        "how to study", "study tips", "revision",
        "procrastination"
    ]):
        return """📚 **Build a realistic study routine**

1. List subjects and deadlines.
2. Prioritize difficult and urgent topics.
3. Use focused 25–50 minute study blocks.
4. Practise active recall.
5. Solve exam-style questions.
6. Review your progress daily.

Open AI Study Planner to generate a schedule."""

    if matches([
        "project", "minor project", "github",
        "streamlit", "portfolio", "debug",
        "error in code", "deployment"
    ]):
        return """🛠️ **Project development checklist**

- Define the problem and intended users.
- Separate features into manageable modules.
- Test normal, missing and invalid inputs.
- Never commit API keys or passwords to GitHub.
- Document architecture, tools and limitations.
- Prepare to explain your own implementation during the viva."""

    if matches(["thank", "thanks", "thank you"]):
        return (
            "You're welcome! 😊 Ask me another question about "
            "academics, programming, career planning or placements."
        )

    return """I couldn't confidently match that question to my prepared topics.

I work without an external AI API, so I use a topic-based knowledge base.

Try asking about **Python, DSA, OOP, DBMS/SQL, Operating Systems, Computer Networks, aptitude, HR interviews, placements, AI/ML, resumes, study techniques or projects**."""


# ==================================================
# AUTHENTICATION PAGE
# ==================================================

def show_auth_page():

    st.markdown(
        """
        <div class="app-hero">
            <span class="hero-tag">STUDENT SUCCESS • POWERED BY AI</span>
            <h2>AI Student Career &amp; Academic Assistant</h2>
            <p>
                Your personal workspace for academic planning,
                resume insights, and career readiness.
                Sign in or create an account to continue.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    login_tab, signup_tab, resend_tab = st.tabs(
        ["🔐 Log in", "📝 Create account", "✉️ Resend verification"]
    )

    # LOGIN
    with login_tab:

        with st.form("login_form"):

            email = st.text_input(
                "Email address",
                key="login_email"
            ).strip().lower()

            password = st.text_input(
                "Password",
                type="password",
                key="login_password"
            )

            submitted = st.form_submit_button(
                "Log in",
                use_container_width=True
            )

        if submitted:

            if not email or not password:

                st.warning("Enter both your email address and password.")

            else:

                try:

                    response = supabase.auth.sign_in_with_password(
                        {
                            "email": email,
                            "password": password
                        }
                    )

                    if response.session is None:

                        st.error(
                            "Login did not return a session. "
                            "Verify your email and try again."
                        )

                    else:

                        set_logged_in(response.session)
                        st.success("Login successful.")
                        st.rerun()

                except Exception:

                    st.error(
                        "Login failed. Check your email and password, "
                        "and confirm your email address if required."
                    )

    # SIGNUP
    with signup_tab:

        with st.form("signup_form"):

            full_name = st.text_input("Full name")

            email = st.text_input(
                "Email address",
                key="signup_email"
            ).strip().lower()

            password = st.text_input(
                "Create password",
                type="password"
            )

            confirm_password = st.text_input(
                "Confirm password",
                type="password"
            )

            course = st.text_input(
                "Course",
                placeholder="e.g., B.Tech CSE-AI"
            )

            study_year = st.selectbox(
                "Current study year",
                [
                    "1st year",
                    "2nd year",
                    "3rd year",
                    "4th year",
                    "Other"
                ]
            )

            submitted = st.form_submit_button(
                "Create account",
                use_container_width=True
            )

        if submitted:

            if not all([
                full_name.strip(),
                email,
                password,
                confirm_password,
                course.strip()
            ]):

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
                                    "study_year": study_year
                                }
                            }
                        }
                    )

                    if (
                        response.session is not None
                        and response.user is not None
                    ):

                        set_logged_in(response.session)

                        try:

                            supabase.table("profiles").upsert(
                                {
                                    "id": response.user.id,
                                    "full_name": full_name.strip(),
                                    "course": course.strip(),
                                    "study_year": study_year
                                }
                            ).execute()

                        except Exception:

                            st.warning(
                                "Your account was created, but your "
                                "profile could not be saved yet."
                            )

                        st.success("Account created.")
                        st.rerun()

                    else:

                        st.success(
                            "Registration started! Check your inbox "
                            "for the verification email. After verifying, "
                            "return here and log in."
                        )

                except Exception as exc:

                    st.error("Registration failed.")

                    st.code(
                        f"{type(exc).__name__}: {str(exc)[:1200]}"
                    )

    # RESEND VERIFICATION
    with resend_tab:

        st.write(
            "If you registered but did not receive a verification email, "
            "request another."
        )

        with st.form("resend_form"):

            resend_email = st.text_input(
                "Registration email"
            ).strip().lower()

            resend_submit = st.form_submit_button(
                "Resend verification email"
            )

        if resend_submit:

            if not resend_email:

                st.warning("Enter your registration email.")

            else:

                try:

                    supabase.auth.resend(
                        {
                            "type": "signup",
                            "email": resend_email
                        }
                    )

                    st.success(
                        "If the address is eligible, Supabase will send "
                        "a verification email. Check your spam folder too."
                    )

                except Exception:

                    st.error(
                        "Could not resend the email. "
                        "Check your Supabase email settings."
                    )


# ==================================================
# AUTH GATE
# ==================================================

if st.session_state.auth_user is None:

    show_auth_page()
    st.stop()

if not restore_supabase_session():

    st.session_state.auth_user = None
    st.session_state.auth_access_token = None
    st.session_state.auth_refresh_token = None
    st.session_state.interview_attempts = []
    st.session_state.pop("interview_history_user", None)
    st.session_state.pop("latest_interview_evaluation", None)

    st.rerun()

user = st.session_state.auth_user
user_id = user.id
user_email = getattr(user, "email", "") or ""


# ==================================================
# LOAD INTERVIEW HISTORY FOR CURRENT USER
# ==================================================

if st.session_state.get("interview_history_user") != user_id:

    loaded_attempts = load_interview_history(user_id)

    if loaded_attempts is not None:

        st.session_state.interview_attempts = loaded_attempts
        st.session_state.interview_history_user = user_id


# ==================================================
# LOAD PROFILE
# ==================================================

profile = {
    "full_name": (
        getattr(user, "user_metadata", None) or {}
    ).get("full_name", ""),

    "course": (
        getattr(user, "user_metadata", None) or {}
    ).get("course", ""),

    "study_year": (
        getattr(user, "user_metadata", None) or {}
    ).get("study_year", "Other")
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


# ==================================================
# HEADER AND NAVIGATION
# ==================================================

st.markdown(
    '<div class="app-eyebrow">AI-POWERED STUDENT WORKSPACE</div>',
    unsafe_allow_html=True
)

st.title("AI Student Career & Academic Assistant")

st.caption(
    "One workspace to plan your studies, strengthen your resume, "
    "and prepare for your career."
)

with st.sidebar:

    st.markdown("## 🎓 Student Hub")
    st.caption("LEARN • PLAN • GROW")
    st.divider()

    st.write("**Signed in as**")
    st.caption(user_email)

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

    if st.button(
        "Log out",
        use_container_width=True
    ):

        try:
            supabase.auth.sign_out()
        except Exception:
            pass

        for key in [
            "auth_user",
            "auth_access_token",
            "auth_refresh_token"
        ]:
            st.session_state[key] = None

        st.session_state.interview_attempts = []

        st.session_state.pop(
            "interview_history_user",
            None
        )

        st.session_state.pop(
            "latest_interview_evaluation",
            None
        )

        st.rerun()


# ==================================================
# DASHBOARD
# ==================================================

if module == "🏠 Dashboard":

    student_name = escape(
        (profile.get("full_name") or "").strip().split(" ")[0]
        or "Student"
    )

    st.markdown(
        f"""
        <div class="app-hero">
            <span class="hero-tag">YOUR PERSONAL LEARNING SPACE</span>
            <h2>Welcome back, {student_name}! 👋</h2>
            <p>
                Build better study habits, understand your skills,
                and take the next step toward your academic
                and career goals.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-label">QUICK OVERVIEW</div>',
        unsafe_allow_html=True
    )

    metric1, metric2, metric3 = st.columns(3)

    with metric1:
        st.metric("Learning Tools", "05")

    with metric2:
        st.metric("Account Status", "Logged In")

    with metric3:

        profile_status = (
            "Complete"
            if profile.get("full_name") and profile.get("course")
            else "Incomplete"
        )

        st.metric("Student Profile", profile_status)

    st.divider()

    st.markdown(
        '<div class="section-label">QUICK ACCESS — YOUR WORKSPACE</div>',
        unsafe_allow_html=True
    )

    feature_data = [
        (
            "📚",
            "AI Study Planner",
            "Create daily priorities and weekly study timetables."
        ),
        (
            "📄",
            "AI Resume Analyzer",
            "Identify resume skills and explore career skill gaps."
        ),
        (
            "📑",
            "PDF Study Assistant",
            "Upload study notes and retrieve relevant passages."
        ),
        (
            "💼",
            "Career & Interview Coach",
            "Explore career roadmaps and practise interviews."
        ),
        (
            "🤖",
            "Student Chatbot",
            "Get academic and career guidance."
        ),
        (
            "👤",
            "My Profile",
            "View and update your student information."
        )
    ]

    for start in range(0, len(feature_data), 3):

        columns = st.columns(3)

        for column, item in zip(
            columns,
            feature_data[start:start + 3]
        ):

            icon, title, description = item

            with column:

                st.markdown(
                    f"""
                    <div class="feature-card">
                        <div class="icon">{icon}</div>
                        <h3>{title}</h3>
                        <p>{description}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    st.divider()

    st.markdown(
        '<div class="section-label">CAREER & LEARNING RECOMMENDATIONS</div>',
        unsafe_allow_html=True
    )

    recommendation_col1, recommendation_col2 = st.columns(2)

    with recommendation_col1:

        st.markdown("### 🎯 Academic Growth")

        st.markdown(
            "- Set realistic daily study targets.\n"
            "- Prioritize difficult subjects and upcoming deadlines.\n"
            "- Use active recall and regular revision.\n"
            "- Track your progress through the Study Planner."
        )

    with recommendation_col2:

        st.markdown("### 🚀 Career Readiness")

        st.markdown(
            "- Strengthen Python and problem-solving skills.\n"
            "- Practise DSA and core computer science subjects.\n"
            "- Build projects and document them on GitHub.\n"
            "- Review your resume against your target role."
        )

    st.info(
        "Select any module from the sidebar to begin."
    )


# ==================================================
# MY PROFILE
# ==================================================

elif module == "👤 My Profile":

    st.markdown(
        '<div class="app-eyebrow">YOUR ACCOUNT</div>',
        unsafe_allow_html=True
    )

    st.header("👤 My Student Profile")

    st.write(
        "Manage the details associated with your student workspace."
    )

    with st.form("profile_form"):

        full_name = st.text_input(
            "Full name",
            value=profile.get("full_name") or ""
        )

        course = st.text_input(
            "Course",
            value=profile.get("course") or ""
        )

        year_options = [
            "1st year",
            "2nd year",
            "3rd year",
            "4th year",
            "Other"
        ]

        saved_year = profile.get("study_year") or "Other"

        study_year_index = (
            year_options.index(saved_year)
            if saved_year in year_options
            else 4
        )

        study_year = st.selectbox(
            "Current study year",
            year_options,
            index=study_year_index
        )

        save_profile = st.form_submit_button(
            "Save profile",
            use_container_width=True
        )

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
                        "study_year": study_year
                    }
                ).execute()

                st.success("Profile saved successfully.")
                st.rerun()

            except Exception:

                st.error(
                    "Could not save your profile. Confirm that the "
                    "profiles table and its Row Level Security policies "
                    "are configured correctly."
                )


# ==================================================
# AI STUDY PLANNER
# ==================================================

elif module == "📚 AI Study Planner":

    st.markdown(
        '<div class="app-eyebrow">PLAN WITH PURPOSE</div>',
        unsafe_allow_html=True
    )

    st.header("📚 AI Study Planner")

    st.write(
        "Build a practical study plan using subject deadlines "
        "and difficulty."
    )

    st.info(
        "Enter each subject's actual deadline and difficulty "
        "for useful results."
    )

    daily_hours = st.number_input(
        "Available study hours per day",
        min_value=0.5,
        max_value=16.0,
        value=4.0,
        step=0.5,
        key="planner_daily_hours"
    )

    schedule_days = st.selectbox(
        "Schedule length",
        options=[3, 5, 7],
        index=2,
        format_func=lambda value: f"{value} days",
        key="planner_schedule_days"
    )

    st.subheader("📝 Subject Details")

    number_of_subjects = st.number_input(
        "Number of subjects",
        min_value=1,
        max_value=10,
        value=3,
        step=1,
        key="planner_subject_count"
    )

    subjects = []

    for i in range(int(number_of_subjects)):

        with st.container(border=True):

            st.markdown(f"### 📘 Subject {i + 1}")

            col1, col2 = st.columns(2)

            with col1:

                name = st.text_input(
                    "Subject name",
                    key=f"name_{i}",
                    placeholder="e.g. Mathematics"
                )

                deadline = st.date_input(
                    "Exam / Submission Date",
                    value=date.today(),
                    key=f"deadline_{i}"
                )

                difficulty = st.selectbox(
                    "Difficulty",
                    ["Easy", "Medium", "Hard"],
                    key=f"difficulty_{i}"
                )

            with col2:

                total_topics = st.number_input(
                    "Total topics",
                    min_value=1,
                    max_value=100,
                    value=10,
                    step=1,
                    key=f"total_topics_{i}"
                )

                completed_topics = st.number_input(
                    "Completed topics",
                    min_value=0,
                    max_value=100,
                    value=0,
                    step=1,
                    key=f"completed_topics_{i}"
                )

                estimated_hours = st.number_input(
                    "Estimated preparation hours",
                    min_value=1.0,
                    max_value=300.0,
                    value=10.0,
                    step=1.0,
                    key=f"estimated_hours_{i}"
                )

            if completed_topics > total_topics:

                st.warning(
                    "Completed topics cannot exceed total topics."
                )

            else:

                progress = completed_topics / total_topics

                st.progress(
                    progress,
                    text=f"Topic completion: {progress * 100:.0f}%"
                )

            subjects.append(
                {
                    "name": name.strip(),
                    "deadline": deadline,
                    "difficulty": difficulty,
                    "total_topics": int(total_topics),
                    "completed_topics": int(completed_topics),
                    "remaining_topics": max(
                        0,
                        int(total_topics - completed_topics)
                    ),
                    "estimated_hours": float(estimated_hours)
                }
            )

    if st.button(
        "🚀 Generate Study Schedule",
        type="primary",
        use_container_width=True
    ):

        valid_subjects = [
            subject
            for subject in subjects
            if subject["name"]
            and subject["completed_topics"] <= subject["total_topics"]
        ]

        if not valid_subjects:

            st.warning(
                "Please enter at least one valid subject."
            )

            st.session_state.pop(
                "study_plan_results",
                None
            )

        else:

            try:

                with st.spinner("Preparing your study schedule..."):

                    st.session_state.study_plan_results = {

                        "subjects": valid_subjects,

                        "daily_hours": float(daily_hours),

                        "days": int(schedule_days),

                        "plan": generate_plan(
                            valid_subjects,
                            float(daily_hours)
                        ),

                        "weekly": generate_weekly_plan(
                            valid_subjects,
                            float(daily_hours),
                            days=int(schedule_days)
                        ),

                        "recommendations": get_study_recommendations(
                            valid_subjects
                        ),

                        "smart_insights": generate_smart_insights(
                            valid_subjects,
                            float(daily_hours)
                        )
                    }

                st.success("Your study schedule is ready!")

            except Exception as exc:

                st.error(
                    "We couldn't generate the schedule. "
                    "Check your subject details and try again."
                )

                with st.expander("Technical details"):
                    st.code(str(exc))

    results = st.session_state.get("study_plan_results")

    if results:

        st.divider()

        st.subheader("📊 Your Study Overview")

        total_subjects = len(results["subjects"])

        total_topics = sum(
            subject["total_topics"]
            for subject in results["subjects"]
        )

        completed_topics = sum(
            subject["completed_topics"]
            for subject in results["subjects"]
        )

        pending_topics = total_topics - completed_topics

        overall_progress = (
            completed_topics / total_topics * 100
            if total_topics > 0
            else 0
        )

        remaining_hours = sum(
            subject["estimated_hours"] * (
                subject["remaining_topics"] /
                subject["total_topics"]
            )
            for subject in results["subjects"]
        )

        urgent_subjects = sum(
            1
            for item in results["subjects"]
            if item["deadline"] <= date.today()
            and item["remaining_topics"] > 0
        )

        m1, m2, m3 = st.columns(3)

        with m1:
            st.metric("Total Subjects", total_subjects)

        with m2:
            st.metric("Completed Topics", completed_topics)

        with m3:
            st.metric("Pending Topics", pending_topics)

        m4, m5, m6 = st.columns(3)

        with m4:
            st.metric(
                "Overall Progress",
                f"{overall_progress:.1f}%"
            )

        with m5:
            st.metric(
                "Remaining Study Hours",
                f"{remaining_hours:.1f} hrs"
            )

        with m6:
            st.metric("Urgent Deadlines", urgent_subjects)

        st.progress(
            overall_progress / 100,
            text=f"Overall syllabus completion: {overall_progress:.1f}%"
        )

        plan_tab, week_tab, tips_tab, insights_tab = st.tabs(
            [
                "🎯 Priority Plan",
                "🗓️ Timetable",
                "💡 Recommendations",
                "📊 Smart Insights"
            ]
        )

        # PRIORITY PLAN
        with plan_tab:

            st.markdown("#### Recommended Study Allocation")

            display_plan = []

            for item in results["plan"]:

                display_plan.append(
                    {
                        "Subject": item["Subject"],
                        "Deadline": item["Deadline"],
                        "Difficulty": item["Difficulty"],
                        "Priority Score": item["Priority Score"],
                        "Recommended Hours/Day": item["Recommended Hours"]
                    }
                )

            if display_plan:

                st.dataframe(
                    display_plan,
                    use_container_width=True,
                    hide_index=True
                )

                st.download_button(
                    "⬇️ Download priority plan (CSV)",
                    data=pd.DataFrame(
                        display_plan
                    ).to_csv(index=False).encode("utf-8"),
                    file_name="study_priority_plan.csv",
                    mime="text/csv"
                )

            else:

                st.info("No priority plan is available.")

        # WEEKLY TIMETABLE
        with week_tab:

            st.markdown(
                f"#### Your {results['days']}-Day Study Timetable"
            )

            weekly_rows = []

            for item in results["weekly"]:

                study_hours = item["Recommended Hours"]

                weekly_rows.append(
                    {
                        "Day": item["Day"],
                        "Date": item["Date"],
                        "Subject": item["Subject"],
                        "Study Hours": study_hours,
                        "Session Length (min)": round(
                            study_hours * 60
                        ),
                        "Session Type": (
                            "Revision"
                            if item["Subject"] == "Revision"
                            else "Study"
                        ),
                        "Remaining Topics": item["Remaining Topics"],
                        "Progress (%)": item["Progress (%)"]
                    }
                )

            if weekly_rows:

                st.dataframe(
                    weekly_rows,
                    use_container_width=True,
                    hide_index=True
                )

                st.download_button(
                    "⬇️ Download timetable (CSV)",
                    data=pd.DataFrame(
                        weekly_rows
                    ).to_csv(index=False).encode("utf-8"),
                    file_name="weekly_study_timetable.csv",
                    mime="text/csv"
                )

            else:

                st.info("No timetable entries available.")

            st.markdown("#### Suggested Study Rhythm")

            st.markdown(
                "- **Focused block:** 25–50 minutes.\n"
                "- **Short break:** 5–10 minutes.\n"
                "- **Revision:** Use active recall and practice questions."
            )

        # RECOMMENDATIONS
        with tips_tab:

            st.markdown("#### Next Best Actions")

            for index, recommendation in enumerate(
                results["recommendations"],
                start=1
            ):

                st.markdown(
                    f"{index}. {recommendation}"
                )

        # SMART INSIGHTS
        with insights_tab:

            st.markdown("#### 📊 Smart Study Analysis")

            insights = results["smart_insights"]

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "Required Daily Hours",
                    f"{insights['total_daily_hours_required']} hrs"
                )

            with col2:

                st.metric(
                    "Available Daily Hours",
                    f"{insights['daily_hours_available']} hrs"
                )

            with col3:

                st.metric(
                    "Workload Status",
                    insights["workload_status"]
                )

            if insights["workload_status"] == "Manageable":

                st.success(
                    "Your estimated daily workload fits "
                    "within your available study hours."
                )

            else:

                st.warning(
                    "Your estimated workload exceeds your "
                    "available daily study hours."
                )

            st.divider()

            st.markdown("#### 📅 Subject-wise Deadline Analysis")

            st.dataframe(
                insights["subjects"],
                use_container_width=True,
                hide_index=True
            )

            st.divider()

            st.markdown("#### 🎯 Subject Completion Forecast")

            for subject in insights["subjects"]:

                with st.container(border=True):

                    st.markdown(
                        f"**{subject['Subject']}**"
                    )

                    st.progress(
                        subject["Progress (%)"] / 100,
                        text=f"Progress: {subject['Progress (%)']}%"
                    )

                    forecast_col1, forecast_col2 = st.columns(2)

                    with forecast_col1:

                        st.write(
                            f"Remaining hours: "
                            f"**{subject['Remaining Hours']} hrs**"
                        )

                    with forecast_col2:

                        st.write(
                            f"Required daily hours: "
                            f"**{subject['Required Hours/Day']} hrs**"
                        )

                    if subject["Status"] == "Completed":

                        st.success("Subject completed!")

                    elif subject["Status"] == "Critical":

                        st.error("Critical: Immediate attention required.")

                    elif subject["Status"] == "Needs Attention":

                        st.warning(
                            "Needs attention: Increase available study time."
                        )

                    else:

                        st.success("On track!")

        if st.button(
            "🧹 Clear generated schedule",
            key="clear_study_schedule"
        ):

            st.session_state.pop(
                "study_plan_results",
                None
            )

            st.rerun()


# ==================================================
# AI RESUME ANALYZER
# ==================================================

elif module == "📄 AI Resume Analyzer":

    st.markdown(
        '<div class="app-eyebrow">CAREER READINESS</div>',
        unsafe_allow_html=True
    )

    st.header("📄 AI Resume Analyzer")

    st.write(
        "Review skills detected in your resume and compare them "
        "with a checklist for your target role."
    )

    st.info(
        "The skill coverage percentage measures matches against "
        "the selected role's checklist. It is not an overall "
        "resume-quality score or a hiring prediction."
    )

    career_goal = st.selectbox(
        "Choose your target career",
        options=list(CAREER_SKILLS.keys()),
        key="resume_career_goal"
    )

    uploaded_file = st.file_uploader(
        "Upload your resume (PDF)",
        type=["pdf"],
        key="resume_pdf_upload"
    )

    if uploaded_file is not None and st.button(
        "🔍 Analyze Resume",
        type="primary"
    ):

        try:

            with st.spinner("Analyzing resume skills..."):

                text = extract_text_from_pdf(uploaded_file)

                if not text.strip():

                    st.warning(
                        "No selectable text was found in this PDF. "
                        "Try uploading a text-based PDF."
                    )

                    st.stop()

                result = analyze_resume(
                    text,
                    career_goal=career_goal
                )

            st.success("Resume analysis completed!")

            st.markdown(
                f"### 🎯 Target role: {result['career_goal']}"
            )

            metric1, metric2, metric3 = st.columns(3)

            with metric1:
                st.metric(
                    "Role Skill Coverage",
                    f"{result['score']}%"
                )

            with metric2:
                st.metric(
                    "Matched Skills",
                    len(result["matched_skills"])
                )

            with metric3:
                st.metric(
                    "Skills to Explore",
                    len(result["missing_skills"])
                )

            st.progress(result["score"] / 100)

            matched_col, gap_col = st.columns(2)

            with matched_col:

                st.subheader("✅ Skills Found")

                if result["matched_skills"]:

                    for skill in result["matched_skills"]:
                        st.markdown(f"- {skill}")

                else:

                    st.write(
                        "No skills from this role checklist were detected."
                    )

            with gap_col:

                st.subheader("🧭 Skills to Develop")

                if result["missing_skills"]:

                    for skill in result["missing_skills"]:
                        st.markdown(f"- {skill}")

                else:

                    st.write(
                        "All skills in this role checklist were detected."
                    )

            st.subheader("💡 Skill Development Suggestions")

            if result["recommendations"]:

                for item in result["recommendations"]:

                    with st.expander(item["skill"]):
                        st.write(item["suggestion"])

            else:

                st.success(
                    "No additional skills from this checklist to recommend."
                )

            with st.expander("View All Detected Resume Skills"):

                if result["skills"]:
                    st.write(", ".join(result["skills"]))
                else:
                    st.write("No predefined skills were detected.")

            with st.expander("View Extracted Resume Text"):
                st.text(text)

        except Exception as exc:

            st.error(
                "We couldn't analyze this PDF. "
                "Please try another text-based PDF resume."
            )

            with st.expander("Technical details"):
                st.code(str(exc))


# ==================================================
# PDF STUDY ASSISTANT
# ==================================================

elif module == "📑 PDF Study Assistant":

    st.markdown(
        '<div class="app-eyebrow">LEARN FROM YOUR OWN NOTES</div>',
        unsafe_allow_html=True
    )

    st.header("📑 PDF Study Assistant")

    st.write(
        "Upload lecture notes or a textbook chapter, "
        "then ask questions about the document."
    )

    st.caption(
        "Answers are retrieved from relevant passages, "
        "not generated by a large language model."
    )

    study_pdf = st.file_uploader(
        "Upload study PDF",
        type=["pdf"],
        key="study_pdf_upload"
    )

    if study_pdf is not None:

        try:

            pdf_text = extract_text_from_pdf(study_pdf)

            if not pdf_text.strip():

                st.warning(
                    "No selectable text was extracted. "
                    "Scanned PDFs may require OCR."
                )

            else:

                st.success(
                    f"PDF ready: {len(pdf_text.split())} words extracted."
                )

                with st.expander("Preview extracted text"):
                    st.text(
                        pdf_text[:5000]
                        + ("…" if len(pdf_text) > 5000 else "")
                    )

                pdf_question = st.text_input(
                    "Ask a question about this PDF",
                    placeholder="Example: Explain the key properties.",
                    key="pdf_study_question"
                )

                if st.button(
                    "Find answer in PDF",
                    type="primary",
                    key="pdf_study_ask"
                ):

                    if pdf_question.strip():

                        result = answer_from_pdf(
                            pdf_question,
                            pdf_text
                        )

                        if result["found"]:

                            st.markdown(result["answer"])

                            st.caption(
                                "Method: keyword-based passage retrieval. "
                                "Verify the passages against the original document."
                            )

                        else:

                            st.info(result["answer"])

                st.download_button(
                    "Download extracted text (.txt)",
                    data=pdf_text,
                    file_name="study_notes_extracted.txt",
                    mime="text/plain"
                )

        except Exception as exc:

            st.error(
                "Could not read this PDF. "
                "Please try a valid, text-based PDF."
            )

            with st.expander("Technical details"):
                st.code(str(exc))


# ==================================================
# CAREER & INTERVIEW COACH
# ==================================================

elif module == "💼 Career & Interview Coach":

    st.markdown(
        '<div class="app-eyebrow">TURN LEARNING INTO CAREER READINESS</div>',
        unsafe_allow_html=True
    )

    st.header("💼 Career & Interview Coach")

    career_tab, interview_tab, prep_tab = st.tabs(
        [
            "Career Roadmap",
            "Interview Practice",
            "Mock Interview"
        ]
    )

    # ------------------------------------------
    # CAREER ROADMAP
    # ------------------------------------------

    with career_tab:

        role = st.selectbox(
            "Choose a target role",
            list(CAREER_ROADMAPS.keys()),
            key="career_roadmap_role"
        )

        st.write(f"### {role}: 5-step roadmap")

        for idx, item in enumerate(
            CAREER_ROADMAPS[role],
            start=1
        ):

            st.markdown(
                f"**Step {idx}.** {item}"
            )

        st.info(
            "Use this as a flexible roadmap, not a guarantee "
            "of employment. Compare it with current job descriptions."
        )

        roadmap_text = "\n".join(
            f"{i}. {item}"
            for i, item in enumerate(
                CAREER_ROADMAPS[role],
                start=1
            )
        )

        st.download_button(
            "Download roadmap (.txt)",
            roadmap_text,
            file_name=(
                f"{role.lower().replace('/', '-')}_roadmap.txt"
            ),
            mime="text/plain"
        )

    # ------------------------------------------
    # INTERVIEW PRACTICE
    # ------------------------------------------

    with interview_tab:

        topic = st.selectbox(
            "Interview topic",
            list(INTERVIEW_BANK.keys()),
            key="interview_topic"
        )

        for idx, (question, answer) in enumerate(
            INTERVIEW_BANK[topic],
            start=1
        ):

            with st.expander(f"{idx}. {question}"):

                st.write(answer)

                st.caption(
                    "Practice tip: answer aloud first, "
                    "then compare your response with this outline."
                )

    # ------------------------------------------
    # MOCK INTERVIEW EVALUATOR
    # ------------------------------------------

    with prep_tab:

        st.markdown("### 🎯 Automated Mock Interview Evaluator")

        st.markdown(
            """
            <div class="module-intro">
                Practise answering technical and HR interview questions.
                Submit your response to receive a practice score,
                keyword coverage, strengths and improvement suggestions.
            </div>
            """,
            unsafe_allow_html=True
        )

        st.info(
            "This API-free evaluator uses keyword coverage, answer length "
            "and basic structure indicators. It does not understand "
            "meaning like a human interviewer or verify technical correctness."
        )

        all_questions = [
            question
            for bank in INTERVIEW_BANK.values()
            for question, answer in bank
        ]

        mock_question = st.selectbox(
            "Select your interview question",
            all_questions,
            key="mock_interview_question"
        )

        reference_answer = next(
            answer
            for bank in INTERVIEW_BANK.values()
            for question, answer in bank
            if question == mock_question
        )

        st.markdown("#### Your Answer")

        mock_answer = st.text_area(
            "Write your response in your own words",
            height=200,
            placeholder=(
                "Type your interview answer here. "
                "Try to include a definition, explanation and example."
            ),
            key="mock_interview_answer"
        )

        word_count = len(mock_answer.strip().split())

        st.caption(f"Word count: {word_count}")

        evaluate_button = st.button(
            "🚀 Evaluate My Answer",
            type="primary",
            use_container_width=True,
            key="evaluate_interview_answer_button"
        )

        if evaluate_button:

            if not mock_answer.strip():

                st.warning(
                    "Please write an answer before submitting."
                )

            else:

                with st.spinner("Evaluating and saving your answer..."):

                    evaluation = evaluate_interview_answer(
                        mock_question,
                        mock_answer
                    )

                    saved_attempt = save_interview_attempt(
                        user_id,
                        mock_question,
                        mock_answer,
                        evaluation
                    )

                if saved_attempt:

                    attempt = {
                        "id": saved_attempt.get("id"),
                        "question": mock_question,
                        "answer": mock_answer,
                        "score": evaluation["score"],
                        "word_count": evaluation["word_count"],
                        "matched": evaluation["matched_keywords"],
                        "missing": evaluation["missing_keywords"],
                        "strengths": evaluation["strengths"],
                        "improvements": evaluation["improvements"],
                        "created_at": saved_attempt.get("created_at")
                    }

                    st.session_state.interview_attempts.append(
                        attempt
                    )

                    st.session_state.latest_interview_evaluation = {
                        "question": mock_question,
                        "answer": mock_answer,
                        "evaluation": evaluation
                    }

                    st.success(
                        "Your interview result has been saved successfully!"
                    )

                    st.rerun()

                else:

                    st.error(
                        "The evaluation could not be saved. "
                        "Your attempt has not been added to the history."
                    )

        # ------------------------------------------
        # EVALUATION RESULTS
        # ------------------------------------------

        latest = st.session_state.get(
            "latest_interview_evaluation"
        )

        if latest:

            evaluation = latest["evaluation"]

            st.divider()

            st.subheader("📊 Your Evaluation Results")

            score = evaluation["score"]

            score_col, word_col, keyword_col = st.columns(3)

            with score_col:

                st.metric(
                    "Interview Score",
                    f"{score}/100"
                )

            with word_col:

                st.metric(
                    "Answer Length",
                    evaluation["word_count"]
                )

            with keyword_col:

                st.metric(
                    "Matched Concepts",
                    len(evaluation["matched_keywords"])
                )

            st.progress(
                score / 100,
                text=f"Practice score: {score}/100"
            )

            if score >= 80:

                st.success(
                    "Strong keyword coverage! Continue improving accuracy and clarity."
                )

            elif score >= 60:

                st.info(
                    "Good attempt. Review the missing concepts to strengthen your answer."
                )

            elif score >= 40:

                st.warning(
                    "Your answer needs improvement. Review the reference explanation."
                )

            else:

                st.error(
                    "Your answer needs more detail and relevant concepts."
                )

            # Matched and missing keywords

            matched_col, missing_col = st.columns(2)

            with matched_col:

                st.markdown("### ✅ Matched Concepts")

                if evaluation["matched_keywords"]:

                    for keyword in evaluation["matched_keywords"]:
                        st.markdown(f"- {keyword}")

                else:

                    st.write("No expected keywords were detected.")

            with missing_col:

                st.markdown("### ❌ Missing Concepts")

                if evaluation["missing_keywords"]:

                    for keyword in evaluation["missing_keywords"]:
                        st.markdown(f"- {keyword}")

                else:

                    st.success(
                        "All expected keywords were detected."
                    )

            st.divider()

            # Strengths

            st.markdown("### 💪 Strengths")

            for strength in evaluation["strengths"]:
                st.markdown(f"- {strength}")

            # Improvements

            st.markdown("### 🧭 Areas to Improve")

            for improvement in evaluation["improvements"]:
                st.markdown(f"- {improvement}")

            # Reference answer for the evaluated question

            latest_reference_answer = next(
                (
                    answer
                    for bank in INTERVIEW_BANK.values()
                    for question, answer in bank
                    if question == latest["question"]
                ),
                "No reference answer is available."
            )

            with st.expander("📖 Compare with Reference Answer"):

                st.write(latest["question"])

                st.markdown(
                    f"**Reference explanation:** {latest_reference_answer}"
                )

                st.caption(
                    "Use this as a learning reference, not as the only acceptable answer."
                )

        # ------------------------------------------
        # PERFORMANCE TRACKING
        # ------------------------------------------

        st.divider()

        st.subheader("📈 Interview Performance Dashboard")

        attempts = st.session_state.interview_attempts

        if attempts:

            total_attempts = len(attempts)

            average_score = sum(
                item["score"] for item in attempts
            ) / total_attempts

            latest_score = attempts[-1]["score"]

            best_score = max(
                item["score"] for item in attempts
            )

            metric1, metric2, metric3, metric4 = st.columns(4)

            with metric1:

                st.metric(
                    "Total Attempts",
                    total_attempts
                )

            with metric2:

                st.metric(
                    "Average Score",
                    f"{average_score:.1f}/100"
                )

            with metric3:

                st.metric(
                    "Latest Score",
                    f"{latest_score}/100"
                )

            with metric4:

                st.metric(
                    "Best Score",
                    f"{best_score}/100"
                )

            st.markdown("#### Attempt History")

            history_rows = []

            for index, item in enumerate(
                attempts,
                start=1
            ):

                history_rows.append(
                    {
                        "Attempt": index,
                        "Question": item["question"],
                        "Score": item["score"],
                        "Word Count": item["word_count"],
                        "Matched Concepts": len(item["matched"])
                    }
                )

            st.dataframe(
                history_rows,
                use_container_width=True,
                hide_index=True
            )

            chart_data = pd.DataFrame(
                {
                    "Attempt": list(
                        range(1, total_attempts + 1)
                    ),
                    "Score": [
                        item["score"]
                        for item in attempts
                    ]
                }
            )

            st.markdown("#### Score Progress")

            st.line_chart(
                chart_data.set_index("Attempt")
            )

            if st.button(
                "🧹 Clear Interview History",
                key="clear_interview_history"
            ):

                if delete_interview_history(user_id):

                    st.session_state.interview_attempts = []

                    st.session_state.pop(
                        "latest_interview_evaluation",
                        None
                    )

                    st.success(
                        "Your interview history has been deleted."
                    )

                    st.rerun()

        else:

            st.info(
                "No interview attempts yet. Submit your first answer "
                "to start tracking your performance."
            )

        st.caption(
            "Your interview attempts are saved securely in Supabase "
            "and linked to your account. You can access your history "
            "again after logging in."
        )


# ==================================================
# STUDENT CHATBOT
# ==================================================

elif module == "🤖 Student Chatbot":

    st.markdown(
        '<div class="app-eyebrow">YOUR STUDY & CAREER COMPANION</div>',
        unsafe_allow_html=True
    )

    st.header("🤖 Student Chatbot")

    st.markdown(
        "Ask about Python, DSA, DBMS/SQL, core CS, AI/ML, "
        "resumes, study habits, placements or projects."
    )

    with st.expander(
        "About this chatbot",
        expanded=False
    ):

        st.write(
            "This chatbot uses topic matching and prepared guidance "
            "without an external API. Conversation history can be "
            "stored in Supabase if the optional chat-history table "
            "has been created."
        )

    history_key = f"student_chat_history_{user_id}"

    if history_key not in st.session_state:

        loaded_history = []

        try:

            history_result = (
                supabase.table("assistant_chat_messages")
                .select("role, content")
                .eq("user_id", user_id)
                .order("created_at")
                .limit(100)
                .execute()
            )

            loaded_history = history_result.data or []

        except Exception:
            pass

        st.session_state[history_key] = loaded_history or [
            {
                "role": "assistant",
                "content": (
                    "Hi! 👋 I'm your Student Assistant. "
                    "Ask me about Python, DSA, placements, "
                    "career options, AI/ML, resumes, projects, "
                    "or study planning."
                )
            }
        ]

    def add_chat_message(role, content):

        st.session_state[history_key].append(
            {
                "role": role,
                "content": content
            }
        )

        try:

            supabase.table("assistant_chat_messages").insert(
                {
                    "user_id": user_id,
                    "role": role,
                    "content": content
                }
            ).execute()

        except Exception:
            pass

    st.markdown("#### 💡 Suggested Questions")

    suggested_questions = [
        "How do I start learning Python?",
        "Give me a placement preparation plan",
        "How should I prepare DSA?",
        "Explain the AI/ML learning path"
    ]

    suggestion_cols = st.columns(2)

    for index, question in enumerate(suggested_questions):

        with suggestion_cols[index % 2]:

            if st.button(
                question,
                key=f"chat_suggestion_{index}",
                use_container_width=True
            ):

                add_chat_message("user", question)

                add_chat_message(
                    "assistant",
                    get_student_chatbot_response(question)
                )

                st.rerun()

    st.divider()

    for message in st.session_state[history_key][-100:]:

        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_prompt = st.chat_input(
        "Ask a study or career question..."
    )

    if user_prompt:

        add_chat_message("user", user_prompt)

        reply = get_student_chatbot_response(
            user_prompt
        )

        add_chat_message("assistant", reply)

        st.rerun()

    if st.button(
        "🧹 Clear chat history",
        key="clear_student_chat"
    ):

        st.session_state[history_key] = [
            {
                "role": "assistant",
                "content": (
                    "Chat cleared. 👋 Ask me about Python, DSA, "
                    "placements, careers, AI/ML, resumes, projects, "
                    "or study planning."
                )
            }
        ]

        try:

            supabase.table(
                "assistant_chat_messages"
            ).delete().eq(
                "user_id",
                user_id
            ).execute()

        except Exception:
            pass

        st.rerun()
