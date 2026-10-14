import streamlit as st
from datetime import date

from planner import generate_plan
from resume_analyzer import (
    extract_text_from_pdf,
    analyze_resume
)

st.set_page_config(
    page_title="AI Student Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Modern AI-product styling. UI only: business logic and imported functions
# are intentionally left unchanged.
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

    :root {
        --ink: #17243a;
        --muted: #65758b;
        --line: #e3eaf4;
        --canvas: #f5f7fc;
        --paper: #ffffff;
        --blue: #4169e1;
        --blue-deep: #294fc0;
        --blue-pale: #edf2ff;
        --violet: #7562d8;
        --teal: #168579;
        --teal-pale: #e8f7f4;
        --amber-pale: #fff5e5;
    }

    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    .stApp { background: var(--canvas); color: var(--ink); }
    [data-testid="stHeader"] { background: rgba(245,247,252,.92); }
    .block-container { padding-top: 2.1rem; padding-bottom: 3rem; max-width: 1440px; }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #17243a 0%, #202d49 100%);
        border-right: 1px solid #2b3a58;
    }
    [data-testid="stSidebar"] * { color: #eef3ff; }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: #b9c7de; }
    [data-testid="stSidebar"] hr { border-color: #34425e; }
    [data-testid="stSidebar"] label { color: #eef3ff !important; }
    [data-testid="stSidebar"] [role="radiogroup"] { gap: .42rem; }
    [data-testid="stSidebar"] [role="radiogroup"] label {
        padding: .58rem .7rem; border-radius: 11px; transition: background .15s ease;
    }
    [data-testid="stSidebar"] [role="radiogroup"] label:hover { background: #2a3a5a; }

    .brand-row { display:flex; align-items:center; gap: .72rem; margin-bottom: .6rem; }
    .brand-mark {
        display:inline-flex; align-items:center; justify-content:center;
        width:45px; height:45px; border-radius:15px;
        background: linear-gradient(135deg, #5d82ff, #7665df);
        color:white; font-size:22px; box-shadow:0 8px 20px rgba(65,105,225,.28);
    }
    .sidebar-brand { font-family:'Manrope',sans-serif; font-size:1.04rem; font-weight:800; color:white; }
    .sidebar-caption { color:#aebdd4 !important; font-size:.8rem; line-height:1.5; margin:0 0 1.25rem 0; }

    .eyebrow { color:var(--blue); text-transform:uppercase; letter-spacing:.14em; font-size:.72rem; font-weight:800; margin-bottom:.55rem; }
    .hero-title {
        font-family:'Manrope',sans-serif; font-size:clamp(2.2rem,4.5vw,3.5rem);
        line-height:1.08; font-weight:800; letter-spacing:-.055em; color:var(--ink);
        margin:0 0 .9rem 0;
    }
    .hero-title .accent { color:var(--blue); }
    .hero-copy { max-width:730px; color:var(--muted); font-size:1.04rem; line-height:1.75; margin-bottom:1.35rem; }
    .page-title { font-family:'Manrope',sans-serif; font-size:clamp(1.8rem,3vw,2.45rem); font-weight:800; letter-spacing:-.04em; color:var(--ink); margin-bottom:.2rem; }
    .page-subtitle { color:var(--muted); line-height:1.7; margin-bottom:1.25rem; }
    .section-label { font-family:'Manrope',sans-serif; font-size:1.12rem; font-weight:800; color:var(--ink); margin:1.2rem 0 .75rem; }

    .hero-panel {
        position:relative; overflow:hidden; padding:1.6rem 1.65rem;
        border:1px solid #dce5ff; border-radius:23px;
        background:linear-gradient(115deg,#ffffff 0%,#f2f5ff 66%,#efedff 100%);
        box-shadow:0 10px 35px rgba(39,63,120,.055);
    }
    .hero-panel:after {
        content:""; position:absolute; width:210px; height:210px; border-radius:50%;
        right:-65px; top:-95px; background:rgba(112,130,238,.10);
    }
    .hero-pill {
        display:inline-block; border:1px solid #d7e1ff; background:#fff; color:#3657b4;
        padding:.35rem .7rem; border-radius:999px; font-size:.76rem; font-weight:700; margin-bottom:1rem;
    }
    .surface-card {
        background:var(--paper); border:1px solid var(--line); border-radius:18px;
        padding:1.25rem 1.3rem; box-shadow:0 5px 20px rgba(28,45,75,.035); height:100%;
    }
    .surface-card:hover { border-color:#cbd8fa; box-shadow:0 10px 28px rgba(35,60,115,.07); }
    .card-icon {
        display:inline-flex; align-items:center; justify-content:center; width:45px; height:45px;
        border-radius:14px; font-size:1.35rem; margin-bottom:.85rem;
    }
    .icon-blue { background:var(--blue-pale); }
    .icon-violet { background:#f0edff; }
    .icon-teal { background:var(--teal-pale); }
    .surface-card h3 { font-family:'Manrope',sans-serif; font-size:1.06rem; font-weight:800; margin:0 0 .45rem; color:var(--ink); }
    .surface-card p { color:var(--muted); font-size:.92rem; line-height:1.65; margin:0; }
    .card-kicker { color:var(--blue); text-transform:uppercase; letter-spacing:.1em; font-size:.68rem; font-weight:800; margin-bottom:.45rem; }
    .step-card { background:#fff; border:1px solid var(--line); border-radius:15px; padding:1rem; height:100%; }
    .step-number { color:var(--blue); font-family:'Manrope',sans-serif; font-weight:800; font-size:.8rem; margin-bottom:.5rem; }
    .step-card h4 { font-family:'Manrope',sans-serif; color:var(--ink); font-size:.96rem; font-weight:800; margin:0 0 .35rem; }
    .step-card p { color:var(--muted); font-size:.86rem; line-height:1.55; margin:0; }

    .helper-panel {
        background:#edf3ff; border:1px solid #dbe5ff; border-radius:14px;
        padding:1rem 1.1rem; color:#34517e; line-height:1.65;
    }
    .helper-panel strong { color:#233f80; }
    .stButton > button {
        border-radius:11px; border:1px solid var(--blue); background:var(--blue); color:white;
        font-weight:700; min-height:2.7rem; padding:.6rem 1rem; transition:all .16s ease;
    }
    .stButton > button:hover { background:var(--blue-deep); border-color:var(--blue-deep); color:white; box-shadow:0 5px 14px rgba(65,105,225,.18); }
    .stTextInput input, .stNumberInput input, .stDateInput input,
    .stSelectbox [data-baseweb="select"] > div { border-radius:10px; }
    [data-testid="stFileUploader"] { background:#fff; border:1px dashed #bdcbe0; border-radius:15px; padding:.7rem; }
    [data-testid="stMetric"] { background:#fff; border:1px solid var(--line); padding:1rem; border-radius:15px; }
    [data-testid="stMetricLabel"] { color:var(--muted); }
    div[data-testid="stDataFrame"] { border:1px solid var(--line); border-radius:13px; overflow:hidden; }
    [data-testid="stExpander"] { background:#fff; border:1px solid var(--line); border-radius:12px; }
    hr { border-color:var(--line); margin:1.45rem 0; }
    @media (max-width:700px) {
        .block-container { padding-top:1.25rem; }
        .hero-title { font-size:2.15rem; }
        .hero-panel { padding:1.2rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown(
        '<div class="brand-row"><div class="brand-mark">✦</div>'
        '<div class="sidebar-brand">AI Student Assistant</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sidebar-caption">Your personal space for academic planning and career readiness.</div>',
        unsafe_allow_html=True,
    )
    st.divider()
    st.markdown("**YOUR WORKSPACE**")
    module = st.radio(
        "Navigate to",
        ["🏠 Home", "📚 AI Study Planner", "📄 AI Resume Analyzer"],
        label_visibility="collapsed",
    )
    st.divider()
    st.markdown("**MADE FOR STUDENTS**")
    st.caption("Plan with purpose. Prepare with confidence.")

# HOME
if module == "🏠 Home":
    st.markdown('<div class="eyebrow">YOUR STUDENT WORKSPACE</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-panel">'
        '<div class="hero-pill">✦ Study smarter · Prepare better</div>'
        '<div class="hero-title">Small steps today.<br><span class="accent">Stronger outcomes tomorrow.</span></div>'
        '<div class="hero-copy">Bring your academic planning and career preparation together in one focused workspace. '
        'Create a study plan, review your resume skills, and decide what to work on next.</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-label">Choose your workspace</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown(
            '<div class="surface-card"><div class="card-icon icon-blue">📚</div>'
            '<div class="card-kicker">LEARN & ORGANIZE</div><h3>AI Study Planner</h3>'
            '<p>Organize subjects by deadlines and difficulty, then generate a recommended study plan around your available time.</p></div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            '<div class="surface-card"><div class="card-icon icon-violet">✧</div>'
            '<div class="card-kicker">CAREER & GROWTH</div><h3>AI Resume Analyzer</h3>'
            '<p>Upload a PDF resume to review detected skills, skill coverage, and the text extracted by the analyzer.</p></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-label">A simple way to get started</div>', unsafe_allow_html=True)
    s1, s2, s3 = st.columns(3, gap="medium")
    with s1:
        st.markdown('<div class="step-card"><div class="step-number">STEP 01</div><h4>Set your priorities</h4><p>Add your subjects, deadlines, and difficulty levels.</p></div>', unsafe_allow_html=True)
    with s2:
        st.markdown('<div class="step-card"><div class="step-number">STEP 02</div><h4>Review your skills</h4><p>Check which predefined skills your resume currently shows.</p></div>', unsafe_allow_html=True)
    with s3:
        st.markdown('<div class="step-card"><div class="step-number">STEP 03</div><h4>Choose your next action</h4><p>Use the results to guide your next study or resume update.</p></div>', unsafe_allow_html=True)
    st.caption("Note: This application provides planning support and basic resume skill detection; results should be reviewed by the user.")

# STUDY PLANNER
elif module == "📚 AI Study Planner":
    st.markdown('<div class="eyebrow">ACADEMIC PLANNING</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">AI Study Planner</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Build a realistic study plan around your subjects, deadlines, difficulty levels, and available time.</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="helper-panel"><strong>Quick tip:</strong> Use real deadlines and choose the difficulty honestly. '
        'Your inputs help the existing planner organize a more useful recommendation.</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-label">01 · Your daily study capacity</div>', unsafe_allow_html=True)
    daily_hours = st.number_input(
        "Available study hours per day",
        min_value=1.0, max_value=24.0, value=4.0, step=0.5,
        help="Enter the number of hours you can realistically study each day.",
    )

    st.markdown('<div class="section-label">02 · Add your subjects</div>', unsafe_allow_html=True)
    number_of_subjects = st.number_input(
        "Number of subjects", min_value=1, max_value=10, value=3, step=1,
    )
    subjects = []
    for i in range(int(number_of_subjects)):
        with st.container(border=True):
            st.markdown(f"**Subject {i + 1}**")
            col1, col2, col3 = st.columns([1.5, 1, 1], gap="medium")
            with col1:
                name = st.text_input("Subject name", key=f"name_{i}", placeholder="e.g. Data Structures")
            with col2:
                deadline = st.date_input("Deadline", value=date.today(), key=f"deadline_{i}")
            with col3:
                difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], key=f"difficulty_{i}")
            subjects.append({"name": name, "deadline": deadline, "difficulty": difficulty})

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Generate study plan  →", type="primary", use_container_width=True):
        valid_subjects = [subject for subject in subjects if subject["name"].strip()]
        if not valid_subjects:
            st.warning("Please enter at least one subject.")
        else:
            plan = generate_plan(valid_subjects, daily_hours)
            st.success("Your study plan is ready.")
            st.markdown('<div class="section-label">Your recommended plan</div>', unsafe_allow_html=True)
            st.dataframe(plan, use_container_width=True)

# RESUME ANALYZER
elif module == "📄 AI Resume Analyzer":
    st.markdown('<div class="eyebrow">CAREER READINESS</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">AI Resume Analyzer</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Get a quick overview of the skills your resume communicates to the current analyzer.</div>', unsafe_allow_html=True)

    left, right = st.columns([1.2, 0.8], gap="large")
    with left:
        st.markdown('<div class="section-label">01 · Upload your resume</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="helper-panel"><strong>PDF only.</strong> Upload a readable resume PDF. '
            'The app extracts the text and checks it against the skills supported by the existing analyzer.</div>',
            unsafe_allow_html=True,
        )
        uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"], help="PDF format only.")
        if uploaded_file is not None:
            st.success(f"Ready to analyze: {uploaded_file.name}")
            if st.button("Analyze resume  →", type="primary", use_container_width=True):
                with st.spinner("Analyzing resume..."):
                    text = extract_text_from_pdf(uploaded_file)
                    result = analyze_resume(text)

                st.success("Resume analysis completed.")
                st.markdown('<div class="section-label">02 · Your results</div>', unsafe_allow_html=True)
                st.metric("Skill Coverage", f"{result['score']}%")
                st.progress(max(0, min(100, int(result["score"]))) / 100)

                detected_col, missing_col = st.columns(2, gap="medium")
                with detected_col:
                    st.markdown("**✅ Detected skills**")
                    if result["skills"]:
                        for skill in result["skills"]:
                            st.markdown(f"- {skill}")
                    else:
                        st.write("No predefined skills detected.")
                with missing_col:
                    st.markdown("**🔎 Skills not detected**")
                    if result["missing_skills"]:
                        for skill in result["missing_skills"]:
                            st.markdown(f"- {skill}")
                    else:
                        st.write("All listed skills were detected.")

                with st.expander("View extracted resume text"):
                    st.text(text)

    with right:
        st.markdown('<div class="section-label">What this analysis includes</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="surface-card"><div class="card-icon icon-blue">◉</div>'
            '<h3>Skill coverage</h3><p>A percentage calculated using the current analyzer logic. It is a basic indicator, not an overall resume quality score.</p></div>',
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            '<div class="surface-card"><div class="card-icon icon-teal">⌕</div>'
            '<h3>Skill recognition</h3><p>Review skills found in the extracted text and skills that were not detected. A missing skill may simply be phrased differently.</p></div>',
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)
        st.caption("Review all results yourself. The analyzer does not guarantee ATS compatibility or hiring outcomes.")
