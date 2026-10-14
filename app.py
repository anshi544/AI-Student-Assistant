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
# PROFESSIONAL UI THEME
# Restrained navy / slate / blue palette for a formal panel presentation.
# No changes to planner or resume-analysis logic.
# --------------------------------------------------
st.markdown("""
<style>
:root {
    --app-bg: #0f172a;
    --panel-bg: #172033;
    --card-bg: #1b263a;
    --border: #334155;
    --text: #f1f5f9;
    --muted: #bdc8d8;
    --accent: #60a5fa;
}
.stApp {
    background: #0b1220;
    color: var(--text);
}
.block-container {
    max-width: 1380px;
    padding-top: 1.8rem;
    padding-bottom: 3rem;
}
section[data-testid="stSidebar"] {
    background: #111827;
    border-right: 1px solid #263449;
}
section[data-testid="stSidebar"] > div {
    padding-top: 1.8rem;
}
h1, h2, h3 {
    color: #f8fafc !important;
    letter-spacing: -0.025em;
}
h1 {
    font-size: clamp(1.8rem, 2.6vw, 2.45rem) !important;
    font-weight: 750 !important;
}
h2 {
    font-size: 1.55rem !important;
    font-weight: 700 !important;
}
h3 {
    font-size: 1.15rem !important;
    font-weight: 650 !important;
}
p, label, [data-testid="stMarkdownContainer"] {
    color: #d5deeb;
}
[data-testid="stCaptionContainer"] {
    color: #aab8cc !important;
}
.hero {
    padding: 1.65rem 1.8rem;
    border-radius: 16px;
    border: 1px solid #34445d;
    background: linear-gradient(115deg, #17243a 0%, #172033 65%, #1c2940 100%);
    margin: 0.25rem 0 1.5rem 0;
}
.eyebrow {
    color: #93c5fd;
    text-transform: uppercase;
    font-size: 0.75rem;
    font-weight: 750;
    letter-spacing: 0.12em;
    margin-bottom: 0.5rem;
}
.hero-title {
    color: #ffffff;
    font-size: clamp(1.65rem, 2.4vw, 2.3rem);
    font-weight: 800;
    line-height: 1.2;
    margin-bottom: 0.65rem;
}
.hero-copy {
    color: #c5d1e2;
    font-size: 1rem;
    line-height: 1.6;
    max-width: 850px;
}
.feature-card {
    height: 100%;
    min-height: 175px;
    padding: 1.3rem;
    border-radius: 14px;
    border: 1px solid #334155;
    background: #151f31;
}
.feature-icon {
    font-size: 1.55rem;
    margin-bottom: 0.7rem;
}
.feature-title {
    color: #f8fafc;
    font-size: 1.12rem;
    font-weight: 750;
    margin-bottom: 0.5rem;
}
.feature-copy {
    color: #c1ccdc;
    line-height: 1.6;
    font-size: 0.93rem;
}
.section-label {
    color: #93c5fd;
    font-size: 0.74rem;
    font-weight: 750;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 0.35rem;
}
div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div,
div[data-baseweb="textarea"] > div {
    background: #151f31 !important;
    border: 1px solid #3a4960 !important;
    border-radius: 8px !important;
}
div[data-baseweb="input"] input,
div[data-baseweb="textarea"] textarea,
div[data-baseweb="select"] * {
    color: #f1f5f9 !important;
}
div[data-testid="stDateInput"] input {
    color: #f1f5f9 !important;
}
div[data-testid="stFileUploader"] {
    background: #151f31;
    border: 1px dashed #526782;
    border-radius: 12px;
    padding: 0.75rem;
}
.stButton > button {
    background: #2563eb;
    color: #ffffff;
    border: 1px solid #3b82f6;
    border-radius: 8px;
    font-weight: 650;
    padding: 0.55rem 0.95rem;
    transition: background 0.15s ease;
}
.stButton > button:hover {
    background: #1d4ed8;
    border-color: #60a5fa;
    color: #ffffff;
}
div[data-testid="stMetric"] {
    background: #151f31;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 1rem;
}
div[data-testid="stMetricLabel"] {
    color: #bdc8d8 !important;
}
div[data-testid="stMetricValue"] {
    color: #bfdbfe !important;
}
div[data-testid="stDataFrame"] {
    border: 1px solid #334155;
    border-radius: 10px;
    overflow: hidden;
}
details {
    background: #151f31;
    border: 1px solid #334155;
    border-radius: 10px;
}
hr {
    border-color: #2d3a4f;
}
@media (max-width: 768px) {
    .block-container {
        padding: 1rem 1rem 2rem 1rem;
    }
    .hero {
        padding: 1.2rem;
    }
    .feature-card {
        min-height: auto;
        margin-bottom: 0.7rem;
    }
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.markdown("""
<div class="hero">
    <div class="eyebrow">Academic planning • Career readiness</div>
    <div class="hero-title">🎓 AI Student Career &amp; Academic Assistant</div>
    <div class="hero-copy">
        A student-focused platform to organize study priorities and review
        the skills highlighted in your resume.
    </div>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
st.sidebar.markdown("## Navigation")
st.sidebar.caption("Select a module")

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
st.sidebar.caption("AI Student Assistant | Academic & Career Toolkit")

# ==================================================
# HOME
# ==================================================
if module == "🏠 Home":

    st.markdown('<div class="section-label">Overview</div>', unsafe_allow_html=True)
    st.header("Welcome")
    st.write(
        "This platform integrates two student-focused modules into one "
        "application to support academic planning and career readiness."
    )

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📚</div>
            <div class="feature-title">AI Study Planner</div>
            <div class="feature-copy">
                Creates a prioritized study plan based on subject difficulty,
                deadlines, and available study time.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📄</div>
            <div class="feature-title">AI Resume Analyzer</div>
            <div class="feature-copy">
                Analyzes a student's PDF resume, identifies predefined skills,
                and provides a basic overview of skill coverage.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.info("Select a module from the sidebar to begin.")

# ==================================================
# STUDY PLANNER — existing calculations retained
# ==================================================
elif module == "📚 AI Study Planner":

    st.markdown('<div class="section-label">Academic planning</div>', unsafe_allow_html=True)
    st.header("📚 AI Study Planner")
    st.write(
        "Create a personalized study plan based on your subjects, deadlines "
        "and difficulty levels."
    )

    st.write("")
    top_col1, top_col2 = st.columns(2, gap="large")

    with top_col1:
        daily_hours = st.number_input(
            "Available study hours per day",
            min_value=1.0,
            max_value=24.0,
            value=4.0,
            step=0.5
        )

    with top_col2:
        number_of_subjects = st.number_input(
            "Number of subjects",
            min_value=1,
            max_value=10,
            value=3,
            step=1
        )

    st.divider()
    st.subheader("Enter Subject Details")
    st.caption("Provide the subject name, deadline, and difficulty level.")

    subjects = []

    for i in range(int(number_of_subjects)):
        with st.container(border=True):
            st.markdown(f"#### Subject {i + 1}")
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
    if st.button("Generate Study Plan  →"):

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
            st.subheader("📋 Recommended Study Plan")
            st.dataframe(
                plan,
                use_container_width=True
            )

# ==================================================
# RESUME ANALYZER — existing analysis retained
# ==================================================
elif module == "📄 AI Resume Analyzer":

    st.markdown('<div class="section-label">Career readiness</div>', unsafe_allow_html=True)
    st.header("📄 AI Resume Analyzer")
    st.write(
        "Upload your resume to identify skills and receive a basic resume analysis."
    )

    st.write("")
    st.markdown("#### Upload your resume (PDF)")
    st.caption("For best results, upload a PDF that contains selectable text.")

    uploaded_file = st.file_uploader(
        "Upload your resume (PDF)",
        type=["pdf"]
    )

    if uploaded_file is not None:
        st.success(f"File ready: {uploaded_file.name}")

        if st.button("Analyze Resume  →"):

            with st.spinner("Analyzing resume..."):

                text = extract_text_from_pdf(
                    uploaded_file
                )

                result = analyze_resume(text)

            if not text.strip():
                st.error(
                    "No readable text was extracted from this PDF. "
                    "Try uploading a text-based PDF."
                )
                st.stop()

            st.success("Resume analysis completed!")

            st.subheader("📊 Resume Score")
            st.metric(
                "Skill Coverage",
                f"{result['score']}%"
            )
            st.caption(
                "This score represents coverage of the analyzer's predefined "
                "skill list; it is not a formal ATS score."
            )

            st.divider()
            col1, col2 = st.columns(2, gap="large")

            with col1:
                st.subheader("✅ Detected Skills")
                if result["skills"]:
                    st.write(", ".join(result["skills"]))
                else:
                    st.write("No predefined skills detected.")

            with col2:
                st.subheader("⚠️ Skills Not Detected")
                if result["missing_skills"]:
                    st.write(", ".join(result["missing_skills"]))
                else:
                    st.write("All listed skills were detected.")

            with st.expander("View Extracted Resume Text"):
                st.text(text)
