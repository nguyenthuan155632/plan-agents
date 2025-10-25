#!/bin/bash

echo "🔍 Checking Railway Environment Variables..."

# Check required environment variables
MISSING=()

if [ -z "$ZAI_API_KEY" ]; then
    MISSING+=("ZAI_API_KEY")
fi

if [ -z "$GEMINI_API_KEY" ]; then
    MISSING+=("GEMINI_API_KEY")
fi

if [ ${#MISSING[@]} -gt 0 ]; then
    echo ""
    echo "❌ ERROR: Missing required environment variables!"
    echo ""
    for var in "${MISSING[@]}"; do
        echo "   - $var"
    done
    echo ""
    echo "📋 To fix this on Railway:"
    echo "   1. Go to your service → Variables"
    echo "   2. Add the missing variables"
    echo "   3. Redeploy"
    echo ""
    exit 1
fi

echo "✅ All required environment variables are set!"
echo "   - ZAI_API_KEY: ${ZAI_API_KEY:0:10}..."
echo "   - GEMINI_API_KEY: ${GEMINI_API_KEY:0:10}..."

