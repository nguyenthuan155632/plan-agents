"""
Conversation analysis service for AI agents.
Analyzes conversation history and provides insights.
"""

from typing import List, Tuple
from core.message import Message, Role


class ConversationAnalyzer:
    """Analyzes conversation history to extract useful information."""
    
    @staticmethod
    def count_agent_exchanges(messages: List[Message]) -> int:
        """
        Count agent exchanges (pairs of A-B exchanges).
        
        Args:
            messages: List of messages
            
        Returns:
            Number of exchange pairs
        """
        agent_messages = [m for m in messages if m.role in [Role.AGENT_A, Role.AGENT_B]]
        return len(agent_messages) // 2
    
    @staticmethod
    def count_exchanges_since_human(messages: List[Message]) -> int:
        """
        Count exchanges since last human input.
        
        Args:
            messages: List of messages
            
        Returns:
            Number of exchanges since last human message
        """
        human_messages = [m for m in messages if m.role == Role.HUMAN]
        if not human_messages:
            return 0
        
        last_human_index = len(messages) - 1 - messages[::-1].index(human_messages[-1])
        agent_messages_since = [
            m for m in messages[last_human_index:] 
            if m.role in [Role.AGENT_A, Role.AGENT_B]
        ]
        return len(agent_messages_since) // 2
    
    @staticmethod
    def detect_human_intervention(
        message: Message,
        agent_role: Role
    ) -> Tuple[bool, bool, bool, bool]:
        """
        Detect human intervention and who they're addressing.
        
        Args:
            message: The message to analyze
            agent_role: Current agent's role
            
        Returns:
            Tuple of (wants_stop, addressing_me, addressing_other, asks_to_summarize_other)
        """
        if message.role != Role.HUMAN:
            return False, False, False, False
        
        content_lower = message.content.lower()
        
        # Check if human wants to stop
        stop_keywords = [
            'stop', 'dừng lại', 'thôi', 'đủ rồi', 'kết thúc', 
            'summarize', 'tóm tắt', 'tổng kết', '🛑'
        ]
        wants_stop = any(keyword in content_lower for keyword in stop_keywords)
        
        # Check who human is addressing
        if agent_role == Role.AGENT_A:
            my_keywords = ['agent a', 'agenta', '@a', 'a,', 'a:', 'bạn a', 'a ơi', 'theo a']
            other_keywords = ['agent b', 'agentb', '@b', 'b,', 'b:', 'bạn b', 'b ơi', 'theo b']
        else:  # AGENT_B
            my_keywords = ['agent b', 'agentb', '@b', 'b,', 'b:', 'bạn b', 'b ơi', 'theo b']
            other_keywords = ['agent a', 'agenta', '@a', 'a,', 'a:', 'bạn a', 'a ơi', 'theo a']
        
        addressing_me = any(keyword in content_lower for keyword in my_keywords)
        addressing_other = any(keyword in content_lower for keyword in other_keywords)
        
        # Check if human asks to summarize the other agent
        summarize_keywords = ['tóm tắt', 'summarize', 'tổng kết', 'cho tôi kết quả', 'kết quả cuối cùng']
        has_summarize_request = any(keyword in content_lower for keyword in summarize_keywords)
        asks_to_summarize_other = addressing_me and addressing_other and has_summarize_request
        
        return wants_stop, addressing_me, addressing_other, asks_to_summarize_other
    
    @staticmethod
    def extract_topic_from_messages(messages: List[Message]) -> str:
        """
        Extract the topic from the first human message.
        
        Args:
            messages: List of messages
            
        Returns:
            The topic string, or empty string if not found
        """
        for msg in messages:
            if msg.role == Role.HUMAN and "Let's discuss:" in msg.content:
                return msg.content.split("Let's discuss:", 1)[1].strip()
        return ""

