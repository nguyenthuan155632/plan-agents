"""
Dynamic Prompt Generator - Creates context-aware planning prompts.

This module generates intelligent prompts based on:
- Task context (type, complexity)
- Codebase structure and tech stack
- Relevant files and patterns
- Agent role (A or B)
"""

from typing import Optional
from enum import Enum

# Import task analyzer types
from agents.shared.task_analyzer import TaskContext, TaskType, ComplexityLevel
from agents.shared.codebase_intelligence import CodebaseStructure, RelevantContext

# Try to import Role from core.message, fallback to local definition
try:
    from core.message import Role
except ImportError:
    # Fallback Role definition for standalone usage
    class Role(Enum):
        AGENT_A = "AGENT_A"
        AGENT_B = "AGENT_B"
        HUMAN = "HUMAN"


class PromptGenerator:
    """Generates dynamic, context-aware prompts for planning agents"""

    @staticmethod
    def generate_planning_prompt(
        role: Role,
        task_context: TaskContext,
        codebase_structure: Optional[CodebaseStructure] = None,
        relevant_context: Optional[RelevantContext] = None
    ) -> str:
        """
        Generate a dynamic system prompt based on task and codebase context.

        Args:
            role: Agent role (AGENT_A or AGENT_B)
            task_context: Analyzed task information
            codebase_structure: Optional codebase structure analysis
            relevant_context: Optional task-specific relevant context

        Returns:
            Dynamic system prompt tailored to the task
        """
        if role == Role.AGENT_A:
            return PromptGenerator._generate_agent_a_prompt(
                task_context, codebase_structure, relevant_context
            )
        else:
            return PromptGenerator._generate_agent_b_prompt(
                task_context, codebase_structure, relevant_context
            )

    @staticmethod
    def _generate_agent_a_prompt(
        task_context: TaskContext,
        codebase_structure: Optional[CodebaseStructure],
        relevant_context: Optional[RelevantContext]
    ) -> str:
        """Generate Agent A prompt with context awareness"""

        # Base role description
        base_prompt = """You are Agent A - a collaborative planning assistant who provides initial solution proposals."""

        # Add task-specific guidance
        task_guidance = PromptGenerator._get_task_specific_guidance(
            task_context.task_type, role="A"
        )

        # Add codebase context
        codebase_context = PromptGenerator._build_codebase_context_section(
            codebase_structure, relevant_context
        )

        # Add planning structure
        planning_structure = PromptGenerator._get_planning_structure(
            task_context, role="A"
        )

        # Add language instruction
        lang = "Vietnamese" if task_context.language == "vietnamese" else "English"
        language_instruction = f"\n\n🌍 LANGUAGE: Respond in {lang} to match the user's request."

        # Build final prompt
        final_prompt = f"""{base_prompt}

{task_guidance}

{codebase_context}

{planning_structure}

💬 YOUR APPROACH:
1. **Analyze the request** considering the codebase context above
2. **Propose a concrete solution** that fits existing patterns
3. **Reference specific files/components** when relevant
4. **Keep it practical** - focus on what works with current tech stack
5. **Be concise** (150-300 words) but include code examples if helpful

✅ GOOD RESPONSES:
- "Based on the existing RAG system in `rag/rag_system.py`, we can extend it by..."
- "Looking at `web/components/`, I suggest creating a new component similar to..."
- "The codebase uses {relevant_context.tech_stack_context if relevant_context else 'standard patterns'}, so we should..."

❌ AVOID:
- Generic advice without codebase context
- Ignoring existing patterns and structure
- Over-complicating when simple solutions exist{language_instruction}
"""

        return final_prompt

    @staticmethod
    def _generate_agent_b_prompt(
        task_context: TaskContext,
        codebase_structure: Optional[CodebaseStructure],
        relevant_context: Optional[RelevantContext]
    ) -> str:
        """Generate Agent B prompt with context awareness"""

        base_prompt = """You are Agent B - a collaborative planning assistant who provides alternative perspectives and constructive critique."""

        # Add task-specific guidance
        task_guidance = PromptGenerator._get_task_specific_guidance(
            task_context.task_type, role="B"
        )

        # Add codebase context
        codebase_context = PromptGenerator._build_codebase_context_section(
            codebase_structure, relevant_context
        )

        # Add planning structure
        planning_structure = PromptGenerator._get_planning_structure(
            task_context, role="B"
        )

        # Add language instruction
        lang = "Vietnamese" if task_context.language == "vietnamese" else "English"
        language_instruction = f"\n\n🌍 LANGUAGE: Respond in {lang} to match the user's request."

        final_prompt = f"""{base_prompt}

{task_guidance}

{codebase_context}

{planning_structure}

💬 YOUR APPROACH:
1. **Acknowledge** what Agent A proposed that works well
2. **Consider alternatives** - "Another approach could be..."
3. **Point out trade-offs** using codebase context
4. **Reference different files/patterns** if applicable
5. **Be constructive** (150-300 words) - debate the approach, not the goal

✅ GOOD RESPONSES:
- "Agent A's approach works. However, looking at `core/coordinator.py`, we could also..."
- "Good suggestion. Trade-off: this adds a dependency. If we use existing libraries, we could..."
- "Solid plan. Alternative perspective: the codebase already has similar patterns, we might reuse..."

❌ AVOID:
- Blindly agreeing without adding value
- Criticizing without offering alternatives
- Ignoring Agent A's proposal completely{language_instruction}
"""

        return final_prompt

    @staticmethod
    def _get_task_specific_guidance(task_type: TaskType, role: str) -> str:
        """Get guidance specific to the task type"""

        if role == "A":
            guidance_map = {
                TaskType.FEATURE: """
🎯 TASK TYPE: Feature Implementation
**Your focus:** Propose a concrete implementation plan
- Break down the feature into components/modules
- Identify which files need to be created/modified
- Suggest data models, APIs, or UI components needed
- Consider integration points with existing code
""",
                TaskType.REFACTOR: """
🎯 TASK TYPE: Code Refactoring
**Your focus:** Propose specific refactoring approach
- Identify code smells or improvement opportunities
- Suggest refactoring pattern (extract method, move class, etc.)
- Show before/after examples if possible
- Ensure backward compatibility considerations
""",
                TaskType.DEBUG: """
🎯 TASK TYPE: Bug Fix
**Your focus:** Diagnose and propose fix
- Analyze the error/issue described
- Identify likely root cause based on codebase
- Suggest specific fix with file/line references
- Consider edge cases and testing
""",
                TaskType.ARCHITECTURE: """
🎯 TASK TYPE: Architecture Decision
**Your focus:** Propose architectural approach
- Suggest architecture pattern that fits the codebase
- Consider scalability and maintainability
- Reference existing architectural patterns found
- Provide high-level design with rationale
""",
                TaskType.OPTIMIZATION: """
🎯 TASK TYPE: Performance Optimization
**Your focus:** Identify optimization opportunities
- Point out performance bottlenecks
- Suggest specific optimizations (caching, indexing, etc.)
- Consider trade-offs (speed vs memory, complexity vs performance)
- Reference similar optimizations in the codebase
""",
            }
        else:  # Role B
            guidance_map = {
                TaskType.FEATURE: """
🎯 TASK TYPE: Feature Implementation
**Your focus:** Provide alternative approaches and considerations
- Suggest different architectural approaches
- Point out potential edge cases Agent A might have missed
- Consider alternative tech choices within the stack
- Discuss scalability and future extensibility
""",
                TaskType.REFACTOR: """
🎯 TASK TYPE: Code Refactoring
**Your focus:** Challenge assumptions and suggest alternatives
- Question if refactoring is necessary or if simpler approach exists
- Suggest alternative refactoring patterns
- Point out risks (breaking changes, test coverage needs)
- Consider incremental vs big-bang refactoring
""",
                TaskType.DEBUG: """
🎯 TASK TYPE: Bug Fix
**Your focus:** Verify diagnosis and consider alternatives
- Double-check if root cause is correctly identified
- Suggest alternative hypotheses
- Consider if fix addresses symptom vs root cause
- Recommend additional debugging steps or tests
""",
                TaskType.ARCHITECTURE: """
🎯 TASK TYPE: Architecture Decision
**Your focus:** Present alternative architectural approaches
- Suggest different patterns with trade-offs
- Question assumptions about requirements
- Consider simpler or more complex alternatives
- Discuss long-term maintenance implications
""",
                TaskType.OPTIMIZATION: """
🎯 TASK TYPE: Performance Optimization
**Your focus:** Challenge optimization and suggest alternatives
- Question if optimization is premature
- Suggest different optimization strategies
- Consider readability vs performance trade-off
- Recommend profiling before/after
""",
            }

        return guidance_map.get(task_type, """
🎯 TASK TYPE: General Planning
**Your focus:** Provide thoughtful analysis and planning
- Understand the request in context of the codebase
- Propose practical solutions
- Consider existing patterns and conventions
""")

    @staticmethod
    def _build_codebase_context_section(
        codebase_structure: Optional[CodebaseStructure],
        relevant_context: Optional[RelevantContext]
    ) -> str:
        """Build the codebase context section of the prompt"""

        if not codebase_structure and not relevant_context:
            return """
📚 CODEBASE CONTEXT:
No codebase context available. Provide general best practices.
"""

        sections = ["📚 CODEBASE CONTEXT:"]

        # Tech stack
        if codebase_structure and codebase_structure.tech_stack:
            ts = codebase_structure.tech_stack
            tech_parts = []

            if ts.languages:
                tech_parts.append(f"**Languages:** {', '.join(ts.languages)}")
            if ts.frameworks:
                tech_parts.append(f"**Frameworks:** {', '.join(ts.frameworks)}")
            if ts.databases:
                tech_parts.append(f"**Databases:** {', '.join(ts.databases)}")

            if tech_parts:
                sections.append("**Tech Stack:**\n" + " | ".join(tech_parts))

        # Architectural patterns
        if codebase_structure and codebase_structure.patterns:
            sections.append(f"**Architecture:** {', '.join(codebase_structure.patterns)}")

        # Relevant files
        if relevant_context and relevant_context.related_files:
            file_list = [f"`{f['path']}`" for f in relevant_context.related_files[:5]]
            sections.append(f"**Relevant Files:** {', '.join(file_list)}")

        # Similar patterns
        if relevant_context and relevant_context.similar_patterns:
            sections.append(f"**Existing Patterns:** {'; '.join(relevant_context.similar_patterns[:3])}")

        # Suggested approach
        if relevant_context and relevant_context.suggested_approach:
            sections.append(f"**Suggestion:** {relevant_context.suggested_approach}")

        # Dependencies to consider
        if relevant_context and relevant_context.dependencies_to_consider:
            deps = ', '.join(relevant_context.dependencies_to_consider[:5])
            sections.append(f"**Available Libraries:** {deps}")

        return "\n".join(sections)

    @staticmethod
    def _get_planning_structure(task_context: TaskContext, role: str) -> str:
        """Get the planning structure based on complexity"""

        if task_context.complexity == ComplexityLevel.SIMPLE:
            if role == "A":
                return """
📝 PLANNING STRUCTURE (Simple Task):
1. **Quick Analysis** (1-2 sentences)
2. **Proposed Solution** (concise approach)
3. **Implementation Note** (key file/function to modify)
"""
            else:
                return """
📝 PLANNING STRUCTURE (Simple Task):
1. **Acknowledge** Agent A's approach
2. **Quick Alternative** (if any) or confirmation
3. **One Key Consideration** (edge case, trade-off, etc.)
"""

        elif task_context.complexity == ComplexityLevel.MODERATE:
            if role == "A":
                return """
📝 PLANNING STRUCTURE (Moderate Task):
1. **Problem Analysis** (understand the request)
2. **Proposed Approach** (step-by-step plan)
3. **Key Files/Components** (what needs to change)
4. **Considerations** (dependencies, testing, etc.)
"""
            else:
                return """
📝 PLANNING STRUCTURE (Moderate Task):
1. **Strengths** of Agent A's approach
2. **Alternative Approach** (different way to solve it)
3. **Trade-offs** (compare the approaches)
4. **Recommendation** (which to prefer and why)
"""

        else:  # COMPLEX
            if role == "A":
                return """
📝 PLANNING STRUCTURE (Complex Task):
1. **Requirement Analysis** (what are we really trying to achieve?)
2. **Architecture Proposal** (high-level design)
3. **Component Breakdown** (modules, services, components needed)
4. **Integration Points** (how it fits with existing code)
5. **Implementation Phases** (what to build first)
6. **Risk Assessment** (potential challenges)
"""
            else:
                return """
📝 PLANNING STRUCTURE (Complex Task):
1. **Architecture Review** (Agent A's proposal analysis)
2. **Alternative Architecture** (different approach)
3. **Detailed Trade-offs** (scalability, maintainability, complexity)
4. **Risk Analysis** (what could go wrong in each approach)
5. **Recommendation** (synthesize the discussion)
"""

    @staticmethod
    def build_context_prompt_addon(
        task_context: TaskContext,
        relevant_context: Optional[RelevantContext] = None
    ) -> str:
        """
        Build an addon to existing prompts with RAG context.
        This can be appended to user prompts for better context.

        Args:
            task_context: The analyzed task
            relevant_context: RAG-retrieved relevant context

        Returns:
            Additional context string to append to prompts
        """
        if not relevant_context:
            return ""

        addon_parts = ["\n\n--- CODEBASE INTELLIGENCE ---"]

        # Add tech stack context
        if relevant_context.tech_stack_context:
            addon_parts.append(f"Tech Stack: {relevant_context.tech_stack_context}")

        # Add relevant files with context
        if relevant_context.related_files:
            addon_parts.append("\nRelevant Files Found:")
            for i, file_info in enumerate(relevant_context.related_files[:3], 1):
                addon_parts.append(f"{i}. `{file_info['path']}`")
                if file_info.get('context'):
                    # Show a snippet of context
                    context_snippet = file_info['context'][:150].strip()
                    addon_parts.append(f"   Context: {context_snippet}...")

        # Add similar patterns
        if relevant_context.similar_patterns:
            addon_parts.append("\nExisting Patterns:")
            for pattern in relevant_context.similar_patterns[:2]:
                addon_parts.append(f"- {pattern}")

        # Add suggested approach
        if relevant_context.suggested_approach:
            addon_parts.append(f"\nSuggested Approach: {relevant_context.suggested_approach}")

        addon_parts.append("--- END CODEBASE INTELLIGENCE ---\n")

        return "\n".join(addon_parts)


# Example usage
if __name__ == "__main__":
    from agents.shared.task_analyzer import TaskAnalyzer

    # Test case 1: Simple feature
    task1 = "Add a delete button to the UserCard component"
    context1 = TaskAnalyzer.analyze(task1)

    prompt1 = PromptGenerator.generate_planning_prompt(
        role=Role.AGENT_A,
        task_context=context1
    )

    print("=" * 60)
    print("SIMPLE FEATURE - Agent A Prompt")
    print("=" * 60)
    print(prompt1)
    print("\n")

    # Test case 2: Complex architecture
    task2 = "Design a real-time notification system for the platform"
    context2 = TaskAnalyzer.analyze(task2)

    prompt2 = PromptGenerator.generate_planning_prompt(
        role=Role.AGENT_B,
        task_context=context2
    )

    print("=" * 60)
    print("COMPLEX ARCHITECTURE - Agent B Prompt")
    print("=" * 60)
    print(prompt2)
