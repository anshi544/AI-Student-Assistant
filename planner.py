from datetime import date, datetime, timedelta


# ============================================================
# CONFIGURATION
# ============================================================

DIFFICULTY_SCORE = {
    "Easy": 1,
    "Medium": 2,
    "Hard": 3
}

MIN_STUDY_SESSION = 0.5
MAX_SUBJECTS_PER_DAY = 3
REVISION_INTERVAL = 6
REVISION_HOURS_RATIO = 0.15


# ============================================================
# DATE AND NUMBER HELPERS
# ============================================================

def _parse_deadline(deadline):
    """Convert a deadline into a date object."""

    if isinstance(deadline, datetime):
        return deadline.date()

    if isinstance(deadline, date):
        return deadline

    if isinstance(deadline, str):
        try:
            return datetime.strptime(
                deadline.strip(), "%Y-%m-%d"
            ).date()
        except ValueError:
            return date.today()

    return date.today()


def _safe_float(value, default=0):
    """Safely convert a value into a non-negative float."""

    try:
        return max(float(value), 0)
    except (ValueError, TypeError):
        return float(default)


def _safe_int(value, default=0):
    """Safely convert a value into a non-negative integer."""

    try:
        return max(int(value), 0)
    except (ValueError, TypeError):
        return int(default)


# ============================================================
# PRIORITY CALCULATION
# ============================================================

def calculate_priority(
    deadline,
    difficulty,
    remaining_topics=1,
    estimated_hours=1
):
    """
    Calculate subject priority.

    Priority considers:
    - Remaining workload
    - Subject difficulty
    - Time remaining before the deadline

    Higher values indicate higher priority.
    """

    deadline = _parse_deadline(deadline)

    days_left = (deadline - date.today()).days

    # Avoid division by zero and handle overdue subjects.
    effective_days = max(days_left, 1)

    difficulty_value = DIFFICULTY_SCORE.get(
        difficulty, 2
    )

    remaining_topics = _safe_int(remaining_topics)
    remaining_hours = _safe_float(estimated_hours)

    if remaining_topics == 0 or remaining_hours == 0:
        return 0

    # Workload is already expressed in remaining hours.
    # Do not multiply by remaining topics again.
    priority = (
        difficulty_value * remaining_hours
    ) / effective_days

    # Slight urgency multiplier for overdue subjects.
    if days_left < 0:
        priority *= 1.5

    return round(priority, 2)


# ============================================================
# SUBJECT PREPARATION
# ============================================================

def _prepare_subjects(subjects):
    """Validate subject information and calculate workload."""

    prepared = []

    for index, subject in enumerate(subjects):

        total_topics = _safe_int(
            subject.get("total_topics", 0)
        )

        completed_topics = min(
            _safe_int(subject.get("completed_topics", 0)),
            total_topics
        )

        remaining_topics = max(
            total_topics - completed_topics,
            0
        )

        estimated_hours = _safe_float(
            subject.get("estimated_hours", 0)
        )

        if total_topics > 0:
            remaining_hours = (
                estimated_hours
                * remaining_topics
                / total_topics
            )
        else:
            remaining_hours = 0

        deadline = _parse_deadline(
            subject.get("deadline", date.today())
        )

        difficulty = subject.get(
            "difficulty", "Medium"
        )

        if difficulty not in DIFFICULTY_SCORE:
            difficulty = "Medium"

        progress = (
            completed_topics / total_topics * 100
            if total_topics > 0
            else 0
        )

        priority = calculate_priority(
            deadline,
            difficulty,
            remaining_topics,
            remaining_hours
        )

        prepared.append({
            "name": str(
                subject.get("name", f"Subject {index + 1}")
            ).strip(),

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


# ============================================================
# SMART HOUR ALLOCATION
# ============================================================

def _allocate_hours(plans, daily_hours):
    """
    Distribute available hours according to priority.

    The allocation:
    - Prioritizes urgent subjects.
    - Considers remaining workload.
    - Does not allocate more hours than the subject needs.
    - Does not exceed the available daily study time.
    """

    daily_hours = _safe_float(daily_hours)

    active_subjects = [
        subject for subject in plans
        if subject["remaining_hours"] > 0
    ]

    for subject in plans:
        subject["recommended_hours"] = 0.0

    remaining_capacity = daily_hours

    # Work with a separate allocation dictionary.
    allocations = {
        subject["name"]: 0.0
        for subject in active_subjects
    }

    # Continue distributing until capacity is exhausted
    # or all remaining workload has been allocated.
    while remaining_capacity > 0.01 and active_subjects:

        total_priority = sum(
            max(subject["priority"], 0.01)
            for subject in active_subjects
        )

        distributed = 0

        for subject in list(active_subjects):

            weight = max(subject["priority"], 0.01)

            proposed = (
                remaining_capacity
                * weight
                / total_priority
            )

            available_work = (
                subject["remaining_hours"]
                - allocations[subject["name"]]
            )

            allocation = min(
                proposed,
                available_work
            )

            allocations[subject["name"]] += allocation

            remaining_capacity -= allocation
            distributed += allocation

            if (
                allocations[subject["name"]]
                >= subject["remaining_hours"] - 0.01
            ):
                active_subjects.remove(subject)

        if distributed <= 0.001:
            break

    for subject in plans:

        subject["recommended_hours"] = round(
            allocations.get(subject["name"], 0),
            2
        )

    return plans


# ============================================================
# PRIORITY-BASED STUDY PLAN
# ============================================================

def generate_plan(subjects, daily_hours):
    """Generate a priority-based study plan."""

    plans = _prepare_subjects(subjects)

    plans = _allocate_hours(
        plans,
        daily_hours
    )

    plans.sort(
        key=lambda subject: (
            subject["priority"],
            subject["remaining_hours"]
        ),
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


# ============================================================
# WEEKLY TIMETABLE
# ============================================================

def generate_weekly_plan(subjects, daily_hours, days=7):
    """
    Generate a practical weekly timetable.

    Features:
    - Distributes subjects across the week.
    - Updates remaining workload after each scheduled day.
    - Prioritizes urgent subjects.
    - Includes revision sessions periodically.
    """

    daily_hours = _safe_float(daily_hours)
    days = max(1, _safe_int(days, 7))

    plans = _prepare_subjects(subjects)

    active_subjects = [
        subject.copy()
        for subject in plans
        if subject["remaining_hours"] > 0
    ]

    if not active_subjects:
        return []

    weekly_plan = []

    for day_number in range(days):

        current_date = (
            date.today()
            + timedelta(days=day_number)
        )

        weekday = current_date.strftime("%A")

        # Recalculate priority as deadlines approach.
        for subject in active_subjects:

            subject["priority"] = calculate_priority(
                subject["deadline"],
                subject["difficulty"],
                subject["remaining_topics"],
                subject["remaining_hours"]
            )

        active_subjects.sort(
            key=lambda subject: (
                subject["priority"],
                subject["remaining_hours"]
            ),
            reverse=True
        )

        # Every sixth day includes a revision session.
        is_revision_day = (
            (day_number + 1) % REVISION_INTERVAL == 0
        )

        revision_hours = 0

        if is_revision_day and day_number > 0:
            revision_hours = round(
                daily_hours * REVISION_HOURS_RATIO,
                2
            )

        available_hours = max(
            daily_hours - revision_hours,
            0
        )

        daily_subjects = active_subjects[
            :MAX_SUBJECTS_PER_DAY
        ]

        if not daily_subjects:
            break

        total_priority = sum(
            max(subject["priority"], 0.01)
            for subject in daily_subjects
        )

        remaining_daily_hours = available_hours

        for index, subject in enumerate(daily_subjects):

            if remaining_daily_hours <= 0.01:
                break

            weight = max(subject["priority"], 0.01)

            if total_priority > 0:
                proposed_hours = (
                    available_hours
                    * weight
                    / total_priority
                )
            else:
                proposed_hours = (
                    available_hours
                    / len(daily_subjects)
                )

            # Ensure the last subject can use any leftover time.
            if index == len(daily_subjects) - 1:
                proposed_hours = remaining_daily_hours

            allocated_hours = min(
                proposed_hours,
                subject["remaining_hours"],
                remaining_daily_hours
            )

            allocated_hours = round(
                allocated_hours, 2
            )

            if allocated_hours <= 0:
                continue

            # Estimate topic completion proportionally.
            if subject["estimated_hours"] > 0:

                hours_per_topic = (
                    subject["estimated_hours"]
                    / max(subject["total_topics"], 1)
                )

                topics_completed_today = (
                    allocated_hours
                    / max(hours_per_topic, 0.01)
                )

                remaining_topics = max(
                    0,
                    subject["remaining_topics"]
                    - topics_completed_today
                )

            else:
                remaining_topics = subject["remaining_topics"]

            weekly_plan.append({
                "Day": weekday,
                "Date": current_date,
                "Subject": subject["name"],
                "Recommended Hours": allocated_hours,
                "Remaining Topics": round(
                    remaining_topics, 1
                ),
                "Progress (%)": subject["progress"]
            })

            # Update simulated remaining workload.
            subject["remaining_hours"] = round(
                max(
                    0,
                    subject["remaining_hours"]
                    - allocated_hours
                ),
                2
            )

            remaining_daily_hours -= allocated_hours

        # Add revision session without exceeding daily hours.
        if revision_hours > 0:

            weekly_plan.append({
                "Day": weekday,
                "Date": current_date,
                "Subject": "Revision",
                "Recommended Hours": revision_hours,
                "Remaining Topics": 0,
                "Progress (%)": 100
            })

        active_subjects = [
            subject for subject in active_subjects
            if subject["remaining_hours"] > 0.01
        ]

        if not active_subjects:
            break

    return weekly_plan


# ============================================================
# PERSONALIZED STUDY RECOMMENDATIONS
# ============================================================

def get_study_recommendations(subjects):
    """Generate personalized study recommendations."""

    recommendations = []

    plans = _prepare_subjects(subjects)

    if not plans:
        return [
            "Add subjects to generate study recommendations."
        ]

    for subject in plans:

        name = subject["name"]
        deadline = subject["deadline"]

        remaining_topics = subject["remaining_topics"]
        remaining_hours = subject["remaining_hours"]
        progress = subject["progress"]

        days_left = (
            deadline - date.today()
        ).days

        if remaining_topics == 0:

            recommendations.append(
                f"{name}: Subject completed. "
                "Focus on revision, mock tests and practice questions."
            )

        elif days_left < 0:

            recommendations.append(
                f"{name}: Deadline has passed. "
                "Create a recovery schedule and prioritize "
                "the most important remaining topics."
            )

        elif days_left == 0:

            recommendations.append(
                f"{name}: Deadline is today! "
                "Focus on high-weightage topics and quick revision."
            )

        elif days_left <= 3:

            recommendations.append(
                f"{name}: Urgent! Only {days_left} days remain. "
                "Prioritize important topics and practice questions."
            )

        elif days_left <= 7:

            recommendations.append(
                f"{name}: Deadline approaching. "
                "Increase consistency and avoid postponing study sessions."
            )

        elif remaining_hours > 0 and (
            remaining_hours / max(days_left, 1) > 3
        ):

            recommendations.append(
                f"{name}: Your remaining workload is high. "
                "Consider dividing the syllabus into smaller daily targets."
            )

        elif progress < 30:

            recommendations.append(
                f"{name}: Progress is below 30%. "
                "Start with foundational topics before moving "
                "to advanced concepts."
            )

        elif progress < 70:

            recommendations.append(
                f"{name}: Good progress. Maintain consistency "
                "and complete the remaining topics."
            )

        else:

            recommendations.append(
                f"{name}: Almost complete. Focus on revision, "
                "practice questions and weak areas."
            )

    recommendations.extend([
        "Use focused 25–50 minute study sessions with "
        "5–10 minute breaks.",

        "Start your study day with the highest-priority subject.",

        "Review completed topics regularly to improve retention.",

        "Keep some time available for practice questions "
        "and self-assessment."
    ])

    return recommendations


# ============================================================
# SMART INSIGHTS AND WORKLOAD ANALYSIS
# ============================================================

def generate_smart_insights(subjects, daily_hours):
    """
    Generate:
    - Deadline alerts
    - Subject progress analysis
    - Required daily study hours
    - Workload status
    """

    insights = []

    daily_hours = _safe_float(daily_hours)

    total_required_daily_hours = 0

    plans = _prepare_subjects(subjects)

    for subject in plans:

        remaining_topics = subject["remaining_topics"]
        remaining_hours = subject["remaining_hours"]
        deadline = subject["deadline"]

        days_left = (
            deadline - date.today()
        ).days

        if remaining_topics == 0:

            required_daily_hours = 0
            deadline_alert = "Completed"
            status = "Completed"

        else:

            effective_days = max(days_left, 1)

            required_daily_hours = (
                remaining_hours / effective_days
            )

            if days_left < 0:
                deadline_alert = "Overdue"

            elif days_left == 0:
                deadline_alert = "Due Today"

            elif days_left <= 3:
                deadline_alert = "Urgent"

            elif days_left <= 7:
                deadline_alert = "Approaching"

            else:
                deadline_alert = "On Schedule"

            if days_left <= 3:
                status = "Critical"

            elif required_daily_hours > daily_hours:
                status = "Needs Attention"

            else:
                status = "On Track"

        total_required_daily_hours += (
            required_daily_hours
        )

        insights.append({

            "Subject": subject["name"],

            "Deadline Alert": deadline_alert,

            "Days Left": days_left,

            "Progress (%)": subject["progress"],

            "Remaining Hours": round(
                remaining_hours, 1
            ),

            "Required Hours/Day": round(
                required_daily_hours, 2
            ),

            "Status": status
        })

    total_required_daily_hours = round(
        total_required_daily_hours, 2
    )

    if total_required_daily_hours <= daily_hours:

        workload_status = "Manageable"

    elif total_required_daily_hours <= daily_hours * 1.5:

        workload_status = "Moderately Overloaded"

    else:

        workload_status = "Overloaded"

    return {

        "subjects": insights,

        "total_daily_hours_required": (
            total_required_daily_hours
        ),

        "daily_hours_available": daily_hours,

        "workload_status": workload_status
    }
