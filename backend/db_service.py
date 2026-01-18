from backend.models import SessionLocal, User, InterviewSession, StudyPlan, ChatHistory
from datetime import datetime

# Export for use in other modules
__all__ = ['SessionLocal', 'create_user', 'save_interview', 'get_interview_history', 
           'get_interview_stats', 'save_study_plan', 'update_plan_completion', 
           'get_user_plans', 'save_chat', 'get_chat_history', 'delete_all_interviews', 
           'get_all_interview_data']

# USER FUNCTIONS
def create_user(username: str):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            user = User(username=username)
            db.add(user)
            db.commit()
            db.refresh(user)
        return {"id": user.id, "username": user.username}
    finally:
        db.close()


# INTERVIEW FUNCTIONS
def save_interview(user_id: int, domain: str, score: float, correct: int, total: int):
    db = SessionLocal()
    try:
        session = InterviewSession(
            user_id=user_id,
            domain=domain,
            score=score,
            questions_answered=total,
            correct_answers=correct
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return {"session_id": session.id, "score": session.score}
    finally:
        db.close()


def get_interview_history(user_id: int, domain: str = None):
    db = SessionLocal()
    try:
        query = db.query(InterviewSession).filter(InterviewSession.user_id == user_id)
        if domain:
            query = query.filter(InterviewSession.domain == domain)
        interviews = query.order_by(InterviewSession.created_at.desc()).all()
        return [
            {
                "id": i.id,
                "domain": i.domain,
                "score": i.score,
                "correct": i.correct_answers,
                "total": i.questions_answered,
                "date": i.created_at.isoformat() if i.created_at else None
            }
            for i in interviews
        ]
    finally:
        db.close()


def get_interview_stats(user_id: int):
    """Calculate average score, improvement, etc."""
    db = SessionLocal()
    try:
        interviews = db.query(InterviewSession).filter(
            InterviewSession.user_id == user_id
        ).order_by(InterviewSession.created_at).all()
        
        if not interviews:
            return {"total_interviews": 0, "avg_score": 0, "improvement": 0, "by_domain": {}}
        
        scores = [i.score for i in interviews]
        
        # Calculate domain stats
        stats_by_domain = {}
        for interview in interviews:
            if interview.domain not in stats_by_domain:
                stats_by_domain[interview.domain] = []
            stats_by_domain[interview.domain].append(interview.score)
        
        domain_stats = {domain: sum(scores_list)/len(scores_list) for domain, scores_list in stats_by_domain.items()}
        
        return {
            "total_interviews": len(interviews),
            "avg_score": round(sum(scores) / len(scores), 2),
            "last_score": scores[-1],
            "first_score": scores[0],
            "improvement": round(scores[-1] - scores[0], 2),
            "by_domain": domain_stats
        }
    finally:
        db.close()


# STUDY PLANNER FUNCTIONS
def save_study_plan(user_id: int, subject: str, topics: list, exam_date: str):
    db = SessionLocal()
    try:
        plan = StudyPlan(
            user_id=user_id,
            subject=subject,
            topics=topics,
            exam_date=datetime.fromisoformat(exam_date)
        )
        db.add(plan)
        db.commit()
        db.refresh(plan)
        return {"plan_id": plan.id, "subject": plan.subject}
    finally:
        db.close()


def update_plan_completion(plan_id: int, percentage: float):
    db = SessionLocal()
    try:
        plan = db.query(StudyPlan).filter(StudyPlan.id == plan_id).first()
        if plan:
            plan.completion_percentage = percentage
            db.commit()
            db.refresh(plan)
            return {"plan_id": plan.id, "completion": plan.completion_percentage}
        return None
    finally:
        db.close()


def get_user_plans(user_id: int):
    db = SessionLocal()
    try:
        plans = db.query(StudyPlan).filter(StudyPlan.user_id == user_id).all()
        return [
            {
                "id": p.id,
                "subject": p.subject,
                "completion": p.completion_percentage,
                "exam_date": p.exam_date.isoformat() if p.exam_date else None,
                "topics": p.topics
            }
            for p in plans
        ]
    finally:
        db.close()


# CHAT HISTORY FUNCTIONS
def save_chat(user_id: int, role: str, message: str, response: str):
    db = SessionLocal()
    try:
        chat = ChatHistory(
            user_id=user_id,
            role=role,
            message=message,
            response=response
        )
        db.add(chat)
        db.commit()
    finally:
        db.close()


def get_chat_history(user_id: int, limit: int = 50):
    db = SessionLocal()
    try:
        chats = db.query(ChatHistory).filter(
            ChatHistory.user_id == user_id
        ).order_by(ChatHistory.created_at.desc()).limit(limit).all()
        return [
            {
                "role": c.role,
                "message": c.message,
                "response": c.response,
                "date": c.created_at.isoformat() if c.created_at else None
            }
            for c in chats
        ]
    finally:
        db.close()


# DEBUG/ADMIN FUNCTIONS
def delete_all_interviews(user_id: int):
    """Delete all interviews for a user (for testing)"""
    db = SessionLocal()
    try:
        db.query(InterviewSession).filter(InterviewSession.user_id == user_id).delete()
        db.commit()
        return {"message": "All interviews deleted"}
    finally:
        db.close()


def get_all_interview_data(user_id: int):
    """Get raw interview data for debugging"""
    db = SessionLocal()
    try:
        interviews = db.query(InterviewSession).filter(InterviewSession.user_id == user_id).all()
        return [
            {
                "id": i.id,
                "user_id": i.user_id,
                "domain": i.domain,
                "score": i.score,
                "correct_answers": i.correct_answers,
                "questions_answered": i.questions_answered,
                "created_at": i.created_at.isoformat() if i.created_at else None
            }
            for i in interviews
        ]
    finally:
        db.close()