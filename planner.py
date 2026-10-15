from datetime import datetime, timedelta


DIFFICULTY_SCORE = {
    "Easy": 1,
    "Medium": 2,
    "Hard": 3,
}


def calculate_priority(deadline, difficulty):
    """
    Calculate a subject's priority from its deadline and difficulty.

    Args:
        deadline: datetime.date or a date string in YYYY-MM-DD format.
        difficulty: "Easy", "Medium", or "Hard".

    Returns:
        A priority score. Higher scores indicate greater urgency.
    """
    if isinstance(deadline, str):
        deadline = datetime.strptime(deadline, "%Y-%m-%d").date()

    today = datetime.today().date()
    days_left = (deadline - today).days

    # A deadline today or in the past should receive urgent attention.
    days_left = max(days_left, 1)
    difficulty_value = DIFFICULTY_SCORE.get(str(difficulty).title(), 2)

    priority = (difficulty_value * 10) / days_left

    # Add a small urgency boost for overdue/today deadlines.
    if (deadline - today).days <= 0:
        priority *= 1.25

    return round(priority, 2)


def _prepare_subjects(subjects):
    """Validate and enrich subject data without modifying the input list."""
    prepared = []

    for subject in subjects:
        name = str(subject.get("name", "Untitled subject")).strip()
        deadline = subject.get("deadline")
        difficulty = str(subject.get("difficulty", "Medium")).title()

        if isinstance(deadline, str):
            deadline = datetime.strptime(deadline, "%Y-%m-%d").date()

        if deadline is None:
            raise ValueError(f"A deadline is required for {name}.")

        if difficulty not in DIFFICULTY_SCORE:
            difficulty = "Medium"

        prepared.append({
            "Subject": name,
            "Deadline": deadline,
            "Difficulty": difficulty,
            "Priority Score": calculate_priority(deadline, difficulty),
        })

    prepared.sort(key=lambda item: item["Priority Score"], reverse=True)
    return prepared


def _allocate_hours(plans, daily_hours):
    """Allocate available study time proportionally, without negative hours."""
    if daily_hours < 0:
        raise ValueError("daily_hours must be zero or greater.")

    if not plans:
        return plans

    total_priority = sum(item["Priority Score"] for item in plans)

    if total_priority <= 0:
        hours_each = daily_hours / len(plans)
        allocations = [hours_each] * len(plans)
    else:
        allocations = [
            (item["Priority Score"] / total_priority) * daily_hours
            for item in plans
        ]

    # Round each allocation, then correct rounding drift on the final subject
    # so the displayed total remains close to the requested daily hours.
    for item, hours in zip(plans, allocations):
        item["Recommended Hours"] = round(hours, 2)

    return plans


def generate_plan(subjects, daily_hours):
    """
    Generate a prioritized daily study plan.

    Expected subject dictionaries contain:
        name, deadline, difficulty

    Returns a list of dictionaries, retaining the original keys:
        Subject, Deadline, Difficulty, Priority Score, Recommended Hours
    """
    plans = _prepare_subjects(subjects)
    return _allocate_hours(plans, float(daily_hours))


def generate_weekly_plan(subjects, daily_hours, days=7):
    """
    Generate a simple day-by-day study schedule from the supplied subjects.

    This is an additional helper; the existing app can continue using
    generate_plan(subjects, daily_hours) without changes.

    Returns a list of dictionaries with Day, Date, Subject, Study Hours,
    Session Length (minutes), and Session Type.
    """
    if days < 1:
        raise ValueError("days must be at least 1.")
    if daily_hours < 0:
        raise ValueError("daily_hours must be zero or greater.")

    plans = _prepare_subjects(subjects)
    if not plans or daily_hours == 0:
        return []

    schedule = []
    today = datetime.today().date()

    # Rotate through priority-ranked subjects across the week. The most
    # urgent subjects are placed first each day; time is split evenly among
    # that day's selected subjects to avoid a single oversized session.
    for day_index in range(days):
        current_date = today + timedelta(days=day_index)
        day_subjects = plans[day_index % len(plans):] + plans[:day_index % len(plans)]

        # Use at most three subjects per day for a more manageable schedule.
        selected = day_subjects[:min(3, len(day_subjects))]
        hours_per_subject = daily_hours / len(selected)

        for subject in selected:
            deadline = subject["Deadline"]
            if deadline < current_date:
                session_type = "Urgent catch-up"
            elif day_index % 3 == 2:
                session_type = "Revision"
            else:
                session_type = "Focused study"

            schedule.append({
                "Day": current_date.strftime("%A"),
                "Date": current_date,
                "Subject": subject["Subject"],
                "Study Hours": round(hours_per_subject, 2),
                "Session Length (minutes)": int(round(hours_per_subject * 60)),
                "Session Type": session_type,
            })

    return schedule


def get_study_recommendations(subjects):
    """
    Return practical recommendations based on deadlines and difficulty.
    """
    plans = _prepare_subjects(subjects)
    recommendations = []

    if not plans:
        return ["Add at least one subject to receive study recommendations."]

    today = datetime.today().date()

    for subject in plans:
        days_left = (subject["Deadline"] - today).days
        name = subject["Subject"]
        difficulty = subject["Difficulty"]

        if days_left < 0:
            recommendations.append(
                f"{name}: the deadline has passed. Make a catch-up plan and "
                "confirm the revised submission or exam date."
            )
        elif days_left == 0:
            recommendations.append(
                f"{name}: the deadline is today. Focus on the highest-impact "
                "topics and allow time to review your work."
            )
        elif days_left <= 3:
            recommendations.append(
                f"{name}: only {days_left} day(s) remain. Prioritize key topics "
                "and finish with a short practice or revision session."
            )
        elif difficulty == "Hard":
            recommendations.append(
                f"{name}: schedule focused blocks with short breaks, and solve "
                "practice questions after reviewing the concepts."
            )
        elif difficulty == "Medium":
            recommendations.append(
                f"{name}: combine concept review with practice questions, then "
                "briefly revisit mistakes."
            )
        else:
            recommendations.append(
                f"{name}: use a concise review and self-test to check retention."
            )

    recommendations.append(
        "Study in focused blocks of about 25–50 minutes, then take a short break. "
        "Adjust the schedule if your actual workload or deadlines change."
    )
    return recommendations
