# 🚀 Flexible Planning System - User Guide

## Overview

The new **Flexible Planning System** transforms your AI planning agents from static, rigid responders into intelligent, context-aware assistants similar to **Cursor Plan** or **Claude Code Plan mode**.

### What's New?

**Before (Static):**
- Fixed prompts for all tasks
- Generic questions regardless of codebase
- No understanding of project structure
- Same approach for simple bugs and complex features

**After (Dynamic & Intelligent):**
- ✅ **Task-aware** - Recognizes feature vs refactor vs debug
- ✅ **Codebase-aware** - Detects tech stack, patterns, and structure
- ✅ **Context-specific** - References actual files and code
- ✅ **Complexity-adjusted** - Different planning depth for simple vs complex tasks
- ✅ **Actionable output** - Generates executable plans with file-level steps

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Request                             │
│         "Add authentication to the app"                     │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│           1. Task Analyzer                                   │
│  ┌──────────────────────────────────────────────┐           │
│  │ • Classify: feature/refactor/debug/arch      │           │
│  │ • Extract: files, functions, requirements    │           │
│  │ • Detect: language (EN/VI)                   │           │
│  │ • Estimate: complexity level                 │           │
│  └──────────────────────────────────────────────┘           │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│         2. Codebase Intelligence (RAG++)                     │
│  ┌──────────────────────────────────────────────┐           │
│  │ • Query RAG for relevant files               │           │
│  │ • Detect tech stack (React, Python, etc.)    │           │
│  │ • Find existing patterns                     │           │
│  │ • Analyze dependencies                       │           │
│  └──────────────────────────────────────────────┘           │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│         3. Dynamic Prompt Generator                          │
│  ┌──────────────────────────────────────────────┐           │
│  │ • Generate context-aware system prompts      │           │
│  │ • Include tech stack context                 │           │
│  │ • Reference specific files/patterns          │           │
│  │ • Adjust complexity (simple/moderate/complex)│           │
│  └──────────────────────────────────────────────┘           │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│         4. Agent Planning Discussion                         │
│  ┌──────────────────────────────────────────────┐           │
│  │ Agent A: Propose solution with context       │           │
│  │ Agent B: Critique & alternative              │           │
│  │ Human: Guide & decide                        │           │
│  └──────────────────────────────────────────────┘           │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│         5. Execution Plan Generator                          │
│  ┌──────────────────────────────────────────────┐           │
│  │ • Extract key decisions from discussion      │           │
│  │ • Generate file-level action steps           │           │
│  │ • Create testing strategy                    │           │
│  │ • Estimate complexity & risks                │           │
│  └──────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. Task Analyzer (`agents/shared/task_analyzer.py`)

**Purpose:** Understands what the user wants to do.

**Features:**
- Classifies task types: `feature`, `refactor`, `debug`, `architecture`, `optimization`, `testing`
- Extracts entities: file paths, function names, components, APIs
- Detects language: English or Vietnamese
- Estimates complexity: `simple`, `moderate`, `complex`

**Example:**
```python
from agents.shared.task_analyzer import TaskAnalyzer

context = TaskAnalyzer.analyze("Add authentication using NextAuth.js")

print(context.task_type)        # TaskType.FEATURE
print(context.complexity)       # ComplexityLevel.SIMPLE
print(context.language)         # "english"
print(context.keywords)         # ["add", "authentication", "nextauth", ...]
print(context.entities)         # {"files": [...], "functions": [...]}
```

---

### 2. Codebase Intelligence (`agents/shared/codebase_intelligence.py`)

**Purpose:** Understands your codebase structure and patterns.

**Features:**
- **Tech stack detection**: Automatically identifies React, Next.js, Python, FastAPI, SQLite, etc.
- **Pattern recognition**: Detects MVC, microservices, component-based, RAG architectures
- **File analysis**: Groups files by type and purpose
- **Dependency tracking**: Identifies libraries and their usage

**Example:**
```python
from agents.shared.codebase_intelligence import CodebaseIntelligence

intel = CodebaseIntelligence(rag_chain)
structure = intel.analyze_codebase()

print(structure.tech_stack.languages)   # ["python", "typescript"]
print(structure.tech_stack.frameworks)  # ["nextjs", "react", "fastapi"]
print(structure.patterns)               # ["component-based", "rag"]

# Get task-specific context
context = intel.get_relevant_context(
    "Add authentication",
    "feature"
)
print(context.related_files)           # Files relevant to auth
print(context.suggested_approach)      # Context-based suggestions
```

---

### 3. Dynamic Prompt Generator (`agents/shared/prompt_generator.py`)

**Purpose:** Generates intelligent, context-aware prompts for each agent.

**Features:**
- **Task-specific guidance**: Different prompts for features vs refactors vs debugging
- **Codebase integration**: References actual files and tech stack
- **Complexity-adjusted**: Simple tasks get concise prompts, complex ones get detailed structure
- **Agent-specific**: Agent A proposes, Agent B critiques

**Example Comparison:**

**Old Static Prompt:**
```
You are Agent A. Provide a solution.
- Be concise
- Include code if needed
```

**New Dynamic Prompt (Feature Implementation):**
```
You are Agent A - a collaborative planning assistant.

🎯 TASK TYPE: Feature Implementation
**Your focus:** Propose a concrete implementation plan
- Break down the feature into components/modules
- Identify which files need to be created/modified
- Suggest data models, APIs, or UI components needed
- Consider integration points with existing code

📚 CODEBASE CONTEXT:
**Tech Stack:** Languages: typescript, python | Frameworks: nextjs, react
**Architecture:** component-based, rag
**Relevant Files:** `web/app/page.tsx`, `agents/base_agent.py`, ...
**Suggestion:** Follow existing component patterns in web/components/

📝 PLANNING STRUCTURE (Simple Task):
1. **Quick Analysis** (1-2 sentences)
2. **Proposed Solution** (concise approach)
3. **Implementation Note** (key file/function to modify)

✅ GOOD RESPONSES:
- "Based on the existing RAG system in `rag/rag_system.py`, we can extend it by..."
- "Looking at `web/components/`, I suggest creating a new component similar to..."
```

---

### 4. Execution Plan Generator (`agents/shared/execution_plan_generator.py`)

**Purpose:** Converts planning discussions into actionable steps.

**Features:**
- **Decision extraction**: Identifies key agreements from conversation
- **Step generation**: Creates ordered, dependency-aware action items
- **File tracking**: Lists all files that need changes
- **Testing strategy**: Suggests appropriate testing approach
- **Complexity estimation**: Estimates time/effort required

**Example Output:**
```markdown
# 📋 Execution Plan

## 📝 Summary
Implement authentication using NextAuth.js with Google and email providers.

## ✅ Key Decisions
1. Use NextAuth.js for robust, production-ready authentication
2. Implement middleware.ts for route protection
3. Add RBAC (Role-Based Access Control) in phase 2
4. Use Redis for session storage in production

## 🔨 Implementation Steps

### Step 1: Install required dependencies
**Type:** install_dependency
**Code:**
```bash
npm install next-auth
```

### Step 2: Create authentication API route
**Type:** create_file
**File:** `app/api/auth/[...nextauth]/route.ts`

### Step 3: Add SessionProvider to layout
**Type:** modify_file
**File:** `app/layout.tsx`

### Step 4: Create authentication middleware
**Type:** create_file
**File:** `middleware.ts`

## 📁 Files to Change
- `app/api/auth/[...nextauth]/route.ts`
- `app/layout.tsx`
- `middleware.ts`
- `components/auth/LoginButton.tsx`

## 🧪 Testing Strategy
- Unit tests for authentication logic
- Integration tests for OAuth flows
- E2E tests for login/logout flows

## 📊 Estimated Complexity: **Medium (3-6 hours)**
```

---

## Usage Guide

### Basic Usage (Automatic)

The planning system is **automatically enabled** in the existing agent workflow. Just use the system normally:

```python
# In your conversation flow, the agents will:
# 1. Analyze the task automatically
# 2. Query codebase intelligence
# 3. Generate dynamic prompts
# 4. Provide context-aware responses

# No changes needed to existing code!
```

### Advanced Usage (Programmatic)

#### Analyze a Task

```python
from agents.shared.task_analyzer import TaskAnalyzer

context = TaskAnalyzer.analyze("Refactor UserService to use dependency injection")

print(f"Task Type: {context.task_type.value}")
print(f"Complexity: {context.complexity.value}")
print(f"Language: {context.language}")
print(f"Files mentioned: {context.entities.get('files', [])}")
```

#### Generate Dynamic Prompts

```python
from agents.shared.prompts import generate_dynamic_prompt
from core.message import Role

prompt = generate_dynamic_prompt(
    role=Role.AGENT_A,
    task_description="Add real-time notifications",
    codebase_structure=structure,  # from CodebaseIntelligence
    relevant_context=context        # task-specific context
)

print(prompt)  # Context-aware prompt ready for LLM
```

#### Create Execution Plans

```python
from agents.shared.prompts import create_execution_plan

# After agents finish planning discussion
messages = [
    {"role": "HUMAN", "content": "Add auth"},
    {"role": "AGENT_A", "content": "Use NextAuth.js..."},
    {"role": "AGENT_B", "content": "Consider JWT..."}
]

plan_markdown = create_execution_plan(
    conversation_messages=messages,
    original_request="Add authentication",
    language="english"  # or "vietnamese"
)

print(plan_markdown)  # Ready to save or display
```

---

## Configuration

### Enable/Disable Dynamic Prompts

In `agents/shared/llm_agent_base.py`:

```python
# Enable (default)
agent = LLMAgentBase(
    role=Role.AGENT_A,
    db=database,
    config={'use_dynamic_prompts': True}
)

# Disable (use old static prompts)
agent = LLMAgentBase(
    role=Role.AGENT_A,
    db=database,
    config={'use_dynamic_prompts': False}
)
```

---

## Examples

### Example 1: Feature Request

**Input:**
```
User: "Add a dark mode toggle to the settings page"
```

**System Processing:**
1. Task Analyzer → Type: `feature`, Complexity: `simple`
2. Codebase Intelligence → Detects React, finds existing theme components
3. Prompt Generator → Creates feature-specific prompt with React context

**Agent A Response:**
```
Based on the existing theme system in `web/components/ThemeProvider.tsx`,
I suggest:

1. Add a toggle component in `components/settings/DarkModeToggle.tsx`
2. Use the existing `useTheme` hook
3. Persist preference in localStorage

This integrates cleanly with the current setup.
```

### Example 2: Refactoring

**Input:**
```
User: "Refactor the database.py to use connection pooling"
```

**System Processing:**
1. Task Analyzer → Type: `refactor`, Complexity: `moderate`
2. Codebase Intelligence → Finds `core/database.py`, detects SQLite
3. Prompt Generator → Creates refactor-specific prompt

**Agent A Response:**
```
Looking at `core/database.py:15`, the current implementation uses
direct sqlite3.connect(). I recommend:

1. Replace with SQLAlchemy connection pool
2. Add pool size configuration
3. Update existing queries to use pooled connections

This improves performance under concurrent load while maintaining
compatibility with existing code.
```

### Example 3: Vietnamese Support

**Input:**
```
User: "Thêm tính năng xuất dữ liệu ra CSV"
```

**System Processing:**
1. Task Analyzer → Language: `vietnamese`, Type: `feature`
2. Generates Vietnamese-language prompts and execution plan

**Agent A Response:**
```
Dựa vào cấu trúc hiện tại của `core/database.py`, tôi đề xuất:

1. Tạo function export_to_csv() trong database.py
2. Sử dụng thư viện pandas để format data
3. Thêm button "Xuất CSV" trong UI

Code mẫu:
...
```

---

## Benefits

### For Developers

✅ **Faster Planning** - Agents understand your codebase structure
✅ **Better Suggestions** - References actual files and patterns
✅ **Actionable Output** - Get executable plans, not just discussions
✅ **Consistency** - Follows your existing code conventions

### For Teams

✅ **Onboarding** - New members learn codebase structure through planning
✅ **Documentation** - Execution plans serve as implementation guides
✅ **Standards** - Enforces consistent architectural patterns

---

## Testing

Run the test suite to verify the system:

```bash
python test_planning_standalone.py
```

Expected output:
```
======================================================================
  🚀 FLEXIBLE PLANNING SYSTEM - STANDALONE TESTS
======================================================================

✓ Task Analyzer working correctly!
✓ Codebase Intelligence working correctly!
✓ Prompt Generator working correctly!
✓ Execution Plan Generator working correctly!

✅ ALL TESTS PASSED
```

---

## Troubleshooting

### Issue: Dynamic prompts not being used

**Solution:** Check the configuration:
```python
# Verify in agent initialization
print(agent.use_dynamic_prompts)  # Should be True
```

### Issue: No codebase context in responses

**Solution:** Ensure RAG is loaded:
```python
# Check if RAG chain exists
print(agent.rag_chain is not None)  # Should be True
```

### Issue: Task type is always "unknown"

**Solution:** Add more keywords to `task_analyzer.py`:
```python
TASK_PATTERNS = {
    TaskType.YOUR_TYPE: [
        r'\b(your|keywords)\b',
    ]
}
```

---

## Architecture Decisions

### Why Task Analyzer?
- LLMs don't consistently classify tasks themselves
- Regex patterns are fast and deterministic
- Easy to extend with new task types

### Why Codebase Intelligence?
- RAG alone doesn't provide structured analysis
- Tech stack detection enables context-specific guidance
- Pattern recognition helps suggest consistent solutions

### Why Dynamic Prompts?
- Static prompts don't scale across diverse tasks
- Context-aware prompts improve response quality
- Reduces need for follow-up questions

### Why Execution Plans?
- Bridges gap between planning and implementation
- Provides accountability and tracking
- Useful for code review and documentation

---

## Future Enhancements

### Planned Features

1. **Interactive Plan Refinement**
   - Allow user to edit execution plan before implementation
   - Re-generate based on feedback

2. **Code Similarity Search**
   - Find similar implementations in codebase
   - Suggest copy-paste starting points

3. **Dependency Impact Analysis**
   - Warn about breaking changes
   - Suggest migration paths

4. **Multi-Language Support**
   - Add support for more languages (Spanish, French, etc.)
   - Auto-translate execution plans

5. **Integration with IDEs**
   - VSCode extension
   - IntelliJ plugin

---

## Contributing

### Adding New Task Types

1. Edit `agents/shared/task_analyzer.py`:
```python
class TaskType(Enum):
    YOUR_TYPE = "your_type"

TASK_PATTERNS = {
    TaskType.YOUR_TYPE: [
        r'\b(pattern1)\b',
        r'\b(pattern2)\b',
    ]
}
```

2. Add task-specific guidance in `agents/shared/prompt_generator.py`:
```python
TaskType.YOUR_TYPE: """
🎯 TASK TYPE: Your Type
**Your focus:** What to focus on
- Guideline 1
- Guideline 2
"""
```

### Adding Tech Stack Detection

Edit `agents/shared/codebase_intelligence.py`:
```python
TECH_PATTERNS = {
    'frameworks': {
        'your_framework': [r'import your_framework', r'from your_framework'],
    }
}
```

---

## License

This planning system is part of the AI Planning Agents project.

---

## Support

For issues, questions, or suggestions:
- Check the test file: `test_planning_standalone.py`
- Review the architecture diagram above
- Examine example outputs in this guide

**Happy Planning! 🚀**
