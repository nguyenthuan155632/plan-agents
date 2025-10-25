#!/usr/bin/env python3
"""
Simple demo to test the dual AI collaboration framework.
Run this directly to see agents in action!
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.database import Database
from core.coordinator import Coordinator
from core.message import Message, Session, Role, Signal
from agents.agent_a import AgentA
from agents.agent_b import AgentB
from datetime import datetime
import uuid


def main():
    print("\n" + "="*60)
    print("🤖 Dual AI Collaboration Framework - Quick Demo")
    print("="*60 + "\n")
    
    # Initialize
    print("📦 Initializing system...")
    db = Database("storage/conversations.db")
    
    config = {
        "timeout_seconds": 60,
        "max_turn_length": 500,
        "auto_continue": True
    }
    
    coordinator = Coordinator(db, config)
    
    # Create and register agents
    agent_a = AgentA(db, config)
    agent_b = AgentB(db, config)
    
    coordinator.register_agent(Role.AGENT_A, agent_a.respond_to)
    coordinator.register_agent(Role.AGENT_B, agent_b.respond_to)
    
    print("✓ Agents registered\n")
    
    # Create demo session
    session_id = str(uuid.uuid4())[:8]
    topic = "What are best practices for error handling in Python?"
    
    session = Session(
        id=session_id,
        topic=topic,
        started_at=datetime.utcnow(),
        status="active"
    )
    
    print(f"🎯 Session ID: {session_id}")
    print(f"📝 Topic: {topic}\n")
    print("="*60)
    print("Starting conversation...\n")
    
    # Create initial message
    initial_message = Message(
        session_id=session_id,
        role=Role.HUMAN,
        content=f"Let's discuss: {topic}\n\nAgent A, please begin the discussion.",
        signal=Signal.CONTINUE,
        timestamp=datetime.utcnow()
    )
    
    try:
        # Start conversation
        coordinator.start_conversation(session, initial_message)
        
        print("\n" + "="*60)
        print("✅ Conversation completed!\n")
        
        # Show summary
        messages = db.get_messages(session_id)
        
        print(f"📊 Summary:")
        print(f"   Total messages: {len(messages)}")
        print(f"   Agent A turns: {sum(1 for m in messages if m.role == Role.AGENT_A)}")
        print(f"   Agent B turns: {sum(1 for m in messages if m.role == Role.AGENT_B)}")
        print(f"\n💾 Conversation saved to database")
        print(f"   Session ID: {session_id}")
        print("\n" + "="*60 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        db.update_session_status(session_id, "paused")
        print(f"   Session {session_id} paused")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

