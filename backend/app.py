from fastapi import FastAPI, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json, os

from backend.agents import (
    academic_agent,
    content_agent,
    code_agent,
    general_agent
)

from backend.rag.pdf_loader import load_pdf_text
from backend.rag.txt_loader import load_txt_text
from backend.rag.vector_store import add_documents

from backend.db_service import (
    create_user, save_interview, get_interview_history,
    get_interview_stats, save_study_plan, get_user_plans,
    save_chat, get_chat_history, update_plan_completion,
    delete_all_interviews, get_all_interview_data, SessionLocal
)
from backend.models import User, SessionLocal as SessionLocal_model

# APP INIT 

app = FastAPI(
    title="UniGenAI",
    description="Multi-Agent LLM System (Academic | Code | Content | General)"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/ui", StaticFiles(directory="backend/static", html=True), name="static")


# MODELS 

class ChatRequest(BaseModel):
    message: str
    forced_role: str | None = None

class InterviewResultRequest(BaseModel):
    user_id: int
    domain: str
    score: float
    correct: int
    total: int

class StudyPlanRequest(BaseModel):
    user_id: int
    subject: str
    topics: list
    exam_date: str

# FILE UPLOAD 

UPLOAD_DIR = "backend/rag/documents"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    path = os.path.join(UPLOAD_DIR, file.filename)

    with open(path, "wb") as f:
        f.write(await file.read())

    ext = os.path.splitext(file.filename)[1].lower()

    if ext == ".pdf":
        text = load_pdf_text(path)
    elif ext == ".txt":
        text = load_txt_text(path)
    else:
        return {"message": "Unsupported file type"}

    add_documents([text])
    return {"message": f"{file.filename} uploaded successfully"}


# CHAT (STREAMING) 
from backend.agents.agent_router import route_agent

@app.post("/chat")
async def chat(req: ChatRequest, user_id: int = Query(None)):
    
    # If no user_id provided, use default
    if user_id is None:
        user_id = 1
    
    agent_name = await route_agent(req.message, req.forced_role, user_id)

    async def event_generator():
        try:
            yield f"data: {json.dumps({'token': '', 'agent': agent_name})}\n\n"

            if agent_name == "academic":
                agent = academic_agent.respond
            elif agent_name == "code":
                agent = code_agent.respond
            elif agent_name == "content":
                agent = content_agent.respond
            else:
                agent = general_agent.respond

            full_response = ""
            async for token in agent(req.message, user_id):
                full_response += token
                yield f"data: {json.dumps({'token': token, 'agent': agent_name})}\n\n"

            save_chat(user_id, agent_name, req.message, full_response)
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

# USER ENDPOINTS
@app.post("/api/user/create")
async def create_user_endpoint(username: str):
    user = create_user(username)
    return user

@app.get("/api/user/{user_id}")
async def get_user(user_id: int):
    """Get user information by ID"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"error": "User not found"}
        return {"id": user.id, "username": user.username, "created_at": user.created_at.isoformat()}
    finally:
        db.close()

@app.get("/api/users/all")
async def get_all_users():
    """Get all users in the system"""
    db = SessionLocal()
    try:
        users = db.query(User).all()
        return [{"id": u.id, "username": u.username, "created_at": u.created_at.isoformat()} for u in users]
    finally:
        db.close()

# INTERVIEW ENDPOINTS
@app.post("/api/interview/save")
async def save_interview_result(req: InterviewResultRequest):
    result = save_interview(
        req.user_id, req.domain, req.score, req.correct, req.total
    )
    return result

@app.get("/api/interview/history/{user_id}")
async def get_user_interview_history(user_id: int, domain: str = None):
    interviews = get_interview_history(user_id, domain)
    return interviews
    
@app.get("/api/interview/stats/{user_id}")
async def get_user_stats(user_id: int):
    return get_interview_stats(user_id)

# STUDY PLANNER ENDPOINTS
@app.post("/api/planner/save")
async def save_planner(req: StudyPlanRequest):
    plan = save_study_plan(req.user_id, req.subject, req.topics, req.exam_date)
    return plan

@app.get("/api/planner/{user_id}")
async def get_plans(user_id: int):
    plans = get_user_plans(user_id)
    return plans
    
@app.put("/api/planner/{plan_id}/update")
async def update_planner(plan_id: int, completion: float):
    plan = update_plan_completion(plan_id, completion)
    return plan

# CHAT HISTORY ENDPOINTS
@app.get("/api/chat/history/{user_id}")
async def get_user_chat_history(user_id: int, limit: int = 50):
    chats = get_chat_history(user_id, limit)
    return chats

# DEBUG ENDPOINTS
@app.get("/api/debug/interviews/{user_id}")
async def debug_interviews(user_id: int):
    """Get raw interview data for debugging"""
    return get_all_interview_data(user_id)

@app.delete("/api/debug/interviews/{user_id}")
async def delete_interviews(user_id: int):
    """Delete all interviews for a user (testing only)"""
    return delete_all_interviews(user_id)