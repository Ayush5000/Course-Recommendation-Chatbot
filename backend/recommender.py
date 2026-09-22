
from rag import retrieve_courses


def recommend_courses(
    topic,
    budget="any",
    level="any",
    limit=6
):
    # Retrieve more candidates so filtering doesn't
    # unnecessarily remove all recommendations.
    candidates = retrieve_courses(
        query=topic,
        top_k=30
    )

    recommendations = []

    for course in candidates:
        pricing = course.get("pricing", "").lower()
        course_level = course.get("level", "").lower()

        # Filter by budget
        if budget.lower() == "free":
            if pricing not in ["free", "free to audit"]:
                continue

        elif budget.lower() == "paid":
            if pricing != "paid":
                continue

        # Filter by skill level
        if level.lower() != "any":
            if course_level != level.lower():
                continue

        recommendations.append(course)

        if len(recommendations) >= limit:
            break

    return recommendations