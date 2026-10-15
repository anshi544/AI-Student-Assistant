import re
from PyPDF2 import PdfReader


# Skills that the system can identify from resume text.
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
    "Leadership",
    "Data Structures and Algorithms",
    "Object-Oriented Programming",
    "Flask",
    "Django",
    "Streamlit",
    "REST API",
    "MongoDB",
    "PostgreSQL",
    "NumPy",
    "Pandas",
    "Scikit-learn",
    "TensorFlow",
    "PyTorch",
    "Statistics",
    "Data Visualization",
    "Problem Solving",
    "Teamwork",
]


# Transparent, predefined skill checklists for common entry-level roles.
# These are guidance checklists, not guarantees of employability.
CAREER_SKILLS = {
    "Python Developer": [
        "Python", "SQL", "Git", "Data Structures and Algorithms",
        "Object-Oriented Programming", "REST API", "Flask",
    ],
    "Data Analyst": [
        "SQL", "Excel", "Python", "Pandas", "Statistics",
        "Data Visualization", "Power BI", "Tableau",
    ],
    "Machine Learning Engineer": [
        "Python", "SQL", "Statistics", "Data Science", "Machine Learning",
        "Deep Learning", "NumPy", "Pandas", "Scikit-learn",
        "TensorFlow", "PyTorch", "Git",
    ],
    "AI/ML Student or Intern": [
        "Python", "Statistics", "Data Science", "Machine Learning",
        "Deep Learning", "NumPy", "Pandas", "Scikit-learn", "Git",
    ],
    "Web Developer": [
        "HTML", "CSS", "JavaScript", "Python", "Git",
        "REST API", "Flask", "Django",
    ],
    "General Software Developer": [
        "Python", "C", "C++", "Java", "SQL", "Git",
        "Data Structures and Algorithms", "Object-Oriented Programming",
        "Problem Solving",
    ],
}

SKILL_LEARNING_TIPS = {
    "Python": "Practise functions, collections, file handling, exceptions, and small projects.",
    "SQL": "Practise SELECT, JOIN, GROUP BY, subqueries, and window functions.",
    "Git": "Learn commits, branches, merges, pull requests, and resolving conflicts.",
    "Data Structures and Algorithms": "Practise arrays, strings, stacks, queues, trees, searching, and sorting.",
    "Object-Oriented Programming": "Practise classes, objects, inheritance, encapsulation, and polymorphism.",
    "REST API": "Learn HTTP methods, status codes, JSON, request validation, and API testing.",
    "Flask": "Build a small Python web app with routes, templates, and form validation.",
    "Django": "Build a small CRUD app and learn models, views, URLs, and authentication.",
    "HTML": "Practise semantic elements, forms, and accessible page structure.",
    "CSS": "Practise Flexbox, Grid, responsive layouts, and reusable styles.",
    "JavaScript": "Learn DOM manipulation, events, async/await, and fetch.",
    "Excel": "Practise formulas, lookups, pivot tables, charts, and data cleaning.",
    "Power BI": "Build a dashboard using Power Query, data models, and DAX basics.",
    "Tableau": "Build interactive dashboards and practise calculated fields and filters.",
    "Statistics": "Revise probability, distributions, hypothesis testing, and descriptive statistics.",
    "Data Science": "Complete a small end-to-end project with cleaning, exploration, and evaluation.",
    "Machine Learning": "Practise train/test splits, baselines, evaluation metrics, and model validation.",
    "Deep Learning": "Learn neural-network basics and build a small, evaluated model.",
    "NumPy": "Practise arrays, vectorized operations, indexing, and broadcasting.",
    "Pandas": "Practise DataFrames, missing values, filtering, grouping, and merging.",
    "Scikit-learn": "Build a reproducible pipeline and compare suitable evaluation metrics.",
    "TensorFlow": "Follow a small model tutorial and evaluate it on held-out data.",
    "PyTorch": "Practise tensors, datasets, training loops, and model evaluation.",
    "Data Visualization": "Choose clear charts and label axes, units, and important comparisons.",
    "Problem Solving": "Practise explaining your approach, edge cases, and time complexity.",
}


def extract_text_from_pdf(uploaded_file):
    """Extract selectable text from an uploaded PDF resume."""
    reader = PdfReader(uploaded_file)
    text_parts = []

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_parts.append(page_text)

    return "\n".join(text_parts)


def find_skills(text):
    """Detect predefined skills in resume text, case-insensitively."""
    if not text:
        return []

    detected_skills = []
    for skill in SKILLS:
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"
        if re.search(pattern, text, re.IGNORECASE):
            detected_skills.append(skill)

    return detected_skills


def analyze_resume(text, career_goal="General Software Developer"):
    """
    Analyze a resume and compare detected skills with a transparent role checklist.

    The score is a skill-coverage indicator for the selected role, not an overall
    resume quality score or a prediction of hiring outcomes.
    """
    detected_skills = find_skills(text)
    selected_goal = career_goal if career_goal in CAREER_SKILLS else "General Software Developer"
    target_skills = CAREER_SKILLS[selected_goal]

    detected_lookup = {skill.casefold() for skill in detected_skills}
    matched_skills = [
        skill for skill in target_skills
        if skill.casefold() in detected_lookup
    ]
    missing_skills = [
        skill for skill in target_skills
        if skill.casefold() not in detected_lookup
    ]

    coverage = (len(matched_skills) / len(target_skills) * 100) if target_skills else 0

    recommendations = []
    for skill in missing_skills:
        tip = SKILL_LEARNING_TIPS.get(
            skill,
            f"Learn the fundamentals of {skill} and practise with a small project."
        )
        recommendations.append({"skill": skill, "suggestion": tip})

    return {
        "score": round(coverage, 2),
        "career_goal": selected_goal,
        "skills": detected_skills,
        "target_skills": target_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "recommendations": recommendations,
    }
