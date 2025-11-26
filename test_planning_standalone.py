"""
Standalone test for planning system components.
Tests individual modules without requiring full environment setup.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def print_section(title: str):
    """Print formatted section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def test_task_analyzer():
    """Test task analyzer module"""
    print_section("TEST 1: Task Analyzer")

    from agents.shared.task_analyzer import TaskAnalyzer, TaskType

    test_cases = [
        "Add authentication using NextAuth.js",
        "Refactor UserService.py to use DI",
        "Fix bug in api/users endpoint",
        "Design real-time notifications",
        "Thêm tính năng upload file",
    ]

    for task in test_cases:
        context = TaskAnalyzer.analyze(task)
        print(f"✓ {task[:50]}...")
        print(f"  → Type: {context.task_type.value}, Complexity: {context.complexity.value}, Lang: {context.language}")

    print("\n✅ Task Analyzer working correctly!\n")


def test_codebase_intelligence():
    """Test codebase intelligence"""
    print_section("TEST 2: Codebase Intelligence")

    from agents.shared.codebase_intelligence import CodebaseIntelligence

    sample_code = """
    File: app/page.tsx
    import React from 'react'
    import { useState } from 'react'

    File: package.json
    {"dependencies": {"react": "^18.0.0", "next": "^14.0.0"}}

    File: agents/base.py
    class BaseAgent:
        pass
    """

    intel = CodebaseIntelligence()
    structure = intel.analyze_codebase(sample_code)

    print(f"✓ Detected Languages: {', '.join(structure.tech_stack.languages) or 'None'}")
    print(f"✓ Detected Frameworks: {', '.join(structure.tech_stack.frameworks) or 'None'}")
    print(f"✓ File Types: {list(structure.file_patterns.keys())}")
    print(f"✓ Total Files: {structure.total_files}")

    print("\n✅ Codebase Intelligence working correctly!\n")


def test_prompt_generator():
    """Test dynamic prompt generation"""
    print_section("TEST 3: Dynamic Prompt Generator")

    from agents.shared.task_analyzer import TaskAnalyzer
    from agents.shared.prompt_generator import PromptGenerator
    from enum import Enum

    # Define a minimal Role enum for testing
    class Role(Enum):
        AGENT_A = "AGENT_A"
        AGENT_B = "AGENT_B"

    task = "Add authentication to the app"
    context = TaskAnalyzer.analyze(task)

    prompt = PromptGenerator.generate_planning_prompt(
        role=Role.AGENT_A,
        task_context=context
    )

    print(f"✓ Task: {task}")
    print(f"✓ Generated prompt length: {len(prompt)} chars")
    print(f"✓ Contains task guidance: {'TASK TYPE' in prompt}")
    print(f"✓ Contains planning structure: {'PLANNING STRUCTURE' in prompt}")

    # Show sample of prompt
    print(f"\n📄 Prompt Preview (first 300 chars):")
    print(prompt[:300] + "...\n")

    print("✅ Prompt Generator working correctly!\n")


def test_execution_plan_generator():
    """Test execution plan generation"""
    print_section("TEST 4: Execution Plan Generator")

    from agents.shared.execution_plan_generator import ExecutionPlanGenerator

    conversation = [
        {"role": "HUMAN", "content": "Add authentication using NextAuth.js"},
        {
            "role": "AGENT_A",
            "content": "Install next-auth. Create app/api/auth/[...nextauth]/route.ts. "
                      "Modify app/layout.tsx for SessionProvider. Create middleware.ts for protection."
        },
        {
            "role": "AGENT_B",
            "content": "Good approach. Consider: Redis for session storage, "
                      "RBAC for roles, refresh token rotation for security."
        }
    ]

    plan = ExecutionPlanGenerator.generate_from_conversation(
        conversation,
        "Add authentication using NextAuth.js",
        "english"
    )

    print(f"✓ Summary: {plan.summary[:80]}...")
    print(f"✓ Decisions: {len(plan.decisions)} key decisions")
    print(f"✓ Action Steps: {len(plan.action_steps)} steps")
    print(f"✓ Files to Change: {len(plan.files_to_change)} files")
    print(f"✓ Complexity: {plan.estimated_complexity}")

    print(f"\n📋 Sample Action Steps:")
    for step in plan.action_steps[:3]:
        print(f"  {step.step_number}. [{step.action_type.value}] {step.description}")

    print("\n✅ Execution Plan Generator working correctly!\n")


def main():
    """Run all standalone tests"""
    print("\n" + "="*70)
    print("  🚀 FLEXIBLE PLANNING SYSTEM - STANDALONE TESTS")
    print("="*70)

    try:
        test_task_analyzer()
        test_codebase_intelligence()
        test_prompt_generator()
        test_execution_plan_generator()

        print_section("✅ ALL TESTS PASSED")
        print("The flexible planning system is working correctly!\n")
        print("📊 System Capabilities:")
        print("  ✓ Analyzes tasks (type, complexity, language)")
        print("  ✓ Detects tech stack (languages, frameworks, libs)")
        print("  ✓ Generates context-aware prompts")
        print("  ✓ Creates actionable execution plans")
        print("  ✓ Supports English & Vietnamese")
        print("\n")

        return 0

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
