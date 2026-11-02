from datetime import date, datetime, timedelta


DIFFICULTY_SCORE = {
    "Easy": 1,
    "Medium": 2,
    "Hard": 3
}


def _parse_deadline(deadline):
    """Convert deadline into a date object."""
    if isinstance(deadline, datetime):
        return deadline.date()

    if isinstance(deadline, date):
        return deadline

    if isinstance(deadline, str):
        return datetime.strptime(deadline, "%Y-%m-%d").date()

    return date.today()


def calculate_priority(
    deadline,
    difficulty,
    remaining_topics=1,
    estimated_hours=1
):
    """Calculate subject priority using deadline and workload."""

    deadline = _parse_deadline(deadline)
    days_left = max((deadline - date.today()).days, 1)

    difficulty_value = DIFFICULTY_SCORE.get(difficulty, 2)

    workload = max(remaining_topics, 1) * max(estimated_hours, 1)

    priority = (
        difficulty_value * workload
    ) / days_left

    return round(priority, 2)


def _prepare_subjects(subjects):
    """Prepare subject data and calculate remaining workload."""

    prepared = []

    for subject in subjects:
        total_topics = int(subject.get("total_topics", 0))
        completed_topics = int(subject.get("completed_topics", 0))

        remaining_topics = max(
            0, total_topics - completed_topics
        )

        estimated_hours = float(
            subject.get("estimated_hours", 0)
        )

        remaining_hours = (
            estimated_hours * remaining_topics / total_topics
            if total_topics > 0 else 0
        )

        deadline = _parse_deadline(
            subject.get("deadline", date.today())
        )

        difficulty = subject.get("difficulty", "Medium")

        progress = (
            completed_topics / total_topics * 100
            if total_topics > 0 else 0
        )

        priority = calculate_priority(
            deadline,
            difficulty,
            remaining_topics,
            remaining_hours
        )

        if remaining_topics == 0:
            priority = 0

        prepared.append({
            "name": subject["name"],
            "deadline": deadline,
            "difficulty": difficulty,
            "total_topics": total_topics,
            "completed_topics": completed_topics,
            "remaining_topics": remaining_topics,
            "estimated_hours": estimated_hours,
            "remaining_hours": round(remaining_hours, 2),
            "progress": round(progress, 1),
            "priority": priority
        })

    return prepared


def _allocate_hours(plans, daily_hours):
    """Allocate daily study hours according to subject priority."""

    active_subjects = [
        subject for subject in plans
        if subject["remaining_topics"] > 0
    ]

    total_priority = sum(
        subject["priority"] for subject in active_subjects
    )

    for subject in plans:
        if subject["remaining_topics"] == 0:
            subject["recommended_hours"] = 0

        elif total_priority > 0:
            allocation = (
                subject["priority"] / total_priority
            ) * daily_hours

            subject["recommended_hours"] = round(
                min(allocation, daily_hours), 2
            )

        else:
            subject["recommended_hours"] = 0

    return plans


def generate_plan(subjects, daily_hours):
    """Generate a priority-based study plan."""

    plans = _prepare_subjects(subjects)

    plans = _allocate_hours(plans, daily_hours)

    plans.sort(
        key=lambda subject: subject["priority"],
        reverse=True
    )

    result = []

    for subject in plans:
        result.append({
            "Subject": subject["name"],
            "Deadline": subject["deadline"],
            "Difficulty": subject["difficulty"],
            "Total Topics": subject["total_topics"],
            "Completed Topics": subject["completed_topics"],
            "Remaining Topics": subject["remaining_topics"],
            "Estimated Hours": subject["estimated_hours"],
            "Remaining Hours": subject["remaining_hours"],
            "Progress (%)": subject["progress"],
            "Priority Score": subject["priority"],
            "Recommended Hours": subject["recommended_hours"]
        })

    return result


def generate_weekly_plan(subjects, daily_hours, days=7):
    """Generate a weekly timetable based on subject priorities."""

    plans = _prepare_subjects(subjects)

    plans = _allocate_hours(plans, daily_hours)

    plans.sort(
        key=lambda subject: subject["priority"],
        reverse=True
    )

    weekly_plan = []

    active_subjects = [
        subject for subject in plans
        if subject["remaining_topics"] > 0
    ]

    if not active_subjects:
        return weekly_plan

    for day_number in range(days):

        current_date = date.today() + timedelta(
            days=day_number
        )

        if (day_number + 1) % 3 == 0:
            weekly_plan.append({
                "Day": current_date.strftime("%A"),
                "Date": current_date,
                "Subject": "Revision",
                "Recommended Hours": daily_hours,
                "Remaining Topics": 0,
                "Progress (%)": 100
            })
            continue

        daily_subjects = active_subjects[:3]

        total_priority = sum(
            subject["priority"]
            for subject in daily_subjects
        )

        for subject in daily_subjects:

            if total_priority > 0:
                allocated_hours = (
                    subject["priority"] / total_priority
                ) * daily_hours
            else:
                allocated_hours = daily_hours / len(daily_subjects)

            allocated_hours = round(allocated_hours, 2)

            weekly_plan.append({
                "Day": current_date.strftime("%A"),
                "Date": current_date,
                "Subject": subject["name"],
                "Recommended Hours": allocated_hours,
                "Remaining Topics": subject["remaining_topics"],
                "Progress (%)": subject["progress"]
            })

    return weekly_plan


def get_study_recommendations(subjects):
    """Generate personalized study recommendations."""

    recommendations = []

    plans = _prepare_subjects(subjects)

    if not plans:
        return ["Add subjects to generate study recommendations."]

    for subject in plans:

        name = subject["name"]
        deadline = subject["deadline"]
        remaining_topics = subject["remaining_topics"]
        progress = subject["progress"]

        days_left = (deadline - date.today()).days

        if remaining_topics == 0:
            recommendations.append(
                f"{name}: Subject completed. Focus on revision and practice."
            )

        elif days_left < 0:
            recommendations.append(
                f"{name}: Deadline has passed. Prioritize completing "
                "the remaining topics."
            )

        elif days_left <= 3:
            recommendations.append(
                f"{name}: Urgent! Only {days_left} days remain. "
                "Focus on important topics."
            )

        elif days_left <= 7:
            recommendations.append(
                f"{name}: Deadline approaching. Increase your "
                "daily preparation time."
            )

        elif progress < 30:
            recommendations.append(
                f"{name}: Progress is below 30%. Try completing "
                "the foundational topics first."
            )

        elif progress < 70:
            recommendations.append(
                f"{name}: Good progress. Maintain consistency "
                "and complete the remaining topics."
            )

        else:
            recommendations.append(
                f"{name}: Almost complete. Focus on revision "
                "and practice questions."
            )

    recommendations.append(
        "Study in focused 25–50 minute sessions and take "
        "5–10 minute breaks between sessions."
    )

    return recommendations


def generate_smart_insights(subjects, daily_hours):
    """Generate deadline alerts, workload analysis and forecasts."""

    insights = []
    total_required_daily_hours = 0

    for subject in _prepare_subjects(subjects):

        total_topics = subject["total_topics"]
        remaining_topics = subject["remaining_topics"]
        remaining_hours = subject["remaining_hours"]
        deadline = subject["deadline"]

        days_left = (deadline - date.today()).days

        if remaining_topics == 0:
            required_daily_hours = 0
        elif days_left > 0:
            required_daily_hours = remaining_hours / days_left
        else:
            required_daily_hours = remaining_hours

        total_required_daily_hours += required_daily_hours

        progress = subject["progress"]

        # Deadline alert
        if remaining_topics == 0:
            deadline_alert = "Completed"
        elif days_left < 0:
            deadline_alert = "Overdue"
        elif days_left <= 3:
            deadline_alert = "Urgent"
        elif days_left <= 7:
            deadline_alert = "Approaching"
        else:
            deadline_alert = "On Schedule"

        # Progress status
        if remaining_topics == 0:
            status = "Completed"
        elif days_left < 0 or days_left <= 3:
            status = "Critical"
        elif required_daily_hours > daily_hours:
            status = "Needs Attention"
        else:
            status = "On Track"

        insights.append({
            "Subject": subject["name"],
            "Deadline Alert": deadline_alert,
            "Days Left": days_left,
            "Progress (%)": progress,
            "Remaining Hours": round(remaining_hours, 1),
            "Required Hours/Day": round(required_daily_hours, 2),
            "Status": status
        })

    workload_status = (
        "Manageable"
        if total_required_daily_hours <= daily_hours
        else "Overloaded"
    )

    return {
        "subjects": insights,
        "total_daily_hours_required": round(
            total_required_daily_hours, 2
        ),
        "daily_hours_available": daily_hours,
        "workload_status": workload_status
    }
