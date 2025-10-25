#!/bin/bash

echo "🚂 Railway Entrypoint - Initializing..."

# Check environment variables first
bash scripts/check_env.sh
if [ $? -ne 0 ]; then
    echo "❌ Environment check failed. Exiting..."
    exit 1
fi

# Create storage directory
mkdir -p storage

# Initialize database if not exists
if [ ! -f storage/conversations.db ]; then
    echo "📦 Initializing database..."
    python scripts/init_db.py
else
    echo "✓ Database already exists"
fi

# Start Python conversation processor in background
echo "🐍 Starting conversation processor..."
python conversation_processor.py &
PYTHON_PID=$!

# Wait for Python to initialize
sleep 2

# Start Next.js in foreground (Railway needs this as primary process)
echo "⚛️  Starting Next.js on port $PORT..."
cd web

# Trap SIGTERM to gracefully shutdown both processes
trap "echo 'Stopping...'; kill $PYTHON_PID 2>/dev/null; exit 0" SIGTERM SIGINT

# Start Next.js (use exec so it receives signals)
exec npm start

