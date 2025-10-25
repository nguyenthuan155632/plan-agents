#!/bin/bash

# Railway startup script - runs both Python backend and Next.js frontend

echo "🚂 Starting Railway deployment..."

# Create storage directory if not exists
mkdir -p storage

# Initialize database if not exists
if [ ! -f storage/conversations.db ]; then
    echo "📦 Initializing database..."
    python scripts/init_db.py
fi

echo "🐍 Starting Python conversation processor..."
python conversation_processor.py &
PYTHON_PID=$!

# Wait for Python to initialize
sleep 3

echo "⚛️  Starting Next.js frontend..."
cd web
npm start &
NEXTJS_PID=$!

echo "✅ Both services started!"
echo "   - Python PID: $PYTHON_PID"
echo "   - Next.js PID: $NEXTJS_PID"

# Keep the script running
wait -n

# If one process exits, kill the other
kill $PYTHON_PID $NEXTJS_PID 2>/dev/null
exit $?

