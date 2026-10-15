import streamlit as st
from datetime import date
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
    st.title("🎓 AI Student Career & Academic Assistant")
    st.write("Sign in or create an account to access your student workspace.")

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
                except Exception:
                    st.error(
                        "Registration failed. The email may already be registered, or Supabase "
                        "may be limiting email delivery. Check the Supabase Auth logs/settings and try again."
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
st.title("🎓 AI Student Career & Academic Assistant")
st.caption("Your workspace for academic planning and career readiness.")

with st.sidebar:
    st.title("Student Workspace")
    st.write(f"Signed in as **{user_email}**")
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
    st.header(f"Welcome, {profile.get('full_name') or 'Student'}! 👋")
    st.write(
        "Use your personal workspace to organize study time, review your resume skills, "
        "and keep your academic profile up to date."
    )

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📚 AI Study Planner")
        st.write("Prioritize subjects using deadlines, difficulty, and your available study hours.")
    with col2:
        st.subheader("📄 AI Resume Analyzer")
        st.write("Upload a PDF resume to identify listed skills and skills to consider developing.")

    st.info("Use the navigation menu in the sidebar to open a module or edit your profile.")


# ==================================================
# PROFILE
# ==================================================
elif module == "👤 My Profile":
    st.header("👤 My Student Profile")
    st.write("Update the details associated with your account.")

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
    st.header("📚 AI Study Planner")
    st.write("Create a personalized study plan based on your subjects, deadlines and difficulty levels.")

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
    st.header("📄 AI Resume Analyzer")
    st.write("Upload your resume to identify skills and receive a basic resume analysis.")

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
