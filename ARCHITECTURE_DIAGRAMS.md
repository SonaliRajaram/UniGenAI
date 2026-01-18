# UniGenAI System Architecture Diagrams

## 1. USER CREATION & SESSION FLOW

```
┌─────────────────────────────────────────────────────────────────┐
│                    FIRST TIME USER VISIT                         │
└─────────────────────────────────────────────────────────────────┘

    Browser Opens: localhost:8000/ui
           ↓
    ┌──────────────────────────────────┐
    │ script.js runs on page load      │
    │ DOMContentLoaded event triggered │
    └──────────────────────────────────┘
           ↓
    ┌──────────────────────────────────┐
    │ initializeUser()                 │
    └──────────────────────────────────┘
           ↓
    localStorage has 'unigenai_user'?
           │
       NO ├─────────→ Generate username: "user_1705424400000"
           │                    ↓
           │          Call: POST /api/user/create?username=user_...
           │                    ↓
           │          Backend creates user in DB
           │          Returns: {id: 1, username: "user_1705424400000"}
           │                    ↓
           │          localStorage.setItem('unigenai_user', {id, username})
           │
       YES ├─────────→ Load existing user from localStorage
           │          currentUserId = stored_id
           ↓
    ┌──────────────────────────────────┐
    │ User is now ready for chat       │
    │ currentUserId = 1                │
    │ currentUsername = "user_1705..." │
    └──────────────────────────────────┘
```

---

## 2. CHAT MESSAGE FLOW

```
┌─────────────────────────────────────────────────────────────────┐
│                    SEND MESSAGE WORKFLOW                         │
└─────────────────────────────────────────────────────────────────┘

    User Types: "What is DSA?"
    Presses Enter or Clicks Send
           ↓
    ┌──────────────────────────────────┐
    │ sendMessage()                    │
    │ • Gets user_id from memory       │
    │ • Creates ChatRequest            │
    │ • Shows message bubble in UI     │
    └──────────────────────────────────┘
           ↓
    ┌──────────────────────────────────┐
    │ fetch(/chat?user_id=1, {         │
    │   method: "POST",                │
    │   body: JSON {                   │
    │     message: "What is DSA?",     │
    │     forced_role: "academic"      │
    │   }                              │
    │ })                               │
    └──────────────────────────────────┘
           ↓
    ╔═════════════════════════════════════════════════════════════╗
    ║                      BACKEND PROCESSING                     ║
    ╠═════════════════════════════════════════════════════════════╣
    ║                                                               ║
    ║  @app.post("/chat")                                          ║
    ║  async def chat(req: ChatRequest, user_id: int):            ║
    ║    • Receives user_id=1 (REQUIRED)                           ║
    ║    • Parses request body                                     ║
    ║           ↓                                                   ║
    ║    agent_name = await route_agent(                          ║
    ║      req.message,                                            ║
    ║      req.forced_role,                                        ║
    ║      user_id=1                                               ║
    ║    )                                                          ║
    ║    • Returns: "academic"                                     ║
    ║           ↓                                                   ║
    ║    agent = academic_agent.respond                            ║
    ║           ↓                                                   ║
    ║    async for token in agent(                                 ║
    ║      req.message,                                            ║
    ║      user_id=1                                               ║
    ║    ):                                                         ║
    ║      yield f"data: {json.dumps({token, agent})}"             ║
    ║           ↓                                                   ║
    ║    Agent processes message and streams response              ║
    ║           ↓                                                   ║
    ║    After response complete:                                  ║
    ║    save_chat(                                                ║
    ║      user_id=1,                                              ║
    ║      role="academic",                                        ║
    ║      message="What is DSA?",                                 ║
    ║      response="<full response>"                              ║
    ║    )                                                          ║
    ║           ↓                                                   ║
    ║    ╔══════════════════════════════════════╗                  ║
    ║    ║     DATABASE: INSERT chat_history    ║                  ║
    ║    ║     user_id: 1                       ║                  ║
    ║    ║     role: "academic"                 ║                  ║
    ║    ║     message: "What is DSA?"          ║                  ║
    ║    ║     response: "..."                  ║                  ║
    ║    ║     created_at: NOW                  ║                  ║
    ║    ╚══════════════════════════════════════╝                  ║
    ║                                                               ║
    ╚═════════════════════════════════════════════════════════════╝
           ↓
    Frontend receives streamed response
           ↓
    ┌──────────────────────────────────┐
    │ Display bot message bubble       │
    │ Accumulate full_response         │
    │ Text updates in real-time        │
    └──────────────────────────────────┘
           ↓
    Response complete
           ↓
    speak(fullResponse)  // Text-to-speech if enabled
           ↓
    Chat visible in UI ✓
    Chat in database ✓
```

---

## 3. INTERVIEW FLOW

```
┌─────────────────────────────────────────────────────────────────┐
│                  MOCK INTERVIEW WORKFLOW                         │
└─────────────────────────────────────────────────────────────────┘

    User: "start mock interview"
           ↓
    send_chat("start mock interview", user_id=1)
           ↓
    Backend receives in academic_agent
           ↓
    academic_agent.respond("start mock interview", user_id=1):
    • is_mock_interview_request() → True
    • clear_session(user_id=1)  ← Clear old session
    • Returns interview prompt
           ↓
    User chooses: "DSA"
           ↓
    send_chat("DSA", user_id=1)
           ↓
    Backend:
    • start_session(user_id=1, "dsa", questions[...])
    • _sessions[1] = {domain: "dsa", questions: [...], ...}
    • Returns Question 1
           ↓
    User: "Answer to Question 1"
           ↓
    send_chat("Answer...", user_id=1)
           ↓
    Backend:
    • Check: if 1 in _sessions  → True
    • Evaluate answer
    • Advance to next question
    • Save as chat entry (for history)
           ↓
    ... repeat for all questions ...
           ↓
    User: "stop interview"
           ↓
    send_chat("stop interview", user_id=1)
           ↓
    Backend:
    • is_stop_interview_request() → True
    • end_interview(user_id=1):
      ├─ Calculate score = 85.0
      ├─ correct_answers = 17
      ├─ total_questions = 20
      └─ save_interview(
          user_id=1,
          domain="DSA",
          score=85.0,
          correct=17,
          total=20
        )
           ↓
    ╔═════════════════════════════════════════╗
    ║  DATABASE: INSERT interview_sessions    ║
    ║  user_id: 1                             ║
    ║  domain: "DSA"                          ║
    ║  score: 85.0                            ║
    ║  correct_answers: 17                    ║
    ║  questions_answered: 20                 ║
    ║  created_at: NOW                        ║
    ╚═════════════════════════════════════════╝
           ↓
    clear_session(user_id=1)
           ↓
    Show completion message
           ↓
    Interview data is now in database ✓
```

---

## 4. METRICS CALCULATION FLOW

```
┌─────────────────────────────────────────────────────────────────┐
│              INTERVIEW STATISTICS CALCULATION                    │
└─────────────────────────────────────────────────────────────────┘

    User: GET /api/interview/stats/1
           ↓
    Backend: get_interview_stats(user_id=1)
           ↓
    Query: SELECT * FROM interview_sessions WHERE user_id = 1
           ↓
    Results:
    ┌─────────────────────────────────────┐
    │ Interview 1:                        │
    │ • Domain: DSA                       │
    │ • Score: 75.0                       │
    │ • Date: 2026-01-17 10:00:00        │
    │                                     │
    │ Interview 2:                        │
    │ • Domain: DSA                       │
    │ • Score: 82.0                       │
    │ • Date: 2026-01-17 11:00:00        │
    │                                     │
    │ Interview 3:                        │
    │ • Domain: OS                        │
    │ • Score: 78.5                       │
    │ • Date: 2026-01-17 12:00:00        │
    └─────────────────────────────────────┘
           ↓
    Calculate Metrics:
    ┌──────────────────────────────┐
    │ total_interviews = 3         │
    │                              │
    │ scores = [75.0, 82.0, 78.5]  │
    │ avg_score = 78.5             │
    │                              │
    │ last_score = 78.5            │
    │ first_score = 75.0           │
    │ improvement = 3.5            │
    │                              │
    │ by_domain:                   │
    │ • DSA: (75.0 + 82.0) / 2 = 78.5    │
    │ • OS: 78.5                   │
    └──────────────────────────────┘
           ↓
    Return JSON:
    {
      "total_interviews": 3,
      "avg_score": 78.5,
      "last_score": 78.5,
      "first_score": 75.0,
      "improvement": 3.5,
      "by_domain": {
        "DSA": 78.5,
        "OS": 78.5
      }
    }
```

---

## 5. DATA ISOLATION - MULTIPLE USERS

```
┌─────────────────────────────────────────────────────────────────┐
│             MULTI-USER DATA ISOLATION MODEL                      │
└─────────────────────────────────────────────────────────────────┘

    Browser Window 1                Browser Window 2
    (Regular Mode)                  (Private Window)
           │                               │
    localStorage:                   localStorage:
    unigenai_user: {                unigenai_user: {
      id: 1,                          id: 2,
      username: "user_1705..."        username: "user_1705..."
    }                               }
           │                               │
        user_id=1                      user_id=2
           │                               │
           ├─ POST /chat?user_id=1        │
           │  "What is DSA?"              │
           │  ↓                           │
           │  Backend saves with user_id=1
           │  ↓                           │
           │  DATABASE:                   │
           │  chat_history WHERE          │
           │  user_id=1                   │
           │                              ├─ POST /chat?user_id=2
           │                              │  "What is OOPS?"
           │                              │  ↓
           │                              │  Backend saves with user_id=2
           │                              │  ↓
           │                              │  DATABASE:
           │                              │  chat_history WHERE
           │                              │  user_id=2
           │                              │
           ├─ GET /api/chat/history/1    │
           │  Returns: Only user_id=1 chats  │
           │           ["What is DSA?"]   │
           │                              ├─ GET /api/chat/history/2
           │                              │  Returns: Only user_id=2 chats
           │                              │           ["What is OOPS?"]
           │                              │
           ├─ GET /api/interview/stats/1 │
           │  DSA: 85.0                   │
           │  OS: 0                       │
           │                              ├─ GET /api/interview/stats/2
           │                              │  DSA: 0
           │                              │  OOPS: 90.0
           │                              │
    ✓ Complete Isolation ◄─────────► ✓ Complete Isolation

    Key Points:
    • Each browser has separate localStorage
    • Each user_id filters all queries
    • No data leakage between users
    • Clearing localStorage creates new user
```

---

## 6. DATABASE SCHEMA

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATABASE RELATIONSHIPS                        │
└─────────────────────────────────────────────────────────────────┘

    ┌──────────────────┐
    │      USERS       │
    ├──────────────────┤
    │ id (PK) ───────────┐
    │ username          │ 1:Many
    │ created_at        │  │
    └──────────────────┘  │
           ▲              │
           │              │
           │     ┌────────┴──────────────────┐
           │     │                           │
           │     ▼                           ▼
    ┌──────────────────────┐    ┌────────────────────────┐
    │   CHAT_HISTORY       │    │ INTERVIEW_SESSIONS     │
    ├──────────────────────┤    ├────────────────────────┤
    │ id (PK)              │    │ id (PK)                │
    │ user_id (FK) ───────────  │ user_id (FK) ──────────
    │ role                 │    │ domain                 │
    │ message              │    │ score                  │
    │ response             │    │ correct_answers        │
    │ created_at           │    │ questions_answered     │
    └──────────────────────┘    │ created_at             │
                                └────────────────────────┘

    ┌────────────────────────┐
    │    STUDY_PLANS         │
    ├────────────────────────┤
    │ id (PK)                │
    │ user_id (FK) ──────┐   │
    │ subject            │   │
    │ topics (JSON)      │   │
    │ exam_date          │   │
    │ completion_%       │   │
    │ created_at         │   │
    └────────────────────┘   │
                 ▲            │
                 │            │
                 └────────────┘
                 (1:Many from USERS)

    Query Examples:
    • Get user 1's chats:
      SELECT * FROM chat_history WHERE user_id = 1;

    • Get user 1's stats:
      SELECT AVG(score) FROM interview_sessions WHERE user_id = 1;

    • Get user 1's plans:
      SELECT * FROM study_plans WHERE user_id = 1;
```

---

## 7. REQUEST/RESPONSE CYCLE

```
┌─────────────────────────────────────────────────────────────────┐
│              HTTP REQUEST/RESPONSE LIFECYCLE                     │
└─────────────────────────────────────────────────────────────────┘

SCENARIO: User sends chat message "What is a LinkedList?"

┌─ Browser (Frontend) ────────────────────────────────────────────┐
│                                                                  │
│  currentUserId = 1 (from localStorage)                          │
│  message = "What is a LinkedList?"                              │
│  selectedRole = "academic"                                      │
│                                                                  │
│  REQUEST:                                                       │
│  POST /chat?user_id=1 HTTP/1.1                                  │
│  Content-Type: application/json                                 │
│  Accept: text/event-stream                                      │
│                                                                  │
│  {                                                              │
│    "message": "What is a LinkedList?",                          │
│    "forced_role": "academic"                                    │
│  }                                                              │
└────────────────────────────────────────────────────────────────┘
                            ↓
┌─ Server (Backend) ─────────────────────────────────────────────┐
│                                                                  │
│  @app.post("/chat")                                             │
│  async def chat(req: ChatRequest, user_id: int):               │
│    # user_id = 1 ✓ EXTRACTED FROM QUERY PARAM                  │
│    # req.message = "What is a LinkedList?"                     │
│    # req.forced_role = "academic"                               │
│                                                                  │
│  agent_name = await route_agent(                                │
│    req.message,                                                 │
│    req.forced_role,                                             │
│    user_id=1                                                    │
│  )  → Returns "academic"                                        │
│                                                                  │
│  agent = academic_agent.respond                                 │
│                                                                  │
│  RESPONSE (Server-Sent Events):                                 │
│  HTTP/1.1 200 OK                                                │
│  Content-Type: text/event-stream                                │
│  Cache-Control: no-cache                                        │
│  Connection: keep-alive                                         │
│                                                                  │
│  data: {"token": "", "agent": "academic"}                       │
│  data: {"token": "A", "agent": "academic"}                      │
│  data: {"token": " LinkedList", "agent": "academic"}            │
│  data: {"token": " is", "agent": "academic"}                    │
│  ...                                                             │
│  data: {"token": ".", "agent": "academic"}                      │
│                                                                  │
│  [Connection ends, then]                                        │
│                                                                  │
│  save_chat(                                                      │
│    user_id=1,                                                   │
│    role="academic",                                             │
│    message="What is a LinkedList?",                             │
│    response="A LinkedList is..."                                │
│  )                                                              │
│  → INSERT into database ✓                                       │
└────────────────────────────────────────────────────────────────┘
                            ↓
┌─ Browser (Frontend) ────────────────────────────────────────────┐
│                                                                  │
│  Receiving streamed response:                                   │
│  ├─ Read events from stream                                     │
│  ├─ Parse JSON from each "data:" line                           │
│  ├─ Accumulate tokens in fullResponse                           │
│  ├─ Update UI with new tokens in real-time                      │
│  ├─ Call speak(fullResponse) if voice enabled                   │
│  ├─ Message visible in chat bubble ✓                            │
│  └─ Message persisted in database ✓                             │
│                                                                  │
└────────────────────────────────────────────────────────────────┘
```

---

## 8. COMPLETE USER LIFECYCLE

```
┌─────────────────────────────────────────────────────────────────┐
│              COMPLETE USER LIFECYCLE IN SYSTEM                   │
└─────────────────────────────────────────────────────────────────┘

TIME →

T₀: User Opens App
├─ Browser loads HTML/CSS/JS
├─ script.js loads
└─ DOMContentLoaded event fires
         ↓
T₁: Initialize User
├─ Check localStorage
├─ Not found
├─ Create new user: "user_1705424400000"
├─ Store in localStorage
├─ currentUserId = 1
└─ UI ready
         ↓
T₂: User Selects Agent
├─ Click "Academic Helper"
├─ Chat interface shows
└─ Ready to send messages
         ↓
T₃: First Chat Message (10:30 AM)
├─ Type: "What is DSA?"
├─ Send: POST /chat?user_id=1
├─ Response streamed and displayed
├─ Saved: chat_history{user_id:1, message:"What is DSA?", ...}
└─ Visible in UI
         ↓
T₄: More Chat Messages (10:35-11:00 AM)
├─ Multiple academic questions
├─ Each saved independently
├─ User can see history
└─ All linked to user_id=1
         ↓
T₅: Start Mock Interview (11:05 AM)
├─ Type: "start mock interview"
├─ Choose domain: "DSA"
├─ Session created: _sessions[1] = {...}
└─ Question 1 displayed
         ↓
T₆: Answer Interview Questions (11:05-11:25 AM)
├─ Answer 20 DSA questions
├─ Each answer saved as chat
├─ Feedback provided
├─ Progress tracked in memory
└─ Interview ongoing
         ↓
T₇: End Interview (11:26 AM)
├─ Type: "stop interview"
├─ Calculate score = 85.0 (17/20 correct)
├─ Save: interview_sessions{user_id:1, domain:"DSA", score:85.0}
├─ Clear session: _sessions.delete(1)
└─ Completion message shown
         ↓
T₈: View Statistics
├─ GET /api/interview/stats/1
├─ Calculate from database
├─ Return:
│  {
│    total_interviews: 1,
│    avg_score: 85.0,
│    improvement: 0.0,
│    by_domain: {DSA: 85.0}
│  }
└─ Display on dashboard
         ↓
T₉: Create Study Plan (11:30 AM)
├─ Type: "Create a study plan..."
├─ Save: study_plans{user_id:1, subject:"DSA", ...}
├─ Plan visible on dashboard
└─ Can track completion
         ↓
T₁₀: User Refreshes Page (11:35 AM)
├─ Page reloads
├─ Check localStorage
├─ Found: user_id=1 (persistent!)
├─ Load user 1
├─ Access all previous data
│  ├─ Chat history (from DB)
│  ├─ Interview results (from DB)
│  └─ Study plans (from DB)
└─ All data still available
         ↓
T₁₁: Take Another Interview (12:00 PM)
├─ Same user_id=1
├─ Start: DSA interview again
├─ Complete with score=88.0
├─ Save: interview_sessions{user_id:1, domain:"DSA", score:88.0}
└─ Now have 2 interviews
         ↓
T₁₂: View Updated Statistics
├─ GET /api/interview/stats/1
├─ Now shows:
│  {
│    total_interviews: 2,
│    avg_score: 86.5 (85+88)/2,
│    improvement: 3.0 (88-85),
│    by_domain: {DSA: 86.5}
│  }
└─ Improvement tracked!
         ↓
T₁₃: Different Device (Another Browser)
├─ Open in Chrome (same device)
├─ Check localStorage: NOT FOUND (different browser)
├─ Create new user: "user_1705424500000"
├─ Store new localStorage
├─ currentUserId = 2
├─ All previous data for user_id=1 remains in DB
└─ User_id=2 starts fresh
         ↓
T₁₄: Complete Isolation Verified
├─ User 1 data: 2 interviews, 5+ chats, 1 plan
├─ User 2 data: 0 interviews, 0 chats, 0 plans
├─ No cross-contamination
├─ No data loss
└─ System working perfectly ✓
```

---

This visual representation shows how the entire system works end-to-end with proper user isolation and persistent data storage.
