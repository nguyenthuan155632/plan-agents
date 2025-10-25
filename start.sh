#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Dual AI Collaboration Platform...${NC}"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${RED}❌ Virtual environment not found. Please run setup.sh first.${NC}"
    exit 1
fi

# Activate virtual environment
echo -e "${GREEN}✓ Activating Python virtual environment...${NC}"
source .venv/bin/activate

# Check if storage directory exists
if [ ! -d "storage" ]; then
    echo -e "${GREEN}✓ Creating storage directory...${NC}"
    mkdir -p storage
fi

# Initialize database if it doesn't exist
if [ ! -f "storage/conversations.db" ]; then
    echo -e "${GREEN}✓ Initializing database...${NC}"
    python scripts/init_db.py
fi

# Function to cleanup on exit
cleanup() {
    echo -e "\n${BLUE}👋 Shutting down services...${NC}"
    kill $PROCESSOR_PID 2>/dev/null
    kill $NEXTJS_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start conversation processor in background
echo -e "${GREEN}✓ Starting conversation processor...${NC}"
python conversation_processor.py &
PROCESSOR_PID=$!

# Give processor time to start
sleep 2

# Start Next.js dev server
echo -e "${GREEN}✓ Starting Next.js web UI...${NC}"
cd web
npm run dev &
NEXTJS_PID=$!
cd ..

echo -e "\n${BLUE}════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✨ Platform is running!${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════${NC}"
echo -e "🌐 Web UI: ${GREEN}http://localhost:3000${NC}"
echo -e "🤖 Backend Processor: ${GREEN}Running (PID: $PROCESSOR_PID)${NC}"
echo -e ""
echo -e "Press ${RED}Ctrl+C${NC} to stop all services"
echo -e "${BLUE}════════════════════════════════════════════════════${NC}\n"

# Wait for both processes
wait

