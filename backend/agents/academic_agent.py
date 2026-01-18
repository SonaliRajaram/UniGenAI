from typing import AsyncGenerator
from backend.llm_client import call_llm_stream
from backend.rag.retriever import retrieve_context
from backend.study_planner.planner_logic import (
    calculate_days_remaining,
    subject_weights,
    daily_time_split
)
from backend.study_planner.planner_llm import generate_plan
from datetime import date, timedelta
import json
from backend.mock_interview.session import (
    start_session,
    get_current_question,
    advance_question,
    _sessions
)
from backend.mock_interview.questions import (
    DSA_QUESTIONS, ML_QUESTIONS, OS_QUESTIONS, DBMS_QUESTIONS, HR_QUESTIONS
)
from backend.mock_interview.evaluator import evaluate_answer
from backend.agents.agent_utils import is_feedback_message


def clear_session(user_id: str):
    if user_id in _sessions:
        del _sessions[user_id]


def is_greeting(message: str) -> bool:
    greetings = [
        "hello", "hi", "hey",
        "good morning", "good afternoon", "good evening",
        "how are you", "how r u"
    ]
    msg = message.lower()
    return any(greet in msg for greet in greetings)

def is_stop_interview_request(message: str) -> bool:
    msg = message.lower()
    
    # 1. Flexible check: Both "stop" and "interview" appear anywhere
    if "stop" in msg and "interview" in msg:
        return True
    
    # 2. Add common variants
    keywords = [
        "end interview", "quit interview", "exit interview", 
        "stop it", "terminate interview", "stop the interview"
    ]
    
    return any(k in msg for k in keywords)


def is_mock_interview_request(message: str) -> bool:
    keywords = ["mock interview", "interview practice", "take interview", "start mock interview"]
    return any(k in message.lower() for k in keywords)


def is_study_plan_request(message: str) -> bool:
    keywords = [
        "study plan", "study schedule", "exam plan",
        "prepare for exam", "how to study",
        "timetable", "revision plan",
        "make a plan", "study timetable"
    ]
    return any(k in message.lower() for k in keywords)


def is_academic_question(message: str) -> bool:
    academic_indicators = [
        "what is", "how", "explain", "define", "why", "difference",
        "example", "concept", "theory", "notes", "study",
        "state", "list", "advantages", "disadvantages",
        "from the pdf", "from the uploaded", "I have uploaded a pdf"
    ]
    msg = message.lower()
    return any(ind in msg for ind in academic_indicators)


# MAIN RESPONSE FUNCTION

async def respond(message: str, user_id: int) -> AsyncGenerator[str, None]:

    msg = message.strip()

    # STOP MOCK INTERVIEW 
    if is_stop_interview_request(msg):
        clear_session(user_id)
        for ch in "Mock interview stopped. How else can I assist you?":
            yield ch
        return
    
    # STUDY PLANNER
    if is_study_plan_request(msg):

        extraction_prompt = f"""
Extract the following details from the user's request.

Return ONLY a valid JSON object with these exact keys:
- "exam_date": string in YYYY-MM-DD format or null
- "hours_per_day": number or null

Do not include any other text.

User request:
{msg}
"""

        try:
            raw = ""
            async for token in call_llm_stream(extraction_prompt):
                raw += token
            data = json.loads(raw)
        except Exception:
            data = {}

        # Defaults
        raw_date = data.get("exam_date")
        if raw_date:
            try:
                exam_date = date.fromisoformat(raw_date)
            except ValueError:
                exam_date = date.today() + timedelta(days=14)
        else:
            exam_date = date.today() + timedelta(days=14)

        hours = data.get("hours_per_day") or 4

        subjects = ["DSA", "OS", "DBMS"]
        difficulty = {
            "DSA": "high",
            "OS": "medium",
            "DBMS": "medium"
        }

        days = calculate_days_remaining(exam_date)
        weights = subject_weights(difficulty)
        split = daily_time_split(hours, weights)
        plan = generate_plan(subjects, days, split)

        yield f"""
📚 Personalized Study Plan

🗓 Days Remaining: {days}

⏱ Daily Time Allocation:
{split}

📝 Study Schedule:
{plan}
"""

    # START MOCK INTERVIEW
    if is_mock_interview_request(msg):
        clear_session(user_id)
        yield (
            "🎯 Mock Interview Mode Started\n\n"
            "Choose a domain:\n"
            "• DSA\n"
            "• OS\n"
            "• DBMS\n"
            "• ML\n"
            "• HR\n\n"
            "Reply with the domain name."
        )
        return

    # DOMAIN SELECTION 
    domain_map = {
        "dsa": DSA_QUESTIONS,
        "os": OS_QUESTIONS,
        "dbms": DBMS_QUESTIONS,
        "ml": ML_QUESTIONS,
        "hr": HR_QUESTIONS
    }

    if msg.lower() in domain_map:
        q = start_session(user_id, msg.lower(), domain_map[msg.lower()])
        yield f"Interview Question 1:\n{q}"
        return

    # MOCK INTERVIEW ANSWER 
    if user_id in _sessions:
        question = get_current_question(user_id)
        yield "--- FEEDBACK ---\n"
        async for token in evaluate_answer(question, msg):
            yield token

        next_q = advance_question(user_id)
        if next_q:
            yield f"\n\nNext Question:\n{next_q}"
        else:
            clear_session(user_id)
            yield "\n\nMock Interview Completed!\nGreat job!"
        return

    # GREETING 
    if is_greeting(msg):
        clear_session(user_id)
        for ch in (
            "Hello! I'm your Academic Helper \n\n"
            "I can help you with:\n"
            "• Concept explanations (DSA, OS, DBMS, ML, etc.)\n"
            "• Mock interviews (DSA, OS, DBMS, HR)\n"
            "• Personalized study plans\n"
            "• Learning from uploaded notes (PDF/TXT)\n\n"
            "How can I assist you today?"
        ):
            yield ch
        return
    
    # HANDLE FEEDBACK
    if is_feedback_message(message):
        response = (
            "Thank you! I'm glad you liked it.\n\n"
            "If you'd like:\n"
            "• Changes or improvements\n"
            "• A different topic\n"
            "• A shorter or longer version\n\n"
            "Just let me know!"
        )
        for ch in response:
            yield ch
        return
    
    # ACADEMIC QUESTION (RAG) 
    context = retrieve_context(msg)

    prompt = f"""
You are an AI academic mentor.
Answer clearly and concisely using ONLY the given academic context.
Follow the user's instructions (number of points, format, etc.).

Context:
{context}

Question:
{msg}

Answer:
"""

    async for token in call_llm_stream(prompt):
        yield token
        
    
