"""
Main entry point for the dual AI collaboration framework.
"""

import sys
import logging
from pathlib import Path

# Ensure modules can be imported
sys.path.insert(0, str(Path(__file__).parent))

from moderator.cli import app


def setup_logging():
    """Setup logging configuration."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/system.log'),
            logging.StreamHandler()
        ]
    )


def main():
    """Main entry point."""
    setup_logging()
    
    # Ensure storage directory exists
    storage_dir = Path("storage")
    storage_dir.mkdir(exist_ok=True)
    
    # Run CLI app
    app()


if __name__ == "__main__":
    main()

