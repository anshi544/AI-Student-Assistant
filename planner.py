
from datetime import datetime, timedelta


DIFFICULTY_SCORE = {
    "Easy": 1,
    "Medium": 2,
    "Hard": 3,
}


def _parse_deadline(deadline):
    """Convert a date string into a date object."""
    if isinstance(deadline, str):
        return datetime.strptime(deadline, "%Y-%m-%d").date()
    return deadline


def calculate_priority(
    deadline,
    difficulty,
    remaining_topics=1,
    estimated_hours=1,
):
    """
    Calculate priority using deadline, difficulty and remaining workload.
    Higher scores indicate greater priority.
    """
    deadline = _parse_deadline(deadline)

    today = datetime.today().date()
    days_left = (deadline - today).days

    days_for_calculation = max(days_left, 1)
    difficulty_value = DIFFICULTY_SCORE.get(
        str(difficulty).title(), 2
    )

    workload = max(float(estimated_hours), 0.0)
    topics = max(int(remaining_topics), 0)

    if topics == 0 or workload == 0:
        return 0.0

    priority = (
        difficulty_value
        * (1 + topics / 10)
        * (1 + workload / 10)
        * 10
        / days_for_calculation
    )

    if days_left <= 0:
        priority *= 1.5

    return round(priority, 2)


def _prepare_subjects(subjects):
    """Validate and enrich subject information."""
    prepared = []

    for subject in subjects:
        name = str(
            subject.get("name", "Untitled subject")
        ).strip()

        deadline = subject.get("deadline")

        if deadline is None:
            raise ValueError(
                f"A deadline is required for {name}."
            )

        deadline = _parse_deadline(deadline)

        difficulty = str(
            subject.get("difficulty", "Medium")
        ).title()

        if difficulty not in DIFFICULTY_SCORE:
            difficulty = "Medium"

        total_topics = max(
            int(subject.get("total_topics", 1)), 1
        )

        completed_topics = max(
            int(subject.get("completed_topics", 0)), 0
        )

        if completed_topics > total_topics:
            raise ValueError(
                f"Completed topics cannot exceed total topics for {name}."
            )

        remaining_topics = (
            total_topics - completed_topics
        )

        estimated_hours = max(
            float(subject.get("estimated_hours", 1)), 0.0
        )

        # Estimate remaining workload proportionally.
        remaining_hours = (
            estimated_hours * remaining_topics / total_topics
        )

        priority = calculate_priority(
            deadline,
            difficulty,
            remaining_topics,
            remaining_hours,
        )

        progress = (
            completed_topics / total_topics
        ) * 100

        prepared.append({
            "Subject": name,
            "Deadline": deadline,
            "Difficulty": difficulty,
            "Total Topics": total_topics,
            "Completed Topics": completed_topics,
            "Remaining Topics": remaining_topics,
            "Estimated Hours": estimated_hours,
            "Remaining Hours": round(remaining_hours, 2),
            "Progress (%)": round(progress, 2),
            "Priority Score": priority,
        })

    prepared.sort(
        key=lambda item: item["Priority Score"],
        reverse=True,
    )

    return prepared


def _allocate_hours(plans, daily_hours):
    """Allocate daily study hours according to priority."""
    daily_hours = float(daily_hours)

    if daily_hours < 0:
        raise ValueError(
            "Daily study hours cannot be negative."
        )

    active_plans = [
        item for item in plans
        if item["Remaining Topics"] > 0
        and item["Remaining Hours"] > 0
    ]

    total_priority = sum(
        item["Priority Score"]
        for item in active_plans
    )

    for item in plans:
        item["Recommended Hours"] = 0.0

    if not active_plans or daily_hours == 0:
        return plans

    if total_priority <= 0:
        for item in active_plans:
            item["Recommended Hours"] = round(
                daily_hours / len(active_plans), 2
            )
    else:
        for item in active_plans:
            allocation = (
                item["Priority Score"]
                / total_priority
            ) * daily_hours

            item["Recommended Hours"] = round(
                allocation, 2
            )

    # Correct rounding differences.
    difference = round(
        daily_hours - sum(
            item["Recommended Hours"]
            for item in active_plans
        ),
        2,
    )

    active_plans[0]["Recommended Hours"] = round(
        active_plans[0]["Recommended Hours"] + difference,
        2,
    )

    return plans


def generate_plan(subjects, daily_hours):
    """
    Generate a prioritized daily study plan.

    Preserves the original function interface and output fields.
    """
    plans = _prepare_subjects(subjects)

    return _allocate_hours(
        plans,
        float(daily_hours),
    )


def generate_weekly_plan(subjects, daily_hours, days=7):
    """
    Generate a workload-aware weekly timetable.
    Completed subjects are excluded from new-topic scheduling.
    """
    daily_hours = float(daily_hours)

    if days < 1:
        raise ValueError(
            "Days must be at least 1."
        )

    if daily_hours < 0:
        raise ValueError(
            "Daily study hours cannot be negative."
        )

    plans = _prepare_subjects(subjects)

    active_plans = [
        item for item in plans
        if item["Remaining Topics"] > 0
        and item["Remaining Hours"] > 0
    ]

    if not active_plans or daily_hours == 0:
        return []

    today = datetime.today().date()
    schedule = []

    for day_index in range(days):

        current_date = today + timedelta(
            days=day_index
        )

        # Select the three highest-priority subjects.
        ranked_subjects = sorted(
            active_plans,
            key=lambda item: (
                item["Priority Score"]
                * (1 + max(
                    (item["Deadline"] - current_date).days,
                    0,
                ) / 10)
            ),
        )

        selected = list(reversed(ranked_subjects))[:3]

        total_priority = sum(
            item["Priority Score"]
            for item in selected
        )

        if total_priority <= 0:
            continue

        for subject in selected:

            hours = (
                subject["Priority Score"]
                / total_priority
            ) * daily_hours

            # Revision sessions every third day.
            if day_index % 3 == 2:
                session_type = "Revision & Practice"
            elif subject["Deadline"] <= current_date:
                session_type = "Urgent Preparation"
            else:
                session_type = "Focused Study"

            schedule.append({
                "Day": current_date.strftime("%A"),
                "Date": current_date,
                "Subject": subject["Subject"],
                "Study Hours": round(hours, 2),
                "Session Length (minutes)": int(
                    round(hours * 60)
                ),
                "Session Type": session_type,
                "Remaining Topics": subject["Remaining Topics"],
                "Progress (%)": subject["Progress (%)"],
            })

    return schedule


def get_study_recommendations(subjects):
    """Generate recommendations based on workload and progress."""
    plans = _prepare_subjects(subjects)

    recommendations = []

    if not plans:
        return [
            "Add at least one subject to receive recommendations."
        ]

    today = datetime.today().date()

    for subject in plans:

        name = subject["Subject"]
        days_left = (
            subject["Deadline"] - today
        ).days

        remaining = subject["Remaining Topics"]
        progress = subject["Progress (%)"]
        difficulty = subject["Difficulty"]
        remaining_hours = subject["Remaining Hours"]

        if remaining == 0:
            recommendations.append(
                f"{name}: All topics are completed. "
                "Use practice tests and revision to maintain preparation."
            )
            continue

        if days_left < 0:
            recommendations.append(
                f"{name}: The deadline has passed. "
                "Create an urgent catch-up plan and confirm the revised deadline."
            )

        elif days_left == 0:
            recommendations.append(
                f"{name}: Your deadline is today. "
                "Focus on important topics and quick revision."
            )

        elif days_left <= 3:
            recommendations.append(
                f"{name}: Only {days_left} day(s) remain. "
                f"Prioritize the {remaining} unfinished topics."
            )

        elif difficulty == "Hard":
            recommendations.append(
                f"{name}: This is a difficult subject. "
                "Use focused study blocks and solve practice questions."
            )

        elif progress < 50:
            recommendations.append(
                f"{name}: Your completion is {progress:.0f}%. "
                "Focus on completing the remaining topics."
            )

        else:
            recommendations.append(
                f"{name}: You have completed {progress:.0f}% of the syllabus. "
                "Concentrate on revision and practice."
            )

        if remaining > 0:
            recommendations.append(
                f"{name}: Approximately {remaining_hours:.1f} "
                "preparation hours remain based on your workload estimate."
            )

    recommendations.append(
        "Study in focused 25–50 minute sessions and take "
        "5–10 minute breaks between sessions."
    )

    return recommendations
