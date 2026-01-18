from backend.llm_client import call_llm_once # Ensure this is your streaming or non-streaming call

async def classify_intent(message: str) -> str:
    msg = message.lower()

    # HARD-CODED PRIORITY CHECK (Rule-First)
    # These keywords are UNIQUE to your Academic Agent functions.
    # Checking these first prevents the LLM from overthinking and picking 'content'.
    academic_commands = [
        "mock interview", "start interview", "practice interview", 
        "study plan", "study schedule", "timetable", "exam prep", "uploaded pdf",
        "dsa", "os", "dbms", "ml", "hr"  # Interview domain selections (NOT "general")
    ]
    
    if any(cmd in msg for cmd in academic_commands):
        return "academic"
    
    content_keywords = [
        "youtube", "script", "essay", "blog", "content",
        "caption", "speech", "article", "story", "creative"
    ]
    if any(kw in msg for kw in content_keywords):
        return "content"
    
    code_commands = ["python", "java", "c++", "debug", "error", "bug", "run code"]
    if any(cmd in msg for cmd in code_commands):
        return "code"

    # LLM-BASED REFINEMENT (The Classifier)
    prompt = f"""
You are an intent classifier for UniGenAI.

Classify the user message into EXACTLY one category:
- academic → definitions, theory, exams, subject doubt solving, RAG queries.
- content → creative writing like YouTube scripts, essays, or blogs.
- code → programming, debugging, algorithms.
- general → greetings and casual talk.

STRICT RULE:
- If the request is about practicing for an interview or making a study schedule, ALWAYS choose "academic".
- Only choose "content" for purely creative or entertainment-focused writing.

User Message: "{message}"
Category:"""

    try:
        # Note: call_llm_once returns a string, not a stream
        response = await call_llm_once(prompt)
        
        intent = response.lower().strip()

        # EXACT MATCHING (not substring matching) to avoid false positives
        if intent.startswith("academic") or "academic" == intent: return "academic"
        if intent.startswith("content") or "content" == intent: return "content"
        if intent.startswith("code") or "code" == intent: return "code"
        return "general"

    except Exception:
        return "general"