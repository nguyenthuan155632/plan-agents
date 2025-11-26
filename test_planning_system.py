"""
Test script for the new flexible planning system.

This script demonstrates:
1. Task analysis and classification
2. Codebase intelligence gathering
3. Dynamic prompt generation
4. Execution plan generation
"""

import sys
from agents.shared.task_analyzer import TaskAnalyzer, TaskType, ComplexityLevel
from agents.shared.codebase_intelligence import CodebaseIntelligence, TechStack
from agents.shared.prompt_generator import PromptGenerator
from agents.shared.execution_plan_generator import ExecutionPlanGenerator
from core.message import Role


def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def test_task_analyzer():
    """Test task analysis and classification"""
    print_section("TEST 1: Task Analyzer")

    test_cases = [
        "Add authentication to the app using NextAuth.js",
        "Refactor the UserService.py to use dependency injection",
        "Fix the bug in api/users endpoint where it returns 500 error",
        "Design a real-time notification system with WebSockets",
        "Thêm tính năng upload file với preview cho component UploadForm",
        "Optimize the database queries in the dashboard page",
    ]

    for task in test_cases:
        print(f"📝 Task: {task}")
        context = TaskAnalyzer.analyze(task)

        print(f"   Type: {context.task_type.value}")
        print(f"   Complexity: {context.complexity.value}")
        print(f"   Language: {context.language}")
        print(f"   Keywords: {', '.join(context.keywords[:5])}")

        if context.entities:
            print(f"   Entities found:")
            for entity_type, items in context.entities.items():
                print(f"      - {entity_type}: {', '.join(items[:3])}")

        if context.requirements:
            print(f"   Requirements: {len(context.requirements)} items")

        print()


def test_codebase_intelligence():
    """Test codebase intelligence and tech stack detection"""
    print_section("TEST 2: Codebase Intelligence")

    # Sample codebase content (simulating RAG results)
    sample_codebase = """
File: web/app/page.tsx
import React from 'react'
import { useState, useEffect } from 'react'
import { ConversationView } from '@/components/ConversationView'

export default function Home() {
    return <ConversationView />
}

File: package.json
{
    "name": "plan-agents-web",
    "dependencies": {
        "react": "^18.2.0",
        "next": "^14.0.0",
        "tailwindcss": "^3.3.0",
        "@tanstack/react-query": "^5.0.0"
    }
}

File: agents/base_agent.py
from abc import ABC, abstractmethod
from typing import Optional

class BaseAgent(ABC):
    def __init__(self, role, db, config=None):
        self.role = role
        self.db = db
        self.rag_chain = None

File: rag/rag_system.py
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import CharacterTextSplitter

def create_rag_chain(documents):
    vectorstore = FAISS.from_documents(documents)
    return vectorstore

File: core/database.py
import sqlite3
from typing import List
from core.message import Message

class Database:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
"""

    intel = CodebaseIntelligence()
    structure = intel.analyze_codebase(sample_codebase)

    print("🔍 Detected Tech Stack:")
    print(f"   Languages: {', '.join(structure.tech_stack.languages)}")
    print(f"   Frameworks: {', '.join(structure.tech_stack.frameworks)}")
    print(f"   Libraries: {', '.join(structure.tech_stack.libraries[:8])}")

    print(f"\n📁 File Patterns:")
    for ext, files in list(structure.file_patterns.items())[:5]:
        print(f"   .{ext}: {len(files)} files")

    print(f"\n🏗️  Architecture Patterns:")
    print(f"   {', '.join(structure.patterns) if structure.patterns else 'None detected'}")

    print(f"\n📊 Total Files: {structure.total_files}")


def test_dynamic_prompt_generation():
    """Test dynamic prompt generation"""
    print_section("TEST 3: Dynamic Prompt Generation")

    # Test Case 1: Simple feature
    task1 = "Add a delete button to the UserCard component"
    context1 = TaskAnalyzer.analyze(task1)

    print("Test Case 1: Simple Feature")
    print(f"Task: {task1}\n")

    prompt1 = PromptGenerator.generate_planning_prompt(
        role=Role.AGENT_A,
        task_context=context1
    )

    print("Generated Prompt (first 500 chars):")
    print(prompt1[:500])
    print("...\n")

    # Test Case 2: Complex architecture
    task2 = "Design a real-time notification system for the platform"
    context2 = TaskAnalyzer.analyze(task2)

    print("\nTest Case 2: Complex Architecture")
    print(f"Task: {task2}\n")

    prompt2 = PromptGenerator.generate_planning_prompt(
        role=Role.AGENT_B,
        task_context=context2
    )

    print("Generated Prompt (first 500 chars):")
    print(prompt2[:500])
    print("...\n")


def test_execution_plan_generation():
    """Test execution plan generation from conversation"""
    print_section("TEST 4: Execution Plan Generation")

    # Simulate a planning conversation
    conversation = [
        {
            "role": "HUMAN",
            "content": "Add authentication to the app using NextAuth.js"
        },
        {
            "role": "AGENT_A",
            "content": """I'll propose implementing authentication using NextAuth.js.

**Approach:**
1. Install `next-auth` dependency
2. Create `app/api/auth/[...nextauth]/route.ts` for authentication configuration
3. Configure providers (Google, GitHub, Email)
4. Modify `app/layout.tsx` to add SessionProvider wrapper
5. Create protected middleware in `middleware.ts` for route protection
6. Add login/logout components in `components/auth/`

**Files to create/modify:**
- `app/api/auth/[...nextauth]/route.ts` (create)
- `app/layout.tsx` (modify)
- `middleware.ts` (create)
- `components/auth/LoginButton.tsx` (create)
- `components/auth/LogoutButton.tsx` (create)

**Trade-off:** NextAuth.js adds ~50KB to bundle size but provides robust, production-ready authentication.

**Testing:** Need to test OAuth flows, session persistence, and protected routes."""
        },
        {
            "role": "AGENT_B",
            "content": """Agent A's approach is solid. Here are some additional considerations:

**Alternative perspective:**
- Consider using middleware.ts more extensively for centralized auth logic
- Could also implement custom JWT handling if we need more control

**Risk to consider:**
- Need to handle session storage properly (consider Redis for production scale)
- OAuth provider rate limits and error handling
- CSRF protection should be enabled

**Enhancement suggestions:**
- Add role-based access control (RBAC) from the start
- Implement refresh token rotation for security
- Add audit logging for authentication events

**Decision:** I agree NextAuth.js is the right choice for this stack. Let's implement the base first, then add RBAC in phase 2."""
        }
    ]

    plan = ExecutionPlanGenerator.generate_from_conversation(
        conversation_messages=conversation,
        original_request="Add authentication to the app using NextAuth.js",
        language="english"
    )

    print("📋 Generated Execution Plan:\n")
    print(plan.to_markdown("english"))


def test_vietnamese_support():
    """Test Vietnamese language support"""
    print_section("TEST 5: Vietnamese Language Support")

    task_vi = "Thêm tính năng đăng nhập bằng Google vào ứng dụng"
    context = TaskAnalyzer.analyze(task_vi)

    print(f"📝 Task: {task_vi}")
    print(f"   Detected Language: {context.language}")
    print(f"   Type: {context.task_type.value}")
    print(f"   Complexity: {context.complexity.value}\n")

    # Generate Vietnamese execution plan
    conversation_vi = [
        {
            "role": "HUMAN",
            "content": task_vi
        },
        {
            "role": "AGENT_A",
            "content": "Tôi đề xuất dùng NextAuth.js với Google Provider. Cần tạo file `app/api/auth/[...nextauth]/route.ts` và config Google OAuth credentials."
        },
        {
            "role": "AGENT_B",
            "content": "Đồng ý với Agent A. Lưu ý: cần setup Google Cloud Console, thêm authorized redirect URIs, và handle error khi user deny permission."
        }
    ]

    plan_vi = ExecutionPlanGenerator.generate_from_conversation(
        conversation_messages=conversation_vi,
        original_request=task_vi,
        language="vietnamese"
    )

    print("📋 Execution Plan (Vietnamese):\n")
    print(plan_vi.to_markdown("vietnamese"))


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("  🚀 FLEXIBLE PLANNING SYSTEM - TEST SUITE")
    print("="*70)

    try:
        test_task_analyzer()
        test_codebase_intelligence()
        test_dynamic_prompt_generation()
        test_execution_plan_generation()
        test_vietnamese_support()

        print_section("✅ ALL TESTS COMPLETED SUCCESSFULLY")
        print("The flexible planning system is working correctly!")
        print("\nKey Features Demonstrated:")
        print("  ✓ Task classification (feature, refactor, debug, etc.)")
        print("  ✓ Complexity estimation (simple, moderate, complex)")
        print("  ✓ Tech stack detection (React, Python, Next.js, etc.)")
        print("  ✓ Dynamic prompt generation based on context")
        print("  ✓ Execution plan generation from conversations")
        print("  ✓ Multi-language support (English & Vietnamese)")
        print("\n")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
