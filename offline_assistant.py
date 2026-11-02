"""Offline utilities for PDF Q&A, career roadmaps and interview practice."""

import re

STOP_WORDS = {
    "the", "a", "an", "and", "or", "to", "of", "in", "on", "for",
    "is", "are", "was", "were", "what", "how", "why", "when",
    "where", "with", "from", "this", "that", "it", "as", "by",
    "be", "can", "i", "me", "my", "you", "your", "about",
    "please", "explain", "tell", "give"
}


# ==================================================
# CAREER ROADMAPS
# ==================================================

CAREER_ROADMAPS = {
    "Python Developer": [
        "Learn Python fundamentals, variables, data types, functions and loops.",
        "Master lists, tuples, dictionaries, sets and exception handling.",
        "Learn OOP, modules, file handling, Git and GitHub.",
        "Practise SQL, REST APIs, testing and Flask/Django basics.",
        "Build and deploy a documented Python project."
    ],

    "Data Analyst": [
        "Learn Excel formulas, data cleaning, pivot tables and charts.",
        "Master SQL filtering, joins, grouping and subqueries.",
        "Learn statistics, NumPy, pandas and exploratory data analysis.",
        "Create dashboards using Power BI or Tableau.",
        "Build an end-to-end data analytics portfolio project."
    ],

    "AI/ML Intern": [
        "Strengthen Python, NumPy, pandas and statistics.",
        "Learn supervised and unsupervised machine learning.",
        "Understand train/test split and evaluation metrics.",
        "Study feature engineering, cross-validation and overfitting.",
        "Build and document an end-to-end machine learning project."
    ],

    "Web Developer": [
        "Learn semantic HTML and CSS fundamentals.",
        "Master responsive layouts and JavaScript.",
        "Learn DOM manipulation, events and asynchronous JavaScript.",
        "Understand APIs, Git and accessibility.",
        "Build and deploy a responsive web application."
    ],

    "General Software Developer": [
        "Learn programming fundamentals, OOP and debugging.",
        "Practise arrays, strings, hashing, searching and sorting.",
        "Study stacks, queues, linked lists, recursion and trees.",
        "Learn DBMS, SQL, operating systems and computer networks.",
        "Build portfolio projects and practise technical interviews."
    ]
}


# ==================================================
# INTERVIEW QUESTION BANK
# ==================================================

INTERVIEW_BANK = {
    "Python": [
        (
            "What is the difference between a list and a tuple?",
            "Lists are mutable, meaning their elements can be changed. "
            "Tuples are immutable after creation. Lists are useful for "
            "modifiable collections, while tuples are useful for fixed data."
        ),
        (
            "What is a dictionary in Python?",
            "A dictionary stores data in key-value pairs. Keys must be "
            "unique and hashable. Dictionaries provide average-case "
            "constant-time lookup."
        ),
        (
            "What is a generator?",
            "A generator produces values lazily using yield. It does not "
            "need to store the entire sequence in memory, making it "
            "memory-efficient."
        ),
        (
            "How do exceptions work in Python?",
            "Exceptions handle runtime errors. The try block contains "
            "potentially problematic code, except handles errors, and "
            "finally executes cleanup code."
        )
    ],

    "DSA": [
        (
            "What is Big-O notation?",
            "Big-O notation describes how an algorithm's time or space "
            "requirements grow as input size increases."
        ),
        (
            "When is binary search applicable?",
            "Binary search works on sorted data or a search space with "
            "a suitable monotonic property. It repeatedly eliminates "
            "approximately half of the remaining search space."
        ),
        (
            "When would you use a hash map?",
            "A hash map is useful for fast key-value lookup, frequency "
            "counting, duplicate detection and mapping related information."
        ),
        (
            "How do you test an algorithm?",
            "Test normal inputs, empty inputs, single-element inputs, "
            "duplicates, boundary conditions and large inputs. Also "
            "evaluate time and space complexity."
        )
    ],

    "DBMS & SQL": [
        (
            "What are ACID properties?",
            "ACID stands for Atomicity, Consistency, Isolation and "
            "Durability. These properties ensure reliable database "
            "transactions."
        ),
        (
            "What is normalization?",
            "Normalization organizes relational database tables to "
            "reduce redundancy and prevent insertion, deletion and "
            "update anomalies."
        ),
        (
            "What is the difference between WHERE and HAVING?",
            "WHERE filters individual rows before grouping. HAVING "
            "filters groups after GROUP BY and is commonly used with "
            "aggregate functions."
        ),
        (
            "What is a primary key?",
            "A primary key uniquely identifies every record in a table. "
            "It cannot contain duplicate or NULL values."
        )
    ],

    "Operating Systems": [
        (
            "What is the difference between a process and a thread?",
            "A process is an executing program with its own address "
            "space. Threads are smaller execution units within a "
            "process and share its memory and resources."
        ),
        (
            "What is deadlock?",
            "Deadlock occurs when processes wait indefinitely for "
            "resources held by one another. The four necessary "
            "conditions are mutual exclusion, hold and wait, no "
            "preemption and circular wait."
        ),
        (
            "What is virtual memory?",
            "Virtual memory provides each process with a virtual "
            "address space. The operating system maps virtual addresses "
            "to physical memory."
        )
    ],

    "HR & Projects": [
        (
            "Tell me about yourself.",
            "Structure your answer around your education, relevant "
            "technical skills, one important project and career goal. "
            "Keep it concise and relevant to the role."
        ),
        (
            "Explain your project.",
            "Explain the problem, intended users, technologies, "
            "architecture, your contribution, challenges, testing "
            "and possible future improvements."
        ),
        (
            "Describe a challenge you handled.",
            "Use the STAR method: Situation, Task, Action and Result. "
            "Describe the challenge and emphasize your own contribution."
        ),
        (
            "Why should we hire you?",
            "Connect your technical skills, projects and learning "
            "ability to the requirements of the role. Support your "
            "claims with genuine examples."
        )
    ]
}


# ==================================================
# INTERVIEW EVALUATION KEYWORDS
# ==================================================

INTERVIEW_KEYWORDS = {
    "What is the difference between a list and a tuple?": [
        "list", "tuple", "mutable", "immutable",
        "change", "modify", "elements", "collection"
    ],

    "What is a dictionary in Python?": [
        "dictionary", "key", "value", "key-value",
        "unique", "hash", "lookup", "mapping"
    ],

    "What is a generator?": [
        "generator", "yield", "iterator",
        "lazy", "memory", "sequence", "values"
    ],

    "How do exceptions work in Python?": [
        "exception", "error", "try", "except",
        "finally", "runtime", "handling"
    ],

    "What is Big-O notation?": [
        "big-o", "complexity", "time", "space",
        "algorithm", "input", "growth"
    ],

    "When is binary search applicable?": [
        "binary search", "sorted", "half", "mid",
        "search space", "divide", "logarithmic"
    ],

    "When would you use a hash map?": [
        "hash map", "dictionary", "lookup", "key",
        "value", "frequency", "duplicate"
    ],

    "How do you test an algorithm?": [
        "test", "edge cases", "boundary", "empty",
        "duplicate", "complexity", "input"
    ],

    "What are ACID properties?": [
        "atomicity", "consistency", "isolation",
        "durability", "transaction", "database"
    ],

    "What is normalization?": [
        "normalization", "redundancy", "database",
        "anomalies", "tables", "data"
    ],

    "What is the difference between WHERE and HAVING?": [
        "where", "having", "filter", "rows",
        "groups", "group by", "aggregate"
    ],

    "What is a primary key?": [
        "primary key", "unique", "identify",
        "record", "null", "duplicate", "table"
    ],

    "What is the difference between a process and a thread?": [
        "process", "thread", "memory",
        "address space", "resources", "execution"
    ],

    "What is deadlock?": [
        "deadlock", "process", "resource",
        "wait", "circular", "mutual exclusion"
    ],

    "What is virtual memory?": [
        "virtual memory", "address", "physical memory",
        "operating system", "mapping", "process"
    ],

    "Tell me about yourself.": [
        "education", "skills", "project",
        "experience", "goal", "career"
    ],

    "Explain your project.": [
        "problem", "project", "technology", "architecture",
        "implementation", "challenge", "result"
    ],

    "Describe a challenge you handled.": [
        "situation", "task", "action", "result",
        "challenge", "solution", "learned"
    ],

    "Why should we hire you?": [
        "skills", "experience", "project", "strength",
        "learning", "contribution", "role"
    ]
}


# ==================================================
# TEXT PROCESSING
# ==================================================

def _terms(text):
    """Extract useful terms from text."""

    words = re.findall(
        r"[a-zA-Z0-9+#.]+",
        (text or "").lower()
    )

    return [
        word for word in words
        if len(word) > 1 and word not in STOP_WORDS
    ]


# ==================================================
# PDF QUESTION ANSWERING
# ==================================================

def answer_from_pdf(question, document_text, max_passages=3):
    """Retrieve relevant passages using keyword matching."""

    paragraphs = [
        re.sub(r"\s+", " ", paragraph).strip()
        for paragraph in re.split(
            r"\n\s*\n|(?<=[.!?])\s+(?=[A-Z0-9])",
            document_text or ""
        )
    ]

    paragraphs = [
        paragraph for paragraph in paragraphs
        if len(paragraph) >= 25
    ]

    if not paragraphs:
        return {
            "found": False,
            "answer": (
                "No selectable text was found. "
                "A scanned PDF may require OCR."
            )
        }

    question_terms = set(_terms(question))

    if not question_terms:
        return {
            "found": False,
            "answer": "Please ask a specific question using document keywords."
        }

    ranked = []

    for paragraph in paragraphs:
        overlap = len(
            question_terms.intersection(_terms(paragraph))
        )

        if overlap:
            ranked.append(
                (overlap / len(question_terms), overlap, paragraph)
            )

    ranked.sort(reverse=True)

    if not ranked:
        return {
            "found": False,
            "answer": (
                "No matching passage was found. "
                "Try rephrasing your question."
            )
        }

    selected = []

    for _, _, paragraph in ranked:
        if paragraph not in selected:
            selected.append(paragraph)

        if len(selected) >= max_passages:
            break

    return {
        "found": True,
        "answer": (
            "**Relevant passages from your PDF**\n\n"
            + "\n\n".join("> " + p for p in selected)
        ),
        "passages": selected
    }


# ==================================================
# AUTOMATED INTERVIEW ANSWER EVALUATION
# ==================================================

def evaluate_interview_answer(question, answer):
    """
    Evaluate an interview answer using keyword coverage,
    answer length and basic structure indicators.

    This is a heuristic evaluator, not semantic AI grading.
    """

    answer = (answer or "").strip()
    answer_lower = answer.lower()
    word_count = len(answer.split())

    keywords = INTERVIEW_KEYWORDS.get(question, [])

    if not answer:
        return {
            "score": 0,
            "matched_keywords": [],
            "missing_keywords": keywords,
            "strengths": [],
            "improvements": [
                "Write an answer before submitting it for evaluation."
            ],
            "word_count": 0
        }

    matched = [
        keyword for keyword in keywords
        if keyword.lower() in answer_lower
    ]

    missing = [
        keyword for keyword in keywords
        if keyword.lower() not in answer_lower
    ]

    # Keyword coverage: 70 points
    keyword_score = (
        (len(matched) / len(keywords)) * 70
        if keywords else 0
    )

    # Answer length: 20 points
    if word_count >= 80:
        length_score = 20
    elif word_count >= 50:
        length_score = 15
    elif word_count >= 30:
        length_score = 10
    elif word_count >= 15:
        length_score = 5
    else:
        length_score = 0

    # Explanation structure: 10 points
    structure_terms = [
        "for example",
        "such as",
        "because",
        "therefore",
        "however",
        "in my project",
        "for instance"
    ]

    structure_matches = [
        term for term in structure_terms
        if term in answer_lower
    ]

    structure_score = min(
        len(structure_matches) * 5,
        10
    )

    score = round(
        keyword_score + length_score + structure_score
    )

    score = min(score, 100)

    # Strengths
    strengths = []

    if matched:
        strengths.append(
            f"You covered {len(matched)} relevant concepts."
        )

    if word_count >= 30:
        strengths.append(
            "Your answer has a reasonable explanation length."
        )

    if structure_matches:
        strengths.append(
            "You included explanation or example-related expressions."
        )

    if not strengths:
        strengths.append(
            "You attempted the question. Continue practising."
        )

    # Improvements
    improvements = []

    if missing:
        improvements.append(
            "Consider covering these concepts: "
            + ", ".join(missing) + "."
        )

    if word_count < 30:
        improvements.append(
            "Expand your answer with a clear explanation and relevant details."
        )

    if not structure_matches:
        improvements.append(
            "Add a short example or explain why the concept is useful."
        )

    if not improvements:
        improvements.append(
            "Keep refining technical accuracy and clarity."
        )

    return {
        "score": score,
        "matched_keywords": matched,
        "missing_keywords": missing,
        "strengths": strengths,
        "improvements": improvements,
        "word_count": word_count
    }
