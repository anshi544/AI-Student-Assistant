# AI-Student-Assistant
AI-based academic planning and resume analysis platform for students



🎓 AI Student Career & Academic Assistant

An integrated student-support platform that combines academic planning and career readiness analysis into a single Streamlit-based application.

The project integrates two student-focused modules:

- 📚 AI Study Planner — helps students prioritize subjects and allocate available study time based on deadlines and difficulty.
- 📄 AI Resume Analyzer — analyzes a PDF resume, identifies predefined skills, calculates a skill-coverage score, and highlights skills that are not detected.

The goal of the project is to provide students with a single platform for managing both academic preparation and career preparation.

---

📌 Project Overview

Students often manage academic preparation and career preparation separately. Academic work involves multiple subjects, deadlines, and different levels of difficulty, while career preparation requires students to understand their skills and improve their resumes.

The AI Student Career & Academic Assistant brings these two areas together in one application.

Academic Side

The Study Planner helps a student answer:

«“What should I study first and how should I distribute my available study time?”»

It considers:

- Subject name
- Deadline
- Difficulty level
- Available study hours per day

The system calculates a priority score and generates a prioritized study plan.

Career Side

The Resume Analyzer helps a student answer:

«“What skills are currently visible in my resume and what areas can I improve?”»

It:

- Accepts a PDF resume
- Extracts text from the document
- Searches for predefined skills
- Calculates a basic skill-coverage score
- Displays detected skills
- Displays skills that were not detected

---

🎯 Objectives

The major objectives of this project are:

1. To develop a unified platform for academic and career assistance.
2. To help students organize their study schedules efficiently.
3. To prioritize subjects using deadline and difficulty information.
4. To analyze resumes using automated text processing.
5. To identify skills present in a student's resume.
6. To highlight skills that are not detected.
7. To provide an easy-to-use web interface using Streamlit.
8. To deploy the application through Streamlit Community Cloud.
9. To demonstrate how multiple student-oriented intelligent tools can be integrated into one modular system.

---

🧩 System Modules

1. 📚 AI Study Planner

The Study Planner is designed to help students manage their academic workload.

Inputs

The user provides:

- Subject name
- Deadline
- Difficulty level:
  - Easy
  - Medium
  - Hard
- Available study hours per day

Processing

The system assigns numerical values to difficulty levels and calculates a priority score using the deadline and difficulty.

The subjects are then sorted according to their calculated priority.

Available study hours are distributed proportionally according to the priority scores.

Output

The system generates a table containing:

Information| Description
Subject| Name of the subject
Deadline| Target date
Difficulty| Easy, Medium or Hard
Priority Score| Calculated urgency/importance
Recommended Hours| Suggested daily study allocation

Workflow

Student Input
     ↓
Subject Details
     ↓
Deadline + Difficulty
     ↓
Priority Calculation
     ↓
Subject Ranking
     ↓
Study-Hour Allocation
     ↓
Personalized Study Plan

---

📄 2. AI Resume Analyzer

The Resume Analyzer provides basic automated resume analysis.

Input

The user uploads a resume in PDF format.

Processing

The system:

1. Reads the uploaded PDF.
2. Extracts text using "PyPDF2".
3. Searches the extracted text for predefined skills.
4. Identifies detected skills.
5. Calculates a skill-coverage score.
6. Identifies skills that were not detected.

Output

The application displays:

- Resume skill-coverage score
- Detected skills
- Skills not detected
- Extracted resume text

Workflow

Resume PDF
     ↓
PDF Text Extraction
     ↓
Resume Text
     ↓
Skill Detection
     ↓
Skill Coverage Calculation
     ↓
Detected Skills + Missing Skills

---

🏗️ System Architecture

                         ┌─────────────────────┐
                         │        USER         │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   STREAMLIT WEB UI  │
                         └──────────┬──────────┘
                                    │
                     ┌──────────────┴──────────────┐
                     │                             │
                     ▼                             ▼
          ┌─────────────────────┐       ┌─────────────────────┐
          │  AI STUDY PLANNER   │       │  AI RESUME ANALYZER │
          └──────────┬──────────┘       └──────────┬──────────┘
                     │                             │
                     ▼                             ▼
          Deadline + Difficulty             PDF Resume
                     │                             │
                     ▼                             ▼
             Priority Calculation           Text Extraction
                     │                             │
                     ▼                             ▼
              Study Allocation              Skill Detection
                     │                             │
                     ▼                             ▼
             Study Plan Output              Resume Analysis
                     │                             │
                     └──────────────┬──────────────┘
                                    ▼
                         ┌─────────────────────┐
                         │  STUDENT SUPPORT    │
                         │ Academic + Career   │
                         └─────────────────────┘

---

🔬 Methodology

The project follows a modular application architecture.

Step 1 — User Input

The student selects the required module and provides the required information.

Step 2 — Data Processing

For the Study Planner, subject information is processed to determine priority.

For the Resume Analyzer, PDF content is converted into text.

Step 3 — Intelligent Analysis

The Study Planner uses a rule-based priority calculation.

The Resume Analyzer uses text processing and predefined skill matching.

Step 4 — Result Generation

The processed information is converted into understandable recommendations and analysis.

Step 5 — Web Presentation

Results are displayed through an interactive Streamlit interface.

Step 6 — Deployment

The application is deployed using Streamlit Community Cloud and the source code is maintained through GitHub.

---

🧮 Study Priority Logic

The Study Planner assigns difficulty values:

Easy   → 1
Medium → 2
Hard   → 3

The priority is influenced by:

- Difficulty
- Number of days remaining until the deadline

A higher priority indicates that a subject requires greater attention.

The available daily study hours are then distributed according to the relative priority of each subject.

«Note: The current prototype uses a rule-based prioritization approach rather than a trained machine-learning model.»

---

🧠 Resume Analysis Logic

The Resume Analyzer currently uses a predefined skill list.

Examples include:

- Python
- C
- C++
- Java
- HTML
- CSS
- JavaScript
- SQL
- Machine Learning
- Artificial Intelligence
- Data Science
- Deep Learning
- Git
- GitHub
- Excel
- Power BI
- Tableau
- Communication
- Leadership

The system searches the extracted resume text for these skills.

The basic skill-coverage score is calculated as:

Skill Coverage (%) =
(Number of detected skills / Total predefined skills) × 100

«Important: This is a prototype-level resume analysis score. It should not be interpreted as a professional ATS score or a complete evaluation of resume quality.»

---

🛠️ Technology Stack

Technology| Purpose
Python| Core programming language
Streamlit| Web application interface
PyPDF2| PDF text extraction
GitHub| Source-code management and version control
Jupyter Notebook| Experimentation and analysis
Streamlit Community Cloud| Application deployment

---

📁 Project Structure

AI-Student-Assistant/
│
├── app.py
├── planner.py
├── resume_analyzer.py
├── requirements.txt
└── README.md

"app.py"

Acts as the main application controller and Streamlit interface.

It provides navigation between the Study Planner and Resume Analyzer modules.

"planner.py"

Contains the Study Planner logic, including:

- Priority calculation
- Subject ranking
- Study-hour allocation

"resume_analyzer.py"

Contains the Resume Analyzer functionality, including:

- PDF text extraction
- Skill detection
- Skill-coverage calculation
- Missing-skill identification

"requirements.txt"

Contains the Python dependencies required to run the application.

"README.md"

Provides project documentation, methodology, setup instructions and technical information.

---

🚀 Running the Project Locally

1. Clone the repository

git clone https://github.com/anshi544/AI-Student-Assistant.git

2. Navigate to the project directory

cd AI-Student-Assistant

3. Install dependencies

pip install -r requirements.txt

4. Run the Streamlit application

streamlit run app.py

The application will open in your browser.

---

☁️ Deployment

The application can be deployed using Streamlit Community Cloud.

Deployment steps:

1. Push the project files to GitHub.
2. Open Streamlit Community Cloud.
3. Connect the GitHub repository.
4. Select the repository.
5. Select the "main" branch.
6. Set "app.py" as the main file.
7. Deploy the application.

The deployed application provides access to both modules through a single web interface.

---

✅ Key Features

Academic Assistance

- Subject-based planning
- Deadline-aware prioritization
- Difficulty-based priority
- Study-hour allocation
- Interactive Streamlit interface

Career Assistance

- PDF resume upload
- Automated text extraction
- Skill detection
- Skill-coverage score
- Missing-skill identification

Platform Features

- Single integrated application
- Modular architecture
- Simple user interface
- GitHub-based development
- Cloud deployment
- No complex installation required for end users

---

🎓 Advantages

1. Provides academic and career assistance through one platform.
2. Simple and beginner-friendly user interface.
3. Helps students prioritize their academic workload.
4. Provides quick resume skill analysis.
5. Uses modular Python components.
6. Can be accessed through a web browser after deployment.
7. Can be extended with advanced AI/ML techniques in future versions.

---

⚠️ Current Limitations

The current version is a prototype and has some limitations:

- Study planning uses rule-based calculations.
- Resume analysis relies on a predefined skill list.
- The resume score represents skill coverage rather than complete resume quality.
- Semantic understanding of resume content is limited.
- The system does not currently compare a resume against a specific job description.
- Study planning does not yet account for factors such as learning speed, previous performance or daily changes in availability.

---

🔮 Future Scope

The project can be enhanced in several ways.

AI/ML Enhancement

- Integrate machine-learning models for personalized recommendations.
- Use NLP for deeper resume understanding.
- Use semantic similarity for skill matching.
- Detect contextual skills rather than exact keyword matches.

Resume Enhancement

- Add job-description matching.
- Provide ATS-oriented feedback.
- Identify missing keywords for a selected job role.
- Recommend relevant skills and courses.

Study Planner Enhancement

- Generate weekly and monthly schedules.
- Adapt plans according to completed tasks.
- Track study progress.
- Include revision and break scheduling.
- Use historical performance to personalize recommendations.

Integrated Student Dashboard

Future versions can include:

Student Profile
      ↓
Academic Performance
      ↓
Study Plan
      ↓
Skill Profile
      ↓
Resume Analysis
      ↓
Career Recommendations

This can transform the current prototype into a more comprehensive AI-powered student academic and career assistant.

---

📊 Expected Outcome

The expected outcome of the project is a unified web-based platform that demonstrates how two practical student-support applications can be integrated into a single modular system.

The system helps students:

- Organize academic preparation.
- Prioritize subjects.
- Allocate study time.
- Understand their resume's detected skills.
- Identify areas for skill improvement.
- Connect academic development with career readiness.

---

👩‍💻 Project Information

Project: AI Student Career & Academic Assistant
Domain: Artificial Intelligence / Student Assistance
Program: B.Tech CSE (Artificial Intelligence)
Semester: 5th Semester
Platform: Streamlit
Source Code: GitHub
Deployment: Streamlit Community Cloud

---

📜 Conclusion

The AI Student Career & Academic Assistant integrates academic planning and career-readiness analysis into a single accessible platform.

The Study Planner focuses on what the student should study and how to prioritize it, while the Resume Analyzer focuses on what skills are visible in the student's resume and what areas may require improvement.

The modular design makes the system easy to understand, maintain and extend. Although the current version uses rule-based prioritization and predefined skill matching, it provides a foundation for incorporating more advanced machine-learning and natural-language-processing techniques in future development.

---

⭐ Project Vision

«“Helping students plan better, understand their skills, and prepare for their careers through one integrated platform.”»
