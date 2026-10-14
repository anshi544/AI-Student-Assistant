import streamlit as st
from datetime import date

from planner import generate_plan
from resume_analyzer import (
    extract_text_from_pdf,
    analyze_resume
)

# ---------------------------------------------------------
# Page setup
# ---------------------------------------------------------
st.set_page_config(
    page_title="AI Student Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# UI styling only — existing planner/analyzer logic remains
# unchanged.
# ---------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

    :root {
        --ink: #17243a;
        --muted: #66758b;
        --line: #e4eaf2;
        --paper: #ffffff;
        --canvas: #f4f7fb;
        --blue: #315fce;
        --blue-dark: #2449a5;
        --blue-soft: #eaf0ff;
        --teal-soft: #e7f6f3;
        --teal: #187b70;
        --amber-soft: #fff4df;
    }

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .stApp {
        background: var(--canvas);
        color: var(--ink);
    }

    [data-testid="stHeader"] {
        background: rgba(244, 247, 251, 0.92);
    }

    [data-testid="stSidebar"] {
        background: #17243a;
        border-right: 1px solid #26344b;
    }
    [data-testid="stSidebar"] * {
        color: #eef3ff;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #c4cee0;
    }
    [data-testid="stSidebar"] hr {
        border-color: #34425a;
    }
    [data-testid="stSidebar"] label {
        color: #eef3ff !important;
    }
    [data-testid="stSidebar"] [role="radiogroup"] {
        gap: 0.4rem;
    }
    [data-testid="stSidebar"] [role="radiogroup"] label {
        border-radius: 10px;
        padding: 0.55rem 0.65rem;
    }

    .brand-mark {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 44px;
        height: 44px;
        border-radius: 14px;
        background: #315fce;
        color: white;
        font-size: 22px;
        margin-bottom: 12px;
        box-shadow: 0 8px 18px rgba(49, 95, 206, 0.25);
    }
    .sidebar-brand {
        font-family: 'Manrope', sans-serif;
        font-size: 1.1rem;
        line-height: 1.25;
        font-weight: 800;
        color: white;
        margin-bottom: 4px;
    }
    .sidebar-caption {
        color: #aebbd1 !important;
        font-size: 0.82rem;
        margin-bottom: 1.1rem;
    }

    .eyebrow {
        color: var(--blue);
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-size: 0.72rem;
        font-weight: 800;
        margin-bottom: 0.55rem;
    }
    .hero-title {
        font-family: 'Manrope', sans-serif;
        font-size: clamp(2rem, 4vw, 3.15rem);
        font-weight: 800;
        letter-spacing: -0.045em;
        line-height: 1.12;
        color: var(--ink);
        margin: 0 0 0.8rem 0;
    }
    .hero-copy {
        max-width: 760px;
        color: var(--muted);
        font-size: 1.05rem;
        line-height: 1.7;
        margin-bottom: 1.5rem;
    }
    .page-title {
        font-family: 'Manrope', sans-serif;
        color: var(--ink);
        font-weight: 800;
        letter-spacing: -0.035em;
        font-size: clamp(1.7rem, 3vw, 2.3rem);
        margin-bottom: 0.25rem;
    }
    .page-subtitle {
        color: var(--muted);
        line-height: 1.65;
        margin-bottom: 1.25rem;
    }

    .surface-card {
        background: var(--paper);
        border: 1px solid var(--line);
        border-radius: 18px;
        padding: 1.25rem 1.3rem;
        box-shadow: 0 4px 18px rgba(28, 45, 75, 0.035);
        min-height: 185px;
    }
    .surface-card .card-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 43px;
        height: 43px;
        border-radius: 13px;
        font-size: 1.3rem;
        margin-bottom: 0.8rem;
    }
    .icon-blue { background: var(--blue-soft); }
    .icon-teal { background: var(--teal-soft); }
    .surface-card h3 {
        font-family: 'Manrope', sans-serif;
        font-size: 1.08rem;
        font-weight: 800;
        margin: 0 0 0.45rem 0;
        color: var(--ink);
    }
    .surface-card p {
        color: var(--muted);
        font-size: 0.94rem;
        line-height: 1.6;
        margin: 0;
    }
    .section-label {
        font-family: 'Manrope', sans-serif;
        font-size: 1.15rem;
        font-weight: 800;
        color: var(--ink);
        margin: 1.2rem 0 0.8rem 0;
    }
    .helper-panel {
        background: #edf3ff;
        border: 1px solid #d8e4ff;
        border-radius: 14px;
        padding: 1rem 1.1rem;
        color: #294577;
        line-height: 1.6;
    }
    .helper-panel strong { color: #1d3c7d; }
    .result-panel {
        background: white;
        border: 1px solid var(--line);
        border-radius: 16px;
        padding: 1.1rem 1.2rem;
        margin: 0.6rem 0 1rem 0;
    }
    .stButton > button {
        border-radius: 10px;
        border: 1px solid var(--blue);
        background: var(--blue);
        color: white;
        font-weight: 700;
        padding: 0.58rem 1rem;
        min-height: 2.7rem;
        transition: all 0.15s ease-in-out;
    }
    .stButton > button:hover {
        background: var(--blue-dark);
        border-color: var(--blue-dark);
        color: white;
    }
    .stTextInput input, .stNumberInput input, .stDateInput input,
    .stSelectbox [data-baseweb="select"] > div {
        border-radius: 10px;
    }
    [data-testid="stFileUploader"] {
        background: white;
        border: 1px dashed #bdcbe0;
        border-radius: 14px;
        padding: 0.7rem;
    }
    [data-testid="stMetric"] {
        background: white;
        border: 1px solid var(--line);
        padding: 1rem;
        border-radius: 14px;
    }
    div[data-testid="stDataFrame"] {
        border: 1px solid var(--line);
        border-radius: 12px;
        overflow: hidden;
    }
    hr {
        border-color: var(--line);
        margin: 1.5rem 0;
    }
    @media (max-width: 700px) {
        .hero-title { font-size: 2rem; }
        .surface-card { min-height: auto; margin-bottom: 0.7rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar brand
with st.sidebar:
    st.markdown('<div class="brand-mark">🎓</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-brand">AI Student Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-caption">Your academic and career workspace</div>', unsafe_allow_html=True)
    st.divider()
    st.markdown("**WORKSPACE**")

    module = st.radio(
        "Navigate to",
        [
            "🏠 Home",
            "📚 AI Study Planner",
            "📄 AI Resume Analyzer"
        ],
        label_visibility="collapsed",
    )

    st.divider()
    st.caption("Plan your learning. Prepare for your next opportunity.")

# ---------------------------------------------------------
# Home — overview and module selection
# ---------------------------------------------------------
if module == "🏠 Home":
    st.markdown('<div class="eyebrow">STUDENT WORKSPACE</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">Make your next step<br>your best step.</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-copy">A focused workspace to organize your study priorities '
        'and review your career readiness. Choose a tool below to get started.</div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.markdown(
            """
            <div class="surface-card">
                <div class="card-icon icon-blue">📚</div>
                <h3>AI Study Planner</h3>
                <p>Turn subjects, deadlines, difficulty levels and available study time
                into a prioritized study plan.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            """
            <div class="surface-card">
                <div class="card-icon icon-teal">📄</div>
                <h3>AI Resume Analyzer</h3>
                <p>Review detected skills, check skill coverage and inspect extracted
                resume text after uploading a PDF.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-label">A simple workflow</div>', unsafe_allow_html=True)
    step1, step2, step3 = st.columns(3, gap="medium")
    with step1:
        st.markdown(
            '<div class="surface-card"><div class="eyebrow">01 / PLAN</div><h3>Set priorities</h3>'
            '<p>Enter your subjects and deadlines to organize study time.</p></div>',
            unsafe_allow_html=True,
        )
    with step2:
        st.markdown(
            '<div class="surface-card"><div class="eyebrow">02 / REVIEW</div><h3>Check your resume</h3>'
            '<p>Upload a PDF and review the skills recognized by the analyzer.</p></div>',
            unsafe_allow_html=True,
        )
    with step3:
        st.markdown(
            '<div class="surface-card"><div class="eyebrow">03 / IMPROVE</div><h3>Take your next step</h3>'
            '<p>Use the results as a starting point for your academic and career preparation.</p></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.info("Choose **AI Study Planner** or **AI Resume Analyzer** from the left navigation to begin.")

# ---------------------------------------------------------
# Study Planner — clean, form-first academic workspace
# ---------------------------------------------------------
elif module == "📚 AI Study Planner":
    st.markdown('<div class="eyebrow">ACADEMIC PLANNING</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">AI Study Planner</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Build a practical study plan around your time, '
        'subjects and deadlines.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="helper-panel"><strong>How it works:</strong> Add each subject, '
        'choose its deadline and difficulty, then generate your recommended plan.</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-label">Your study capacity</div>', unsafe_allow_html=True)
    daily_hours = st.number_input(
        "Available study hours per day",
        min_value=1.0,
        max_value=24.0,
        value=4.0,
        step=0.5,
        help="Enter the total number of hours you can realistically study each day.",
    )

    st.markdown('<div class="section-label">Subject details</div>', unsafe_allow_html=True)
    number_of_subjects = st.number_input(
        "How many subjects do you want to plan for?",
        min_value=1,
        max_value=10,
        value=3,
        step=1,
    )

    subjects = []
    for i in range(int(number_of_subjects)):
        with st.container(border=True):
            st.markdown(f"**Subject {i + 1}**")
            col1, col2, col3 = st.columns([1.5, 1, 1], gap="medium")
            with col1:
                name = st.text_input("Subject name", key=f"name_{i}", placeholder="e.g. Data Structures")
            with col2:
                deadline = st.date_input(
                    "Deadline", value=date.today(), key=f"deadline_{i}"
                )
            with col3:
                difficulty = st.selectbox(
                    "Difficulty", ["Easy", "Medium", "Hard"], key=f"difficulty_{i}"
                )
            subjects.append({
                "name": name,
                "deadline": deadline,
                "difficulty": difficulty
            })

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Generate study plan  →", type="primary", use_container_width=True):
        valid_subjects = [
            subject for subject in subjects if subject["name"].strip()
        ]
        if not valid_subjects:
            st.warning("Please enter at least one subject.")
        else:
            plan = generate_plan(valid_subjects, daily_hours)
            st.success("Your study plan is ready.")
            st.markdown('<div class="section-label">Recommended study plan</div>', unsafe_allow_html=True)
            st.dataframe(plan, use_container_width=True)

# ---------------------------------------------------------
# Resume Analyzer — upload and results-focused career workspace
# ---------------------------------------------------------
elif module == "📄 AI Resume Analyzer":
    st.markdown('<div class="eyebrow">CAREER READINESS</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">AI Resume Analyzer</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Review the skills detected in your resume and '
        'get a quick view of your current skill coverage.</div>',
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.25, 0.75], gap="large")
    with left:
        st.markdown('<div class="section-label">Upload your resume</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="helper-panel"><strong>Before you begin:</strong> Upload a PDF resume. '
            'The analyzer will extract its text and check for skills supported by the current analyzer.</div>',
            unsafe_allow_html=True,
        )
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=["pdf"],
            help="PDF format only.",
        )
        if uploaded_file is not None:
            st.success(f"Ready to analyze: {uploaded_file.name}")
            if st.button("Analyze resume  →", type="primary", use_container_width=True):
                with st.spinner("Analyzing resume..."):
                    text = extract_text_from_pdf(uploaded_file)
                    result = analyze_resume(text)

                st.success("Resume analysis completed!")
                st.markdown('<div class="section-label">Analysis results</div>', unsafe_allow_html=True)
                st.metric("Skill Coverage", f"{result['score']}%")

                result_col1, result_col2 = st.columns(2, gap="medium")
                with result_col1:
                    st.markdown("**✅ Detected skills**")
                    if result["skills"]:
                        st.write(", ".join(result["skills"]))
                    else:
                        st.write("No predefined skills detected.")
                with result_col2:
                    st.markdown("**⚠️ Skills not detected**")
                    if result["missing_skills"]:
                        st.write(", ".join(result["missing_skills"]))
                    else:
                        st.write("All listed skills were detected.")

                with st.expander("View extracted resume text"):
                    st.text(text)

    with right:
        st.markdown('<div class="section-label">What you will see</div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="surface-card">
                <div class="card-icon icon-blue">🎯</div>
                <h3>Skill coverage</h3>
                <p>A percentage based on the existing analyzer's scoring logic.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            """
            <div class="surface-card">
                <div class="card-icon icon-teal">🧩</div>
                <h3>Skill review</h3>
                <p>A list of skills detected and skills not detected by the current analyzer.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption("This is a basic skills check, not a guarantee of ATS compatibility or hiring outcomes.")
