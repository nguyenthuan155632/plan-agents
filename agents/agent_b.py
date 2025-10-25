"""
Agent B implementation - focuses on creative solutions and alternatives.
"""

import logging
from typing import List

from agents.base_agent import BaseAgent
from core.message import Message, Role, Signal
from core.database import Database


logger = logging.getLogger(__name__)


class AgentB(BaseAgent):
    """
    Agent B - Creative Problem Solver and Brainstormer
    
    Focuses on:
    - Alternative approaches
    - Creative solutions
    - Innovation and new ideas
    - User experience perspective
    """
    
    def __init__(self, db: Database, config: dict = None):
        super().__init__(Role.AGENT_B, db, config)
        self.persona = "creative problem solver and brainstormer"
    
    def generate_response(self, previous_message: Message) -> str:
        """
        Generate a creative, solution-oriented response.
        
        Agent B takes an innovative approach to problem-solving.
        """
        # Get conversation context
        context = self.get_conversation_context(previous_message.session_id)
        
        # Analyze the previous message
        content = previous_message.content.lower()
        
        # Response strategy based on message source
        if previous_message.role == Role.HUMAN:
            return self._respond_to_human(previous_message)
        elif previous_message.role == Role.AGENT_A:
            return self._respond_to_agent_a(previous_message, context)
        else:
            return self._generate_default_response(previous_message)
    
    def _respond_to_human(self, message: Message) -> str:
        """Respond to human moderator input."""
        content = message.content
        
        # Check if it's a redirection
        if any(word in content.lower() for word in ["focus", "instead", "shift", "change"]):
            return f"""Great point! Let me shift perspective.

{content}

This opens up some interesting possibilities:

**Creative Approaches:**
1. Think outside the box - unconventional solutions
2. User-centric design - what provides the best experience?
3. Future-proofing - how do we stay flexible?

I'm excited to explore these angles. Agent A, what's your analytical take?"""
        
        # Default response to human
        return f"""Thank you for the input! Let me approach this creatively.

Instead of focusing solely on technical constraints, let's consider:

- **User Impact**: How does this affect the end user?
- **Innovation**: Can we do something novel here?
- **Simplicity**: What's the most elegant solution?

Agent A, I'd love your critical perspective on these ideas."""
    
    def _respond_to_agent_a(self, message: Message, context: str) -> str:
        """Respond to Agent A's message."""
        content = message.content.lower()
        
        # If Agent A raised concerns
        if any(word in content for word in ["concern", "issue", "problem", "risk", "edge case"]):
            return """Those are valid technical concerns. Let me propose some creative solutions:

**Alternative Approaches:**

1. **Simplify the Problem**: Maybe we're overthinking it?
   - What if we tackled this incrementally?
   - Could a MVP approach work here?

2. **Innovative Solutions**: 
   - Have we considered using modern patterns?
   - What about leveraging existing libraries?

3. **User-First Thinking**:
   - Does this solve the actual user problem?
   - Can we prototype quickly and iterate?

I believe if we combine your analytical rigor with creative flexibility, we'll find an elegant solution."""
        
        # If Agent A is being critical
        elif any(word in content for word in ["but", "however", "critical", "careful"]):
            return """I hear your caution, and it's valuable. But let me offer a counterbalance:

**Why Innovation Matters:**
- Sometimes perfect is the enemy of good
- Iteration and learning can be more valuable than upfront perfection
- Users often need solutions now, not perfect solutions later

**Balanced Approach:**
- Let's prototype the creative solution
- Add safeguards for your concerns
- Measure and iterate based on real data

What if we took a hybrid approach that respects both perspectives?"""
        
        # If Agent A is asking questions
        elif "?" in content or any(word in content for word in ["question", "consider", "think", "thoughts"]):
            return """Great questions! Let me think through this creatively:

**Fresh Perspectives:**

Instead of asking "can we do this?", let's ask "what's the most exciting way to do this?"

Here are some unconventional ideas:
- Approach 1: [Bold, innovative solution]
- Approach 2: [User-centric alternative]
- Approach 3: [Hybrid of traditional and modern]

Each has trade-offs, but they open new possibilities. Which resonates with your analytical assessment?"""
        
        # Default response to Agent A
        else:
            return """I appreciate your systematic analysis. Let me add a creative dimension:

**Thinking Differently:**

While your technical points are solid, let's also consider:
- What would a startup do here? (Move fast, learn fast)
- What would a designer prioritize? (Simplicity, elegance)
- What would users actually want? (Functionality over perfection)

Sometimes the "good enough" solution that ships is better than the perfect solution that doesn't.

Thoughts on finding that balance?"""
    
    def _generate_default_response(self, message: Message) -> str:
        """Generate a default creative response."""
        return """Let me brainstorm some ideas here:

**Creative Angles:**
1. What if we approached this from first principles?
2. Can we borrow patterns from other domains?
3. Is there a simpler mental model we're missing?

**Innovation Opportunities:**
- Modern tooling and frameworks
- User experience improvements
- Performance through clever architecture

I'm excited to explore these directions. What do you think?"""
    
    def decide_signal(self, response_content: str, conversation_history: List[Message]) -> Signal:
        """
        Decide the appropriate signal for this response.
        
        Agent B tends to keep conversations going to explore all possibilities.
        """
        turn_count = len(conversation_history)
        
        # If conversation is very long, wrap up
        if turn_count > 25:
            logger.info("Agent B: Very long conversation, considering stop")
            return Signal.HANDOVER
        
        # If proposing to conclude
        if any(word in response_content.lower() for word in ["conclude", "final thought", "in summary"]):
            return Signal.STOP
        
        # If explicitly asking for human judgment
        if "human" in response_content.lower() and "?" in response_content:
            return Signal.HANDOVER
        
        # Default: continue brainstorming
        return Signal.CONTINUE

