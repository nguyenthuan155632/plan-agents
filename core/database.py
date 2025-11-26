"""
SQLite database operations for the dual AI collaboration framework.
"""

import sqlite3
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from contextlib import contextmanager

from core.message import Message, Session, Role, Signal, ConversationMode


class Database:
    """SQLite database manager for agent communication."""
    
    def __init__(self, db_path: str = "storage/conversations.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()
    
    @contextmanager
    def get_connection(self):
        """Get database connection with automatic cleanup."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def initialize(self):
        """Initialize database schema."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    topic TEXT,
                    started_at TEXT NOT NULL,
                    ended_at TEXT,
                    status TEXT DEFAULT 'active',
                    mode TEXT DEFAULT 'planning'
                )
            """)

            # Add mode column if it doesn't exist (migration for existing DBs)
            try:
                cursor.execute("ALTER TABLE sessions ADD COLUMN mode TEXT DEFAULT 'planning'")
            except sqlite3.OperationalError:
                pass  # Column already exists
            
            # Messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    signal TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES sessions(id)
                )
            """)
            
            # Planning state table for LangGraph persistence
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS planning_state (
                    session_id TEXT PRIMARY KEY,
                    current_node TEXT NOT NULL DEFAULT 'analyze_codebase',
                    request TEXT,
                    language TEXT DEFAULT 'english',
                    codebase_context TEXT,
                    identified_files TEXT,
                    agent_a_analysis TEXT,
                    agent_a_proposal TEXT,
                    agent_b_review TEXT,
                    validation_passed INTEGER DEFAULT 0,
                    validation_issues TEXT,
                    final_plan TEXT,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES sessions(id)
                )
            """)

            # Create indexes for better query performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_session
                ON messages(session_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_timestamp
                ON messages(timestamp)
            """)
    
    def create_session(self, session: Session) -> Session:
        """Create a new conversation session."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO sessions (id, topic, started_at, ended_at, status, mode)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                session.id,
                session.topic,
                session.started_at.isoformat(),
                session.ended_at.isoformat() if session.ended_at else None,
                session.status,
                session.mode.value
            ))
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM sessions WHERE id = ?
            """, (session_id,))

            row = cursor.fetchone()
            if not row:
                return None

            # Handle mode column (may not exist in old DBs)
            mode_value = row["mode"] if "mode" in row.keys() else "planning"

            return Session(
                id=row["id"],
                topic=row["topic"],
                started_at=datetime.fromisoformat(row["started_at"]),
                ended_at=datetime.fromisoformat(row["ended_at"]) if row["ended_at"] else None,
                status=row["status"],
                mode=ConversationMode(mode_value)
            )
    
    def update_session_status(self, session_id: str, status: str, ended_at: Optional[datetime] = None):
        """Update session status."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE sessions 
                SET status = ?, ended_at = ?
                WHERE id = ?
            """, (status, ended_at.isoformat() if ended_at else None, session_id))
    
    def add_message(self, message: Message) -> Message:
        """Add a message to the database."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO messages (session_id, role, content, signal, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (
                message.session_id,
                message.role.value,
                message.content,
                message.signal.value,
                message.timestamp.isoformat()
            ))
            message.id = cursor.lastrowid
        return message
    
    def get_messages(self, session_id: str, limit: Optional[int] = None) -> List[Message]:
        """Get all messages for a session."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT * FROM messages 
                WHERE session_id = ? 
                ORDER BY timestamp ASC
            """
            
            if limit:
                query += f" LIMIT {limit}"
            
            cursor.execute(query, (session_id,))
            
            messages = []
            for row in cursor.fetchall():
                messages.append(Message(
                    id=row["id"],
                    session_id=row["session_id"],
                    role=Role(row["role"]),
                    content=row["content"],
                    signal=Signal(row["signal"]),
                    timestamp=datetime.fromisoformat(row["timestamp"])
                ))
            
            return messages
    
    def get_last_message(self, session_id: str) -> Optional[Message]:
        """Get the most recent message in a session."""
        messages = self.get_messages(session_id, limit=1)
        return messages[-1] if messages else None
    
    def get_message_count(self, session_id: str) -> int:
        """Get total message count for a session."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) as count FROM messages WHERE session_id = ?
            """, (session_id,))
            return cursor.fetchone()["count"]
    
    def list_sessions(self, status: Optional[str] = None) -> List[Session]:
        """List all sessions, optionally filtered by status."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if status:
                cursor.execute("""
                    SELECT * FROM sessions WHERE status = ? ORDER BY started_at DESC
                """, (status,))
            else:
                cursor.execute("""
                    SELECT * FROM sessions ORDER BY started_at DESC
                """)
            
            sessions = []
            for row in cursor.fetchall():
                # Handle mode column (may not exist in old DBs)
                mode_value = row["mode"] if "mode" in row.keys() else "planning"
                sessions.append(Session(
                    id=row["id"],
                    topic=row["topic"],
                    started_at=datetime.fromisoformat(row["started_at"]),
                    ended_at=datetime.fromisoformat(row["ended_at"]) if row["ended_at"] else None,
                    status=row["status"],
                    mode=ConversationMode(mode_value)
                ))

            return sessions

    # ==================== PLANNING STATE METHODS ====================

    def get_planning_state(self, session_id: str) -> Optional[dict]:
        """Get planning state for a session."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM planning_state WHERE session_id = ?
            """, (session_id,))

            row = cursor.fetchone()
            if not row:
                return None

            import json
            return {
                "session_id": row["session_id"],
                "current_node": row["current_node"],
                "request": row["request"],
                "language": row["language"],
                "codebase_context": json.loads(row["codebase_context"]) if row["codebase_context"] else [],
                "identified_files": json.loads(row["identified_files"]) if row["identified_files"] else [],
                "agent_a_analysis": row["agent_a_analysis"] or "",
                "agent_a_proposal": row["agent_a_proposal"] or "",
                "agent_b_review": row["agent_b_review"] or "",
                "validation_passed": bool(row["validation_passed"]),
                "validation_issues": json.loads(row["validation_issues"]) if row["validation_issues"] else [],
                "final_plan": row["final_plan"] or "",
                "updated_at": row["updated_at"]
            }

    def save_planning_state(self, session_id: str, state: dict):
        """Save or update planning state for a session."""
        import json
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO planning_state
                (session_id, current_node, request, language, codebase_context,
                 identified_files, agent_a_analysis, agent_a_proposal, agent_b_review,
                 validation_passed, validation_issues, final_plan, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                state.get("current_node", "analyze_codebase"),
                state.get("request", ""),
                state.get("language", "english"),
                json.dumps(state.get("codebase_context", [])),
                json.dumps(state.get("identified_files", [])),
                state.get("agent_a_analysis", ""),
                state.get("agent_a_proposal", ""),
                state.get("agent_b_review", ""),
                1 if state.get("validation_passed") else 0,
                json.dumps(state.get("validation_issues", [])),
                state.get("final_plan", ""),
                datetime.now().isoformat()
            ))

    def delete_planning_state(self, session_id: str):
        """Delete planning state for a session."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM planning_state WHERE session_id = ?
            """, (session_id,))

