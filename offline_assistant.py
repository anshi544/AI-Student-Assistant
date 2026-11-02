```python
"""Offline utilities for PDF Q&A, career roadmaps and interview practice."""

import re

STOP_WORDS = {
    "the", "a", "an", "and", "or", "to", "of", "in", "on", "for",
    "is", "are", "was", "were", "what", "how", "why", "when",
    "where", "with", "from", "this", "that", "it", "as", "by",
    "be", "can", "i", "me", "my", "you", "your", "about",
    "please", "explain", "tell", "give"
}


# --------------------------------------------------
# CAREER ROADMAPS
# --------------------------------------------------

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
        "Study stacks, queues, linked lists, recursion and
```
