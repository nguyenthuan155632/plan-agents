#!/bin/bash
set -e

echo "🚂 Starting Next.js only (simplified for Railway)..."

# Create storage directory
mkdir -p /app/storage
echo "📁 Storage created"

# Initialize DB if needed
if [ ! -f /app/storage/conversations.db ]; then
    echo "📦 Init database..."
    cd /app && python scripts/init_db.py
fi

# Start Next.js ONLY (conversation_processor will run separately)
echo "⚛️  Starting Next.js on PORT ${PORT:-3000}..."
cd /app/web
exec npm start

