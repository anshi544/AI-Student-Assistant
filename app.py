import streamlit as st
from datetime import date
from planner import generate_plan
from resume_analyzer import extract_text_from_pdf, analyze_resume

st.set_page_config(page_title="AI Student Assistant", page_icon="🎓", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
:root{--ink:#172338;--muted:#69778b;--line:#e7ebf2;--canvas:#f7f8fb;--blue:#315fce;--blue-soft:#edf2ff;--green-soft:#eaf6f2;--purple-soft:#f1edff}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif}
.stApp{background:var(--canvas);color:var(--ink)}
[data-testid="stHeader"]{background:rgba(247,248,251,.96)}
.block-container{max-width:1380px;padding-top:1.7rem;padding-bottom:3rem}
[data-testid="stSidebar"]{background:#fff;border-right:1px solid var(--line)}
[data-testid="stSidebar"] *{color:var(--ink)}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p{color:var(--muted)}
[data-testid="stSidebar"] hr{border-color:var(--line)}
[data-testid="stSidebar"] [role="radiogroup"]{gap:.35rem}
[data-testid="stSidebar"] [role="radiogroup"] label{border-radius:10px;padding:.55rem .65rem;border:1px solid transparent}
[data-testid="stSidebar"] [role="radiogroup"] label:hover{background:#f5f7fb;border-color:#e9edf5}
.brand{display:flex;align-items:center;gap:.7rem;margin-bottom:.45rem}
.brand-icon{display:flex;align-items:center;justify-content:center;width:42px;height:42px;border-radius:12px;background:var(--blue-soft);color:var(--blue);font-size:21px}
.brand-name{font-family:'Manrope',sans-serif;font-weight:800;font-size:1rem;letter-spacing:-.025em}
.brand-sub{color:var(--muted);font-size:.79rem;line-height:1.5;margin-bottom:1.1rem}
.side-label{color:#8a95a6;font-size:.68rem;font-weight:800;letter-spacing:.13em;margin:1rem 0 .55rem}
.eyebrow{color:var(--blue);font-size:.71rem;font-weight:800;letter-spacing:.13em;text-transform:uppercase;margin-bottom:.55rem}
.hero-title{font-family:'Manrope',sans-serif;font-weight:800;letter-spacing:-.055em;color:var(--ink);font-size:clamp(2.1rem,4vw,3.35rem);line-height:1.1;margin:0 0 .8rem}
.hero-title span{color:var(--blue)}
.hero-copy{color:var(--muted);font-size:1rem;line-height:1.75;max-width:680px;margin:0}
.page-title{font-family:'Manrope',sans-serif;color:var(--ink);font-size:clamp(1.8rem,3vw,2.45rem);font-weight:800;letter-spacing:-.045em;margin:0 0 .35rem}
.page-subtitle{color:var(--muted);line-height:1.7;margin:0 0 1.3rem}
.section-heading{font-family:'Manrope',sans-serif;color:var(--ink);font-size:1.1rem;font-weight:800;margin:1.35rem 0 .75rem}
.hero{background:#fff;border:1px solid var(--line);border-radius:22px;padding:2rem 2.1rem;box-shadow:0 8px 28px rgba(25,42,75,.035);position:relative;overflow:hidden}
.hero:after{content:"";position:absolute;right:-52px;top:-80px;width:220px;height:220px;border:35px solid #f0f4ff;border-radius:50%;pointer-events:none}
.hero-badge{display:inline-block;padding:.35rem .65rem;border:1px solid #dfe7fb;border-radius:999px;background:#f8faff;color:#3b5eb4;font-size:.75rem;font-weight:700;margin-bottom:1.05rem}
.feature-card{background:#fff;border:1px solid var(--line);border-radius:17px;padding:1.25rem;min-height:195px;box-shadow:0 5px 20px rgba(25,42,75,.025)}
.feature-top{display:flex;align-items:center;justify-content:space-between;margin-bottom:1rem}
.feature-icon{display:flex;align-items:center;justify-content:center;width:46px;height:46px;border-radius:13px;font-size:1.35rem}
.blue-bg{background:var(--blue-soft)}.green-bg{background:var(--green-soft)}.purple-bg{background:var(--purple-soft)}
.feature-tag{color:#7a879a;font-size:.68rem;font-weight:800;letter-spacing:.1em}
.feature-card h3,.result-card h3{font-family:'Manrope',sans-serif;font-size:1.08rem;font-weight:800;color:var(--ink);margin:0 0 .45rem}
.feature-card p,.result-card p{color:var(--muted);font-size:.9rem;line-height:1.65;margin:0}
.workflow-card{background:#fff;border:1px solid var(--line);border-radius:14px;padding:1rem 1.05rem;min-height:112px}
.workflow-num{color:var(--blue);font-size:.7rem;letter-spacing:.1em;font-weight:800;margin-bottom:.4rem}
.workflow-title{color:var(--ink);font-family:'Manrope',sans-serif;font-weight:800;font-size:.94rem;margin-bottom:.3rem}
.workflow-copy{color:var(--muted);font-size:.83rem;line-height:1.5}
.info-box{background:#f0f4ff;border:1px solid #e0e8ff;border-radius:12px;padding:.95rem 1.05rem;color:#3e547c;line-height:1.6}
.info-box strong{color:#23468f}
.result-card{background:#fff;border:1px solid var(--line);border-radius:15px;padding:1rem 1.1rem}
.stButton>button{background:var(--blue);color:#fff;border:1px solid var(--blue);border-radius:10px;font-weight:700;min-height:2.7rem;padding:.55rem 1rem}
.stButton>button:hover{background:#244ba9;color:#fff;border-color:#244ba9;box-shadow:0 5px 12px rgba(49,95,206,.16)}
.stTextInput input,.stNumberInput input,.stDateInput input,.stSelectbox [data-baseweb="select"]>div{border-radius:9px}
[data-testid="stFileUploader"]{background:#fff;border:1px dashed #cbd5e4;border-radius:13px;padding:.7rem}
[data-testid="stMetric"]{background:#fff;border:1px solid var(--line);padding:1rem;border-radius:14px}
div[data-testid="stDataFrame"]{border:1px solid var(--line);border-radius:12px;overflow:hidden}
[data-testid="stExpander"]{background:#fff;border:1px solid var(--line);border-radius:11px}
hr{border-color:var(--line);margin:1.4rem 0}
@media(max-width:700px){.block-container{padding-top:1rem}.hero{padding:1.3rem}.hero-title{font-size:2.1rem}.feature-card{min-height:0}}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div class="brand"><div class="brand-icon">🎓</div><div class="brand-name">AI Student Assistant</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Academic planning & career readiness</div>', unsafe_allow_html=True)
    st.divider()
    st.markdown('<div class="side-label">WORKSPACE</div>', unsafe_allow_html=True)
    module = st.radio("Navigate", ["🏠 Home", "📚 AI Study Planner", "📄 AI Resume Analyzer"], label_visibility="collapsed")
    st.divider()
    st.markdown('<div class="side-label">YOUR GOALS</div>', unsafe_allow_html=True)
    st.caption("Organize your learning. Make your next step count.")

if module == "🏠 Home":
    st.markdown('<div class="eyebrow">STUDENT WORKSPACE</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero"><div class="hero-badge">✦ One workspace, two useful tools</div><div class="hero-title">Learn with a plan.<br><span>Move forward with confidence.</span></div><p class="hero-copy">A simple space to structure your study time and review the skills in your resume. Choose a tool to get started and keep your next steps clear.</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Explore your tools</div>', unsafe_allow_html=True)
    c1,c2=st.columns(2,gap="large")
    with c1:
        st.markdown('<div class="feature-card"><div class="feature-top"><div class="feature-icon blue-bg">📚</div><div class="feature-tag">PLAN & ORGANIZE</div></div><h3>AI Study Planner</h3><p>Enter subjects, deadlines, and difficulty levels to generate a recommended study plan based on your available time.</p></div>',unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="feature-card"><div class="feature-top"><div class="feature-icon purple-bg">📄</div><div class="feature-tag">REVIEW & PREPARE</div></div><h3>AI Resume Analyzer</h3><p>Upload your resume as a PDF to inspect detected skills, skills not detected, and extracted text.</p></div>',unsafe_allow_html=True)
    st.markdown('<div class="section-heading">How to use the assistant</div>',unsafe_allow_html=True)
    w1,w2,w3=st.columns(3,gap="medium")
    with w1: st.markdown('<div class="workflow-card"><div class="workflow-num">01 / PLAN</div><div class="workflow-title">Set your priorities</div><div class="workflow-copy">Add subjects and their deadlines.</div></div>',unsafe_allow_html=True)
    with w2: st.markdown('<div class="workflow-card"><div class="workflow-num">02 / ANALYZE</div><div class="workflow-title">Review your resume</div><div class="workflow-copy">Check which predefined skills are detected.</div></div>',unsafe_allow_html=True)
    with w3: st.markdown('<div class="workflow-card"><div class="workflow-num">03 / ACT</div><div class="workflow-title">Choose your next step</div><div class="workflow-copy">Use the results to guide your preparation.</div></div>',unsafe_allow_html=True)
    st.markdown("<br>",unsafe_allow_html=True)
    st.caption("The resume analyzer performs basic skill detection. Review its output before making career decisions.")

elif module == "📚 AI Study Planner":
    st.markdown('<div class="eyebrow">ACADEMIC PLANNING</div>',unsafe_allow_html=True)
    st.markdown('<div class="page-title">AI Study Planner</div>',unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Turn your subjects and deadlines into a structured study plan.</div>',unsafe_allow_html=True)
    st.markdown('<div class="info-box"><strong>Before you start:</strong> Set a realistic daily study limit, then add each subject with its deadline and difficulty.</div>',unsafe_allow_html=True)
    st.markdown('<div class="section-heading">01 &nbsp; Study capacity</div>',unsafe_allow_html=True)
    daily_hours=st.number_input("Available study hours per day",min_value=1.0,max_value=24.0,value=4.0,step=0.5,help="Choose the number of hours you can consistently dedicate to studying each day.")
    st.markdown('<div class="section-heading">02 &nbsp; Subject details</div>',unsafe_allow_html=True)
    number_of_subjects=st.number_input("Number of subjects",min_value=1,max_value=10,value=3,step=1)
    subjects=[]
    for i in range(int(number_of_subjects)):
        with st.container(border=True):
            st.markdown(f"**Subject {i+1}**")
            col1,col2,col3=st.columns([1.5,1,1],gap="medium")
            with col1: name=st.text_input("Subject name",key=f"name_{i}",placeholder="e.g. Data Structures")
            with col2: deadline=st.date_input("Deadline",value=date.today(),key=f"deadline_{i}")
            with col3: difficulty=st.selectbox("Difficulty",["Easy","Medium","Hard"],key=f"difficulty_{i}")
            subjects.append({"name":name,"deadline":deadline,"difficulty":difficulty})
    st.markdown("<br>",unsafe_allow_html=True)
    if st.button("Generate study plan",type="primary",use_container_width=True):
        valid_subjects=[subject for subject in subjects if subject["name"].strip()]
        if not valid_subjects: st.warning("Please enter at least one subject.")
        else:
            plan=generate_plan(valid_subjects,daily_hours)
            st.success("Your study plan is ready.")
            st.markdown('<div class="section-heading">Your recommended plan</div>',unsafe_allow_html=True)
            st.dataframe(plan,use_container_width=True)

elif module == "📄 AI Resume Analyzer":
    st.markdown('<div class="eyebrow">CAREER READINESS</div>',unsafe_allow_html=True)
    st.markdown('<div class="page-title">AI Resume Analyzer</div>',unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">See which skills the current analyzer recognizes in your resume.</div>',unsafe_allow_html=True)
    upload_col,guide_col=st.columns([1.15,.85],gap="large")
    with upload_col:
        st.markdown('<div class="section-heading">01 &nbsp; Upload resume</div>',unsafe_allow_html=True)
        st.markdown('<div class="info-box"><strong>PDF format only.</strong> For best results, upload a readable PDF with selectable text.</div>',unsafe_allow_html=True)
        uploaded_file=st.file_uploader("Choose your resume",type=["pdf"])
        if uploaded_file is not None:
            st.success(f"File ready: {uploaded_file.name}")
            if st.button("Analyze resume",type="primary",use_container_width=True):
                with st.spinner("Analyzing your resume..."):
                    text=extract_text_from_pdf(uploaded_file)
                    result=analyze_resume(text)
                st.markdown('<div class="section-heading">02 &nbsp; Analysis results</div>',unsafe_allow_html=True)
                st.metric("Skill Coverage",f"{result['score']}%")
                st.progress(max(0,min(100,int(result["score"])))/100)
                detected_col,missing_col=st.columns(2,gap="medium")
                with detected_col:
                    st.markdown("**✓ Detected skills**")
                    st.write(", ".join(result["skills"]) if result["skills"] else "No predefined skills detected.")
                with missing_col:
                    st.markdown("**Skills not detected**")
                    st.write(", ".join(result["missing_skills"]) if result["missing_skills"] else "All listed skills were detected.")
                with st.expander("View extracted resume text"):
                    st.text(text)
    with guide_col:
        st.markdown('<div class="section-heading">What you will get</div>',unsafe_allow_html=True)
        st.markdown('<div class="result-card"><div class="feature-icon blue-bg">◉</div><h3>Skill coverage</h3><p>A percentage based on the existing analyzer scoring logic. It is not an overall resume quality score.</p></div>',unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        st.markdown('<div class="result-card"><div class="feature-icon green-bg">⌕</div><h3>Skill recognition</h3><p>Compare detected skills with skills not detected by the current analyzer.</p></div>',unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        st.caption("A skill may not be detected because of wording differences. Review results manually; they do not guarantee ATS compatibility or hiring outcomes.")
