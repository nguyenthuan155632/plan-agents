# Contributing to Dual AI Collaboration Framework

Thank you for your interest in contributing! This document provides guidelines and best practices.

## 🌟 How to Contribute

### 1. Fork and Clone
```bash
git clone https://github.com/your-username/plan-agents.git
cd plan-agents
git checkout -b feature/your-feature-name
```

### 2. Set Up Development Environment
```bash
# Backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd web
npm install
cd ..
```

### 3. Make Your Changes

#### For Backend (Python)
- Follow **PEP 8** style guide
- Use **type hints** for all functions
- Add **docstrings** for classes and methods
- Write **unit tests** for new features

Example:
```python
def process_message(message: Message, session_id: str) -> Optional[Response]:
    """
    Process a message and generate a response.
    
    Args:
        message: The message to process
        session_id: UUID of the conversation session
        
    Returns:
        Response object or None if processing fails
    """
    # Implementation here
    pass
```

#### For Frontend (TypeScript/React)
- Follow **ESLint** rules
- Use **TypeScript** interfaces (avoid `any`)
- Follow **React hooks** best practices
- Use **Neobrutalism** design system

Example:
```tsx
interface MessageProps {
  message: Message
  isAnimating: boolean
  onComplete: () => void
}

export default function MessageComponent({ 
  message, 
  isAnimating, 
  onComplete 
}: MessageProps) {
  // Implementation here
}
```

### 4. Test Your Changes

#### Backend Testing
```bash
# Run Python scripts
python conversation_processor.py

# Test specific components
python -c "from agents.glm_agent import GLMAgent; print('OK')"

# Check database
sqlite3 storage/conversations.db ".tables"
```

#### Frontend Testing
```bash
cd web

# Development mode
npm run dev

# Build check
npm run build

# Type check
npx tsc --noEmit
```

### 5. Commit Your Changes
Follow **Conventional Commits** format:
```bash
git add .
git commit -m "feat: add support for new AI model"
git commit -m "fix: resolve auto-scroll issue in conversation view"
git commit -m "docs: update API reference for new endpoints"
```

Commit types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### 6. Push and Create Pull Request
```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:
- Clear title and description
- Screenshots for UI changes
- Test results
- Related issue numbers (if any)

## 🎯 Areas for Contribution

### High Priority
- [ ] Add more AI model integrations (Claude, GPT-4, etc.)
- [ ] Implement message export (PDF, Markdown)
- [ ] Add conversation search functionality
- [ ] Create Docker containerization
- [ ] Add unit tests for agents

### Medium Priority
- [ ] Add conversation templates
- [ ] Implement message reactions/voting
- [ ] Add dark mode toggle in UI
- [ ] Create admin dashboard
- [ ] Add multi-user support

### Low Priority
- [ ] Add emoji reactions to messages
- [ ] Implement message editing
- [ ] Add code syntax highlighting
- [ ] Create mobile-responsive design improvements
- [ ] Add keyboard shortcuts

## 📋 Code Style Guidelines

### Python
```python
# Good
def generate_response(message: Message, context: str) -> str:
    """Generate AI response based on message and context."""
    response = self.model.generate(
        prompt=f"{context}\n\n{message.content}",
        temperature=0.9
    )
    return response.strip()

# Bad
def gen_resp(msg, ctx):
    resp = self.model.generate(ctx + "\n\n" + msg.content, 0.9)
    return resp.strip()
```

### TypeScript
```typescript
// Good
interface ConversationState {
  messages: Message[]
  isActive: boolean
  currentAgent: 'AgentA' | 'AgentB' | null
}

const [state, setState] = useState<ConversationState>({
  messages: [],
  isActive: false,
  currentAgent: null
})

// Bad
const [msgs, setMsgs] = useState([])
const [active, setActive] = useState(false)
const [agent, setAgent] = useState(null)
```

### CSS (Tailwind + Neobrutalism)
```tsx
// Good - Neobrutalism style
<div className="bg-white dark:bg-gray-900 rounded-none neo-border neo-shadow p-6">
  <h2 className="text-2xl font-black text-black dark:text-white uppercase tracking-tight">
    Title
  </h2>
</div>

// Bad - Missing Neobrutalism utilities
<div className="bg-white rounded-lg shadow-md p-4">
  <h2 className="text-xl font-semibold">Title</h2>
</div>
```

## 🧪 Testing Guidelines

### Unit Tests (Python)
```python
import unittest
from agents.glm_agent import GLMAgent
from core.message import Message, Role

class TestGLMAgent(unittest.TestCase):
    def setUp(self):
        self.agent = GLMAgent(Role.AGENT_A, None, {})
    
    def test_language_detection(self):
        self.assertEqual(
            self.agent._detect_language("Hello world"),
            "english"
        )
        self.assertEqual(
            self.agent._detect_language("Xin chào"),
            "vietnamese"
        )
```

### Integration Tests (Frontend)
```typescript
describe('ConversationView', () => {
  it('should render messages correctly', () => {
    const messages = [
      { id: 1, role: 'Human', content: 'Test', signal: 'continue' }
    ]
    render(<ConversationView sessionId="test" />)
    expect(screen.getByText('Test')).toBeInTheDocument()
  })
})
```

## 🐛 Bug Reports

When reporting bugs, include:
1. **Description**: What happened vs what you expected
2. **Steps to Reproduce**: Detailed steps
3. **Environment**: OS, Python version, Node version
4. **Screenshots**: If applicable
5. **Logs**: Relevant error messages

Example:
```markdown
## Bug: Typewriter animation stuck on long messages

**Description**: When a message exceeds 1000 characters, the typewriter 
animation freezes at character 500.

**Steps to Reproduce**:
1. Start a new conversation
2. Wait for Agent A to generate a long response (1000+ chars)
3. Observe the animation stops midway

**Environment**:
- OS: macOS 14.6
- Python: 3.13.0
- Node: 18.17.0

**Screenshot**: [Attach screenshot]

**Logs**:
```
console.error: Animation timeout at index 500
```
```

## 💡 Feature Requests

When proposing features, include:
1. **Use Case**: Why is this needed?
2. **Proposed Solution**: How should it work?
3. **Alternatives**: Other approaches considered
4. **Impact**: Who benefits from this?

Example:
```markdown
## Feature: Export conversation to PDF

**Use Case**: Users want to save conversations for later reference or sharing.

**Proposed Solution**: 
- Add "Export" button in ConversationView
- Generate PDF with proper formatting
- Include timestamps and agent names

**Alternatives**:
- Export to Markdown (simpler)
- Export to JSON (for developers)

**Impact**: All users who want to archive conversations
```

## 📚 Documentation

When adding features, update:
- [ ] `DOCUMENTATION.md` - Main documentation
- [ ] `README.md` - If it affects quick start
- [ ] Inline code comments
- [ ] API reference (if adding endpoints)

## 🔍 Code Review Process

All contributions go through code review:
1. Automated checks (linting, type checking)
2. Manual review by maintainers
3. Testing in development environment
4. Approval and merge

Expect feedback on:
- Code quality and style
- Test coverage
- Documentation completeness
- Performance implications

## ❓ Questions?

- Check [DOCUMENTATION.md](DOCUMENTATION.md) first
- Open a [GitHub Discussion](https://github.com/your-repo/discussions)
- Ask in Pull Request comments

## 🎉 Thank You!

Every contribution helps make this project better. We appreciate your time and effort!

---

**Maintainers**: [List maintainer names/contacts]  
**Last Updated**: October 25, 2025
