"""
Base agent class for AI agents in the collaboration framework.
"""

from abc import ABC, abstractmethod
from typing import Optional
from datetime import datetime
import logging

from core.message import Message, Role, Signal
from core.database import Database


logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Abstract base class for AI agents."""
    
    def __init__(self, role: Role, db: Database, config: dict = None):
        self.role = role
        self.db = db
        self.config = config or {}
        self.max_response_length = self.config.get("max_turn_length", 5000)
        self.rag_chain = None  # RAG chain for querying codebase
        
        logger.info(f"Initialized {self.role.value}")
    
    @abstractmethod
    def generate_response(self, previous_message: Message) -> str:
        """
        Generate a response based on the previous message.
        
        This method should be implemented by each specific agent.
        It should contain the AI logic for generating responses.
        
        Args:
            previous_message: The message to respond to
            
        Returns:
            The generated response content
        """
        pass
    
    @abstractmethod
    def decide_signal(self, response_content: str, conversation_history: list) -> Signal:
        """
        Decide what signal to send with the response.
        
        Args:
            response_content: The response that will be sent
            conversation_history: List of previous messages
            
        Returns:
            The signal to use (CONTINUE, STOP, or HANDOVER)
        """
        pass
    
    def respond_to(self, previous_message: Message) -> Message:
        """
        Main method to generate and format a complete response.
        
        Args:
            previous_message: The message to respond to
            
        Returns:
            A complete Message object with the agent's response
        """
        logger.info(f"{self.role.value} processing message from {previous_message.role.value}")
        
        # Get conversation history for context
        conversation_history = self.db.get_messages(previous_message.session_id)
        
        # Generate response content
        response_content = self.generate_response(previous_message)
        
        # Optional: Log if response is very long (but don't truncate)
        if len(response_content) > self.max_response_length:
            logger.info(f"{self.role.value} response is {len(response_content)} chars (longer than suggested {self.max_response_length})")
        
        # Decide signal
        signal = self.decide_signal(response_content, conversation_history)
        
        # Create message
        message = Message(
            session_id=previous_message.session_id,
            role=self.role,
            content=response_content,
            signal=signal,
            timestamp=datetime.utcnow()
        )
        
        logger.info(f"{self.role.value} generated response with signal '{signal.value}'")
        
        return message
    
    def get_conversation_context(self, session_id: str, max_messages: Optional[int] = 10) -> str:
        """
        Get formatted conversation history for context.
        
        Args:
            session_id: The session to get context from
            max_messages: Maximum number of recent messages to include (None = all messages)
            
        Returns:
            Formatted string of conversation history
        """
        messages = self.db.get_messages(session_id)
        
        # If max_messages is None, include ALL messages (for comprehensive summaries)
        if max_messages is None:
            recent_messages = messages
        else:
            recent_messages = messages[-max_messages:] if len(messages) > max_messages else messages
        
        context = []
        for msg in recent_messages:
            context.append(f"{msg.role.value}: {msg.content}")
        
        return "\n\n".join(context)
    def query_rag(self, query: str) -> str:
        """
        Query the RAG system for context.

        Args:
            query: The question to ask the RAG system

        Returns:
            Relevant documents from the RAG system, or None if RAG is not available
        """
        if not self.rag_chain:
            return None

        try:
            logger.info(f"{self.role.value} querying RAG: {query}")
            # Use retriever to get relevant documents directly (no LLM call)
            docs = self.rag_chain.get_relevant_documents(query)
            # Format documents into readable context
            context_parts = []
            for i, doc in enumerate(docs, 1):
                context_parts.append(f"[Document {i}]\n{doc.page_content}\n")
            return "\n".join(context_parts) if context_parts else None
        except Exception as e:
            logger.error(f"RAG query failed: {e}")
            return None

