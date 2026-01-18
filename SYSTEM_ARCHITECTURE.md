# UniGenAI System Architecture - User Management & Chat Storage

## Overview
This document explains how user IDs, sessions, chat history, and metrics are managed in the UniGenAI system.

---

## 1. USER CREATION & SESSION MANAGEMENT

### Automatic User Creation
**When:** On first page load
**How:** 
- Frontend checks localStorage for `unigenai_user` key
- If NOT found: Creates new user with auto-generated username `user_<timestamp>`
- Calls `POST /api/user/create?username=<username>`
- Backend creates user in database and returns `{id, username}`
- Frontend stores user info in localStorage

**Result:** 
- Each browser/device gets a unique user ID
- User ID persists across sessions (stored in localStorage)
- Users can manually clear localStorage to reset identity

### User Session Flow
```
Browser Page Load
    ↓
Check localStorage for 'unigenai_user'
    ├─ EXISTS: Load stored user_id
    └─ NOT EXISTS: Create new user
         ↓
    Call POST /api/user/create?username=user_<timestamp>
         ↓
    Get response: {id: 1, username: "user_1705424400000"}
         ↓
    Store in localStorage
         ↓
    All subsequent requests include user_id
```

---

## 2. CHAT FLOW & STORAGE

### Chat Request Flow
```
User Types Message
    ↓
Frontend: sendMessage()
    ├─ Gets currentUserId from memory
    ├─ Creates ChatRequest {message, forced_role}
    └─ Sends POST /chat?user_id=<currentUserId>
         ↓
Backend: @app.post("/chat")
    ├─ Parameter: user_id (required)
    ├─ Receives ChatRequest with message
    ├─ Routes to appropriate agent
    ├─ Streams response back
    └─ Saves to DB after full response
         ↓
Database: INSERT into chat_history
    (user_id, role, message, response, created_at)
         ↓
Result: Chat stored with this user's ID permanently
```

### Key Points
- **user_id is required** - Not optional anymore
- **Each chat is tied to a user** - Cannot be null
- **Immediate storage** - After agent finishes, response is saved to DB
- **Immutable association** - Chat cannot be transferred to another user

---

## 3. CHAT HISTORY ACCESS & RETRIEVAL

### Get Chat History
**Endpoint:** `GET /api/chat/history/{user_id}`
**Parameters:** 
- `user_id` (path parameter) - Which user's history
- `limit` (query) - Number of chats (default: 50)

**Response:**
```json
[
    {
        "role": "academic",
        "message": "What is DSA?",
        "response": "Data Structures and Algorithms...",
        "date": "2026-01-17T10:30:00"
    },
    ...
]
```

**How to Access:**
```javascript
// Frontend
const userId = currentUserId;  // From localStorage
const response = await fetch(`/api/chat/history/${userId}`);
const chatHistory = await response.json();
```

**Database Query (Backend):**
- Filters `ChatHistory` table by `user_id`
- Ordered by `created_at DESC` (newest first)
- Returns only this user's chats

---

## 4. INTERVIEW METRICS & STORAGE

### Interview Data Storage
When user completes mock interview:
```
Interview End
    ↓
Backend calculates: score, correct_answers, total_questions
    ↓
Saves to DB: INSERT into interview_sessions
    (user_id, domain, score, correct_answers, questions_answered, created_at)
    ↓
Data is now accessible via metrics endpoints
```

### Get Interview Stats
**Endpoint:** `GET /api/interview/stats/{user_id}`

**Returns:**
```json
{
    "total_interviews": 5,
    "avg_score": 78.5,
    "last_score": 85.0,
    "first_score": 65.0,
    "improvement": 20.0,
    "by_domain": {
        "DSA": 75.0,
        "OS": 80.5,
        "DBMS": 85.0
    }
}
```

**Calculation Logic:**
```python
interviews = Get all interviews where user_id matches
scores = [75, 68, 82, 85, 79]
avg_score = sum(scores) / len(scores) = 77.8

improvement = last_score - first_score = 85 - 75 = 10

by_domain = Group interviews by domain, calculate avg per domain
```

### Interview History
**Endpoint:** `GET /api/interview/history/{user_id}?domain=DSA`

**Returns:**
```json
[
    {
        "id": 1,
        "domain": "DSA",
        "score": 85.0,
        "correct": 8,
        "total": 10,
        "date": "2026-01-17T10:30:00"
    },
    ...
]
```

---

## 5. STUDY PLANNER INTEGRATION

### Save Study Plan
**Endpoint:** `POST /api/planner/save`
**Payload:**
```json
{
    "user_id": 1,
    "subject": "DSA",
    "topics": ["Arrays", "LinkedLists", "Trees"],
    "exam_date": "2026-02-17"
}
```

**Storage:**
- Saved to `study_plans` table with user_id
- Each user's plans are separate
- Completion percentage tracked separately

### Get User's Plans
**Endpoint:** `GET /api/planner/{user_id}`

**Returns only plans for that user:**
```json
[
    {
        "id": 1,
        "subject": "DSA",
        "completion": 45.0,
        "exam_date": "2026-02-17",
        "topics": ["Arrays", "LinkedLists", "Trees"]
    }
]
```

---

## 6. DATABASE SCHEMA

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username STRING UNIQUE,
    created_at DATETIME
);
```

### Chat History Table
```sql
CREATE TABLE chat_history (
    id INTEGER PRIMARY KEY,
    user_id INTEGER (FOREIGN KEY -> users.id),
    role STRING,          -- academic, content, code, general
    message STRING,
    response STRING,
    created_at DATETIME
);
```

### Interview Sessions Table
```sql
CREATE TABLE interview_sessions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER (FOREIGN KEY -> users.id),
    domain STRING,        -- DSA, OS, DBMS, ML, HR, General
    score FLOAT,
    questions_answered INTEGER,
    correct_answers INTEGER,
    created_at DATETIME
);
```

### Study Plans Table
```sql
CREATE TABLE study_plans (
    id INTEGER PRIMARY KEY,
    user_id INTEGER (FOREIGN KEY -> users.id),
    subject STRING,
    topics JSON,
    exam_date DATETIME,
    completion_percentage FLOAT,
    created_at DATETIME
);
```

---

## 7. COMPLETE WORKFLOW EXAMPLE

### Scenario: New User Chats & Takes Interview

**Step 1: Page Load**
```
User opens http://localhost:8000/ui
→ script.js runs initializeUser()
→ No localStorage found
→ Creates user "user_1705424400000"
→ POST /api/user/create?username=user_1705424400000
→ Gets back {id: 1, username: "user_1705424400000"}
→ Stores in localStorage
```

**Step 2: User Selects Agent**
```
User clicks "Academic Helper"
→ selectRole('academic') called
→ Chat interface shown
→ currentUserId = 1 (from localStorage)
```

**Step 3: User Sends Message**
```
User: "What is a LinkedList?"
→ sendMessage()
→ fetch(/chat?user_id=1, {message: "What is a LinkedList?"})
→ Backend receives user_id=1
→ Routes to academic_agent
→ academic_agent.respond("What is a LinkedList?", user_id=1)
→ Response streamed back to frontend
→ After response complete:
   save_chat(1, "academic", "What is a LinkedList?", "<response>")
   → INSERT into chat_history (user_id=1, ...)
→ Chat visible in frontend
```

**Step 4: Verify Chat Stored**
```
Frontend: GET /api/chat/history/1
→ Returns all chats for user_id=1
→ Includes the message from Step 3
```

**Step 5: Start Mock Interview**
```
User: "start mock interview"
→ sendMessage()
→ fetch(/chat?user_id=1, {message: "start mock interview"})
→ academic_agent detects interview request
→ start_session(1, "dsa", [questions...])
→ User answers questions
→ Each answer saved as chat
→ User says "stop interview"
→ end_interview(session_id="1", user_id=1)
→ Calculates score=85.0, correct=8, total=10
→ INSERT into interview_sessions (user_id=1, domain="DSA", score=85.0, ...)
```

**Step 6: View Metrics**
```
Frontend: GET /api/interview/stats/1
→ Returns:
{
    "total_interviews": 1,
    "avg_score": 85.0,
    "last_score": 85.0,
    "first_score": 85.0,
    "improvement": 0.0,
    "by_domain": {"DSA": 85.0}
}
```

**Step 7: Another User on Same Browser (After Clearing localStorage)**
```
User clears localStorage manually or deletes cache
→ Page reloads
→ No localStorage found
→ Creates user "user_1705424500000" (different ID)
→ Gets {id: 2, username: "user_1705424500000"}
→ All chats/metrics separate from user 1
→ GET /api/chat/history/2 → Only user 2's chats
→ GET /api/interview/stats/2 → Only user 2's stats
```

---

## 8. TROUBLESHOOTING

### Problem: Metrics always zero
**Possible Causes:**
1. `user_id` not being passed to `/chat` endpoint
2. Interview not properly ending and saving
3. User viewing stats for wrong user_id

**Fix:**
- Check browser console: `console.log(currentUserId)`
- Verify localStorage: `localStorage.getItem('unigenai_user')`
- Check API calls: Open Network tab → See if `user_id` in URL

### Problem: Chat history not showing
**Possible Causes:**
1. Wrong `user_id` in endpoint call
2. Chat not being saved after response
3. Database not persisting data

**Fix:**
- Verify endpoint: GET /api/chat/history/{correct_user_id}
- Check backend logs during chat
- Verify database file exists: `unigenai.db`

### Problem: Different user seeing another's data
**Fix:**
- Check that `user_id` filtering is applied in all queries
- Verify localStorage isolation (different browsers/profiles)
- Check database for accidental NULL user_ids

---

## 9. KEY CHANGES MADE (From Previous System)

| Aspect | Before | After |
|--------|--------|-------|
| User Creation | Manual POST or hardcoded | Automatic on first load |
| User Tracking | None (single user) | Automatic via localStorage |
| Chat Endpoint | `/chat` (no user_id) | `/chat?user_id={id}` (required) |
| Chat Storage | Conditional (if user_id) | Always stored |
| Metrics | Hardcoded USER_ID = "user1" | Passed user_id parameter |
| Data Isolation | None | Complete user isolation |
| Session Persistence | Lost on reload | Stored in localStorage |

---

## 10. TESTING CHECKLIST

- [ ] Open application in private window → New user created
- [ ] Send a message → Chat appears in history
- [ ] Take interview → Metrics updated
- [ ] Open new private window → Different user, different data
- [ ] Refresh page → Same user, all data persists
- [ ] Check `/api/chat/history/{user_id}` → Only that user's chats
- [ ] Check `/api/interview/stats/{user_id}` → Only that user's interviews
- [ ] Clear localStorage → Next refresh creates new user
- [ ] Multiple interviews → Improvement calculated correctly
- [ ] By domain stats → Separated by domain

---

## 11. API ENDPOINTS REFERENCE

### User Management
- `POST /api/user/create?username={username}` - Create user
- `GET /api/user/{user_id}` - Get user info

### Chat
- `POST /chat?user_id={user_id}` - Send chat (required user_id)
- `GET /api/chat/history/{user_id}` - Get chat history

### Interviews
- `POST /api/interview/save` - Save interview result
- `GET /api/interview/history/{user_id}` - Get interview history
- `GET /api/interview/stats/{user_id}` - Get interview statistics
- `GET /api/debug/interviews/{user_id}` - Raw interview data

### Study Planner
- `POST /api/planner/save` - Save study plan
- `GET /api/planner/{user_id}` - Get user's plans
- `PUT /api/planner/{plan_id}/update` - Update plan completion

---

**Last Updated:** January 17, 2026
**System Status:** Complete implementation with proper user isolation and data persistence
