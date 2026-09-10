import re
from PyPDF2 import PdfReader


# Skills that the system can identify
SKILLS = [
    "Python",
    "C",
    "C++",
    "Java",
    "HTML",
    "CSS",
    "JavaScript",
    "SQL",
    "Machine Learning",
    "Artificial Intelligence",
    "Data Science",
    "Deep Learning",
    "Git",
    "GitHub",
    "Excel",
    "Power BI",
    "Tableau",
    "Communication",
    "Leadership"
]


def extract_text_from_pdf(uploaded_file):
    """
    Extract text from an uploaded PDF resume.
    """

    reader = PdfReader(uploaded_file)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


def find_skills(text):
    """
    Detect predefined skills from resume text.
    """

    detected_skills = []

    for skill in SKILLS:

        pattern = r"\b" + re.escape(skill) + r"\b"

        if re.search(pattern, text, re.IGNORECASE):
            detected_skills.append(skill)

    return detected_skills


def analyze_resume(text):
    """
    Analyze resume and calculate a basic score.
    """

    detected_skills = find_skills(text)

    total_skills = len(SKILLS)

    if total_skills > 0:
        score = (len(detected_skills) / total_skills) * 100
    else:
        score = 0

    missing_skills = [
        skill for skill in SKILLS
        if skill not in detected_skills
    ]

    return {
        "score": round(score, 2),
        "skills": detected_skills,
        "missing_skills": missing_skills
    }