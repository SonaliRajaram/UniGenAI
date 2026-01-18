
from backend.db_service import save_interview

async def end_interview(session_id: str, user_id: int):
    """End interview and save results"""
    session = get_session(session_id)
    
    score = calculate_score(session)
    correct = count_correct_answers(session)
    total = len(session.questions)
    
    # SAVE TO DATABASE
    save_interview(user_id, session.domain, score, correct, total)
    
    return {
        "score": score,
        "correct": correct,
        "total": total,
        "feedback": generate_feedback(score)
    }
    
_sessions = {}

def start_session(user_id: str, domain: str, questions: list):
    """Initializes a new interview session safely."""
    if not questions:
        return None
        
    _sessions[user_id] = {
        "domain": domain,
        "questions": questions,
        "current_index": 0,
        "current_question": questions[0],
        "is_active": True
    }
    return questions[0]

def is_session_active(user_id: str) -> bool:
    """Helper to check if the user is currently in an interview."""
    return user_id in _sessions and _sessions[user_id].get("is_active", False)

def get_current_question(user_id: str):
    """Returns the current question without moving the index."""
    session = _sessions.get(user_id)
    if not session:
        return None
    return session.get("current_question")

def advance_question(user_id: str):
    """Moves to the next question and returns it, or returns None if finished."""
    session = _sessions.get(user_id)
    if not session:
        return None

    session["current_index"] += 1

    # Check if we reached the end of the list
    if session["current_index"] >= len(session["questions"]):
        session["is_active"] = False
        return None

    next_q = session["questions"][session["current_index"]]
    session["current_question"] = next_q
    return next_q

def clear_session(user_id: str):
    """Cleanly deletes the session data."""
    if user_id in _sessions:
        del _sessions[user_id]

def get_session(session_id: str):
    """Retrieve a session by ID."""
    session = _sessions.get(session_id)
    if not session:
        raise ValueError(f"Session {session_id} not found")
    return session

def count_correct_answers(session: dict) -> int:
    """Count the number of correct answers in a session."""
    if "answers" not in session:
        return 0
    correct_count = 0
    for answer in session.get("answers", []):
        if answer.get("is_correct", False):
            correct_count += 1
    return correct_count

def calculate_score(session: dict) -> float:
    """Calculate interview score as a percentage."""
    total_questions = len(session.get("questions", []))
    if total_questions == 0:
        return 0.0
    correct_answers = count_correct_answers(session)
    score = (correct_answers / total_questions) * 100
    return round(score, 2)

def generate_feedback(score: float) -> str:
    """Generate feedback based on the interview score."""
    if score >= 90:
        return "Excellent! Outstanding performance. Keep up the great work!"
    elif score >= 80:
        return "Great job! You demonstrated solid knowledge. Well done!"
    elif score >= 70:
        return "Good effort! You have a solid understanding. Review weaker areas."
    elif score >= 60:
        return "Fair performance. Focus on strengthening key concepts."
    else:
        return "Needs improvement. Study the material more thoroughly and try again."