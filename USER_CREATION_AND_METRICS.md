# User Creation, Chat History, and Metrics Calculation - Complete Trace

## ❌ NO - User is NOT Created Each Time You Visit

**Reality**: User is created **ONLY on first visit**, then reused.

---

### 1. USER CREATION FLOW (First Visit Only)

**Location**: [backend/static/script.js](backend/static/script.js) - Lines 7-27

```javascript
// Line 7-9: Check localStorage on page load
async function initializeUser() {
    const stored = localStorage.getItem("unigenai_user");  // LINE 9
    
    // Line 11-14: If user EXISTS - reuse it
    if (stored) {
        const user = JSON.parse(stored);
        currentUserId = user.id;  // LINE 13 - REUSE EXISTING ID
        // Don't create new user
    } else {
        // Line 16-20: Only if NOT stored - create NEW user
        const username = `user_${Date.now()}`;  // LINE 17 - Unique timestamp
        await createNewUser(username);  // LINE 19 - Create once
    }
}
```

**What happens**:
```
First Visit:
├─ localStorage empty
├─ Create user: "user_1705424400000"
├─ Store in localStorage
└─ Use that ID for all requests

Second Visit (Same Day):
├─ localStorage has user
├─ Load user_id from localStorage
├─ NO new user created
└─ Use same ID for all requests

Different Browser/Private Window:
├─ localStorage is separate
├─ Treated as new user
└─ Creates new user for that browser
```

**Code Evidence**:
```javascript
// Line 31-53: createNewUser() function
async function createNewUser(username) {
    // LINE 36: POST /api/user/create
    const response = await fetch(`/api/user/create?username=${username}`, {
        method: "POST"
    });
    
    // LINE 47: Store in localStorage
    localStorage.setItem("unigenai_user", JSON.stringify({
        id: user.id,
        username: user.username
    }));
    
    // LINE 50: Creates only if NOT found
    console.log(`✓ Created new user: ${username} (ID: ${currentUserId})`);
}
```

---

## 💬 CHAT HISTORY STORAGE - YES, Always Stored

**Every message is automatically saved** after response completes.

### Location: [backend/app.py](backend/app.py) - Lines 94-122

```python
# LINE 94-95: Chat endpoint receives user_id
@app.post("/chat")
async def chat(req: ChatRequest, user_id: int = Query(None)):
    
    # LINE 100: Get agent name based on message
    agent_name = await route_agent(req.message, req.forced_role, user_id)

    # LINE 102-103: Start streaming generator
    async def event_generator():
        # LINE 114-115: Collect full response
        full_response = ""
        async for token in agent(req.message, user_id):
            full_response += token
            yield f"data: {json.dumps({'token': token, 'agent': agent_name})}\n\n"

        # LINE 121: SAVE CHAT - Always executed
        save_chat(user_id, agent_name, req.message, full_response)
```

### Where Saved: [backend/db_service.py](backend/db_service.py) - Lines 162-174

```python
# LINE 162-174: save_chat function
def save_chat(user_id: int, role: str, message: str, response: str):
    db = SessionLocal()
    try:
        # LINE 166-170: Create ChatHistory record
        chat = ChatHistory(
            user_id=user_id,        # LINE 167: Your user ID
            role=role,              # LINE 168: Which agent (academic/code/content/general)
            message=message,        # LINE 169: Your message
            response=response       # LINE 170: AI response
        )
        db.add(chat)
        db.commit()  # LINE 172: Save to database
    finally:
        db.close()
```

**What Gets Saved**:
```
Each chat record stores:
├─ user_id (INTEGER) - Identifies you
├─ role (STRING) - Which agent responded (academic/code/content/general)
├─ message (STRING) - Your message
├─ response (STRING) - AI's full response
└─ created_at (DATETIME) - When it happened (auto-added)
```

---

## 📊 METRICS CALCULATION - From Interview Sessions, NOT Chat History

**Important**: Metrics are calculated from **interview_sessions table**, NOT from chat_history.

### Location: [backend/db_service.py](backend/db_service.py) - Lines 57-90

```python
# LINE 57-90: get_interview_stats function
def get_interview_stats(user_id: int):
    """Calculate average score, improvement, etc."""
    db = SessionLocal()
    try:
        # LINE 60-61: Get all interviews for user, sorted by date
        interviews = db.query(InterviewSession).filter(
            InterviewSession.user_id == user_id
        ).order_by(InterviewSession.created_at).all()
        
        # LINE 63-64: If no interviews, return zeros
        if not interviews:
            return {"total_interviews": 0, "avg_score": 0, "improvement": 0, "by_domain": {}}
        
        # LINE 66: Extract all scores
        scores = [i.score for i in interviews]  # LINE 66: [85.0, 75.0, 80.0, ...]
        
        # LINE 68-72: Calculate by-domain stats
        stats_by_domain = {}
        for interview in interviews:
            if interview.domain not in stats_by_domain:
                stats_by_domain[interview.domain] = []
            stats_by_domain[interview.domain].append(interview.score)
        
        # LINE 73: Average score per domain
        domain_stats = {
            domain: sum(scores_list)/len(scores_list) 
            for domain, scores_list in stats_by_domain.items()
        }
        
        # LINE 75-80: Return calculated metrics
        return {
            "total_interviews": len(interviews),              # LINE 76: Count of interviews
            "avg_score": round(sum(scores) / len(scores), 2), # LINE 77: ⭐ FORMULA 1
            "last_score": scores[-1],                          # LINE 78: Latest attempt
            "first_score": scores[0],                          # LINE 79: First attempt
            "improvement": round(scores[-1] - scores[0], 2),   # LINE 80: ⭐ FORMULA 2
            "by_domain": domain_stats                          # LINE 81: ⭐ FORMULA 3
        }
```

---

## ⭐ METRICS FORMULAS (Exact Code)

### Formula 1: Average Score
**Line 77** in [backend/db_service.py](backend/db_service.py)

```python
"avg_score": round(sum(scores) / len(scores), 2)
```

**Calculation**:
```
scores = [85.0, 75.0, 80.0]
avg_score = (85.0 + 75.0 + 80.0) / 3 = 240.0 / 3 = 80.0
```

**Formula**: `Average = (Sum of all scores) / (Total count of interviews)`

---

### Formula 2: Improvement
**Line 80** in [backend/db_service.py](backend/db_service.py)

```python
"improvement": round(scores[-1] - scores[0], 2)
```

**Calculation**:
```
scores = [85.0, 75.0, 80.0]
improvement = 80.0 - 85.0 = -5.0  (decreased)

OR

scores = [65.0, 70.0, 85.0]
improvement = 85.0 - 65.0 = 20.0  (improved by 20%)
```

**Formula**: `Improvement = (Last score) - (First score)`

---

### Formula 3: Domain-wise Average
**Line 73** in [backend/db_service.py](backend/db_service.py)

```python
domain_stats = {
    domain: sum(scores_list)/len(scores_list) 
    for domain, scores_list in stats_by_domain.items()
}
```

**Calculation Example**:
```
Interviews taken:
├─ DSA: 85.0
├─ DSA: 75.0
├─ OS: 80.0
└─ OS: 90.0

stats_by_domain:
├─ "DSA": [85.0, 75.0] → average = 80.0
└─ "OS": [80.0, 90.0] → average = 85.0

Result: {"DSA": 80.0, "OS": 85.0}
```

**Formula**: `Domain Average = (Sum of scores in domain) / (Count in domain)`

---

## 📍 Complete Flow Diagram

```
VISIT SITE
    ↓
┌──────────────────────────────────────────────┐
│ script.js: initializeUser() [LINE 7-27]      │
├──────────────────────────────────────────────┤
│ Check localStorage                           │
│ ├─ Has user_id? YES → REUSE (don't create)  │
│ └─ No user_id?  NO  → CREATE once            │
│                                              │
│ IF creating:                                 │
│ ├─ POST /api/user/create?username=...       │
│ ├─ app.py: create_user_endpoint() [LINE 136]│
│ ├─ db_service.py: create_user() [LINE 11-21]│
│ ├─ INSERT INTO users table                   │
│ └─ Store in localStorage [LINE 47]           │
└──────────────────────────────────────────────┘
    ↓
USER STARTS CHATTING
    ↓
┌──────────────────────────────────────────────┐
│ script.js: sendMessage() [LINE 120+]         │
├──────────────────────────────────────────────┤
│ POST /chat?user_id={currentUserId}           │
│ Body: {message: "...", forced_role: "..."}  │
└──────────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────────┐
│ app.py: chat() endpoint [LINE 94-122]        │
├──────────────────────────────────────────────┤
│ 1. Get agent_name from route_agent()         │
│ 2. Stream response token by token            │
│ 3. AFTER response complete:                  │
│    save_chat(user_id, agent_name, msg, resp)│
│    [LINE 121 in app.py]                      │
└──────────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────────┐
│ db_service.py: save_chat() [LINE 162-174]    │
├──────────────────────────────────────────────┤
│ INSERT INTO chat_history:                    │
│ ├─ user_id                                   │
│ ├─ role                                      │
│ ├─ message                                   │
│ ├─ response                                  │
│ └─ created_at (auto)                         │
└──────────────────────────────────────────────┘
    ↓
TAKE INTERVIEW
    ↓
┌──────────────────────────────────────────────┐
│ User answers questions                       │
│ Each answer saved as chat (above)            │
└──────────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────────┐
│ Academic Agent: end_interview()              │
├──────────────────────────────────────────────┤
│ Calculate: score, correct, total             │
│ POST /api/interview/save                     │
│ {user_id, domain, score, correct, total}     │
└──────────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────────┐
│ app.py: save_interview_result() [LINE 157]   │
├──────────────────────────────────────────────┤
│ db_service.py: save_interview() [LINE 27-38] │
│                                              │
│ INSERT INTO interview_sessions:              │
│ ├─ user_id                                   │
│ ├─ domain                                    │
│ ├─ score                                     │
│ ├─ correct_answers                           │
│ ├─ questions_answered                        │
│ └─ created_at (auto)                         │
└──────────────────────────────────────────────┘
    ↓
CHECK METRICS
    ↓
┌──────────────────────────────────────────────┐
│ GET /api/interview/stats/{user_id}           │
│ app.py: [LINE 161-173]                       │
├──────────────────────────────────────────────┤
│ db_service.py: get_interview_stats()         │
│ [LINE 57-90]                                 │
│                                              │
│ SELECT * FROM interview_sessions             │
│ WHERE user_id = {user_id}                    │
│ ORDER BY created_at                          │
│                                              │
│ Calculate:                                   │
│ ├─ total_interviews: len(interviews)         │
│ ├─ avg_score: sum(scores)/len(scores)        │
│ ├─ improvement: last - first                 │
│ └─ by_domain: avg per domain                 │
└──────────────────────────────────────────────┘
    ↓
METRICS DISPLAYED
```

---

## 📊 Actual Database Structure

### Users Table (Created Once Per Browser)
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,        -- Auto-increment
    username STRING UNIQUE,         -- user_1705424400000
    created_at DATETIME             -- When created
);

Example:
ID | USERNAME              | CREATED_AT
1  | user_1705424400000   | 2026-01-17 10:30:00
2  | user_1705424410000   | 2026-01-17 10:35:00
```

### Chat History Table (Every Chat Saved)
```sql
CREATE TABLE chat_history (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,                -- Foreign key to users
    role STRING,                    -- academic/code/content/general
    message STRING,                 -- Your message
    response STRING,                -- AI response
    created_at DATETIME
);

Example:
ID | USER_ID | ROLE       | MESSAGE         | RESPONSE  | CREATED_AT
1  | 1       | academic   | "What is DSA?"  | "D.S. is" | 2026-01-17 10:31:00
2  | 1       | academic   | "start mock..." | "Choose.."| 2026-01-17 10:32:00
```

### Interview Sessions Table (Only Interview Data)
```sql
CREATE TABLE interview_sessions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,                -- Foreign key
    domain STRING,                  -- DSA/OS/DBMS/ML/HR/General
    score FLOAT,                    -- Calculated score
    correct_answers INTEGER,        -- How many correct
    questions_answered INTEGER,     -- Total questions
    created_at DATETIME
);

Example:
ID | USER_ID | DOMAIN | SCORE | CORRECT | TOTAL | CREATED_AT
1  | 1       | DSA    | 85.0  | 17      | 20    | 2026-01-17 10:50:00
2  | 1       | DSA    | 75.0  | 15      | 20    | 2026-01-18 09:20:00
```

---

## 🎯 Key Points Summary

### User Creation
- ✅ Created **ONCE** on first visit
- ✅ Stored in **localStorage** browser storage
- ✅ **Reused** on every subsequent visit
- ✅ Different browser/private window = different user
- **File**: [backend/static/script.js](backend/static/script.js) Lines 7-53

### Chat History Storage
- ✅ **EVERY chat message saved** automatically
- ✅ Saved **AFTER response completes**
- ✅ Includes: message, response, agent, timestamp
- ✅ Per-user filtered
- **File**: [backend/app.py](backend/app.py) Line 121
- **Storage**: [backend/db_service.py](backend/db_service.py) Lines 162-174

### Metrics Calculation
- ❌ **NOT from chat history** - from interview_sessions table
- ✅ **Only calculated from interviews** taken
- ✅ Uses **3 formulas**:
  1. Average Score: `sum(scores) / count`
  2. Improvement: `last_score - first_score`
  3. Domain Average: `sum(domain_scores) / domain_count`
- **File**: [backend/db_service.py](backend/db_service.py) Lines 57-90

---

## 💡 Why This Design?

```
Why separate interview_sessions from chat_history?

Chat History:
├─ Purpose: Store every conversation
├─ Used for: Reviewing past discussions
└─ NOT for: Calculating performance metrics

Interview Sessions:
├─ Purpose: Store structured interview data
├─ Stores: Domain, score, correct answers
└─ Used for: Calculating metrics (avg, improvement, by-domain)

Result:
├─ Cleaner data model
├─ More efficient metric queries
├─ Better performance
└─ Clear separation of concerns
```

---

## ✅ Verification

To verify this works, run:

```bash
# Start backend
uvicorn backend.app:app --reload

# In another terminal
python test_system.py
```

Or check database directly:

```bash
sqlite3 unigenai.db

# View users (check if created only once)
SELECT * FROM users;

# View chat history (all messages)
SELECT COUNT(*) FROM chat_history WHERE user_id=1;

# View interview data (what metrics are from)
SELECT * FROM interview_sessions WHERE user_id=1;

# Check metrics calculation
SELECT 
    AVG(score) as avg_score,
    MAX(score) - MIN(score) as improvement
FROM interview_sessions 
WHERE user_id=1;
```

---

**Last Updated**: January 18, 2026
