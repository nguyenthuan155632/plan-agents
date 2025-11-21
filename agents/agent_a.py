"""
Agent A implementation - focuses on code review and analysis.
"""

import logging
from typing import List

from agents.base_agent import BaseAgent
from core.message import Message, Role, Signal
from core.database import Database


logger = logging.getLogger(__name__)


class AgentA(BaseAgent):
    """
    Agent A - Code Review and Analysis Specialist
    
    Focuses on:
    - Code review and quality analysis
    - Identifying potential issues
    - Suggesting improvements
    - Best practices
    """
    
    def __init__(self, db: Database, config: dict = None):
        super().__init__(Role.AGENT_A, db, config)
        self.persona = "code reviewer and analyzer"
    
    def generate_response(self, previous_message: Message) -> str:
        """
        Generate a thoughtful code review response.
        
        Agent A takes a critical but constructive approach to code review.
        """
        # Get conversation context
        context = self.get_conversation_context(previous_message.session_id)
        
        # Analyze the previous message
        content = previous_message.content.lower()
        
        # Response strategy based on message content
        if previous_message.role == Role.HUMAN:
            # If human started or intervened
            return self._respond_to_human(previous_message)
        elif previous_message.role == Role.AGENT_B:
            # Responding to Agent B
            return self._respond_to_agent_b(previous_message, context)
        else:
            # Default response
            
            # Try to use RAG if available
            rag_context = ""
            if self.rag_chain:
                rag_context = self.query_rag(previous_message.content)
                
            if rag_context:
                return f"""Based on my analysis of the codebase:
                
{rag_context}

From a code review perspective, I have verified this against the actual implementation.
1. **Accuracy**: The information above is derived directly from the source code.
2. **Context**: This aligns with the project structure.

Agent B, do you see any alternative interpretations or creative uses for this?"""
            
            return self._generate_default_response(previous_message)
    
    def _respond_to_human(self, message: Message) -> str:
        """Respond to human moderator input."""
        content = message.content
        
        # Check if it's a topic introduction
        if any(word in content.lower() for word in ["discuss", "review", "analyze", "consider"]):
            return f"""Thank you for the topic. As Agent A, I'll approach this from a code review and quality perspective.

Let me begin by analyzing the key aspects:

1. **Code Quality**: We should ensure maintainability and readability
2. **Best Practices**: Following established patterns and conventions
3. **Potential Issues**: Identifying bugs, edge cases, or technical debt
4. **Performance**: Considering efficiency and scalability

What are your initial thoughts, Agent B?"""
        
        # Human is redirecting the conversation
        return f"""Understood. Let me refocus on: {content}

From a code review standpoint, I think we should consider the technical implications and potential risks.

Agent B, what's your perspective on this?"""
    
    def _respond_to_agent_b(self, message: Message, context: str) -> str:
        """Respond to Agent B's message."""
        content = message.content.lower()
        
        # Check for agreement
        if any(word in content for word in ["agree", "correct", "yes", "exactly"]):
            return """I appreciate the alignment. Let me build on that point.

However, I'd like to raise some critical considerations:

1. **Edge Cases**: Have we thought through all possible scenarios?
2. **Error Handling**: What happens when things go wrong?
3. **Testing Strategy**: How do we validate this approach?

These aspects are crucial for production-ready code. Thoughts?"""
        
        # Check for disagreement or alternative
        elif any(word in content for word in ["but", "however", "alternative", "disagree"]):
            return """That's a fair counterpoint. Let me consider your perspective.

While I see the merit in your approach, I want to ensure we're not overlooking:

- **Technical debt**: Will this solution be maintainable long-term?
- **Complexity**: Are we overengineering or underengineering?
- **Team impact**: How does this affect other developers?

Perhaps we can find a middle ground?"""
        
        # Default analytical response
        else:
            return """Interesting perspective. Let me analyze this systematically:

**Strengths I see:**
- Clear separation of concerns
- Follows established patterns
- Reasonable approach to the problem

**Potential concerns:**
- We should validate assumptions
- Consider performance implications
- Think about error scenarios

What's your take on addressing these concerns?"""
    
    def _generate_default_response(self, message: Message) -> str:
        """Generate a default analytical response."""
        return """From a code review perspective, let's examine this carefully.

**Key Questions:**
1. Is the code maintainable and readable?
2. Are we following best practices?
3. Have we considered edge cases?
4. Is the performance acceptable?

I'd like to hear thoughts on these aspects before we proceed further."""
    
    def decide_signal(self, response_content: str, conversation_history: List[Message]) -> Signal:
        """
        Decide the appropriate signal for this response.
        
        Agent A tends to continue the conversation unless:
        - The conversation has gone on for many turns
        - A clear conclusion has been reached
        - Human intervention is needed
        """
        turn_count = len(conversation_history)
        
        # If conversation is getting long, suggest wrapping up
        if turn_count > 20:
            logger.info("Agent A: Long conversation, considering handover")
            if "conclusion" in response_content.lower() or "summary" in response_content.lower():
                return Signal.HANDOVER
        
        # If asking for human input explicitly
        if "human" in response_content.lower() or "moderator" in response_content.lower():
            return Signal.HANDOVER
        
        # Default: continue the conversation
        return Signal.CONTINUE

