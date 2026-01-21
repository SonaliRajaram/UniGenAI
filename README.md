# UniGenAI: An Intelligent Multi-Role LLM System for Learning, Content Generation and Software Support

> An AI-powered platform for learning, content creation, coding assistance, and interview preparation with advanced user management, real-time streaming, and comprehensive analytics.
> A Multi-Agent, Intent-Aware AI Assistant Platform with Real-Time Streaming, RAG, and Interview Evaluation

**Version**: 2.0 (Production Ready)  
**Last Updated**: January 18, 2026  
**Status**: Fully Operational

---

## Overview

UniGenAI is a sophisticated multi-agent AI system that intelligently routes user queries to specialized agents while providing comprehensive features for learning, interview preparation, and content creation. The system leverages Ollama for local LLM inference, FastAPI for async processing, and a robust architecture for real-time streaming responses with complete user tracking and analytics.

### Key Highlights
- **4 Specialized Agents**: Academic, Code, Content, and General assistance
- **Real-time Streaming**: Server-Sent Events (SSE) for immediate response feedback
- **Smart Agent Routing**: Automatic agent selection with manual override capability
- **Complete User Management**: Automatic user creation with persistent sessions
- **Advanced Analytics**: Interview metrics, performance tracking, improvement analysis
- **RAG Integration**: Learn from your own documents (PDFs and text files)
- **Mock Interviews**: Domain-specific interview practice with AI evaluation
- **Study Planning**: Automated study schedules based on exam dates
- **Voice Support**: Text-to-speech and speech-to-text integration
- **Multi-User**: Complete data isolation between users

---

## Core Features

### 1. **Multi-Agent System**

Your queries are intelligently routed to specialized agents:

| Agent | Capabilities | Examples |
|-------|-------------|----------|
| **Academic**  | Explains concepts, generates study plans, conducts mock interviews | "What is DSA?", "Start mock interview in DSA", "Create study plan for exam" |
| **Code**  | Programming assistance, debugging, error resolution, code explanations | "Write Python function for...", "Debug this error", "Fix Java bug" |
| **Content**  | Content creation, scriptwriting, essays, blogs, creative writing | "Write YouTube script", "Create blog post", "Draft email" |
| **General**  | Casual conversations, general knowledge, random queries | "Hello!", "How are you?", "Tell me a joke" |

**Auto-Agent Switching**: The system detects query type and automatically switches agents while you chat. You can also force a specific agent.

### 2. **Interview Preparation System**

Comprehensive mock interview functionality with real AI evaluation:

- **6 Domains**: DSA, Operating Systems, DBMS, Machine Learning, HR, General
- **Adaptive Questions**: Questions selected from curated question bank
- **AI Evaluation**: Each answer evaluated with scoring and feedback
- **Performance Metrics**: 
  - Individual scores per interview
  - Average score across interviews
  - Improvement tracking
  - Domain-wise performance breakdown
  - First vs. last score comparison

**How it works**:
```
User: "start mock interview"
→ System: "Choose domain: DSA / OS / DBMS / ML / HR / General"
→ User: "DSA"
→ System: Presents Question 1
→ User: Answers question
→ System: Evaluates answer (AI-powered), scores, moves to next
→ After all questions: Calculates metrics and saves results
```

### 3. **Study Planning**

Generate intelligent study schedules:

- **Exam-Date Based**: Input exam date and get day-wise breakdown
- **Topic-Aware**: Organize topics by difficulty and prerequisites
- **Time Allocation**: Balanced daily schedule with review sessions
- **Progress Tracking**: Monitor completion percentage for each plan
- **Adaptive Planning**: Adjust based on your progress

**Features**:
- Weight-based topic prioritization
- Daily time split across topics
- Built-in review schedules
- Flexible duration handling

### 4. **Document-Based Learning (RAG)**

Learn from your own knowledge sources:

- **Upload Documents**: PDF and TXT file support
- **Semantic Search**: FAISS-powered vector similarity search
- **Context Integration**: Answers augmented with your documents
- **Automatic Chunking**: Smart document segmentation
- **Embeddings**: Using Sentence Transformers (all-MiniLM-L6-v2)

**How it works**:
```
1. Upload your study notes (PDF/TXT)
2. System processes and creates embeddings
3. When you ask questions, relevant sections are retrieved
4. AI generates answers using both training + your documents
```

### 5. **Real-Time Streaming**

Get instant response feedback:

- **Server-Sent Events (SSE)**: Token-by-token streaming
- **Live UI Updates**: See AI response appear as it's generated
- **No Waiting**: Immediate feedback while AI is thinking
- **Async Architecture**: Non-blocking concurrent request handling
- **Efficient Client Handling**: Smart buffer management for chunks

### 6. **Complete User Management**

Automatic, persistent user sessions:

- **Auto-Creation**: User automatically created on first visit
- **localStorage Persistence**: User ID survives page reloads
- **Multi-User Support**: Each browser/device = separate user
- **Complete Isolation**: Users see only their data
- **No Authentication Required**: Anonymous but tracked

**How it works**:
```
First Visit:
→ System checks localStorage
→ User not found → Create new user
→ Save user ID in localStorage
→ All subsequent requests include user ID

Subsequent Visits:
→ Load user ID from localStorage
→ Continue as same user
→ All chat history and metrics available
```

### 7. **Chat History & Persistence**

Every conversation is saved and accessible:

- **Per-User History**: Each user's chats isolated
- **Searchable**: Retrieve specific conversations
- **Permanent Storage**: Data survives refreshes
- **Role Tagged**: Know which agent responded
- **Timestamped**: When conversations occurred

### 8. **Performance Analytics**

Comprehensive metrics and tracking:

- **Interview Statistics**: Average score, improvement, by-domain breakdown
- **Interview History**: Complete record of all interviews
- **Progress Dashboard**: Track learning over time
- **Comparative Analysis**: First vs. latest performance
- **Domain Breakdown**: Performance in each interview domain

---

##  Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend Framework** | FastAPI | High-performance async web framework |
| **Server** | Uvicorn | ASGI application server |
| **LLM** | Ollama (llama3.2:1b) | Local language model inference |
| **Async HTTP** | httpx | Non-blocking HTTP client |
| **Database** | SQLite + SQLAlchemy | Persistent data storage with ORM |
| **Embeddings** | Sentence Transformers | Semantic vector embeddings |
| **Vector Store** | FAISS | Fast similarity search |
| **Document Processing** | PyPDF2 | PDF text extraction |
| **Frontend** | HTML5/CSS3/JavaScript | Interactive UI with streaming support |
| **Data Validation** | Pydantic | Request/response validation |

---

##  Project Structure

```
UniGenAI/
├── backend/
│   ├── app.py                          # FastAPI app + all API endpoints
│   ├── llm_client.py                   # Ollama communication (sync/async)
│   ├── intent_router.py                # Intent classification
│   ├── models.py                       # SQLAlchemy database models
│   ├── db_service.py                   # Database CRUD operations
│   │
│   ├── agents/                         # Specialized AI agents
│   │   ├── academic_agent.py           # Academic + interviews + study planning
│   │   ├── code_agent.py               # Code assistance + debugging
│   │   ├── content_agent.py            # Content creation
│   │   ├── general_agent.py            # General conversation
│   │   ├── agent_router.py             # Intent-based routing + auto-switching
│   │   └── agent_utils.py              # Shared utilities
│   │
│   ├── mock_interview/                 # Interview system
│   │   ├── session.py                  # Interview session management + scoring
│   │   ├── evaluator.py                # Answer evaluation
│   │   └── questions.py                # Question database (6 domains)
│   │
│   ├── rag/                            # Document learning system
│   │   ├── pdf_loader.py               # PDF text extraction
│   │   ├── txt_loader.py               # Text file loading
│   │   ├── text_splitter.py            # Document chunking
│   │   ├── vector_store.py             # FAISS index management
│   │   ├── retriever.py                # Context retrieval
│   │   └── documents/                  # Knowledge base
│   │       ├── dsa_notes.txt
│   │       ├── os_notes.txt
│   │       ├── dbms_notes.txt
│   │       └── ml_notes.txt
│   │
│   ├── study_planner/                  # Study planning system
│   │   ├── planner_logic.py            # Schedule computation
│   │   ├── planner_llm.py              # LLM-based generation
│   │   └── topics.py                   # Topic database
│   │
│   ├── static/                         # Frontend UI
│   │   ├── index.html                  # Main interface
│   │   ├── script.js                   # Client-side logic + user management
│   │   ├── style.css                   # Styling
│   │   └── images/                     # UI images
│   │
│   └── __pycache__/
│
├── requirements.txt                    # Python dependencies
├── README.md                           # Main documentation (this file)
├── ARCHITECTURE_DIAGRAMS.md            # Visual flow diagrams
├── unigenai.db                         # SQLite database (created on first run)
├── venv/                               # Python virtual environment
└── test_*.py                           # Test files
```

---

##  Quick Start

### Prerequisites
- Python 3.8+
- Ollama installed and running
- 2GB+ RAM recommended

### Installation

1. **Clone/Download the project**
```bash
cd UniGenAI
```

2. **Create virtual environment**
```bash
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Mac/Linux
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Start Ollama service**
```bash
ollama run llama3.2:1b
# Keep this running in a separate terminal
```

5. **Start the backend**
```bash
uvicorn backend.app:app --reload
```

6. **Open in browser**
```
http://localhost:8000/ui
```

### First Use

1. **Page loads automatically**:
   - System creates a unique user ID
   - Stored in browser localStorage
   - Welcome message displayed

2. **Select an agent**:
   - Click "Academic Helper", "Code Assistant", "Content Creator", or "General Assistant"
   - Chat interface opens

3. **Start chatting**:
   - Type your message
   - Press Enter or click Send
   - Response streams in real-time
   - Message saved automatically

---

##  API Endpoints

All endpoints are documented in `SYSTEM_ARCHITECTURE.md`. Here's a quick reference:

### Chat
```bash
# Send message (required: user_id, message)
POST /chat?user_id=1
Content-Type: application/json
{
  "message": "What is DSA?",
  "forced_role": "academic"  # optional
}
# Returns: Server-Sent Events stream
```

### Interview
```bash
# Save interview result
POST /api/interview/save
{
  "user_id": 1,
  "domain": "DSA",
  "score": 85.5,
  "correct": 17,
  "total": 20
}

# Get interview statistics
GET /api/interview/stats/1
# Response: {"avg_score": 85.5, "by_domain": {...}, ...}

# Get interview history
GET /api/interview/history/1?domain=DSA
```

### Chat History
```bash
# Get all chats for a user
GET /api/chat/history/1?limit=50
```

### Study Planner
```bash
# Save study plan
POST /api/planner/save
{
  "user_id": 1,
  "subject": "DSA",
  "topics": ["Arrays", "LinkedLists", "Trees"],
  "exam_date": "2026-02-17"
}

# Get user's plans
GET /api/planner/1

# Update plan completion
PUT /api/planner/1/update?completion=45.5
```

---

##  Database Schema

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
  user_id INTEGER FOREIGN KEY,
  role STRING,              -- academic/code/content/general
  message STRING,
  response STRING,
  created_at DATETIME
);
```

### Interview Sessions Table
```sql
CREATE TABLE interview_sessions (
  id INTEGER PRIMARY KEY,
  user_id INTEGER FOREIGN KEY,
  domain STRING,            -- DSA/OS/DBMS/ML/HR/General
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
  user_id INTEGER FOREIGN KEY,
  subject STRING,
  topics JSON,
  exam_date DATETIME,
  completion_percentage FLOAT,
  created_at DATETIME
);
```

---

##  How It Works

### Chat Flow
```
User Input
    ↓
Frontend: sendMessage()
    ├─ Get user_id from localStorage
    ├─ Detect forced_role (if any)
    └─ Send POST /chat?user_id={id}
         ↓
Backend: route_agent()
    ├─ Classify intent
    ├─ Select appropriate agent
    └─ Call agent.respond(message, user_id)
         ↓
Agent Processing
    ├─ Generate response using LLM
    ├─ Stream tokens to frontend
    └─ Save to database
         ↓
Frontend: Receive stream
    ├─ Parse Server-Sent Events
    ├─ Display tokens in real-time
    └─ Enable text-to-speech
         ↓
Database: Persist
    ├─ Save message with user_id
    ├─ Save response
    └─ Record timestamp
```

### Interview Flow
```
User: "start mock interview"
    ↓
Academic Agent: Detect interview request
    ├─ Clear old session
    ├─ Ask for domain
    └─ Return domain selection prompt
         ↓
User: "DSA"
    ↓
Academic Agent: Start interview
    ├─ Initialize session with user_id
    ├─ Select questions for domain
    └─ Present Question 1
         ↓
User: Answers questions
    (Repeat: answer → evaluate → next question)
         ↓
User: "stop interview"
    ↓
Academic Agent: End interview
    ├─ Calculate score
    ├─ Save to database
    └─ Display results
         ↓
Database: Store results
    └─ Interview record with all metrics
```

### Auto-Agent Switching
```
User selects Academic Agent
    ↓
User: "Write Python code"
    ├─ Intent detected: CODE
    ├─ CODE not in {academic, general}
    └─ Auto-switch to CODE agent
         ↓
Response from CODE agent
    ├─ UI updates "Code Assistant"
    └─ Response delivered
         ↓
User: "What is DSA?"
    ├─ Intent detected: ACADEMIC
    ├─ ACADEMIC in {academic, general}
    └─ Stay in ACADEMIC agent
```

---

##  Use Cases

### For Students
- **Mock Interviews**: Practice interviews across 6 domains
- **Study Planning**: Get structured study schedules
- **Concept Clarification**: Ask about any topic
- **Performance Tracking**: Monitor improvement over time

### For Content Creators
- **Script Writing**: YouTube scripts, podcasts
- **Blog Writing**: Article generation
- **Social Media**: Captions, posts
- **Creative Writing**: Stories, essays

### For Developers
- **Code Assistance**: Write, debug, optimize code
- **Error Resolution**: Get help with error messages
- **Code Explanation**: Understand existing code
- **Best Practices**: Learn optimal approaches

### For Learners
- **General Knowledge**: Ask anything
- **Learning Resources**: Get study materials
- **Progress Tracking**: Monitor learning journey
- **Personalized Plans**: Custom study schedules

---

##  Security & Privacy

- **No Authentication Required**: For simplicity and accessibility
- **Data Isolation**: Each user sees only their data
- **localStorage-based**: User ID stored in browser (not transmitted unsecured)
- **Local LLM**: Ollama runs locally (data stays on your machine)
- **SQLite Database**: All data stored locally

### Multi-User Data Isolation
```
Browser 1 (Regular Window)  →  user_id=1  →  Database queries: user_id=1
Browser 2 (Private Window)  →  user_id=2  →  Database queries: user_id=2

Result: Complete isolation, different users see different data
```

---

##  Performance Features

### Async/Await Architecture
- Non-blocking I/O for concurrent requests
- Multiple users handled simultaneously
- Efficient resource utilization

### Streaming Responses
- Token-by-token delivery
- Real-time UI updates
- No waiting for full response
- Better perceived performance

### Database Optimization
- Indexed queries for fast retrieval
- Efficient user-based filtering
- SQLite for single-machine deployment

### Smart Intent Classification
- Keyword matching for instant detection (fast path)
- LLM classification for ambiguous queries
- Reduces unnecessary computation

---

##  Testing

### Run Automated Tests
```bash
python test_system.py
```

Tests cover:
- User creation and persistence
- Chat history storage
- Interview metrics calculation
- Data isolation between users
- Study plan management
- Agent routing

### Manual Testing
See `QUICK_START.md` for detailed manual testing procedures.


##  Troubleshooting

### Issue: Application won't start
**Solution**: 
1. Ensure Ollama is running: `ollama run llama3.2:1b`
2. Check port 8000 is available
3. Verify all dependencies installed: `pip install -r requirements.txt`

### Issue: No responses from AI
**Solution**:
1. Check Ollama is running
2. Verify network connectivity: `curl http://localhost:11434/api/generate`
3. Check backend logs for errors
4. Restart both Ollama and FastAPI

### Issue: Chat not being saved
**Solution**:
1. Check user_id is included in request
2. Verify database file exists: `unigenai.db`
3. Check file permissions
4. Restart application

### Issue: Metrics showing zero
**Solution**:
1. Take a new interview (complete the full flow)
2. Check user_id matches in requests
3. Verify database has interview_sessions table
4. Try different domain

---

##  Key Features Status

| Feature | Status | Details |
|---------|--------|---------|
| Multi-Agent System |  Working | 4 agents with auto-switching |
| Real-Time Streaming |  Working | SSE with token streaming |
| Interview System |  Working | 6 domains, scoring, metrics |
| Study Planner |  Working | Exam-date based scheduling |
| RAG System |  Working | PDF/TXT upload and retrieval |
| User Management |  Working | Auto-creation, persistence |
| Chat History |  Working | Per-user permanent storage |
| Performance Analytics |  Working | Metrics, improvement tracking |
| Voice Support |  Working | Text-to-speech enabled |
| Multi-User |  Working | Complete data isolation |
| Database |  Working | SQLite with full schema |

---

##  What's Next

### Potential Enhancements
- User authentication and login system
- Role-based access control
- Advanced filtering and search
- Export chat/metrics to PDF
- Custom question bank upload
- API rate limiting
- Cloud deployment options
- Mobile app companion

---

##  Tips & Tricks

### Maximize Learning
1. Upload your study notes as PDFs/TXT
2. Ask questions from your notes
3. Take mock interviews regularly
4. Create structured study plans
5. Track improvement over time

### Get Better Responses
1. Be specific in your questions
2. Provide context when needed
3. Ask follow-up questions
4. Use forced agent selection when needed
5. Refer to your uploaded documents

### Performance Tips
1. Keep Ollama running in background
2. Don't restart unnecessarily
3. Clear browser cache if issues
4. Use consistent user account (don't clear localStorage)

---

##  Support

For issues or questions:

1. **Check Documentation**: Start with relevant .md file
2. **Run Tests**: `python test_system.py` to verify everything
3. **Check Logs**: Review terminal output for errors
4. **Database Inspection**: Use sqlite3 to check data
5. **Manual Testing**: Follow procedures in QUICK_START.md

---

##  License

This project is provided as-is for educational and personal use.

---

##  Acknowledgments

Built with:
- FastAPI for robust async backend
- Ollama for efficient local LLM inference
- FAISS for fast similarity search
- SQLAlchemy for database ORM
- Sentence Transformers for embeddings

---

**Last Updated**: January 18, 2026  
**Version**: 2.0 Production  
**Status**:  Fully Operational and Ready to Use
