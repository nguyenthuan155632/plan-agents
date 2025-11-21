# AI Planning Agents - System Architecture

## System Overview

```mermaid
flowchart TB
    subgraph Frontend["🌐 Next.js Frontend (web/)"]
        UI[Page.tsx]
        SC[StartConversation]
        CV[ConversationView]
        CC[ContinueConversation]
        CU[CodebaseUpload]
        API["/api/codebase"]
    end

    subgraph Backend["⚙️ Python Backend"]
        CP[ConversationProcessor]
        DB[(SQLite Database)]
        COORD[Coordinator]
    end

    subgraph Agents["🤖 AI Agents"]
        AA[Agent A<br/>GLM-4.6]
        AB[Agent B<br/>GLM/Gemini]
        BASE[LLMAgentBase]
    end

    subgraph RAG["📚 RAG System (rag/)"]
        RS[rag_system.py]
        EMB[Embeddings<br/>all-MiniLM-L6-v2]
        VS[(FAISS<br/>VectorStore)]
        CB[codebase.json]
    end

    UI --> SC & CV & CC & CU
    CU --> API
    API --> CB
    API --> RS

    SC -->|"signal_*.txt"| CP
    CC -->|"continue_*.txt"| CP

    CP --> DB
    CP --> COORD
    CP -->|Load RAG| RS

    COORD --> AA & AB
    AA & AB --> BASE
    BASE -->|Query| RS

    RS --> EMB --> VS
    VS -->|Similarity Search| RS
    CB --> RS
```

## Conversation Flow

```mermaid
sequenceDiagram
    participant U as User
    participant FE as Frontend
    participant FS as File System
    participant CP as ConversationProcessor
    participant C as Coordinator
    participant A as Agent A
    participant B as Agent B
    participant RAG as RAG System

    U->>FE: Enter task/question
    FE->>FS: Create signal_<session>.txt
    FE->>FE: Poll for new messages

    loop Monitor Loop
        CP->>FS: Check for signal files
        CP->>FS: Delete signal file
    end

    CP->>C: process_turn(session, message)
    C->>A: respond_to(message)
    A->>RAG: query_rag(content)
    RAG-->>A: Relevant code context
    A->>A: Generate response with context
    A-->>C: Response + Signal
    C->>CP: Save message to DB

    alt Signal = CONTINUE
        C->>B: respond_to(message)
        B->>RAG: query_rag(content)
        RAG-->>B: Relevant code context
        B->>B: Generate response with context
        B-->>C: Response + Signal
    end

    alt Signal = HANDOVER
        C-->>FE: Wait for human input
        U->>FE: Continue / Stop
        FE->>FS: Create continue_<session>.txt
    end

    FE->>CP: Poll messages
    CP-->>FE: Return messages
    FE->>U: Display conversation
```

## RAG Pipeline

```mermaid
flowchart LR
    subgraph Input["📥 Input"]
        JSON[Repomix JSON]
        MD[Markdown]
        TXT[Text]
    end

    subgraph Processing["⚙️ Processing"]
        LOAD[Load Documents]
        SPLIT[Text Splitter<br/>chunk_size=2000]
        EMBED[Sentence Transformer<br/>all-MiniLM-L6-v2]
    end

    subgraph Storage["💾 Storage"]
        FAISS[(FAISS Index)]
        CACHE[vectorstore_cache/]
    end

    subgraph Query["🔍 Query"]
        Q[User Question]
        RET[Retriever<br/>top_k=4]
        CTX[Relevant Context]
    end

    JSON & MD & TXT --> LOAD
    LOAD --> SPLIT --> EMBED --> FAISS
    FAISS <--> CACHE

    Q --> RET
    FAISS --> RET
    RET --> CTX
```

## Agent Debate Flow

```mermaid
stateDiagram-v2
    [*] --> UserInput: User submits task

    UserInput --> AgentA: Process turn

    AgentA --> QueryRAG_A: Has RAG chain?
    QueryRAG_A --> GenerateA: Add codebase context
    GenerateA --> DecideSignal_A: Generate response

    DecideSignal_A --> AgentB: CONTINUE
    DecideSignal_A --> WaitHuman: HANDOVER (2+ exchanges)

    AgentB --> QueryRAG_B: Has RAG chain?
    QueryRAG_B --> GenerateB: Add codebase context
    GenerateB --> DecideSignal_B: Generate response

    DecideSignal_B --> AgentA: CONTINUE
    DecideSignal_B --> WaitHuman: HANDOVER

    WaitHuman --> UserInput: User continues
    WaitHuman --> Summary: User requests STOP

    Summary --> [*]: Conversation ends
```

## File Structure

```
plan-agents/
├── web/                          # Next.js Frontend
│   ├── app/
│   │   ├── page.tsx              # Main planning page
│   │   └── api/codebase/         # Codebase upload API
│   └── components/
│       ├── StartConversation.tsx
│       ├── ConversationView.tsx
│       ├── ContinueConversation.tsx
│       └── CodebaseUpload.tsx
│
├── agents/                       # AI Agents
│   ├── base_agent.py             # Base class with RAG query
│   ├── glm_agent.py              # GLM (z.ai) agent
│   ├── gemini_agent.py           # Google Gemini agent
│   └── shared/
│       ├── llm_agent_base.py     # Shared LLM logic + RAG integration
│       └── prompts.py            # System prompts
│
├── core/                         # Core Infrastructure
│   ├── coordinator.py            # Turn management
│   ├── database.py               # SQLite operations
│   └── message.py                # Message/Signal types
│
├── rag/                          # RAG System
│   ├── rag_system.py             # Main RAG logic
│   ├── embeddings.py             # Local embeddings
│   ├── config.py                 # RAG configuration
│   └── codebase.json             # Uploaded codebase (gitignored)
│
├── storage/                      # Runtime Data
│   ├── signal_*.txt              # New conversation signals
│   ├── continue_*.txt            # Continue conversation signals
│   └── conversations.db          # SQLite database
│
├── conversation_processor.py     # Main backend process
├── .env                          # Configuration
└── requirements.txt              # Python dependencies
```

## Key Components

| Component | Purpose |
|-----------|---------|
| **ConversationProcessor** | Main loop monitoring signals, manages agents and RAG |
| **Coordinator** | Orchestrates turn-taking between agents |
| **LLMAgentBase** | Shared logic for all LLM agents, includes RAG query |
| **RAG System** | Retrieves relevant code context from uploaded codebase |
| **FAISS VectorStore** | Stores embeddings for similarity search |
| **Signal Files** | IPC mechanism between frontend and backend |
