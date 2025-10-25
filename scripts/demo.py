#!/usr/bin/env python3
"""
Demo script to showcase the Dual AI Collaboration Framework.
This creates a sample conversation you can observe.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.database import Database
from core.coordinator import Coordinator
from core.message import Message, Session, Role, Signal
from agents.agent_a import AgentA
from agents.agent_b import AgentB
from datetime import datetime
import uuid


def main():
    print("🤖 Dual AI Collaboration Framework - Demo")
    print("=" * 50)
    print()
    
    # Initialize
    print("📦 Setting up...")
    db = Database("storage/conversations.db")
    
    config = {
        "timeout_seconds": 60,
        "max_turn_length": 500,
        "auto_continue": True
    }
    
    coordinator = Coordinator(db, config)
    
    # Create agents
    agent_a = AgentA(db, config)
    agent_b = AgentB(db, config)
    
    # Register agents
    coordinator.register_agent(Role.AGENT_A, agent_a.respond_to)
    coordinator.register_agent(Role.AGENT_B, agent_b.respond_to)
    
    print("✓ Agents registered")
    print()
    
    # Create demo session
    session_id = str(uuid.uuid4())[:8]
    topic = "What are best practices for error handling in Python?"
    
    session = Session(
        id=session_id,
        topic=topic,
        started_at=datetime.utcnow(),
        status="active"
    )
    
    print(f"🎯 Starting conversation")
    print(f"   Session ID: {session_id}")
    print(f"   Topic: {topic}")
    print()
    print("=" * 50)
    print()
    
    # Create initial message
    initial_message = Message(
        session_id=session_id,
        role=Role.HUMAN,
        content=f"Let's discuss: {topic}\n\nAgent A, please begin the discussion.",
        signal=Signal.CONTINUE,
        timestamp=datetime.utcnow()
    )
    
    # Start the conversation
    try:
        coordinator.start_conversation(session, initial_message)
        
        print()
        print("=" * 50)
        print()
        print("✅ Conversation completed!")
        print()
        
        # Show summary
        messages = db.get_messages(session_id)
        
        print(f"📊 Summary:")
        print(f"   Total messages: {len(messages)}")
        print(f"   Agent A turns: {sum(1 for m in messages if m.role == Role.AGENT_A)}")
        print(f"   Agent B turns: {sum(1 for m in messages if m.role == Role.AGENT_B)}")
        print()
        
        print("💡 Next steps:")
        print(f"   1. View conversation: python main.py show {session_id}")
        print(f"   2. Export to markdown: python main.py export {session_id}")
        print(f"   3. View in web UI: cd web && npm run dev")
        print()
        
    except KeyboardInterrupt:
        print()
        print("⚠️  Interrupted by user")
        db.update_session_status(session_id, "paused")
        print(f"   Resume with: python main.py resume {session_id}")
    except Exception as e:
        print()
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

