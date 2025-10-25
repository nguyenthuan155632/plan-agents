#!/bin/bash
set -e  # Exit on error

echo "🚂 Railway Deployment Starting..."

# Get PORT from Railway or default to 3000
PORT=${PORT:-3000}
echo "📡 PORT: $PORT"

# Create storage directory
mkdir -p /app/storage
echo "📁 Storage directory created"

# Initialize database if needed
if [ ! -f /app/storage/conversations.db ]; then
    echo "📦 Initializing database..."
    cd /app
    python scripts/init_db.py || echo "⚠️  Database init skipped (may already exist)"
fi

# Start Python backend in background on port 8000
echo "🐍 Starting Python backend..."
cd /app
python conversation_processor.py > /tmp/python.log 2>&1 &
PYTHON_PID=$!
echo "   Python PID: $PYTHON_PID"

# Give Python time to start
sleep 5

# Check if Python is still running
if ! kill -0 $PYTHON_PID 2>/dev/null; then
    echo "❌ Python failed to start!"
    cat /tmp/python.log
    exit 1
fi
echo "✅ Python backend running"

# Start Next.js on Railway's PORT
echo "⚛️  Starting Next.js on 0.0.0.0:$PORT..."
cd /app/web
exec npm start
