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
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# CUSTOM UI THEME — presentation only
# --------------------------------------------------
st.markdown("""
<style>
/* App canvas */
.stApp {
    background:
        radial-gradient(ellipse at 12% 0%, rgba(91, 63, 170, 0.15), transparent 34%),
        radial-gradient(ellipse at 95% 10%, rgba(37, 99, 235, 0.10), transparent 30%),
        #0b0d14;
    color: #edf0f7;
}

/* Main content spacing and width */
.block-container {
    padding-top: 2.2rem;
    padding-bottom: 3rem;
    max-width: 1450px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #171923 0%, #141622 100%);
    border-right: 1px solid rgba(167, 139, 250, 0.18);
}
section[data-testid="stSidebar"] > div {
    padding-top: 2rem;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #f4f1ff;
}

/* Typography */
h1, h2, h3 {
    letter-spacing: -0.035em;
}
h1 {
    color: #fbfaff;
    font-size: clamp(2rem, 3vw, 2.8rem) !important;
    font-weight: 750 !important;
}
h2 {
    color: #f2edff;
    font-weight: 700 !important;
}
h3 {
    color: #dcd2ff;
    font-weight: 650 !important;
}
p, label, [data-testid="stMarkdownContainer"] {
    color: #d7d9e4;
}
small, .stCaption {
    color: #a9afc2 !important;
}

/* Hero panel */
.hero-panel {
    background: linear-gradient(120deg, rgba(124, 58, 237, 0.20), rgba(37, 99, 235, 0.12) 58%, rgba(20, 24, 40, 0.78));
    border: 1px solid rgba(167, 139, 250, 0.28);
    border-radius: 22px;
    padding: 1.6rem 1.8rem;
    margin: 0.35rem 0 1.35rem 0;
    box-shadow: 0 14px 40px rgba(0, 0, 0, 0.16);
}
.hero-eyebrow {
    color: #c4b5fd;
    font-size: 0.78rem;
    font-weight: 750;
    letter-spacing: 0.13em;
    text-transform: uppercase;
    margin-bottom: 0.55rem;
}
.hero-title {
    color: #ffffff;
    font-size: clamp(1.65rem, 2.7vw, 2.35rem);
    line-height: 1.18;
    font-weight: 800;
    margin-bottom: 0.65rem;
}
.hero-copy {
    color: #cdd2e2;
    font-size: 1rem;
    line-height: 1.65;
    max-width: 760px;
}

/* Feature cards */
.feature-card {
    height: 100%;
    min-height: 190px;
    padding: 1.35rem 1.4rem;
    background: linear-gradient(145deg, rgba(27, 31, 48, 0.96), rgba(19, 22, 35, 0.96));
    border: 1px solid rgba(148, 163, 184, 0.17);
    border-radius: 18px;
    box-shadow: 0 10px 28px rgba(0, 0, 0, 0.12);
}
.feature-icon {
    font-size: 1.7rem;
    margin-bottom: 0.65rem;
}
.feature-title {
    color: #f6f4ff;
    font-size: 1.15rem;
    font-weight: 750;
    margin-bottom: 0.5rem;
}
.feature-copy {
    color: #b9c0d2;
    line-height: 1.6;
    font-size: 0.94rem;
}

/* Section labels */
.section-kicker {
    color: #a78bfa;
    font-size: 0.76rem;
    font-weight: 750;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 0.35rem;
}

/* Form controls */
div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div,
div[data-baseweb="textarea"] > div {
    background: #191c29 !important;
    border: 1px solid #34384b !important;
    border-radius: 10px !important;
}
div[data-baseweb="input"] input,
div[data-baseweb="textarea"] textarea {
    color: #f4f5fb !important;
}
div[data-baseweb="select"] * {
    color: #f4f5fb !important;
}
div[data-testid="stDateInput"] input {
    color: #f4f5fb !important;
}
div[data-testid="stFileUploader"] {
    background: rgba(25, 28, 41, 0.72);
    border: 1px dashed rgba(167, 139, 250, 0.48);
    border-radius: 15px;
    padding: 0.85rem;
}
div[data-testid="stFileUploader"] section {
    border: 0;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(100deg, #7c3aed 0%, #4f46e5 55%, #2563eb 100%);
    color: #ffffff;
    border: 1px solid rgba(196, 181, 253, 0.25);
    border-radius: 10px;
    padding: 0.58rem 1rem;
    font-weight: 700;
    transition: filter 0.15s ease, transform 0.15s ease;
}
.stButton > button:hover {
    color: #ffffff;
    border-color: rgba(221, 214, 254, 0.65);
    filter: brightness(1.12);
    transform: translateY(-1px);
}

/* Metrics, alerts, tables and expanders */
div[data-testid="stMetric"] {
    background: linear-gradient(145deg, #1b1f30, #151827);
    border: 1px solid rgba(167, 139, 250, 0.22);
    border-radius: 16px;
    padding: 1rem 1.15rem;
}
div[data-testid="stMetricLabel"] {
    color: #b9c0d2 !important;
}
div[data-testid="stMetricValue"] {
    color: #e9ddff !important;
}
div[data-testid="stAlert"] {
    border-radius: 12px;
}
div[data-testid="stDataFrame"] {
    border: 1px solid rgba(167, 139, 250, 0.2);
    border-radius: 12px;
    overflow: hidden;
}
details {
    background: rgba(25, 28, 41, 0.55);
    border: 1px solid rgba(148, 163, 184, 0.15);
    border-radius: 12px;
}
hr {
    border-color: rgba(148, 163, 184, 0.18);
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .block-container {
        padding-top: 1.2rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    .hero-panel {
        padding: 1.2rem;
        border-radius: 16px;
    }
    .feature-card {
        min-height: auto;
        margin-bottom: 0.8rem;
    }
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.markdown("""
<div class="hero-panel">
    <div class="hero-eyebrow">Your academic and career workspace</div>
    <div class="hero-title">🎓 AI Student Career &amp; Academic Assistant</div>
    <div class="hero-copy">
        Plan your study time, organize your academic priorities, and review
        the skills highlighted in your resume — all in one place.
    </div>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
st.sidebar.markdown("## Navigation")
st.sidebar.caption("Choose a workspace")

module = st.sidebar.radio(
    "Select a module:",
    [
        "🏠 Home",
        "📚 AI Study Planner",
        "📄 AI Resume Analyzer"
    ],
    label_visibility="collapsed"
)

st.sidebar.divider()
st.sidebar.markdown(
    "<div style='color:#9ca3b8;font-size:0.8rem;line-height:1.6;'>"
    "AI Student Assistant<br>Academic planning • Career readiness"
    "</div>",
    unsafe_allow_html=True
)

# ==================================================
# HOME
# ==================================================
if module == "🏠 Home":

    st.markdown('<div class="section-kicker">Overview</div>', unsafe_allow_html=True)
    st.header("Welcome to your workspace")
    st.write(
        "Your student-focused toolkit brings academic planning and career "
        "readiness together in one simple application."
    )

    st.write("")
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📚</div>
            <div class="feature-title">AI Study Planner</div>
            <div class="feature-copy">
                Build a prioritized study plan based on subject difficulty,
                deadlines, and the amount of time you have available each day.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📄</div>
            <div class="feature-title">AI Resume Analyzer</div>
            <div class="feature-copy">
                Upload a PDF resume to identify predefined skills, review
                detected and missing skills, and understand your skill coverage.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.info("Choose a module from the navigation sidebar to get started.")

# ==================================================
# STUDY PLANNER — existing functionality retained
# ==================================================
elif module == "📚 AI Study Planner":

    st.markdown('<div class="section-kicker">Academic planning</div>', unsafe_allow_html=True)
    st.header("📚 AI Study Planner")
    st.write(
        "Create a personalized study plan based on your subjects, deadlines "
        "and difficulty levels."
    )

    st.write("")
    hours_col, subjects_col = st.columns([1, 1], gap="large")

    with hours_col:
        daily_hours = st.number_input(
            "Available study hours per day",
            min_value=1.0,
            max_value=24.0,
            value=4.0,
            step=0.5
        )

    with subjects_col:
        number_of_subjects = st.number_input(
            "Number of subjects",
            min_value=1,
            max_value=10,
            value=3,
            step=1
        )

    st.divider()
    st.markdown('<div class="section-kicker">Your subjects</div>', unsafe_allow_html=True)
    st.subheader("Enter Subject Details")
    st.caption("Add a name, deadline, and difficulty level for each subject.")

    subjects = []

    for i in range(int(number_of_subjects)):
        with st.container(border=True):
            st.markdown(f"#### 📘 Subject {i + 1}")
            col1, col2, col3 = st.columns(3, gap="medium")

            with col1:
                name = st.text_input(
                    "Subject name",
                    key=f"name_{i}",
                    placeholder="e.g. Machine Learning"
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

    st.write("")
    if st.button("🚀 Generate Study Plan", use_container_width=False):

        valid_subjects = [
            subject
            for subject in subjects
            if subject["name"].strip()
        ]

        if not valid_subjects:
            st.warning("Please enter at least one subject.")

        else:
            plan = generate_plan(
                valid_subjects,
                daily_hours
            )

            st.success("Study plan generated successfully!")
            st.markdown('<div class="section-kicker">Your results</div>', unsafe_allow_html=True)
            st.subheader("📋 Recommended Study Plan")
            st.dataframe(
                plan,
                use_container_width=True,
                hide_index=True
            )

# ==================================================
# RESUME ANALYZER — existing functionality retained
# ==================================================
elif module == "📄 AI Resume Analyzer":

    st.markdown('<div class="section-kicker">Career readiness</div>', unsafe_allow_html=True)
    st.header("📄 AI Resume Analyzer")
    st.write(
        "Upload your resume to identify skills and receive a basic resume analysis."
    )

    st.write("")
    st.markdown("#### Upload your resume")
    st.caption("Choose a text-based PDF file for the best extraction results.")

    uploaded_file = st.file_uploader(
        "Upload your resume (PDF)",
        type=["pdf"],
        help="Only PDF files are supported."
    )

    if uploaded_file is not None:
        st.success(f"Ready to analyze: {uploaded_file.name}")

        if st.button("🔍 Analyze Resume", use_container_width=False):

            with st.spinner("Analyzing your resume..."):
                text = extract_text_from_pdf(uploaded_file)
                result = analyze_resume(text)

            if not text.strip():
                st.error(
                    "No readable text was extracted from this PDF. "
                    "Try uploading a text-based PDF rather than a scanned image."
                )
                st.stop()

            st.success("Resume analysis completed!")

            st.markdown('<div class="section-kicker">Analysis results</div>', unsafe_allow_html=True)
            st.subheader("📊 Resume Score")

            st.metric(
                "Skill Coverage",
                f"{result['score']}%"
            )

            st.caption(
                "Skill coverage reflects the predefined skills detected by this "
                "analyzer; it is not a formal ATS score."
            )

            st.divider()
            skills_col, missing_col = st.columns(2, gap="large")

            with skills_col:
                st.subheader("✅ Detected Skills")
                if result["skills"]:
                    st.write(", ".join(result["skills"]))
                else:
                    st.write("No predefined skills detected.")

            with missing_col:
                st.subheader("⚠️ Skills Not Detected")
                if result["missing_skills"]:
                    st.write(", ".join(result["missing_skills"]))
                else:
                    st.write("All listed skills were detected.")

            with st.expander("View Extracted Resume Text"):
                st.text(text)
