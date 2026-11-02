"""API-free utilities for student PDF Q&A, career roadmaps and interview practice."""
import re

STOP_WORDS = {"the", "a", "an", "and", "or", "to", "of", "in", "on", "for", "is", "are", "was", "were", "what", "how", "why", "when", "where", "with", "from", "this", "that", "it", "as", "by", "be", "can", "i", "me", "my", "you", "your", "about", "please", "explain", "tell", "give"}

CAREER_ROADMAPS = {
    "Python Developer": ["Python fundamentals, functions, collections and exceptions", "OOP, modules, Git and GitHub", "SQL, REST APIs, testing and Flask/Django basics", "Build and deploy a documented CRUD/API project", "Practise DSA, debugging and project explanation"],
    "Data Analyst": ["Excel formulas, cleaning, pivot tables and charts", "SQL filtering, joins, aggregation and subqueries", "Statistics, pandas and exploratory data analysis", "Build a Power BI/Tableau dashboard with an insight report", "Practise business questions, SQL and portfolio storytelling"],
    "AI/ML Intern": ["Python, NumPy, pandas, visualization and statistics", "Supervised learning, train/test split and evaluation metrics", "Feature preparation, cross-validation and overfitting", "Build an end-to-end ML project with honest evaluation", "Revise probability, model explanation and Python DSA"],
    "Web Developer": ["Semantic HTML, CSS and responsive layouts", "JavaScript, DOM, events and async/await", "Forms, APIs, accessibility and Git", "Build and deploy a responsive web project", "Practise debugging and explaining design choices"],
    "General Software Developer": ["One language, functions, collections, OOP and debugging", "Arrays, strings, hashing, searching, sorting and complexity", "Stacks, queues, linked lists, recursion and trees", "SQL, DBMS, OS, networking, Git and one portfolio project", "Mock interviews, DSA revision and role-specific preparation"],
}

INTERVIEW_BANK = {
    "Python": [
        ("What is the difference between a list and a tuple?", "Lists are mutable; tuples are immutable. Choose based on whether the collection needs in-place changes."),
        ("What is a dictionary?", "A mapping of hashable keys to values, commonly used for average-case fast key lookup."),
        ("What is a generator?", "An iterator-producing function or expression that yields values lazily, often saving memory."),
        ("How do exceptions work?", "Use try/except for expected errors and finally for cleanup. Avoid hiding unexpected errors with overly broad catches."),
    ],
    "DSA": [
        ("What is Big-O notation?", "It describes how resource use grows with input size, usually focusing on asymptotic growth."),
        ("When is binary search applicable?", "When the search space is ordered or has a suitable monotonic property; each step discards roughly half."),
        ("When would you use a hash map?", "For key lookup, frequency counting, deduplication or mapping values to related information."),
        ("How do you test an algorithm?", "Check normal cases, empty and single-element inputs, duplicates, boundaries and expected complexity."),
    ],
    "DBMS & SQL": [
        ("What are ACID properties?", "Atomicity, Consistency, Isolation and Durability describe important transaction guarantees."),
        ("What is normalization?", "Structuring relational data to reduce avoidable redundancy and update anomalies."),
        ("WHERE vs HAVING?", "WHERE filters rows before grouping; HAVING filters groups after aggregation."),
        ("What is a primary key?", "A column or column set that uniquely identifies each row and cannot contain NULL values."),
    ],
    "Operating Systems": [
        ("Process vs thread?", "A process has its own address space; threads in a process share memory/resources while retaining separate execution state."),
        ("What is deadlock?", "A set of processes is deadlocked when each waits for a resource or event that another process in the set must provide."),
        ("What is virtual memory?", "An abstraction that gives processes a virtual address space mapped to physical memory and, where configured, backing storage."),
    ],
    "HR & Projects": [
        ("Tell me about yourself.", "Use 45–60 seconds: education, relevant skills, one project and target role. Keep all claims accurate."),
        ("Explain your project.", "Cover the problem, intended users, architecture, your contribution, a challenge, testing, limitations and next steps."),
        ("Describe a challenge you handled.", "Use STAR: Situation, Task, Action, Result. Explain your own actions and what you learned."),
        ("Why should we hire you?", "Connect relevant skills and a demonstrated project to the role; avoid unsupported claims and show willingness to learn."),
    ],
}


def _terms(text):
    return [w for w in re.findall(r"[a-zA-Z0-9+#.]+", (text or "").lower()) if len(w) > 1 and w not in STOP_WORDS]


def answer_from_pdf(question, document_text, max_passages=3):
    """Return relevant extracted PDF passages using simple keyword overlap, not an LLM."""
    paragraphs = [re.sub(r"\s+", " ", p).strip() for p in re.split(r"\n\s*\n|(?<=[.!?])\s+(?=[A-Z0-9])", document_text or "")]
    paragraphs = [p for p in paragraphs if len(p) >= 25]
    if not paragraphs:
        return {"found": False, "answer": "No selectable text was found. If this is a scanned PDF, it may need OCR before it can be searched."}
    q_terms = set(_terms(question))
    if not q_terms:
        return {"found": False, "answer": "Please ask a specific question using keywords from the document."}
    ranked = []
    for paragraph in paragraphs:
        overlap = len(q_terms.intersection(_terms(paragraph)))
        if overlap:
            ranked.append((overlap / len(q_terms), overlap, paragraph))
    ranked.sort(reverse=True)
    if not ranked:
        return {"found": False, "answer": "I couldn't find a matching passage. Try rephrasing the question using terminology from the PDF."}
    selected = []
    for _, _, paragraph in ranked:
        if paragraph not in selected:
            selected.append(paragraph)
        if len(selected) >= max_passages:
            break
    return {"found": True, "answer": "**Relevant passages from your PDF**\n\n" + "\n\n".join("> " + p for p in selected), "passages": selected}
