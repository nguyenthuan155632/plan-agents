#!/usr/bin/env python3
"""
Quick test to verify environment configuration.
Run this to make sure your .env file is set up correctly.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from dotenv import load_dotenv
except ImportError:
    print("❌ Error: python-dotenv not installed")
    print("   Run: pip install -r requirements.txt")
    sys.exit(1)

# Load environment variables
load_dotenv()

def test_env_vars():
    """Test if all required environment variables are set."""
    print("🔍 Checking environment configuration...\n")
    
    required_vars = {
        'ZAI_API_KEY': 'z.ai API Key for GLM-4.5-air (Agent A)',
        'GEMINI_API_KEY': 'Google Gemini API Key (Agent B)'
    }
    
    optional_vars = {
        'ZAI_BASE_URL': 'z.ai API base URL',
        'GLM_MODEL': 'GLM model name',
        'GEMINI_MODEL': 'Gemini model name',
        'MAX_TURN_LENGTH': 'Maximum response length'
    }
    
    all_ok = True
    
    # Check required variables
    print("📋 Required Variables:")
    print("-" * 60)
    for var_name, description in required_vars.items():
        value = os.getenv(var_name)
        if value:
            # Mask the key for security
            masked = value[:10] + '...' if len(value) > 10 else value
            print(f"✅ {var_name:20} {description}")
            print(f"   Value: {masked}")
        else:
            print(f"❌ {var_name:20} {description}")
            print(f"   Status: NOT SET")
            all_ok = False
        print()
    
    # Check optional variables
    print("\n📝 Optional Variables (with defaults):")
    print("-" * 60)
    for var_name, description in optional_vars.items():
        value = os.getenv(var_name)
        if value:
            print(f"✅ {var_name:20} {description}")
            print(f"   Value: {value}")
        else:
            print(f"ℹ️  {var_name:20} {description}")
            print(f"   Status: Using default")
        print()
    
    # Summary
    print("\n" + "=" * 60)
    if all_ok:
        print("✅ All required environment variables are set!")
        print("🚀 Your application is ready to run.")
        print("\nStart the application with:")
        print("   ./start.sh")
    else:
        print("❌ Some required environment variables are missing!")
        print("\n📝 To fix this:")
        print("   1. Copy env.example to .env:")
        print("      cp env.example .env")
        print("   2. Edit .env and add your API keys:")
        print("      nano .env")
        print("   3. Run this test again:")
        print("      python test_env.py")
        print("\n📚 See ENV_SETUP.md for detailed instructions.")
    print("=" * 60)
    
    return all_ok

if __name__ == '__main__':
    success = test_env_vars()
    sys.exit(0 if success else 1)

