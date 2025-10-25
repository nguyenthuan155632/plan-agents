#!/usr/bin/env python3
"""
Demo script using real GLM AI models from z.ai.
This replaces the dummy responses with actual AI-generated content.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.database import Database
from core.coordinator import Coordinator
from core.message import Message, Session, Role, Signal
from agents.glm_agent import GLMAgent
from datetime import datetime, UTC
import uuid


def main():
    print("\n" + "="*60)
    print("🤖 Dual AI Collaboration Framework - GLM AI Demo")
    print("   Powered by z.ai GLM-4.6")
    print("="*60 + "\n")
    
    # Configuration with z.ai credentials
    config = {
        "timeout_seconds": 120,  # Longer timeout for API calls
        "max_turn_length": 10000,  # Allow very long responses (no truncation)
        "auto_continue": True,
        # z.ai API configuration
        "z_ai_api_key": "bfc0ba4defa24b909bae2fdce3f7802e.cia5P6s2JimydvkQ",
        "z_ai_base_url": "https://api.z.ai/api/coding/paas/v4",
        "model": "glm-4.6"  # GLM-4.6 model
    }
    
    # Initialize
    print("📦 Initializing system with GLM AI models...")
    db = Database("storage/conversations.db")
    coordinator = Coordinator(db, config)
    
    # Create GLM-powered agents
    print("🔧 Creating Agent A with glm-4.6...")
    agent_a_config = config.copy()
    agent_a_config["model"] = "glm-4.6"  # GLM-4.6 model for Agent A
    agent_a = GLMAgent(Role.AGENT_A, db, agent_a_config)
    
    print("🔧 Creating Agent B with glm-4.6...")
    agent_b_config = config.copy()
    agent_b_config["model"] = "glm-4.6"  # GLM-4.6 model for Agent B
    agent_b = GLMAgent(Role.AGENT_B, db, agent_b_config)
    
    # Register agents
    coordinator.register_agent(Role.AGENT_A, agent_a.respond_to)
    coordinator.register_agent(Role.AGENT_B, agent_b.respond_to)
    
    print("✓ GLM AI agents registered\n")
    
    # Create demo session
    session_id = str(uuid.uuid4())[:8]
    
    # Get topic from user or use default
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        topic = "What are the best practices for designing RESTful APIs in modern web applications?"
    
    session = Session(
        id=session_id,
        topic=topic,
        started_at=datetime.now(UTC),
        status="active"
    )
    
    print(f"🎯 Session ID: {session_id}")
    print(f"📝 Topic: {topic}\n")
    print("="*60)
    print("Starting AI conversation...\n")
    print("💡 Tip: Press Ctrl+C to stop the conversation\n")
    print("="*60 + "\n")
    
    # Create initial message
    initial_message = Message(
        session_id=session_id,
        role=Role.HUMAN,
        content=f"Let's have a thoughtful discussion about: {topic}\n\nAgent A, please share your analytical perspective to begin.",
        signal=Signal.CONTINUE,
        timestamp=datetime.now(UTC)
    )
    
    try:
        # Start conversation with real AI
        coordinator.start_conversation(session, initial_message)
        
        print("\n" + "="*60)
        print("✅ AI Conversation completed!\n")
        
        # Show summary
        messages = db.get_messages(session_id)
        
        print(f"📊 Summary:")
        print(f"   Total messages: {len(messages)}")
        print(f"   Agent A turns: {sum(1 for m in messages if m.role == Role.AGENT_A)}")
        print(f"   Agent B turns: {sum(1 for m in messages if m.role == Role.AGENT_B)}")
        print(f"\n💾 Full conversation saved to database")
        print(f"   Session ID: {session_id}")
        print(f"\n📖 View conversation:")
        print(f"   python run.py show {session_id}")
        print("\n" + "="*60 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Conversation interrupted by user")
        db.update_session_status(session_id, "paused")
        print(f"   Session {session_id} paused")
        print(f"\n📖 View partial conversation:")
        print(f"   python run.py show {session_id}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

