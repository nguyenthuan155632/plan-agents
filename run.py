#!/usr/bin/env python3
"""
Simple CLI wrapper for the Dual AI Collaboration Framework.
Now using GLM-4.6 AI by default!
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.database import Database
from core.coordinator import Coordinator
from core.message import Message, Session, Role, Signal
from agents.glm_agent import GLMAgent  # Using GLM AI instead of dummy agents
from datetime import datetime, UTC
import uuid


def print_help():
    print("""
🤖 Dual AI Collaboration Framework - CLI
   Powered by GLM-4.6 Real AI

Usage:
  python run.py start <topic>              Start an AI conversation
  python run.py list                       List all sessions
  python run.py show <session_id>          Show conversation
  python run.py demo                       Run quick demo

Examples:
  python run.py start "Best practices for error handling"
  python run.py list
  python run.py show 3dacd435
  python run.py demo
""")


def start_conversation(topic):
    """Start a new conversation with GLM-4.6 AI."""
    print(f"\n🚀 Starting AI conversation: {topic}\n")
    
    db = Database("storage/conversations.db")
    
    # Load API key from environment
    z_ai_api_key = os.getenv('ZAI_API_KEY')
    if not z_ai_api_key:
        print("❌ Error: ZAI_API_KEY not found in environment variables.")
        print("   Please create a .env file with your API key.")
        print("   See ENV_SETUP.md for instructions.")
        return
    
    # GLM-4.6 configuration
    config = {
        "timeout_seconds": 120,
        "max_turn_length": 10000,
        "auto_continue": True,
        # z.ai API configuration
        "z_ai_api_key": z_ai_api_key,
        "z_ai_base_url": os.getenv('ZAI_BASE_URL', 'https://api.z.ai/api/coding/paas/v4'),
        "model": os.getenv('GLM_MODEL', 'glm-4.6')
    }
    
    coordinator = Coordinator(db, config)
    
    # Create GLM AI agents
    agent_a = GLMAgent(Role.AGENT_A, db, config)
    agent_b = GLMAgent(Role.AGENT_B, db, config)
    
    coordinator.register_agent(Role.AGENT_A, agent_a.respond_to)
    coordinator.register_agent(Role.AGENT_B, agent_b.respond_to)
    
    session_id = str(uuid.uuid4())[:8]
    session = Session(id=session_id, topic=topic, started_at=datetime.now(UTC), status="active")
    
    initial_message = Message(
        session_id=session_id,
        role=Role.HUMAN,
        content=f"Let's discuss: {topic}\n\nAgent A, please begin.",
        signal=Signal.CONTINUE,
        timestamp=datetime.now(UTC)
    )
    
    print(f"Session ID: {session_id}\n")
    print("="*60 + "\n")
    
    try:
        coordinator.start_conversation(session, initial_message)
        messages = db.get_messages(session_id)
        print(f"\n✅ Completed! {len(messages)} messages exchanged")
        print(f"💾 Session ID: {session_id}")
        print(f"\n📖 View full conversation:")
        print(f"   python run.py show {session_id}\n")
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted")
        db.update_session_status(session_id, "paused")


def list_sessions():
    """List all sessions."""
    db = Database("storage/conversations.db")
    sessions = db.list_sessions()
    
    if not sessions:
        print("\nNo sessions found\n")
        return
    
    print("\n📚 Sessions:\n")
    for session in sessions:
        msg_count = db.get_message_count(session.id)
        print(f"  {session.id}  {session.status:10s}  {msg_count:3d} msgs  {session.topic or 'Untitled'}")
    print()


def show_conversation(session_id):
    """Show conversation details."""
    db = Database("storage/conversations.db")
    session = db.get_session(session_id)
    
    if not session:
        print(f"\n❌ Session '{session_id}' not found\n")
        return
    
    messages = db.get_messages(session_id)
    
    print(f"\n📝 Session {session_id}")
    print(f"Topic: {session.topic or 'Untitled'}")
    print(f"Status: {session.status}")
    print(f"Messages: {len(messages)}\n")
    print("="*60 + "\n")
    
    for msg in messages:
        icon = {"AgentA": "🔍", "AgentB": "💡", "Human": "👤"}.get(msg.role.value, "❓")
        print(f"{icon} {msg.role.value} → {msg.signal.value}")
        print(f"   {msg.content[:200]}{'...' if len(msg.content) > 200 else ''}\n")


def main():
    if len(sys.argv) < 2:
        print_help()
        return
    
    command = sys.argv[1]
    
    if command == "start":
        if len(sys.argv) < 3:
            print("\n❌ Error: Topic required\n")
            print("Usage: python run.py start <topic>\n")
            return
        topic = " ".join(sys.argv[2:])
        start_conversation(topic)
    
    elif command == "list":
        list_sessions()
    
    elif command == "show":
        if len(sys.argv) < 3:
            print("\n❌ Error: Session ID required\n")
            print("Usage: python run.py show <session_id>\n")
            return
        show_conversation(sys.argv[2])
    
    elif command == "demo":
        start_conversation("What are best practices for error handling in Python?")
    
    elif command == "help" or command == "--help" or command == "-h":
        print_help()
    
    else:
        print(f"\n❌ Unknown command: {command}\n")
        print_help()


if __name__ == "__main__":
    main()

