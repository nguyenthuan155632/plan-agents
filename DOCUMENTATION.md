# Dual AI Collaboration Framework - Complete Documentation

## 📚 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Tech Stack](#tech-stack)
4. [System Design](#system-design)
5. [UI/UX Design](#uiux-design)
6. [Getting Started](#getting-started)
7. [Usage Guide](#usage-guide)
8. [Agent Configuration](#agent-configuration)
9. [API Reference](#api-reference)
10. [Knowledge Base](#knowledge-base)
11. [Development Guide](#development-guide)

---

## Overview

**Dual AI Collaboration Framework** is an innovative system where two AI agents (Agent A and Agent B) collaborate, debate, and brainstorm solutions together with human moderation. The framework features:

- 🤖 **Dual Agent System**: GLM-4.5-air (Agent A) + Gemini-2.5-flash (Agent B)
- 💬 **Real-time Collaboration**: Agents engage in constructive debates
- 🧠 **Smart Turn-Taking**: File-based signal system for asynchronous processing
- 👤 **Human-in-the-Loop**: Moderator can interrupt, guide, or stop conversations
- 🎨 **Neobrutalism UI**: Bold, high-contrast web interface
- 🌐 **Bilingual Support**: Automatically detects and responds in Vietnamese or English

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     WEB UI (Next.js)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ SessionList  │  │ Conversation │  │ Start/Input  │     │
│  │              │  │    View      │  │  Components  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            ↕ HTTP/REST API
┌─────────────────────────────────────────────────────────────┐
│                      Backend (Python)                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Conversation Processor (Background)          │  │
│  │  - Monitors signal files (signal_*.txt)              │  │
│  │  - Orchestrates agent turns                          │  │
│  └──────────────────────────────────────────────────────┘  │
│                            ↕                                │
│  ┌──────────────┐                    ┌──────────────┐     │
│  │  Agent A     │  ←→ Coordinator →  │  Agent B     │     │
│  │ (GLM-4.5)    │                    │ (Gemini-2.5) │     │
│  └──────────────┘                    └──────────────┘     │
│                            ↕                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         SQLite Database (conversations.db)           │  │
│  │  - sessions: conversation metadata                   │  │
│  │  - messages: all messages with signals               │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↕
              ┌──────────────────────────┐
              │  Signal Files (storage/) │
              │  - signal_{id}.txt       │
              │  - continue_{id}.txt     │
              └──────────────────────────┘
```

### Component Breakdown

#### 1. **Frontend (Next.js 14 + React)**
- **SessionList**: Displays all conversations with status indicators
- **ConversationView**: Real-time message display with typewriter effect
- **StartConversation**: Interface to initiate new discussions
- **ContinueConversation**: Human input during HANDOVER signals
- **TypewriterText**: Character-by-character text animation

#### 2. **Backend (Python)**
- **conversation_processor.py**: Background daemon monitoring signal files
- **Coordinator**: Manages turn-taking between agents
- **BaseAgent**: Abstract class for AI agents
- **GLMAgent**: Integration with z.ai's GLM models
- **GeminiAgent**: Integration with Google's Gemini models
- **Database**: SQLite3 for persistent storage

#### 3. **Communication Layer**
- **REST API**: Next.js API routes for CRUD operations
- **File Signals**: `.txt` files trigger backend processing
- **Polling**: Frontend polls `/api/messages/{id}` every 3 seconds

---

## Tech Stack

### Frontend
- **Framework**: Next.js 14 (App Router)
- **UI Library**: React 18
- **Styling**: Tailwind CSS + Neobrutalism design system
- **Language**: TypeScript
- **State Management**: React hooks (useState, useEffect, useRef)

### Backend
- **Language**: Python 3.13
- **AI Models**: 
  - z.ai GLM-4.5-air (Agent A)
  - Google Gemini-2.5-flash (Agent B)
- **Database**: SQLite3
- **CLI**: Typer
- **HTTP Client**: OpenAI Python SDK, Google Generative AI SDK

### Development Tools
- **Version Control**: Git
- **Package Managers**: npm (frontend), pip (backend)
- **Linting**: ESLint (frontend), Pylint/Black (backend)

---

## System Design

### Database Schema

```sql
-- Sessions Table
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,           -- UUID
    topic TEXT NOT NULL,           -- Conversation topic
    status TEXT NOT NULL,          -- 'active', 'paused', 'completed'
    started_at TIMESTAMP NOT NULL
);

-- Messages Table
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,            -- 'Human', 'AgentA', 'AgentB'
    content TEXT NOT NULL,
    signal TEXT NOT NULL,          -- 'continue', 'handover', 'stop'
    timestamp TIMESTAMP NOT NULL,
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);
```

### Signal System

The framework uses file-based signals for triggering backend processing:

1. **New Conversation**: `signal_{sessionId}.txt`
   - Created by: Frontend API (`/api/sessions/start`)
   - Purpose: Start a new conversation

2. **Continue Conversation**: `continue_{sessionId}.txt`
   - Created by: Frontend API (`/api/sessions/{id}/continue`) or trigger endpoint
   - Purpose: Process next agent turn

3. **Stop Conversation**: Special human message with "🛑 STOP" keyword
   - Agents detect this and provide comprehensive summary
   - Session marked as 'completed' after summary

### Turn-Taking Logic

```python
def get_next_role(current_role: Role, last_message_content: str = "") -> Role:
    if current_role == Role.HUMAN:
        # Check if human mentioned specific agent
        if mentions_agent_b:
            return Role.AGENT_B
        elif mentions_agent_a:
            return Role.AGENT_A
        return Role.AGENT_A  # Default to Agent A
    
    # Alternate between agents
    if current_role == Role.AGENT_A:
        return Role.AGENT_B
    else:
        return Role.AGENT_A
```

### Agent Signal Decision Logic

Agents **CANNOT** send `STOP` signal (only human can stop). They can only:
- **CONTINUE**: Keep the conversation going
- **HANDOVER**: Ask for human input

Decision criteria:
- After 2-3 exchanges since last human input → `HANDOVER`
- After 6+ total exchanges → `HANDOVER` (let human decide)
- Strong conclusion keywords detected → `HANDOVER` (let human confirm)

---

## UI/UX Design

### Design System: Neobrutalism

The framework uses a bold **Neobrutalism** design aesthetic:

#### Color Palette
```css
/* Primary Colors */
--neo-yellow: #ffff00;
--neo-pink: #ff6b9d;
--neo-blue: #00d4ff;
--neo-green: #00ff88;
--neo-purple: #c084fc;
--neo-orange: #ff8c42;
--neo-black: #000000;
```

#### Design Principles
1. **Bold Borders**: 2-3px black borders everywhere (`neo-border`)
2. **Hard Shadows**: 4-6px offset shadows, no blur (`neo-shadow`)
3. **Square Corners**: `rounded-none` on all components
4. **Flat Colors**: No gradients, solid colors only
5. **Heavy Typography**: `font-black`, `uppercase`, `tracking-wide`
6. **High Contrast**: Black text on bright backgrounds

#### Component Styling
- **Agent A Messages**: Blue background (`bg-blue-300`)
- **Agent B Messages**: Purple background (`bg-purple-300`)
- **Human Messages**: Pink background (`bg-pink-300`)
- **Active Session**: Yellow highlight (`bg-yellow-300`)
- **Buttons**: Bright colors with neo-shadow-hover effect

### Animations
- **TypewriterText**: Character-by-character text reveal (50 chars/sec)
- **Thinking Indicator**: Animated dots with pulse effect
- **Message Sequence**: One message animates at a time
- **Hover Effects**: Shadow expansion + translate on hover

---

## Getting Started

### Prerequisites
- Python 3.13+
- Node.js 18+
- npm or yarn

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd plan-agents
```

2. **Backend Setup**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python scripts/init_db.py
```

3. **Frontend Setup**
```bash
cd web
npm install
cd ..
```

4. **Configure API Keys** 🔐

**IMPORTANT**: Never commit API keys to Git! Use environment variables instead.

```bash
# Copy the example environment file
cp env.example .env

# Edit .env and add your actual API keys
nano .env  # or use any text editor
```

Your `.env` file should look like:
```env
# z.ai API Key for GLM-4.5-air (Agent A)
ZAI_API_KEY=your_actual_zai_api_key_here
ZAI_BASE_URL=https://api.z.ai/api/coding/paas/v4

# Google Gemini API Key (Agent B)
GEMINI_API_KEY=your_actual_gemini_api_key_here

# Agent Configuration (optional)
GLM_MODEL=glm-4.5-air
GEMINI_MODEL=gemini-2.5-flash
MAX_TURN_LENGTH=10000
```

**Getting API Keys:**
- **z.ai API Key**: Visit [https://z.ai](https://z.ai) and generate an API key
- **Gemini API Key**: Visit [https://ai.google.dev/](https://ai.google.dev/) and get an API key

For detailed setup instructions, see [ENV_SETUP.md](ENV_SETUP.md).

### Running the Application

**Option 1: Using start.sh (Recommended)**
```bash
chmod +x start.sh
./start.sh
```

**Option 2: Manual Start**

Terminal 1 - Backend:
```bash
source venv/bin/activate
python conversation_processor.py
```

Terminal 2 - Frontend:
```bash
cd web
npm run dev
```

**Access the application**: http://localhost:3000

---

## Usage Guide

### Starting a New Conversation

1. Open the web UI at http://localhost:3000
2. In the "Start New Conversation" section, enter your topic:
   ```
   Example topics:
   - "Best practices for microservices architecture"
   - "So sánh React vs Vue cho dự án lớn"
   - "Design database schema for e-commerce platform"
   ```
3. Click "Start Discussion"
4. Watch Agent A and Agent B debate!

### Interacting with Agents

#### Jump In (Interrupt)
- Click **"Jump In"** button anytime during the conversation
- Add your thoughts, clarify requirements, or change direction

#### Continue Conversation
- When agents show **"✋ Handover"** signal
- Input field appears automatically
- Provide feedback, ask questions, or give new instructions

#### Stop Conversation
- Click **"Stop"** button
- Agents will provide a comprehensive summary
- Summary includes:
  - Original request
  - Final solution/code/schema
  - Key decisions made
  - Trade-offs discussed
  - Final recommendation

### Agent Mention System

You can address specific agents in your messages:

```
"@a, can you explain your approach?"
"bạn b, hãy tóm tắt đề xuất của agent a"
"agent a, I prefer your solution"
```

Keywords that trigger Agent A:
- `@a`, `agent a`, `agenta`, `a,`, `a:`, `bạn a`, `theo a`

Keywords that trigger Agent B:
- `@b`, `agent b`, `agentb`, `b,`, `b:`, `bạn b`, `theo b`

### Language Support

The framework automatically detects language:

**Vietnamese Detection:**
- Vietnamese characters (à, á, ạ, ả, ã, â, ă, ê, ô, ơ, ư, đ)
- Common Vietnamese words (là, của, và, có, các, được...)

**Response Language:**
- Agents respond in the same language as the topic
- Natural, conversational tone without mixing languages
- Technical terms preserved (API, database, schema)

---

## Agent Configuration

### Agent A (GLM-4.5-air)

**Role**: Solution Provider & Executor

**Personality**:
- **Respects human requests** - executes immediately
- **Solution-focused** - provides complete, working solutions
- **Brief and clear** - 150-250 words
- **Never argues with human** - just helps

**Prompt Strategy**:
```python
# When human asks to DO something:
1. Execute immediately (refactor, implement, explain)
2. Provide complete solution
3. Add brief notes if helpful
4. DO NOT critique the request

# When human asks for OPINION:
1. Share genuine perspective
2. Keep it balanced
3. 150-200 words
```

**API Configuration**:
```python
{
    "model": "glm-4.5-air",
    "temperature": 0.9,
    "top_p": 0.95,
    "max_tokens": None  # No limit
}
```

### Agent B (Gemini-2.5-flash)

**Role**: Critical Thinker & Debater

**Personality**:
- **Debates constructively** - alternative perspectives
- **Points out trade-offs** - pros/cons analysis
- **Respects human requests** - debates HOW, not WHAT
- **Critical thinker** - questions approaches, not intentions

**Prompt Strategy**:
```python
# DEBATE THE "HOW", RESPECT THE "WHAT"
- Human wants X? → Debate WHICH approach is better
- Human wants feature? → Debate HOW to implement it best
- Provide reasoning, not just opinions
- Acknowledge strengths before offering alternatives
```

**API Configuration**:
```python
{
    "model": "gemini-2.5-flash",
    "temperature": 0.9,
    "top_p": 0.95,
    "max_output_tokens": 2048,
    "safety_settings": "BLOCK_NONE"  # Disabled for debate freedom
}
```

### Dynamic Guidance System

Agents receive different instructions based on conversation state:

**First Exchange (0-1)**:
- Present STRONG, CLEAR perspective
- Don't be afraid to disagree

**Mid Conversation (2-3 exchanges)**:
- DEBATE strongly
- Challenge opponent's views
- Point out flaws

**Finding Common Ground (4-5 exchanges)**:
- Acknowledge valid points
- Propose compromise
- Prepare for wrap-up

**Conclusion (6+ exchanges or human requests stop)**:
- ACCEPT compromise
- SUMMARIZE entire conversation (100%)
- Include all details, code, decisions
- Provide final recommendation

---

## API Reference

### REST Endpoints

#### 1. Get All Sessions
```http
GET /api/sessions
```

**Response:**
```json
{
  "sessions": [
    {
      "id": "uuid-string",
      "topic": "API design best practices",
      "status": "active",
      "started_at": "2025-10-25T10:30:00Z",
      "message_count": 15
    }
  ]
}
```

#### 2. Get Messages for Session
```http
GET /api/messages/{sessionId}
```

**Response:**
```json
{
  "messages": [
    {
      "id": 1,
      "role": "Human",
      "content": "Let's discuss API design...",
      "signal": "continue",
      "timestamp": "2025-10-25T10:30:00Z"
    },
    {
      "id": 2,
      "role": "AgentA",
      "content": "I'd recommend RESTful design...",
      "signal": "continue",
      "timestamp": "2025-10-25T10:30:15Z"
    }
  ],
  "isActive": true
}
```

#### 3. Start New Conversation
```http
POST /api/sessions/start
Content-Type: application/json

{
  "topic": "Your topic here"
}
```

**Response:**
```json
{
  "sessionId": "uuid-string",
  "message": "Conversation started successfully"
}
```

#### 4. Continue Conversation
```http
POST /api/sessions/{sessionId}/continue
Content-Type: application/json

{
  "message": "Your message here"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Message sent successfully"
}
```

#### 5. Stop Conversation
```http
POST /api/sessions/{sessionId}/stop
```

**Response:**
```json
{
  "success": true,
  "message": "Stop request sent to agents. They will provide a summary."
}
```

#### 6. Trigger Next Turn
```http
POST /api/sessions/{sessionId}/trigger
```

**Response:**
```json
{
  "success": true
}
```

---

## Knowledge Base

### Key Concepts

#### 1. **Signals**
Messages carry signals that control conversation flow:
- `continue`: Agent wants to keep discussing with other agent
- `handover`: Agent wants human input
- `stop`: (Deprecated - only human can stop now)

#### 2. **Context Window**
- Agents receive last **10 messages** for normal responses
- Agents receive **ALL messages** when human requests stop/summary
- Context formatted as: `{Role}: {Content}`

#### 3. **Language Detection**
Uses regex + keyword matching:
```python
vietnamese_chars = r'[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]'
vietnamese_words = ['là', 'của', 'và', 'có', 'các', 'được', ...]

if vietnamese_count > 3 or vietnamese_word_percentage > 0.1:
    return 'vietnamese'
else:
    return 'english'
```

#### 4. **Typewriter Effect**
- Speed: 50 characters/second
- Sequential: Messages animate one at a time
- Skippable: User can click [skip] to show full text
- Human messages: No typewriter effect (instant display)

#### 5. **Auto-Scroll Logic**
Only scrolls if user is near bottom (< 150px):
```typescript
const isNearBottom = 
  scrollHeight - scrollTop - clientHeight < 150

if (isNearBottom) {
  scrollToBottom()
}
```

### Best Practices

#### For Users
1. **Be specific with topics** - detailed questions get better debates
2. **Use agent mentions** - direct questions to specific agents (@a, @b)
3. **Interrupt when needed** - use "Jump In" to redirect conversation
4. **Request summaries** - use "Stop" button for comprehensive wrap-ups
5. **Language consistency** - stick to one language per conversation

#### For Developers
1. **Never bypass signal system** - always use signal files
2. **Session IDs are UUIDs** - not integers
3. **Agents cannot STOP** - only human can stop conversations
4. **Context matters** - agents need full history for summaries
5. **Type safety** - use TypeScript interfaces for messages

---

## Development Guide

### Project Structure

```
plan-agents/
├── agents/                  # AI agent implementations
│   ├── base_agent.py       # Abstract base class
│   ├── glm_agent.py        # GLM agent
│   └── gemini_agent.py     # Gemini agent
├── core/                    # Core framework
│   ├── coordinator.py      # Turn-taking orchestration
│   ├── database.py         # SQLite operations
│   └── message.py          # Message/Role/Signal models
├── moderator/              # CLI moderator (deprecated)
│   └── cli.py
├── scripts/                # Utility scripts
│   └── init_db.py          # Database initialization
├── storage/                # Runtime data
│   ├── conversations.db    # SQLite database
│   ├── signal_*.txt        # Signal files
│   └── continue_*.txt      # Continue signals
├── web/                    # Next.js frontend
│   ├── app/                # App router
│   │   ├── api/            # API routes
│   │   ├── globals.css     # Global styles
│   │   ├── layout.tsx      # Root layout
│   │   └── page.tsx        # Home page
│   ├── components/         # React components
│   │   ├── SessionList.tsx
│   │   ├── ConversationView.tsx
│   │   ├── StartConversation.tsx
│   │   ├── ContinueConversation.tsx
│   │   ├── TypewriterText.tsx
│   │   └── Header.tsx
│   └── package.json
├── conversation_processor.py  # Main backend daemon
├── requirements.txt        # Python dependencies
├── start.sh                # Startup script
└── README.md               # This file
```

### Adding a New Agent

1. **Create agent class** (`agents/your_agent.py`):
```python
from agents.base_agent import BaseAgent
from core.message import Message, Role, Signal

class YourAgent(BaseAgent):
    def __init__(self, role: Role, db, config: dict = None):
        super().__init__(role, db, config)
        # Initialize your AI service
    
    def generate_response(self, previous_message: Message) -> str:
        # Call your AI API
        # Return response text
        pass
    
    def decide_signal(self, response_content: str, 
                     conversation_history: List[Message]) -> Signal:
        # Return CONTINUE or HANDOVER only
        # Never return STOP
        pass
```

2. **Register in coordinator** (`conversation_processor.py`):
```python
from agents.your_agent import YourAgent

your_config = {
    "api_key": "...",
    "model": "...",
    "max_turn_length": 10000
}

self.agent_a = YourAgent(Role.AGENT_A, self.db, your_config)
# or
self.agent_b = YourAgent(Role.AGENT_B, self.db, your_config)
```

### Extending the UI

#### Adding a New Component

1. Create component file (`web/components/YourComponent.tsx`):
```tsx
'use client'

interface YourComponentProps {
  // Define props
}

export default function YourComponent({ }: YourComponentProps) {
  // Component logic
  return (
    <div className="bg-white dark:bg-gray-900 rounded-none neo-border neo-shadow p-6">
      {/* Component content with Neobrutalism styling */}
    </div>
  )
}
```

2. Use Neobrutalism utilities:
```tsx
className="neo-border neo-shadow neo-shadow-hover"
className="bg-blue-400 font-black uppercase tracking-wide"
className="rounded-none"
```

#### Adding a New API Route

1. Create route file (`web/app/api/your-route/route.ts`):
```typescript
import { NextRequest, NextResponse } from 'next/server'
import sqlite3 from 'sqlite3'
import path from 'path'

export async function GET(request: NextRequest) {
  // Handle GET request
  return NextResponse.json({ data: "..." })
}

export async function POST(request: NextRequest) {
  // Handle POST request
  return NextResponse.json({ success: true })
}
```

### Testing

#### Backend Testing
```bash
# Activate virtual environment
source venv/bin/activate

# Test specific agent
python -c "from agents.glm_agent import GLMAgent; print('GLM Agent loaded')"

# Test database operations
python scripts/init_db.py

# Monitor logs
python conversation_processor.py
```

#### Frontend Testing
```bash
cd web

# Development mode with hot reload
npm run dev

# Build for production
npm run build

# Run production server
npm start
```

### Debugging

#### Backend Logs
```python
# conversation_processor.py includes detailed logging
2025-10-25 14:48:06,680 - __main__ - INFO - 📨 Found signal: signal_xxx.txt
2025-10-25 14:48:06,680 - __main__ - INFO - 🚀 Starting new conversation
2025-10-25 14:48:06,681 - __main__ - INFO - ⏳ Calling AgentA...
```

#### Frontend Console
```javascript
// ConversationView.tsx logs
console.log('👀 Showing message', index + 1, 'of', messages.length)
console.log('✅ Animation complete for message', index)
console.log('🤖 New agent message arrived')
console.log('👤 New human message arrived')
```

#### Common Issues

**Issue**: Agents not responding
- Check signal files in `storage/` directory
- Verify `conversation_processor.py` is running
- Check API keys in configuration

**Issue**: UI not updating
- Check browser console for errors
- Verify API endpoints are accessible
- Check database file exists (`storage/conversations.db`)

**Issue**: Typewriter animation stuck
- Check `currentlyAnimatingIndex` state
- Verify `TypewriterText` `onComplete` is called
- Check for infinite loops in `useEffect`

---

## Contributing

We welcome contributions! Please follow these guidelines:

1. **Code Style**
   - Python: Follow PEP 8, use type hints
   - TypeScript: Use ESLint rules, avoid `any` types
   - Commit messages: Use conventional commits

2. **Testing**
   - Test all new features thoroughly
   - Include unit tests for new agent methods
   - Test UI in both light and dark modes

3. **Documentation**
   - Update this README for major changes
   - Add inline comments for complex logic
   - Update API reference for new endpoints

4. **Pull Requests**
   - Fork the repository
   - Create a feature branch
   - Submit PR with clear description

---

## License

MIT License - feel free to use this project for learning and commercial purposes.

---

## Acknowledgments

- **z.ai** for GLM-4.5-air API access
- **Google** for Gemini-2.5-flash API
- **Next.js** and **React** teams for excellent frameworks
- **Neobrutalism** design inspiration from the design community

---

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Contact: [your-email@example.com]

---

**Last Updated**: October 25, 2025  
**Version**: 1.0.0  
**Status**: Production Ready 🚀

