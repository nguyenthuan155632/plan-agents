"""
Coordination system for managing turn-taking and signal handling between agents.
"""

import time
import logging
from typing import Optional, Callable
from datetime import datetime

from core.database import Database
from core.message import Message, Session, Role, Signal


logger = logging.getLogger(__name__)


class Coordinator:
    """Manages turn-taking and coordination between AI agents."""
    
    def __init__(self, db: Database, config: dict = None):
        self.db = db
        self.config = config or {}
        self.timeout_seconds = self.config.get("timeout_seconds", 60)
        self.max_turn_length = self.config.get("max_turn_length", 500)
        self.auto_continue = self.config.get("auto_continue", True)
        
        # Callbacks for agent responses
        self.agent_callbacks = {}
    
    def register_agent(self, role: Role, callback: Callable[[Message], Message]):
        """Register an agent with a callback function."""
        self.agent_callbacks[role] = callback
        logger.info(f"Registered {role.value} with callback")
    
    def get_next_role(self, current_role: Role, last_message_content: str = "") -> Role:
        """
        Determine which agent should respond next.
        
        If human mentions a specific agent, that agent responds.
        Otherwise, alternate between agents.
        """
        if current_role == Role.HUMAN:
            # Check if human is addressing a specific agent
            content_lower = last_message_content.lower()
            
            # Keywords for Agent A
            agent_a_keywords = ['agent a', 'agenta', '@a', 'a,', 'a:', 'bạn a', 'a ơi', 'theo a']
            # Keywords for Agent B  
            agent_b_keywords = ['agent b', 'agentb', '@b', 'b,', 'b:', 'bạn b', 'b ơi', 'theo b']
            
            # Check for explicit mentions
            mentions_a = any(keyword in content_lower for keyword in agent_a_keywords)
            mentions_b = any(keyword in content_lower for keyword in agent_b_keywords)
            
            if mentions_b and not mentions_a:
                logger.info(f"🎯 Human mentioned Agent B specifically → Agent B responds")
                return Role.AGENT_B
            elif mentions_a and not mentions_b:
                logger.info(f"🎯 Human mentioned Agent A specifically → Agent A responds")
                return Role.AGENT_A
            
            # If no specific mention, default to Agent A
            logger.info(f"🎯 Human didn't mention specific agent → Agent A responds (default)")
            return Role.AGENT_A
        
        # Agent to agent: alternate
        if current_role == Role.AGENT_A:
            return Role.AGENT_B
        elif current_role == Role.AGENT_B:
            return Role.AGENT_A
        
        # Fallback
        return Role.AGENT_A
    
    def wait_for_signal(self, session_id: str, expected_role: Role, timeout: Optional[int] = None) -> Optional[Message]:
        """Wait for a specific agent to send a message with a signal."""
        timeout = timeout or self.timeout_seconds
        start_time = time.time()
        
        last_checked_id = 0
        messages = self.db.get_messages(session_id)
        if messages:
            last_checked_id = messages[-1].id or 0
        
        while time.time() - start_time < timeout:
            messages = self.db.get_messages(session_id)
            
            # Check if there's a new message
            if messages and (messages[-1].id or 0) > last_checked_id:
                last_msg = messages[-1]
                
                # Check if it's from the expected role
                if last_msg.role == expected_role:
                    logger.info(f"Received signal '{last_msg.signal.value}' from {expected_role.value}")
                    return last_msg
                
                # Check if human intervened
                if last_msg.role == Role.HUMAN:
                    logger.info("Human intervention detected")
                    return last_msg
                
                last_checked_id = last_msg.id or 0
            
            time.sleep(0.5)  # Poll every 500ms
        
        logger.warning(f"Timeout waiting for {expected_role.value}")
        return None
    
    def should_continue(self, message: Message) -> bool:
        """Check if the conversation should continue based on the signal."""
        if message.signal == Signal.STOP:
            logger.info("STOP signal received, ending conversation")
            return False
        
        if message.signal == Signal.HANDOVER:
            logger.info("HANDOVER signal received, waiting for human")
            return False
        
        return True
    
    def process_turn(self, session_id: str, current_message: Message) -> Optional[Message]:
        """Process one turn of the conversation."""
        # Check if we should continue
        if not self.should_continue(current_message):
            return None
        
        # Determine next agent (pass message content for mention detection)
        next_role = self.get_next_role(current_message.role, current_message.content)
        
        logger.info(f"🎯 Next turn: {next_role.value} (waiting for {current_message.role.value} to finish)")
        
        # Check if agent is registered
        if next_role not in self.agent_callbacks:
            logger.warning(f"{next_role.value} not registered, cannot continue")
            return None
        
        # Get agent callback
        callback = self.agent_callbacks[next_role]
        
        # Invoke agent
        try:
            logger.info(f"⏳ Calling {next_role.value}...")
            response = callback(current_message)
            
            # Validate response
            if response.role != next_role:
                logger.error(f"Agent returned wrong role: expected {next_role.value}, got {response.role.value}")
                return None
            
            # Save response to database
            logger.info(f"💾 Saving {next_role.value} response to DB...")
            response = self.db.add_message(response)
            logger.info(f"✅ {next_role.value} responded with signal '{response.signal.value}'")
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing turn for {next_role.value}: {e}", exc_info=True)
            return None
    
    def start_conversation(self, session: Session, initial_message: Message) -> None:
        """Start a new conversation session."""
        # Create session in database
        self.db.create_session(session)
        logger.info(f"Started session {session.id} with topic: {session.topic}")
        
        # Add initial message
        initial_message = self.db.add_message(initial_message)
        logger.info(f"Initial message from {initial_message.role.value}")
        
        # Process conversation loop
        current_message = initial_message
        
        while self.auto_continue and current_message:
            # Check session status
            session_data = self.db.get_session(session.id)
            if session_data and session_data.status != "active":
                logger.info(f"Session {session.id} is {session_data.status}, stopping")
                break
            
            # Process next turn
            current_message = self.process_turn(session.id, current_message)
            
            # Delay between turns to allow frontend to fetch and display
            if current_message:
                logger.info(f"⏱️  Waiting 1s before next turn...")
                time.sleep(1.0)  # Increased from 0.2s to 1s
        
        # Mark session as completed
        self.db.update_session_status(session.id, "completed", datetime.utcnow())
        logger.info(f"Session {session.id} completed")
    
    def pause_session(self, session_id: str):
        """Pause a conversation session."""
        self.db.update_session_status(session_id, "paused")
        logger.info(f"Session {session_id} paused")
    
    def resume_session(self, session_id: str):
        """Resume a paused conversation session."""
        self.db.update_session_status(session_id, "active")
        logger.info(f"Session {session_id} resumed")
        
        # Get last message and continue from there
        last_message = self.db.get_last_message(session_id)
        if last_message and self.auto_continue:
            current_message = last_message
            while current_message:
                session_data = self.db.get_session(session_id)
                if session_data and session_data.status != "active":
                    break
                
                current_message = self.process_turn(session_id, current_message)
                if current_message:
                    time.sleep(0.2)
    
    def inject_message(self, session_id: str, content: str, signal: Signal = Signal.CONTINUE):
        """Allow human to inject a message into the conversation."""
        message = Message(
            session_id=session_id,
            role=Role.HUMAN,
            content=content,
            signal=signal,
            timestamp=datetime.utcnow()
        )
        
        message = self.db.add_message(message)
        logger.info(f"Human injected message with signal '{signal.value}'")
        
        # If auto-continue is enabled and signal is CONTINUE, process next turn
        if self.auto_continue and signal == Signal.CONTINUE:
            self.process_turn(session_id, message)
        
        return message

