from datetime import date

def calculate_days_remaining(exam_date: date) -> int:
    today = date.today()
    days = (exam_date - today).days
    return max(days, 0)

def subject_weights(difficulty: dict):
    weights = {}
    for subject, level in difficulty.items():
        if level == "high":
            weights[subject] = 0.5
        elif level == "medium":
            weights[subject] = 0.3
        else:
            weights[subject] = 0.2
    return weights

def daily_time_split(hours_per_day: float, weights: dict) -> dict:
    total_weight = sum(weights.values())

    split = {}
    used = 0

    keys = list(weights.keys())
    for i, subject in enumerate(keys):
        if i == len(keys) - 1:
            split[subject] = round(hours_per_day - used, 1)
        else:
            h = round(hours_per_day * (weights[subject] / total_weight), 1)
            split[subject] = h
            used += h

    return split
