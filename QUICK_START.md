# UniGenAI - Quick Start Guide

**Latest Version**: 2.0 (Production Ready)  
**For**: New users and developers

---

## ⚡ Get Started in 5 Minutes

### Step 1: Prerequisites
- Python 3.8+
- Ollama installed

### Step 2: Install & Run
```bash
# Navigate to project
cd UniGenAI

# Create virtual environment
python -m venv venv
venv\Scripts\activate              # Windows
# OR
source venv/bin/activate          # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# In Terminal 1: Start Ollama
ollama run llama3.2:1b

# In Terminal 2: Start FastAPI
uvicorn backend.app:app --reload
```

### Step 3: Open Browser
```
http://localhost:8000/ui
```

### Step 4: Start Using
1. First time? User created automatically ✓
2. Select an agent (Academic, Code, Content, or General)
3. Start chatting!

---

## 🎯 All Features Overview

### 1. **Multi-Agent Chat System**

Select an agent or let it auto-switch:

#### Academic Helper 📚
```
"What is binary search?"
→ Explains concept with examples

"Start mock interview"
→ Begins domain-specific interview

"Create study plan for DSA exam on Feb 17"
→ Generates structured study schedule
```

#### Code Assistant 💻
```
"Write a Python function to sort array"
→ Provides solution with explanation

"Debug this error: TypeError on line 23"
→ Helps identify and fix issue

"How to optimize this code?"
→ Provides performance tips
```

#### Content Creator ✍️
```
"Write a YouTube script about AI"
→ Full script with intro, body, outro

"Create blog post about machine learning"
→ Article-style content
```

#### General Assistant 💬
```
"Hello!" → Friendly conversation
"Tell me a joke" → General queries
"What's the capital of France?" → General knowledge
```

### 2. **Mock Interview System**
- 6 domains: DSA, OS, DBMS, ML, HR, General
- AI-powered answer evaluation
- Real-time scoring
- Performance tracking with improvement metrics

### 3. **Study Planning**
- Auto-calculates from exam date
- Balanced topic distribution
- Built-in review sessions
- Completion tracking

### 4. **Document Learning (RAG)**
- Upload PDF/TXT files
- Semantic search across documents
- Answers augmented with your materials
- Automatic chunking and indexing

### 5. **Voice Integration**
- Text-to-speech for AI responses
- Speech-to-text for user input
- Hands-free interaction

### 6. **Chat History**
- All conversations saved per user
- Permanent storage
- Complete access history

### 7. **Performance Analytics**
- Average score across interviews
- Improvement tracking
- Performance by domain
- Complete interview history

### 8. **User Management**
- Automatic user creation
- localStorage persistence
- Multi-user support
- Complete data isolation

---

## 🔌 API Endpoints Cheatsheet

### Chat
```bash
curl -X POST "http://localhost:8000/chat?user_id=1" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is DSA?", "forced_role": "academic"}'
```

### Interview
```bash
# Save result
curl -X POST "http://localhost:8000/api/interview/save" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "domain": "DSA",
    "score": 85.5,
    "correct": 17,
    "total": 20
  }'

# Get statistics
curl "http://localhost:8000/api/interview/stats/1"

# Get history
curl "http://localhost:8000/api/interview/history/1?domain=DSA"
```

### Study Planner
```bash
curl -X POST "http://localhost:8000/api/planner/save" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "subject": "DSA",
    "topics": ["Arrays", "LinkedLists", "Trees"],
    "exam_date": "2026-02-17"
  }'
```

---

## 🧪 Testing

### Run Automated Tests
```bash
python test_system.py
```

### Manual Checklist
- [ ] Page loads → User ID auto-created
- [ ] Send message → Appears in UI and database
- [ ] Start interview → Can select domain and answer questions
- [ ] Create study plan → Shows day-wise schedule
- [ ] Check metrics → Shows scores and improvement
- [ ] Multiple windows → Different users, different data

---

## 📊 Database Inspection

```bash
sqlite3 unigenai.db

# View all tables
.tables

# Check users
SELECT * FROM users;

# View chats for user 1
SELECT * FROM chat_history WHERE user_id=1;

# View interviews for user 1
SELECT * FROM interview_sessions WHERE user_id=1;

# Calculate average score
SELECT AVG(score) FROM interview_sessions WHERE user_id=1;

.exit
```

---

## 🎓 Common Tasks

### Take Mock Interview
```
1. Chat: "Start mock interview"
2. Choose domain: "DSA"
3. Answer all questions
4. Chat: "Stop interview"
5. Check metrics: /api/interview/stats/1
```

### Create Study Plan
```
Chat: "Create study plan for DSA exam on Feb 20"
System creates day-wise schedule automatically
```

### Upload Documents
```
1. Click upload button
2. Select PDF or TXT
3. System processes and indexes
4. Ask questions referencing your docs
```

---

## ⚙️ Configuration

### Change LLM Model
Edit `backend/llm_client.py`:
```python
MODEL_NAME = "llama3.2:1b"  # Default, fast
# Change to: llama3.2:3b for better quality
```

---

## 🚀 Performance Tips

1. Keep Ollama running in background
2. Clear browser cache if issues
3. Don't clear localStorage (loses user ID)
4. SQLite handles local use fine
5. Streaming provides instant feedback

---

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Connection refused | Start Ollama: `ollama run llama3.2:1b` |
| No AI responses | Check Ollama, restart FastAPI |
| Metrics showing zero | Take new complete interview |
| Chat not saving | Check user_id in localStorage |
| New user each reload | Don't clear localStorage |
| Port 8000 in use | `netstat -ano \| findstr :8000` |

---

## 📚 Full Documentation

| Document | Purpose |
|----------|---------|
| [README.md](README.md) | Complete project overview |
| [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) | Detailed system docs |
| [ARCHITECTURE_DIAGRAMS.md](ARCHITECTURE_DIAGRAMS.md) | Visual flows |
| [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) | Technical details |
| [FINAL_SUMMARY.md](FINAL_SUMMARY.md) | Project status |
| [STATUS_DASHBOARD.txt](STATUS_DASHBOARD.txt) | Visual overview |
| [AUTO_SWITCH_VERIFICATION.txt](AUTO_SWITCH_VERIFICATION.txt) | Agent logic |

---

## 🎉 You're Ready!

```
✅ User management working
✅ Chat system functional
✅ Interviews operational
✅ Analytics tracking
✅ Voice enabled
✅ Multi-user ready

→ Start chatting now at http://localhost:8000/ui
```

**Questions?** Check documentation or run `python test_system.py` to verify everything works.

---

**Last Updated**: January 18, 2026  
**Version**: 2.0 Production Ready
