AI Student Career & Academic Assistant

A web-based student support application built with Python and
Streamlit that brings academic planning and basic career preparation
tools together in one place.

🔗 Live Demo:
https://ai-student-assistant-dng942echs65vuvlrwiwqk.streamlit.app/\
💻 GitHub Repository:
https://github.com/anshi544/AI-Student-Assistant

📌 Project Overview

Students often need to manage subject deadlines, prepare for examinations, improve their resumes, and get ready for placements. This project provides a single web application with tools to support these activities.

The application includes three primary modules:

AI Study Planner --- organizes study tasks using deadlines and
difficulty levels, generates a weekly plan, provides study
recommendations, and supports CSV downloads.

AI Resume Analyzer --- extracts text from PDF resumes,
identifies skills using predefined skill matching, compares them
with career-related skill checklists, and suggests skills to
consider developing.

Student Chatbot --- provides basic academic, programming, and
career guidance using predefined, topic-based responses.

The application also supports user registration, email verification, and
login through Supabase.

Implementation note: The chatbot currently uses topic-based
response matching rather than a generative AI model. The Resume
Analyzer uses PDF text extraction and predefined skill matching; it
does not predict hiring outcomes.

✨ Features

📚 Study Planner

Add study tasks and subject information.

Prioritize tasks using difficulty and time remaining until
deadlines.

Generate an organized study plan and weekly timetable.

View study recommendations.

Download planning results as CSV files.

The priority calculation uses the following heuristic:

Priority Score = (Difficulty Score × 10) / max(Days Left, 1)

Difficulty scores: - Easy = 1 - Medium = 2 - Hard = 3

This is a rule-based prioritization formula, not a trained
machine-learning model.

📄 Resume Analyzer

Upload a PDF resume.

Extract text from the PDF using PyPDF2.

Identify skills using predefined skill lists.

Compare detected skills with a selected career checklist.

Display relevant skills and suggest skills that were not detected.

A skill that is not detected may still be a skill the student possesses;
it may simply be absent from the resume or expressed using different
wording.

💬 Student Chatbot

Ask basic academic, programming, and career-related questions.

Access topic-based guidance for supported subjects such as Python,
DSA, DBMS, AI/ML, resumes, projects, and placement preparation.

Receive predefined responses based on recognized topics.

The chatbot's responses are limited to the topics and rules implemented
in the application.

🔐 User Authentication

Create an account.

Verify an email address.

Log in through Supabase authentication.

Maintain the user's authentication session within the application.

🛠️ Technology Stack

Technology                  Purpose

Python                      Main programming language
Streamlit                   Web interface and dashboard
Supabase                    Authentication and backend services
PyPDF2                      PDF text extraction
Pandas                      Tabular data handling, where used
GitHub                      Source-code hosting and version control
Streamlit Community Cloud   Application deployment

🗂️ Project Structure

AI-Student-Assistant/
├── app.py                 # Main Streamlit application
├── planner.py             # Study planning and prioritization logic
├── resume_analyzer.py     # PDF extraction and resume skill matching
├── requirements.txt       # Python package dependencies
└── README.md              # Project documentation

The repository may contain additional files as the project evolves.

🚀 Run the Project Locally

Prerequisites

Python 3.10 or a compatible Python version

Git

A Supabase project with authentication configured

1. Clone the repository

git clone https://github.com/anshi544/AI-Student-Assistant.git
cd AI-Student-Assistant

2. Install dependencies

pip install -r requirements.txt

3. Configure Supabase secrets

The application expects the following Streamlit secrets:

SUPABASE_URL = "your-supabase-project-url"
SUPABASE_KEY = "your-supabase-publishable-or-anon-key"

For local development, save these values in .streamlit/secrets.toml.

Make sure this secrets file is excluded from Git and never commit API
keys, passwords, access tokens, or other private credentials. Use only
the appropriate client-side/publishable key for this application; do not
expose a Supabase service_role key.

Configure Supabase email authentication and any required profile table
or row-level security policies to match the application code.

4. Start the Streamlit application

streamlit run app.py

Streamlit will provide a local address, usually http://localhost:8501.

☁️ Deployment

The project is hosted using GitHub and Streamlit Community Cloud.

Push the project files to GitHub.

Sign in to Streamlit Community Cloud.

Create or select an app linked to the repository.

Set app.py as the main application file.

Add SUPABASE_URL and SUPABASE_KEY in the app's Secrets settings.

Deploy the app and check the deployment logs if an error occurs.

Live application:
https://ai-student-assistant-dng942echs65vuvlrwiwqk.streamlit.app/

🔄 How It Works

Study Planner

Student enters study information → planner calculates priority scores →
tasks are organized → weekly plan and recommendations are displayed →
results can be downloaded as CSV.

Resume Analyzer

Student uploads a PDF → text is extracted → predefined skills are
matched → results are compared with a career checklist → skill
suggestions are displayed.

Student Chatbot

Student enters a question → the application matches it to a supported
topic → a predefined response is displayed.

Authentication

Student registers or logs in → Supabase handles the authentication
request → the application responds based on the authentication result
and session.

⚠️ Current Limitations

Resume analysis depends on text that can be extracted from the
uploaded PDF.

Image-only or unusually formatted PDFs may not yield usable text.

Skill detection relies on predefined matching and may miss synonyms
or differently phrased skills.

The chatbot can answer only within its implemented topics and
response rules.

Study-plan usefulness depends on the accuracy of the information
entered by the student.

The priority score is a heuristic and should be treated as a
planning aid, not a prediction.

🔮 Future Scope

Potential improvements include: - Integrating a generative AI model for
more flexible conversations. - Improving resume skill detection with
semantic matching. - Adding student progress tracking and personalized
recommendations. - Adding reminders and calendar integration. -
Supporting more career paths and skill frameworks. - Gathering user
feedback to improve the planning experience.

These are proposed improvements and should not be interpreted as
features already implemented.

🎯 Project Objective

The objective of this project is to provide students with an accessible
platform that supports study organization, resume skill review, and
basic academic and career guidance through a single web application.

👩‍💻 Author

Anshika Saxena
B.Tech --- Computer Science Engineering (Artificial Intelligence)
SSIPMT

📄 License

No license has been specified for this repository. If you intend to
allow others to reuse, modify, or distribute the code, consider adding
an appropriate open-source license.
