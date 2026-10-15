import streamlit as st
from datetime import date
from html import escape
from supabase import create_client, Client

from planner import generate_plan
from resume_analyzer import extract_text_from_pdf, analyze_resume


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
    card1, card2, card3 = st.columns(3)
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
# STUDY PLANNER (EXISTING FUNCTIONALITY PRESERVED)
# ==================================================
elif module == "📚 AI Study Planner":
    st.markdown('<div class="app-eyebrow">PLAN WITH PURPOSE</div>', unsafe_allow_html=True)
    st.header("📚 AI Study Planner")
    st.write("Create a personalized study plan based on your subjects, deadlines and difficulty levels.")
    st.info("Tip: Add each subject with its deadline and difficulty so the planner can prioritize your workload.")

    daily_hours = st.number_input(
        "Available study hours per day",
        min_value=1.0,
        max_value=24.0,
        value=4.0,
        step=0.5,
    )
    st.subheader("Enter Subject Details")
    number_of_subjects = st.number_input(
        "Number of subjects", min_value=1, max_value=10, value=3, step=1
    )

    subjects = []
    for i in range(int(number_of_subjects)):
        st.markdown(f"### Subject {i + 1}")
        col1, col2, col3 = st.columns(3)
        with col1:
            name = st.text_input("Subject name", key=f"name_{i}")
        with col2:
            deadline = st.date_input("Deadline", value=date.today(), key=f"deadline_{i}")
        with col3:
            difficulty = st.selectbox(
                "Difficulty", ["Easy", "Medium", "Hard"], key=f"difficulty_{i}"
            )
        subjects.append({"name": name, "deadline": deadline, "difficulty": difficulty})

    if st.button("🚀 Generate Study Plan"):
        valid_subjects = [subject for subject in subjects if subject["name"].strip()]
        if not valid_subjects:
            st.warning("Please enter at least one subject.")
        else:
            plan = generate_plan(valid_subjects, daily_hours)
            st.success("Study plan generated successfully!")
            st.subheader("📋 Recommended Study Plan")
            st.dataframe(plan, use_container_width=True)


# ==================================================
# RESUME ANALYZER (EXISTING FUNCTIONALITY PRESERVED)
# ==================================================
elif module == "📄 AI Resume Analyzer":
    st.markdown('<div class="app-eyebrow">CAREER READINESS</div>', unsafe_allow_html=True)
    st.header("📄 AI Resume Analyzer")
    st.write("Upload your resume to identify skills and review your current skill coverage.")
    st.info("For best results, upload a text-based PDF rather than a scanned image of a resume.")

    uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
    if uploaded_file is not None and st.button("🔍 Analyze Resume"):
        with st.spinner("Analyzing resume..."):
            text = extract_text_from_pdf(uploaded_file)
            result = analyze_resume(text)

        st.success("Resume analysis completed!")
        st.subheader("📊 Resume Score")
        st.metric("Skill Coverage", f"{result['score']}%")

        st.subheader("✅ Detected Skills")
        if result["skills"]:
            st.write(", ".join(result["skills"]))
        else:
            st.write("No predefined skills detected.")

        st.subheader("⚠️ Skills Not Detected")
        if result["missing_skills"]:
            st.write(", ".join(result["missing_skills"]))
        else:
            st.write("All listed skills were detected.")

        with st.expander("View Extracted Resume Text"):
            st.text(text)
