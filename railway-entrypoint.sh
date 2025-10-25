#!/bin/bash

echo "🚂 Railway Entrypoint - Initializing..."

# Create storage directory
mkdir -p storage

# Initialize database if not exists
if [ ! -f storage/conversations.db ]; then
    echo "📦 Initializing database..."
    python scripts/init_db.py
else
    echo "✓ Database already exists"
fi

# Start Next.js
echo "⚛️  Starting Next.js on port $PORT..."
cd web
exec npm start

