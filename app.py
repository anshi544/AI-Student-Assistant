import streamlit as st
from datetime import date, timedelta
from planner import generate_plan
from resume_analyzer import extract_text_from_pdf, analyze_resume, get_skill_recommendations
from auth import render_auth_gate
from chatbot import get_bot_reply

st.set_page_config(page_title="AI Student Assistant", page_icon="🎓", layout="wide")

if not render_auth_gate():
    st.stop()

st.title("🎓 AI Student Career & Academic Assistant")
st.caption("Plan your study time, improve your resume, and get student-focused guidance.")
st.divider()

PAGES = ["🏠 Home", "📚 AI Study Planner", "📄 AI Resume Analyzer", "🤖 Student Chatbot"]
module = st.sidebar.radio("Navigate", PAGES)

if module == "🏠 Home":
    st.header("Welcome to your student workspace")
    st.write("Choose a tool to get started.")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.subheader("📚 Study Planner")
        st.write("Prioritize subjects by deadline, difficulty, confidence, and workload. Get a day-by-day schedule with revision and breaks.")
    with c2:
        st.subheader("📄 Resume Analyzer")
        st.write("Find skills already visible in your resume and get role-oriented suggestions for skills to learn or demonstrate.")
    with c3:
        st.subheader("🤖 Student Chatbot")
        st.write("Ask about study strategies, resume improvement, interview preparation, programming, and using this application.")
    st.info("Your plan and recommendations are guidance. Adjust them to your actual syllabus, available time, and career goals.")

elif module == "📚 AI Study Planner":
    st.header("📚 Smart Study Planner")
    st.write("The plan considers deadlines, difficulty, confidence, estimated workload, and available daily time.")
    with st.form("planner_form"):
        c1, c2 = st.columns(2)
        with c1:
            daily_hours = st.number_input("Available focused study hours per day", min_value=1.0, max_value=16.0, value=4.0, step=0.5)
            plan_days = st.slider("Plan length (days)", 3, 30, 7)
        with c2:
            start_date = st.date_input("Start date", value=date.today())
            include_revision = st.checkbox("Reserve time for revision and practice", value=True)
        st.subheader("Subject details")
        number_of_subjects = st.number_input("Number of subjects", min_value=1, max_value=10, value=3, step=1)
        subjects = []
        for i in range(int(number_of_subjects)):
            st.markdown(f"**Subject {i + 1}**")
            a, b, c, d = st.columns(4)
            with a:
                name = st.text_input("Subject name", key=f"subject_name_{i}")
            with b:
                deadline = st.date_input("Deadline", value=start_date + timedelta(days=plan_days-1), key=f"subject_deadline_{i}")
            with c:
                difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], index=1, key=f"subject_diff_{i}")
            with d:
                confidence = st.select_slider("Confidence", options=["Low", "Medium", "High"], value="Medium", key=f"subject_conf_{i}")
            workload = st.select_slider("Estimated workload", options=["Small", "Moderate", "Large"], value="Moderate", key=f"subject_load_{i}")
            subjects.append({"name": name.strip(), "deadline": deadline, "difficulty": difficulty,
                             "confidence": confidence, "workload": workload})
        submitted = st.form_submit_button("Generate improved study plan", type="primary")

    if submitted:
        valid_subjects = [s for s in subjects if s["name"]]
        if not valid_subjects:
            st.warning("Enter at least one subject name.")
        elif any(s["deadline"] < start_date for s in valid_subjects):
            st.warning("A deadline cannot be earlier than the selected start date.")
        else:
            result = generate_plan(valid_subjects, daily_hours, start_date=start_date,
                                   plan_days=plan_days, include_revision=include_revision)
            st.success("Your personalized plan is ready.")
            m1, m2, m3 = st.columns(3)
            m1.metric("Subjects", len(valid_subjects))
            m2.metric("Daily focused time", f"{daily_hours:g} hrs")
            m3.metric("Schedule length", f"{plan_days} days")
            st.subheader("Subject priority overview")
            st.dataframe(result["overview"], use_container_width=True, hide_index=True)
            st.subheader("Day-by-day schedule")
            st.dataframe(result["schedule"], use_container_width=True, hide_index=True)
            st.subheader("How to use this plan")
            for tip in result["tips"]:
                st.write(f"• {tip}")
            csv = result["schedule"].to_csv(index=False).encode("utf-8")
            st.download_button("Download schedule as CSV", csv, "study_plan.csv", "text/csv")

elif module == "📄 AI Resume Analyzer":
    st.header("📄 Resume Analyzer + Skill Suggestions")
    st.write("Upload a text-based PDF resume. Suggestions are role-oriented learning ideas—not a claim that every listed skill is required.")
    role = st.selectbox("Target role", [
        "General Software Developer", "Python Developer", "AI / Machine Learning Intern",
        "Data Analyst", "Web Developer", "Software Engineer Intern"
    ])
    uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
    if uploaded_file is not None and st.button("Analyze resume", type="primary"):
        with st.spinner("Reading and analyzing your resume..."):
            text = extract_text_from_pdf(uploaded_file)
            if not text.strip():
                st.error("No selectable text was found. If your PDF is scanned, run OCR on it and upload a text-based PDF.")
                st.stop()
            result = analyze_resume(text)
            suggestions = get_skill_recommendations(result["skills"], role)
        st.success("Resume analysis completed.")
        a, b = st.columns(2)
        with a:
            st.metric("Detected listed skills", len(result["skills"]))
            st.progress(min(result["score"] / 100, 1.0), text=f"Prototype skill-list coverage: {result['score']}%")
        with b:
            st.metric("Suggested skills to explore", len(suggestions))
            st.caption("Coverage is based on the project's predefined skill list; it is not an ATS score.")
        st.subheader("✅ Skills detected")
        st.write(", ".join(result["skills"]) if result["skills"] else "No predefined skills were detected.")
        st.subheader(f"🎯 Skills to consider for {role}")
        if suggestions:
            for item in suggestions:
                with st.container(border=True):
                    st.markdown(f"**{item['skill']}** · {item['priority']} priority")
                    st.write(item["why"])
                    st.caption(f"Suggested evidence: {item['evidence']}")
        else:
            st.success("The analyzer did not identify additional suggestions from its role checklist. Review the role requirements of the jobs you plan to apply for.")
        if result["missing_skills"]:
            with st.expander("Other skills in the analyzer checklist not detected"):
                st.write(", ".join(result["missing_skills"]))
        with st.expander("View extracted resume text"):
            st.text(text)
        st.info("Only add a skill to your resume when you can explain it and demonstrate it honestly. Build a small project or complete practice tasks first.")

elif module == "🤖 Student Chatbot":
    st.header("🤖 Student Assistant Chatbot")
    st.caption("Built-in student-help assistant. It works without an external AI API key.")
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "Hi! Ask me about study planning, revision, resume skills, projects, Python, DSA, or interview preparation."}
        ]
    left, right = st.columns([5, 1])
    with right:
        if st.button("Clear chat"):
            st.session_state.chat_messages = []
            st.rerun()
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    prompt = st.chat_input("Ask your student assistant...")
    if prompt:
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        reply = get_bot_reply(prompt)
        st.session_state.chat_messages.append({"role": "assistant", "content": reply})
        st.rerun()
