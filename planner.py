from datetime import datetime


def calculate_priority(deadline, difficulty):
    """
    Calculate priority based on deadline and difficulty.

    Higher priority means the subject needs earlier attention.
    """

    today = datetime.today().date()
    days_left = (deadline - today).days

    # Avoid division by zero or negative values
    days_left = max(days_left, 1)

    difficulty_score = {
        "Easy": 1,
        "Medium": 2,
        "Hard": 3
    }

    difficulty_value = difficulty_score.get(difficulty, 2)

    priority = (difficulty_value * 10) / days_left

    return round(priority, 2)


def generate_plan(subjects, daily_hours):
    """
    Generate a prioritized study plan.

    subjects = list of dictionaries containing:
        name
        deadline
        difficulty
    """

    plans = []

    for subject in subjects:

        priority = calculate_priority(
            subject["deadline"],
            subject["difficulty"]
        )

        plans.append({
            "Subject": subject["name"],
            "Deadline": subject["deadline"],
            "Difficulty": subject["difficulty"],
            "Priority Score": priority
        })

    # Highest priority first
    plans.sort(
        key=lambda x: x["Priority Score"],
        reverse=True
    )

    # Divide available study time according to priority
    total_priority = sum(
        item["Priority Score"] for item in plans
    )

    for item in plans:

        if total_priority > 0:
            recommended_hours = (
                item["Priority Score"] / total_priority
            ) * daily_hours
        else:
            recommended_hours = 0

        item["Recommended Hours"] = round(
            recommended_hours,
            2
        )

    return plans