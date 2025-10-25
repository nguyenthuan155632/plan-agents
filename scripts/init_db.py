"""
Initialize the database for the dual AI collaboration framework.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.database import Database


def main():
    """Initialize the database."""
    print("🔧 Initializing database...")
    
    # Create storage directory
    storage_path = Path("storage")
    storage_path.mkdir(exist_ok=True)
    
    # Initialize database
    db = Database("storage/conversations.db")
    
    print("✓ Database initialized successfully!")
    print(f"  Location: {storage_path.absolute() / 'conversations.db'}")
    
    # Create logs directory
    logs_path = Path("logs")
    logs_path.mkdir(exist_ok=True)
    print(f"✓ Logs directory created: {logs_path.absolute()}")


if __name__ == "__main__":
    main()

