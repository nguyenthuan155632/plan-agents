"""
CLI interface for human moderator to control and interact with AI agents.
"""

import typer
import uuid
import logging
from datetime import datetime
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

from core.database import Database
from core.coordinator import Coordinator
from core.message import Message, Session, Role, Signal
from agents.agent_a import AgentA
from agents.agent_b import AgentB


# Initialize CLI
app = typer.Typer(help="🤖 Dual AI Collaboration Framework - Moderator CLI")
console = Console()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/moderator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def get_db() -> Database:
    """Get database instance."""
    return Database("storage/conversations.db")


def get_coordinator(db: Database) -> Coordinator:
    """Get coordinator with registered agents."""
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
    
    return coordinator


@app.command()
def start(
    topic: str = typer.Argument(..., help="The discussion topic"),
    starter: str = typer.Option("AgentA", "--starter", help="Which agent starts (AgentA or AgentB)"),
    auto: bool = typer.Option(True, "--auto", help="Auto-continue conversation")
):
    """
    Start a new conversation session between the agents.
    """
    console.print(Panel.fit(
        f"🚀 Starting new conversation\n\n[bold]Topic:[/bold] {topic}",
        title="Dual AI Collaboration",
        border_style="green"
    ))
    
    # Initialize
    db = get_db()
    coordinator = get_coordinator(db)
    coordinator.auto_continue = auto
    
    # Create session
    session_id = str(uuid.uuid4())[:8]
    session = Session(
        id=session_id,
        topic=topic,
        started_at=datetime.utcnow(),
        status="active"
    )
    
    # Determine starting role
    start_role = Role.AGENT_A if starter.lower() == "agenta" else Role.AGENT_B
    
    # Create initial message from human
    initial_message = Message(
        session_id=session_id,
        role=Role.HUMAN,
        content=f"Let's discuss: {topic}\n\n{start_role.value}, please begin the discussion.",
        signal=Signal.CONTINUE,
        timestamp=datetime.utcnow()
    )
    
    console.print(f"\n[cyan]Session ID:[/cyan] {session_id}")
    console.print(f"[cyan]Starting agent:[/cyan] {start_role.value}\n")
    
    try:
        # Start conversation
        coordinator.start_conversation(session, initial_message)
        
        console.print("\n[green]✓ Conversation completed[/green]")
        
        # Show summary
        show_conversation(session_id)
        
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠ Conversation interrupted by user[/yellow]")
        db.update_session_status(session_id, "paused")
    except Exception as e:
        console.print(f"\n[red]✗ Error: {e}[/red]")
        logger.error(f"Error in conversation: {e}", exc_info=True)


@app.command()
def inject(
    session_id: str = typer.Argument(..., help="Session ID"),
    message: str = typer.Argument(..., help="Your message"),
    signal: str = typer.Option("continue", "--signal", help="Signal: continue, stop, or handover")
):
    """
    Inject a message into an ongoing conversation.
    """
    db = get_db()
    coordinator = get_coordinator(db)
    
    # Validate session
    session = db.get_session(session_id)
    if not session:
        console.print(f"[red]✗ Session '{session_id}' not found[/red]")
        return
    
    # Parse signal
    signal_map = {
        "continue": Signal.CONTINUE,
        "stop": Signal.STOP,
        "handover": Signal.HANDOVER
    }
    sig = signal_map.get(signal.lower(), Signal.CONTINUE)
    
    console.print(Panel.fit(
        f"💬 Injecting message\n\n[bold]Message:[/bold] {message}\n[bold]Signal:[/bold] {sig.value}",
        border_style="yellow"
    ))
    
    try:
        coordinator.inject_message(session_id, message, sig)
        console.print("[green]✓ Message injected successfully[/green]")
        
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        logger.error(f"Error injecting message: {e}", exc_info=True)


@app.command()
def pause(session_id: str = typer.Argument(..., help="Session ID")):
    """
    Pause an active conversation session.
    """
    db = get_db()
    coordinator = get_coordinator(db)
    
    try:
        coordinator.pause_session(session_id)
        console.print(f"[yellow]⏸ Session '{session_id}' paused[/yellow]")
        
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")


@app.command()
def resume(session_id: str = typer.Argument(..., help="Session ID")):
    """
    Resume a paused conversation session.
    """
    db = get_db()
    coordinator = get_coordinator(db)
    
    console.print(f"[cyan]▶ Resuming session '{session_id}'...[/cyan]")
    
    try:
        coordinator.resume_session(session_id)
        console.print(f"[green]✓ Session resumed[/green]")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠ Resumed conversation interrupted[/yellow]")
        db.update_session_status(session_id, "paused")
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")


@app.command()
def show(session_id: str = typer.Argument(..., help="Session ID")):
    """
    Display the conversation history for a session.
    """
    show_conversation(session_id)


def show_conversation(session_id: str):
    """Helper to display conversation."""
    db = get_db()
    
    # Get session
    session = db.get_session(session_id)
    if not session:
        console.print(f"[red]✗ Session '{session_id}' not found[/red]")
        return
    
    # Get messages
    messages = db.get_messages(session_id)
    
    console.print(Panel.fit(
        f"[bold]Topic:[/bold] {session.topic or 'N/A'}\n"
        f"[bold]Status:[/bold] {session.status}\n"
        f"[bold]Messages:[/bold] {len(messages)}",
        title=f"📝 Session {session_id}",
        border_style="cyan"
    ))
    
    # Display messages
    for msg in messages:
        color = {
            Role.AGENT_A: "blue",
            Role.AGENT_B: "magenta",
            Role.HUMAN: "green"
        }.get(msg.role, "white")
        
        console.print(f"\n[{color}]● {msg.role.value}[/{color}] "
                     f"[dim]{msg.timestamp.strftime('%H:%M:%S')}[/dim] "
                     f"[yellow]→ {msg.signal.value}[/yellow]")
        console.print(f"  {msg.content[:200]}{'...' if len(msg.content) > 200 else ''}")


@app.command()
def list(
    status: Optional[str] = typer.Option(None, "--status", help="Filter by status")
):
    """
    List all conversation sessions.
    """
    db = get_db()
    sessions = db.list_sessions(status)
    
    if not sessions:
        console.print("[yellow]No sessions found[/yellow]")
        return
    
    # Create table
    table = Table(title="📚 Conversation Sessions")
    table.add_column("Session ID", style="cyan")
    table.add_column("Topic", style="white")
    table.add_column("Status", style="yellow")
    table.add_column("Started", style="dim")
    table.add_column("Messages", style="green")
    
    for session in sessions:
        msg_count = db.get_message_count(session.id)
        table.add_row(
            session.id,
            (session.topic or "N/A")[:40],
            session.status,
            session.started_at.strftime('%Y-%m-%d %H:%M'),
            str(msg_count)
        )
    
    console.print(table)


@app.command()
def export(
    session_id: str = typer.Argument(..., help="Session ID"),
    format: str = typer.Option("markdown", "--format", help="Export format (markdown or json)")
):
    """
    Export conversation to a file.
    """
    db = get_db()
    
    # Get session and messages
    session = db.get_session(session_id)
    if not session:
        console.print(f"[red]✗ Session '{session_id}' not found[/red]")
        return
    
    messages = db.get_messages(session_id)
    
    # Export based on format
    if format == "markdown":
        output_file = f"storage/export_{session_id}.md"
        
        with open(output_file, 'w') as f:
            f.write(f"# Conversation: {session.topic or 'Untitled'}\n\n")
            f.write(f"**Session ID:** {session_id}\n")
            f.write(f"**Started:** {session.started_at}\n")
            f.write(f"**Status:** {session.status}\n\n")
            f.write("---\n\n")
            
            for msg in messages:
                f.write(msg.to_markdown())
        
        console.print(f"[green]✓ Exported to {output_file}[/green]")
    
    else:
        console.print(f"[red]✗ Format '{format}' not supported[/red]")


if __name__ == "__main__":
    # Create logs directory
    import os
    os.makedirs("logs", exist_ok=True)
    os.makedirs("storage", exist_ok=True)
    
    app()

