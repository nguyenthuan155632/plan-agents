"""
Execution Plan Generator - Converts planning discussions into actionable steps.

This module analyzes the conversation between Agent A and Agent B to:
- Extract key decisions and consensus points
- Generate actionable implementation steps
- Create file-level change checklist
- Suggest testing strategy
- Provide clear next steps for developers
"""

import re
from typing import List, Dict, Optional, Set
from dataclasses import dataclass
from enum import Enum


class ActionType(Enum):
    """Types of actions in execution plan"""
    CREATE_FILE = "create_file"
    MODIFY_FILE = "modify_file"
    DELETE_FILE = "delete_file"
    INSTALL_DEPENDENCY = "install_dependency"
    RUN_COMMAND = "run_command"
    TEST = "test"
    REVIEW = "review"


@dataclass
class ActionStep:
    """Single action step in execution plan"""
    step_number: int
    action_type: ActionType
    description: str
    file_path: Optional[str] = None
    code_snippet: Optional[str] = None
    dependencies: List[int] = None  # Step numbers this depends on

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

    def __str__(self):
        result = f"{self.step_number}. [{self.action_type.value.upper()}] {self.description}"
        if self.file_path:
            result += f"\n   File: `{self.file_path}`"
        if self.code_snippet:
            snippet = self.code_snippet[:100].strip()
            result += f"\n   Code: {snippet}..."
        if self.dependencies:
            result += f"\n   Depends on: steps {', '.join(map(str, self.dependencies))}"
        return result


@dataclass
class ExecutionPlan:
    """Complete execution plan with all steps and metadata"""
    summary: str
    decisions: List[str]
    action_steps: List[ActionStep]
    testing_strategy: str
    estimated_complexity: str
    files_to_change: List[str]
    dependencies_to_add: List[str]
    risks_and_considerations: List[str]

    def to_markdown(self, language: str = "english") -> str:
        """Convert execution plan to markdown format"""
        if language == "vietnamese":
            return self._to_markdown_vi()
        else:
            return self._to_markdown_en()

    def _to_markdown_en(self) -> str:
        """English markdown format"""
        sections = []

        # Header
        sections.append("# 📋 Execution Plan\n")

        # Summary
        sections.append("## 📝 Summary\n")
        sections.append(f"{self.summary}\n")

        # Key Decisions
        if self.decisions:
            sections.append("## ✅ Key Decisions\n")
            for i, decision in enumerate(self.decisions, 1):
                sections.append(f"{i}. {decision}")
            sections.append("")

        # Action Steps
        sections.append("## 🔨 Implementation Steps\n")
        for step in self.action_steps:
            sections.append(f"### Step {step.step_number}: {step.description}\n")
            sections.append(f"**Type:** {step.action_type.value}\n")

            if step.file_path:
                sections.append(f"**File:** `{step.file_path}`\n")

            if step.code_snippet:
                sections.append("**Code:**\n```")
                sections.append(step.code_snippet)
                sections.append("```\n")

            if step.dependencies:
                sections.append(f"**Dependencies:** Requires steps {', '.join(map(str, step.dependencies))}\n")

        # Files to Change
        if self.files_to_change:
            sections.append("## 📁 Files to Change\n")
            for file in self.files_to_change:
                sections.append(f"- `{file}`")
            sections.append("")

        # Dependencies
        if self.dependencies_to_add:
            sections.append("## 📦 Dependencies to Install\n")
            for dep in self.dependencies_to_add:
                sections.append(f"- {dep}")
            sections.append("")

        # Testing Strategy
        sections.append("## 🧪 Testing Strategy\n")
        sections.append(f"{self.testing_strategy}\n")

        # Risks
        if self.risks_and_considerations:
            sections.append("## ⚠️ Risks & Considerations\n")
            for risk in self.risks_and_considerations:
                sections.append(f"- {risk}")
            sections.append("")

        # Complexity
        sections.append(f"## 📊 Estimated Complexity: **{self.estimated_complexity}**\n")

        return "\n".join(sections)

    def _to_markdown_vi(self) -> str:
        """Vietnamese markdown format"""
        sections = []

        # Header
        sections.append("# 📋 Kế Hoạch Thực Thi\n")

        # Summary
        sections.append("## 📝 Tóm Tắt\n")
        sections.append(f"{self.summary}\n")

        # Key Decisions
        if self.decisions:
            sections.append("## ✅ Quyết Định Chính\n")
            for i, decision in enumerate(self.decisions, 1):
                sections.append(f"{i}. {decision}")
            sections.append("")

        # Action Steps
        sections.append("## 🔨 Các Bước Thực Hiện\n")
        for step in self.action_steps:
            sections.append(f"### Bước {step.step_number}: {step.description}\n")
            sections.append(f"**Loại:** {step.action_type.value}\n")

            if step.file_path:
                sections.append(f"**File:** `{step.file_path}`\n")

            if step.code_snippet:
                sections.append("**Code:**\n```")
                sections.append(step.code_snippet)
                sections.append("```\n")

            if step.dependencies:
                sections.append(f"**Phụ thuộc:** Cần hoàn thành bước {', '.join(map(str, step.dependencies))}\n")

        # Files to Change
        if self.files_to_change:
            sections.append("## 📁 File Cần Thay Đổi\n")
            for file in self.files_to_change:
                sections.append(f"- `{file}`")
            sections.append("")

        # Dependencies
        if self.dependencies_to_add:
            sections.append("## 📦 Dependencies Cần Cài\n")
            for dep in self.dependencies_to_add:
                sections.append(f"- {dep}")
            sections.append("")

        # Testing Strategy
        sections.append("## 🧪 Chiến Lược Test\n")
        sections.append(f"{self.testing_strategy}\n")

        # Risks
        if self.risks_and_considerations:
            sections.append("## ⚠️ Rủi Ro & Lưu Ý\n")
            for risk in self.risks_and_considerations:
                sections.append(f"- {risk}")
            sections.append("")

        # Complexity
        sections.append(f"## 📊 Độ Phức Tạp Ước Tính: **{self.estimated_complexity}**\n")

        return "\n".join(sections)


class ExecutionPlanGenerator:
    """Generates executable plans from planning discussions"""

    @staticmethod
    def generate_from_conversation(
        conversation_messages: List[Dict[str, str]],
        original_request: str,
        language: str = "english"
    ) -> ExecutionPlan:
        """
        Generate execution plan from conversation history.

        Args:
            conversation_messages: List of messages with 'role' and 'content'
            original_request: The original user request
            language: Language for the plan (english/vietnamese)

        Returns:
            ExecutionPlan object
        """
        # Extract key information from conversation
        summary = ExecutionPlanGenerator._extract_summary(conversation_messages, original_request)
        decisions = ExecutionPlanGenerator._extract_decisions(conversation_messages)
        files_to_change = ExecutionPlanGenerator._extract_files(conversation_messages)
        dependencies = ExecutionPlanGenerator._extract_dependencies(conversation_messages)
        risks = ExecutionPlanGenerator._extract_risks(conversation_messages)

        # Generate action steps
        action_steps = ExecutionPlanGenerator._generate_action_steps(
            conversation_messages, files_to_change, dependencies
        )

        # Generate testing strategy
        testing_strategy = ExecutionPlanGenerator._generate_testing_strategy(
            conversation_messages, language
        )

        # Estimate complexity
        complexity = ExecutionPlanGenerator._estimate_complexity(action_steps)

        return ExecutionPlan(
            summary=summary,
            decisions=decisions,
            action_steps=action_steps,
            testing_strategy=testing_strategy,
            estimated_complexity=complexity,
            files_to_change=files_to_change,
            dependencies_to_add=dependencies,
            risks_and_considerations=risks
        )

    @staticmethod
    def _extract_summary(messages: List[Dict[str, str]], original_request: str) -> str:
        """Extract summary of what needs to be done"""
        # Look for summary sections in agent responses
        all_content = " ".join([msg['content'] for msg in messages if msg['role'] != 'HUMAN'])

        # Try to find explicit summary sections
        summary_pattern = r'(?:summary|tóm tắt|kết luận|conclusion)[:\s]+(.+?)(?:\n\n|$)'
        matches = re.findall(summary_pattern, all_content, re.IGNORECASE | re.DOTALL)

        if matches:
            return matches[-1].strip()[:300]  # Get last summary, max 300 chars

        # Fallback: use original request as summary
        return f"Implement: {original_request}"

    @staticmethod
    def _extract_decisions(messages: List[Dict[str, str]]) -> List[str]:
        """Extract key decisions made during discussion"""
        decisions = []
        all_content = "\n\n".join([msg['content'] for msg in messages])

        # Look for decision indicators
        decision_patterns = [
            r'(?:decided|quyết định|agreed|thống nhất)[:\s]+(.+?)(?:\n|\.)',
            r'(?:we will|we should|chúng ta sẽ|nên)[:\s]+(.+?)(?:\n|\.)',
            r'(?:final decision|quyết định cuối)[:\s]+(.+?)(?:\n|\.)',
        ]

        for pattern in decision_patterns:
            matches = re.findall(pattern, all_content, re.IGNORECASE)
            decisions.extend([m.strip() for m in matches if len(m.strip()) > 10])

        # Look for numbered/bulleted decisions
        numbered = re.findall(r'[\d]+[\.)]\s*(.+?)(?:\n|$)', all_content)
        decisions.extend([item.strip() for item in numbered if len(item.strip()) > 10])

        # Deduplicate and limit
        unique_decisions = []
        seen = set()
        for decision in decisions:
            if decision.lower() not in seen:
                unique_decisions.append(decision)
                seen.add(decision.lower())

        return unique_decisions[:10]  # Top 10 decisions

    @staticmethod
    def _extract_files(messages: List[Dict[str, str]]) -> List[str]:
        """Extract file paths mentioned in conversation"""
        all_content = " ".join([msg['content'] for msg in messages])

        # Pattern for file paths
        file_pattern = r'`([a-zA-Z0-9_/\-]+\.[a-zA-Z]+)`|([a-zA-Z0-9_/\-]+\.(py|js|tsx|ts|json|yml|yaml|md))'

        matches = re.findall(file_pattern, all_content)

        # Flatten and clean
        files = set()
        for match in matches:
            if isinstance(match, tuple):
                for m in match:
                    if m and len(m) > 0 and '.' in m:
                        files.add(m)
            else:
                files.add(match)

        return sorted(list(files))[:15]  # Max 15 files

    @staticmethod
    def _extract_dependencies(messages: List[Dict[str, str]]) -> List[str]:
        """Extract dependencies/libraries mentioned"""
        all_content = " ".join([msg['content'] for msg in messages])

        dependencies = set()

        # Look for npm/yarn install patterns
        npm_pattern = r'(?:npm install|yarn add|pip install)\s+([a-zA-Z0-9\-@/]+)'
        npm_matches = re.findall(npm_pattern, all_content)
        dependencies.update(npm_matches)

        # Look for import statements
        import_pattern = r'import.*?from\s+["\']([^"\']+)["\']'
        import_matches = re.findall(import_pattern, all_content)
        # Filter to external packages (not relative imports)
        external = [imp for imp in import_matches if not imp.startswith('.') and not imp.startswith('/')]
        dependencies.update([imp.split('/')[0] for imp in external])

        # Remove common built-ins
        built_ins = {'react', 'next', 'python', 'os', 'sys', 're', 'json'}
        filtered = [dep for dep in dependencies if dep.lower() not in built_ins]

        return sorted(list(filtered))[:10]

    @staticmethod
    def _extract_risks(messages: List[Dict[str, str]]) -> List[str]:
        """Extract risks and considerations mentioned"""
        all_content = "\n".join([msg['content'] for msg in messages])

        risks = []

        # Look for risk indicators
        risk_patterns = [
            r'(?:risk|rủi ro|concern|lo ngại)[:\s]+(.+?)(?:\n|\.)',
            r'(?:trade-off|đánh đổi|caveat|lưu ý)[:\s]+(.+?)(?:\n|\.)',
            r'(?:be careful|cẩn thận|watch out|chú ý)[:\s]+(.+?)(?:\n|\.)',
            r'(?:potential issue|vấn đề tiềm ẩn)[:\s]+(.+?)(?:\n|\.)',
        ]

        for pattern in risk_patterns:
            matches = re.findall(pattern, all_content, re.IGNORECASE)
            risks.extend([m.strip() for m in matches if len(m.strip()) > 10])

        # Deduplicate
        unique_risks = list(set(risks))

        return unique_risks[:8]  # Max 8 risks

    @staticmethod
    def _generate_action_steps(
        messages: List[Dict[str, str]],
        files: List[str],
        dependencies: List[str]
    ) -> List[ActionStep]:
        """Generate actionable steps from discussion"""
        steps = []
        step_num = 1

        # Step 1: Install dependencies if any
        if dependencies:
            steps.append(ActionStep(
                step_number=step_num,
                action_type=ActionType.INSTALL_DEPENDENCY,
                description=f"Install required dependencies: {', '.join(dependencies[:3])}{'...' if len(dependencies) > 3 else ''}",
                code_snippet=f"npm install {' '.join(dependencies)}" if dependencies else None
            ))
            step_num += 1

        # Step 2-N: File operations
        all_content = "\n".join([msg['content'] for msg in messages])

        # Detect file creation
        create_patterns = [
            r'create\s+(?:a\s+)?(?:new\s+)?(?:file\s+)?`?([a-zA-Z0-9_/\-]+\.[a-zA-Z]+)`?',
            r'tạo\s+(?:file\s+)?`?([a-zA-Z0-9_/\-]+\.[a-zA-Z]+)`?',
        ]

        files_to_create = set()
        for pattern in create_patterns:
            matches = re.findall(pattern, all_content, re.IGNORECASE)
            files_to_create.update(matches)

        for file in files_to_create:
            if file in files:
                steps.append(ActionStep(
                    step_number=step_num,
                    action_type=ActionType.CREATE_FILE,
                    description=f"Create new file: {file}",
                    file_path=file,
                    dependencies=[1] if dependencies else []
                ))
                step_num += 1

        # Detect file modifications
        modify_patterns = [
            r'(?:modify|update|change|edit|refactor)\s+`?([a-zA-Z0-9_/\-]+\.[a-zA-Z]+)`?',
            r'(?:sửa|cập nhật|thay đổi)\s+`?([a-zA-Z0-9_/\-]+\.[a-zA-Z]+)`?',
        ]

        files_to_modify = set()
        for pattern in modify_patterns:
            matches = re.findall(pattern, all_content, re.IGNORECASE)
            files_to_modify.update(matches)

        for file in files_to_modify:
            if file in files and file not in files_to_create:
                steps.append(ActionStep(
                    step_number=step_num,
                    action_type=ActionType.MODIFY_FILE,
                    description=f"Modify existing file: {file}",
                    file_path=file
                ))
                step_num += 1

        # Add remaining files as generic modifications
        processed_files = files_to_create | files_to_modify
        for file in files:
            if file not in processed_files:
                steps.append(ActionStep(
                    step_number=step_num,
                    action_type=ActionType.MODIFY_FILE,
                    description=f"Update file: {file}",
                    file_path=file
                ))
                step_num += 1

        # Add testing step
        steps.append(ActionStep(
            step_number=step_num,
            action_type=ActionType.TEST,
            description="Run tests to verify implementation",
            dependencies=list(range(1, step_num))
        ))
        step_num += 1

        # Add review step
        steps.append(ActionStep(
            step_number=step_num,
            action_type=ActionType.REVIEW,
            description="Code review and quality check",
            dependencies=[step_num - 1]
        ))

        return steps

    @staticmethod
    def _generate_testing_strategy(messages: List[Dict[str, str]], language: str) -> str:
        """Generate testing strategy from discussion"""
        all_content = " ".join([msg['content'] for msg in messages])

        # Look for test mentions
        has_unit_test = bool(re.search(r'unit test', all_content, re.IGNORECASE))
        has_integration = bool(re.search(r'integration test', all_content, re.IGNORECASE))
        has_e2e = bool(re.search(r'e2e|end-to-end', all_content, re.IGNORECASE))

        if language == "vietnamese":
            strategy = "Chiến lược test:\n"
            if has_unit_test:
                strategy += "- Unit test cho từng component/function riêng lẻ\n"
            if has_integration:
                strategy += "- Integration test cho các module tương tác với nhau\n"
            if has_e2e:
                strategy += "- E2E test cho user flow hoàn chỉnh\n"

            if not (has_unit_test or has_integration or has_e2e):
                strategy += "- Test thủ công các tính năng chính\n"
                strategy += "- Kiểm tra edge cases và error handling"
        else:
            strategy = "Testing Strategy:\n"
            if has_unit_test:
                strategy += "- Unit tests for individual components/functions\n"
            if has_integration:
                strategy += "- Integration tests for module interactions\n"
            if has_e2e:
                strategy += "- E2E tests for complete user flows\n"

            if not (has_unit_test or has_integration or has_e2e):
                strategy += "- Manual testing of key features\n"
                strategy += "- Verify edge cases and error handling"

        return strategy

    @staticmethod
    def _estimate_complexity(steps: List[ActionStep]) -> str:
        """Estimate complexity based on action steps"""
        num_steps = len(steps)
        num_files = len([s for s in steps if s.action_type in [ActionType.CREATE_FILE, ActionType.MODIFY_FILE]])

        if num_files <= 2 and num_steps <= 4:
            return "Low (1-2 hours)"
        elif num_files <= 5 and num_steps <= 8:
            return "Medium (3-6 hours)"
        else:
            return "High (1-2 days)"


# Example usage
if __name__ == "__main__":
    # Sample conversation
    sample_messages = [
        {
            "role": "HUMAN",
            "content": "Add authentication to the app using NextAuth.js"
        },
        {
            "role": "AGENT_A",
            "content": """I'll propose implementing authentication using NextAuth.js.

Steps:
1. Install next-auth dependency
2. Create `pages/api/auth/[...nextauth].ts` for auth configuration
3. Modify `pages/_app.tsx` to add SessionProvider
4. Create login/logout components

Trade-off: NextAuth.js adds some bundle size but provides robust auth."""
        },
        {
            "role": "AGENT_B",
            "content": """Agent A's approach is solid. Alternative consideration:

We could also use middleware in `middleware.ts` for route protection.
Risk: Need to handle session storage (consider Redis for production).

Decision: NextAuth.js is good choice for this stack."""
        }
    ]

    plan = ExecutionPlanGenerator.generate_from_conversation(
        sample_messages,
        "Add authentication to the app using NextAuth.js",
        language="english"
    )

    print(plan.to_markdown())
