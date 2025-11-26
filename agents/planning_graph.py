"""
LangGraph workflow for structured planning with human interrupt support.

Key design:
- State persisted in database (not in-memory)
- Each signal triggers ONE node execution
- Human messages can interrupt/redirect the flow
"""

import logging
from typing import Optional, Callable, Tuple
from datetime import datetime

from agents.planning_nodes import PlanningNodes
from agents.shared.language_detector import LanguageDetector
from core.message import Message, Role, Signal

logger = logging.getLogger(__name__)


# Node execution order
NODE_SEQUENCE = [
    "analyze_codebase",
    "propose_changes",
    "review_and_refine",
    "validate_proposal",
    "finalize_plan",
    "completed"
]


class TurnBasedPlanningWorkflow:
    """
    Turn-based LangGraph workflow with database persistence.

    Features:
    - Each turn executes ONE node
    - State saved to database after each node
    - Human can interrupt at any point
    - Supports resumption from any node
    """

    def __init__(self, db, rag_chain, agent_a, agent_b):
        """
        Initialize turn-based planning workflow.

        Args:
            db: Database instance for state persistence
            rag_chain: RAG chain for codebase queries
            agent_a: Agent A instance (has generate_response method)
            agent_b: Agent B instance (has generate_response method)
        """
        self.db = db
        self.rag_chain = rag_chain
        self.agent_a = agent_a
        self.agent_b = agent_b

        # Create LLM callers that use generate_response for dynamic prompts
        def llm_caller_a(system_prompt: str, user_prompt: str) -> str:
            # Create a fake message to trigger generate_response
            from core.message import Message, Signal
            from datetime import datetime

            # Extract session_id from context if available, otherwise use dummy
            session_id = getattr(llm_caller_a, '_current_session_id', 'planning-session')

            fake_message = Message(
                session_id=session_id,
                role=Role.HUMAN,
                content=user_prompt,
                signal=Signal.CONTINUE,
                timestamp=datetime.utcnow()
            )

            # Use generate_response which includes dynamic prompts
            return agent_a.generate_response(fake_message)

        def llm_caller_b(system_prompt: str, user_prompt: str) -> str:
            # Create a fake message to trigger generate_response
            from core.message import Message, Signal
            from datetime import datetime

            session_id = getattr(llm_caller_b, '_current_session_id', 'planning-session')

            fake_message = Message(
                session_id=session_id,
                role=Role.HUMAN,
                content=user_prompt,
                signal=Signal.CONTINUE,
                timestamp=datetime.utcnow()
            )

            # Use generate_response which includes dynamic prompts
            return agent_b.generate_response(fake_message)

        # Store references for session_id injection
        self.llm_caller_a = llm_caller_a
        self.llm_caller_b = llm_caller_b

        # Initialize nodes
        self.nodes = PlanningNodes(rag_chain, llm_caller_a, llm_caller_b)

        # Map node names to functions
        self.node_functions = {
            "analyze_codebase": self.nodes.analyze_codebase,
            "propose_changes": self.nodes.propose_changes,
            "review_and_refine": self.nodes.review_and_refine,
            "validate_proposal": self.nodes.validate_proposal,
            "finalize_plan": self.nodes.finalize_plan,
        }

    def initialize_state(self, session_id: str, request: str, language: str = "english") -> dict:
        """Initialize planning state for a new session."""
        state = {
            "session_id": session_id,
            "current_node": "analyze_codebase",
            "request": request,
            "language": language,
            "codebase_context": [],
            "identified_files": [],
            "agent_a_analysis": "",
            "agent_a_proposal": "",
            "agent_b_review": "",
            "validation_passed": False,
            "validation_issues": [],
            "final_plan": "",
            "messages": []
        }
        self.db.save_planning_state(session_id, state)
        return state

    def get_or_create_state(self, session_id: str, request: str = "", language: str = "english") -> dict:
        """Get existing state or create new one."""
        state = self.db.get_planning_state(session_id)
        if state:
            # Add messages list (not persisted)
            state["messages"] = []
            return state
        return self.initialize_state(session_id, request, language)

    def execute_one_turn(self, session_id: str, human_message: Optional[Message] = None) -> Tuple[dict, Message]:
        """
        Execute ONE turn in the planning workflow.

        Args:
            session_id: Session ID
            human_message: Optional human message that triggered this turn

        Returns:
            Tuple of (updated state, response message)
        """
        # Get current state
        state = self.db.get_planning_state(session_id)
        if not state:
            logger.error(f"No planning state found for session {session_id}")
            return None, None

        state["messages"] = []  # Reset messages for this turn
        current_node = state.get("current_node", "analyze_codebase")

        # Check if human interrupted
        if human_message and human_message.role == Role.HUMAN:
            return self._handle_human_interrupt(state, human_message)

        # Check if already completed
        if current_node == "completed":
            logger.info(f"[Planning] Session {session_id} already completed")
            return state, self._create_completion_message(state)

        # Execute current node
        logger.info(f"[Planning] Executing node: {current_node}")
        node_func = self.node_functions.get(current_node)
        if not node_func:
            logger.error(f"Unknown node: {current_node}")
            return state, None

        try:
            # Inject session_id into LLM callers for dynamic prompts
            self.llm_caller_a._current_session_id = session_id
            self.llm_caller_b._current_session_id = session_id

            # Execute node
            logger.info(f"[Planning] >>> Executing node function: {current_node}")
            updated_state = node_func(state)
            logger.info(f"[Planning] <<< Node function completed: {current_node}")

            # Get next node
            next_node = self._get_next_node(current_node)
            updated_state["current_node"] = next_node
            logger.info(f"[Planning] Node {current_node} completed. Next node will be: {next_node}")

            # Save state to database
            self.db.save_planning_state(session_id, updated_state)

            # Create response message
            response_message = self._create_node_message(updated_state, current_node)
            logger.info(f"[Planning] Response signal: {response_message.signal.value}")
            return updated_state, response_message

        except Exception as e:
            logger.error(f"[Planning] Node {current_node} failed: {e}", exc_info=True)
            error_msg = self._create_error_message(state, str(e))
            return state, error_msg

    def _handle_human_interrupt(self, state: dict, human_message: Message) -> Tuple[dict, Message]:
        """Handle human interruption during planning."""
        session_id = state["session_id"]
        content = human_message.content.lower()
        language = state.get("language", "english")

        # Check for STOP request
        if any(kw in content for kw in ['stop', 'dừng', '🛑', 'tóm tắt', 'summarize']):
            logger.info(f"[Planning] Human requested STOP")
            return self._generate_summary(state, human_message)

        # Check for feedback/modification request
        if any(kw in content for kw in ['sửa', 'thay đổi', 'modify', 'change', 'update', 'chỉnh']):
            logger.info(f"[Planning] Human requested modification")
            return self._handle_modification(state, human_message)

        # Default: incorporate human input and continue
        logger.info(f"[Planning] Human input received, incorporating into current step")
        return self._incorporate_human_input(state, human_message)

    def _generate_summary(self, state: dict, human_message: Message) -> Tuple[dict, Message]:
        """Generate summary when human requests stop."""
        language = state.get("language", "english")
        session_id = state["session_id"]

        # Build summary from current state
        if language == 'vietnamese':
            summary = f"""## 📋 Tóm tắt kế hoạch

### Yêu cầu ban đầu:
{state.get('request', 'Không có')}

### Phân tích codebase (Agent A):
{state.get('agent_a_analysis', 'Chưa hoàn thành')[:500]}...

### Đề xuất (Agent A):
{state.get('agent_a_proposal', 'Chưa hoàn thành')[:500]}...

### Xem xét (Agent B):
{state.get('agent_b_review', 'Chưa hoàn thành')[:500]}...

### File liên quan:
{chr(10).join(f'- {f}' for f in state.get('identified_files', [])) or '- Chưa xác định'}

---
⛔ Kế hoạch đã dừng theo yêu cầu."""
        else:
            summary = f"""## 📋 Plan Summary

### Original Request:
{state.get('request', 'None')}

### Codebase Analysis (Agent A):
{state.get('agent_a_analysis', 'Not completed')[:500]}...

### Proposal (Agent A):
{state.get('agent_a_proposal', 'Not completed')[:500]}...

### Review (Agent B):
{state.get('agent_b_review', 'Not completed')[:500]}...

### Related Files:
{chr(10).join(f'- {f}' for f in state.get('identified_files', [])) or '- Not identified'}

---
⛔ Planning stopped as requested."""

        # Mark as completed
        state["current_node"] = "completed"
        state["final_plan"] = summary
        self.db.save_planning_state(session_id, state)

        # Create response message
        response = Message(
            session_id=session_id,
            role=Role.AGENT_A,  # Summary comes from Agent A
            content=summary,
            signal=Signal.HANDOVER
        )

        return state, response

    def _handle_modification(self, state: dict, human_message: Message) -> Tuple[dict, Message]:
        """Handle modification request from human."""
        language = state.get("language", "english")
        session_id = state["session_id"]
        current_node = state.get("current_node", "analyze_codebase")

        # Determine which step to go back to based on what human wants to modify
        content = human_message.content.lower()

        if any(kw in content for kw in ['phân tích', 'analysis', 'analyze']):
            state["current_node"] = "analyze_codebase"
            state["agent_a_analysis"] = ""
        elif any(kw in content for kw in ['đề xuất', 'proposal', 'propose']):
            state["current_node"] = "propose_changes"
            state["agent_a_proposal"] = ""
        elif any(kw in content for kw in ['review', 'xem xét']):
            state["current_node"] = "review_and_refine"
            state["agent_b_review"] = ""
        else:
            # Default: go back one step
            current_idx = NODE_SEQUENCE.index(current_node) if current_node in NODE_SEQUENCE else 0
            if current_idx > 0:
                state["current_node"] = NODE_SEQUENCE[current_idx - 1]

        # Append human's modification to request
        state["request"] = f"{state.get('request', '')}\n\n[Bổ sung từ human]: {human_message.content}"

        self.db.save_planning_state(session_id, state)

        # Create acknowledgment message
        if language == 'vietnamese':
            ack = f"✅ Đã nhận phản hồi. Sẽ quay lại bước '{state['current_node']}' với thông tin mới."
        else:
            ack = f"✅ Feedback received. Will go back to '{state['current_node']}' step with new information."

        response = Message(
            session_id=session_id,
            role=Role.AGENT_A,
            content=ack,
            signal=Signal.CONTINUE  # Continue to re-execute the step
        )

        return state, response

    def _incorporate_human_input(self, state: dict, human_message: Message) -> Tuple[dict, Message]:
        """Incorporate human input and continue planning."""
        session_id = state["session_id"]
        language = state.get("language", "english")
        current_node = state.get("current_node", "analyze_codebase")

        # Add human input to the request context
        state["request"] = f"{state.get('request', '')}\n\n[Góp ý từ human]: {human_message.content}"

        # If at completed node, RESTART workflow from beginning with full context
        if current_node == "completed":
            logger.info(f"[Planning] At completed node - restarting workflow from beginning with new input")
            state["current_node"] = "analyze_codebase"  # Restart from first node
            # Keep all previous context (agent_a_analysis, agent_b_review, etc.) for reference

            if language == 'vietnamese':
                ack = f"✅ Đã nhận góp ý. Bắt đầu vòng thảo luận mới với context đầy đủ."
            else:
                ack = f"✅ Input received. Starting new discussion round with full context."
        else:
            # For other nodes, continue with current step
            if language == 'vietnamese':
                ack = f"✅ Đã nhận góp ý. Tiếp tục với bước hiện tại."
            else:
                ack = f"✅ Input received. Continuing with current step."

        self.db.save_planning_state(session_id, state)

        response = Message(
            session_id=session_id,
            role=Role.AGENT_A,
            content=ack,
            signal=Signal.CONTINUE
        )

        return state, response

    def _get_next_node(self, current_node: str) -> str:
        """Get the next node in sequence."""
        try:
            idx = NODE_SEQUENCE.index(current_node)
            return NODE_SEQUENCE[idx + 1] if idx + 1 < len(NODE_SEQUENCE) else "completed"
        except ValueError:
            return "completed"

    def _create_node_message(self, state: dict, node_name: str) -> Message:
        """Create a message from node execution result."""
        session_id = state["session_id"]
        language = state.get("language", "english")

        # Determine which agent and content based on node
        if node_name in ["analyze_codebase", "propose_changes"]:
            role = Role.AGENT_A
            if node_name == "analyze_codebase":
                content = state.get("agent_a_analysis", "")
                prefix = "[Agent A - Phân tích]" if language == 'vietnamese' else "[Agent A - Analysis]"
            else:
                content = state.get("agent_a_proposal", "")
                prefix = "[Agent A - Đề xuất]" if language == 'vietnamese' else "[Agent A - Proposal]"
        elif node_name == "review_and_refine":
            role = Role.AGENT_B
            content = state.get("agent_b_review", "")
            prefix = "[Agent B - Xem xét]" if language == 'vietnamese' else "[Agent B - Review]"
        elif node_name == "validate_proposal":
            role = Role.AGENT_A
            passed = state.get("validation_passed", False)
            issues = state.get("validation_issues", [])
            if passed:
                content = "✅ Đề xuất đã qua kiểm tra" if language == 'vietnamese' else "✅ Proposal validated"
            else:
                content = f"⚠️ Cần điều chỉnh:\n" + "\n".join(f"- {i}" for i in issues) if language == 'vietnamese' else f"⚠️ Needs adjustment:\n" + "\n".join(f"- {i}" for i in issues)
            prefix = "[Kiểm tra]" if language == 'vietnamese' else "[Validation]"
        else:  # finalize_plan
            role = Role.AGENT_A
            content = state.get("final_plan", "")
            prefix = "[Kế hoạch cuối cùng]" if language == 'vietnamese' else "[Final Plan]"

        # Determine signal based on next node
        # CONTINUE = auto-proceed to next node
        # HANDOVER = wait for human input (only at certain checkpoints)
        next_node = state.get("current_node", "completed")
        logger.info(f"[Planning] Signal logic: next_node={next_node}, checking against ['validate_proposal', 'completed']")

        # Auto-continue between nodes, HANDOVER only at:
        # - After review (before validation) - checkpoint for human feedback
        # - After finalize (completed)
        if next_node in ["validate_proposal", "completed"]:
            signal = Signal.HANDOVER  # Checkpoint - wait for human
            logger.info(f"[Planning] Signal = HANDOVER (checkpoint)")
        else:
            signal = Signal.CONTINUE  # Auto-proceed to next node
            logger.info(f"[Planning] Signal = CONTINUE (auto-proceed)")

        logger.info(f"[Planning] Creating message: node={node_name}, next={next_node}, signal={signal.value}")

        return Message(
            session_id=session_id,
            role=role,
            content=f"{prefix}\n\n{content}",
            signal=signal
        )

    def _create_completion_message(self, state: dict) -> Message:
        """Create message when workflow is already completed."""
        language = state.get("language", "english")
        if language == 'vietnamese':
            content = "✅ Kế hoạch đã hoàn thành. Bạn có thể bắt đầu thực hiện hoặc yêu cầu điều chỉnh."
        else:
            content = "✅ Planning completed. You can start implementation or request modifications."

        return Message(
            session_id=state["session_id"],
            role=Role.AGENT_A,
            content=content,
            signal=Signal.HANDOVER
        )

    def _create_error_message(self, state: dict, error: str) -> Message:
        """Create error message."""
        language = state.get("language", "english")
        if language == 'vietnamese':
            content = f"❌ Lỗi khi thực hiện bước lập kế hoạch: {error}"
        else:
            content = f"❌ Error during planning step: {error}"

        return Message(
            session_id=state["session_id"],
            role=Role.AGENT_A,
            content=content,
            signal=Signal.HANDOVER
        )

    def is_completed(self, session_id: str) -> bool:
        """Check if planning is completed for a session."""
        state = self.db.get_planning_state(session_id)
        return state and state.get("current_node") == "completed"

    def get_current_node(self, session_id: str) -> str:
        """Get current node for a session."""
        state = self.db.get_planning_state(session_id)
        return state.get("current_node", "analyze_codebase") if state else "analyze_codebase"


# Backwards compatibility alias
PlanningWorkflow = TurnBasedPlanningWorkflow
