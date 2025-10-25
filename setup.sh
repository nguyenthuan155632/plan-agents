#!/bin/bash
# setup.sh - One-command setup script for the Dual AI Collaboration Framework

set -e

echo "🤖 Dual AI Collaboration Framework - Setup"
echo "=========================================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.9 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✓ Found Python $PYTHON_VERSION"

# Check Node.js (optional for web UI)
if command -v node &> /dev/null; then
    NODE_VERSION=$(node -v)
    echo "✓ Found Node.js $NODE_VERSION"
    HAS_NODE=true
else
    echo "⚠ Node.js not found (optional for web UI)"
    HAS_NODE=false
fi

echo ""
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

echo ""
echo "🗄️ Initializing database..."
python3 scripts/init_db.py

echo ""
echo "✓ Core system setup complete!"

# Optional web UI setup
if [ "$HAS_NODE" = true ]; then
    echo ""
    read -p "Install web UI dependencies? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📦 Installing web UI dependencies..."
        cd web
        npm install
        cd ..
        echo "✓ Web UI setup complete!"
    fi
fi

echo ""
echo "=========================================="
echo "🎉 Setup Complete!"
echo ""
echo "Quick Start:"
echo "  python3 main.py start \"Your first topic\""
echo ""
if [ "$HAS_NODE" = true ]; then
    echo "Start Web UI:"
    echo "  cd web && npm run dev"
    echo ""
fi
echo "Documentation:"
echo "  README.md - Project overview"
echo "  docs/GETTING_STARTED.md - Detailed guide"
echo "  QUICKREF.md - Quick reference"
echo ""
echo "Happy collaborating! 🤖🤝🤖"

