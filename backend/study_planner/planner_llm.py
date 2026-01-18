from backend.study_planner.topics import DSA_TOPICS, OS_TOPICS, DBMS_TOPICS

def generate_plan(subjects, days, daily_split):
    plan = []

    for day in range(days):
        dsa = DSA_TOPICS[day % len(DSA_TOPICS)]
        os = OS_TOPICS[day % len(OS_TOPICS)]
        dbms = DBMS_TOPICS[day % len(DBMS_TOPICS)]

        plan.append(
            f"""Day {day + 1}:
- DSA ({daily_split['DSA']} hrs): {dsa} + coding practice
- OS ({daily_split['OS']} hrs): {os} + concept notes
- DBMS ({daily_split['DBMS']} hrs): {dbms} + SQL practice
"""
        )

    return "\n".join(plan)