"""
Planning workflow nodes for LangGraph.
Each node represents a step in the structured planning process.
"""

import logging
from typing import TypedDict, Optional, List, Annotated
from operator import add

from core.message import Role

logger = logging.getLogger(__name__)


class PlanningState(TypedDict):
    """State schema for planning workflow."""
    # Input
    request: str                           # Human's original request
    session_id: str                        # Session ID for database
    language: str                          # Detected language

    # RAG context
    codebase_context: Annotated[List[str], add]  # RAG query results
    identified_files: List[str]            # Files relevant to the request

    # Agent proposals
    agent_a_analysis: str                  # Agent A's codebase analysis
    agent_a_proposal: str                  # Agent A's concrete proposal
    agent_b_review: str                    # Agent B's review and refinements

    # Validation
    validation_passed: bool                # Did proposal pass validation?
    validation_issues: List[str]           # Issues found during validation

    # Final output
    final_plan: str                        # Merged final plan
    messages: Annotated[List[str], add]    # Messages to display to user


class PlanningNodes:
    """Node implementations for planning workflow."""

    def __init__(self, rag_chain, llm_caller_a, llm_caller_b):
        """
        Initialize planning nodes.

        Args:
            rag_chain: RAG chain for querying codebase
            llm_caller_a: Function to call LLM for Agent A (system_prompt, user_prompt) -> str
            llm_caller_b: Function to call LLM for Agent B (system_prompt, user_prompt) -> str
        """
        self.rag_chain = rag_chain
        self.llm_caller_a = llm_caller_a
        self.llm_caller_b = llm_caller_b

    def analyze_codebase(self, state: PlanningState) -> PlanningState:
        """
        Node 1: Analyze codebase using RAG.
        MUST query RAG before any proposal can be made.
        """
        request = state["request"]
        language = state.get("language", "english")

        logger.info(f"[Planning] Analyzing codebase for: {request[:100]}...")

        # Single RAG query combining all aspects
        combined_query = f"Analyze codebase for: {request}. Show related files, functions, architecture, and implementation details."

        context_results = []
        identified_files = set()

        if self.rag_chain:
            try:
                # Use retriever to get documents directly (no LLM call)
                # Try invoke() first (LangChain new API), fallback to get_relevant_documents() (old API)
                try:
                    docs = self.rag_chain.invoke(combined_query)
                except AttributeError:
                    docs = self.rag_chain.get_relevant_documents(combined_query)

                # Format documents into readable context
                for i, doc in enumerate(docs, 1):
                    answer = f"[Document {i}]\n{doc.page_content}\n"
                    context_results.append(answer)
                    # Extract file paths from RAG results
                    for line in doc.page_content.split('\n'):
                        if '/' in line and ('.' in line.split('/')[-1]):
                            # Likely a file path
                            parts = line.split()
                            for part in parts:
                                if '/' in part and '.' in part:
                                    clean_path = part.strip('`"\',:;')
                                    if clean_path:
                                        identified_files.add(clean_path)
            except Exception as e:
                logger.warning(f"RAG query failed: {e}")

        # Generate analysis summary using Agent A
        if language == 'vietnamese':
            system_prompt = """Bạn là Agent A - chuyên gia phân tích code.
Nhiệm vụ: Phân tích codebase dựa trên thông tin từ RAG và yêu cầu của người dùng.
Chỉ dựa vào thông tin thực tế từ codebase, KHÔNG đoán mò.

⚠️⚠️⚠️ QUY TẮC NGÔN NGỮ QUAN TRỌNG ⚠️⚠️⚠️
BẮT BUỘC trả lời HOÀN TOÀN bằng tiếng Việt!

✅ CHỈ được dùng tiếng Anh cho:
- Tên file, tên hàm, tên class, tên biến (ví dụ: getUserById, OrderService, config.py)
- Từ khóa code (if, for, return, async, await...)
- Thuật ngữ KHÔNG CÓ từ Việt: API, database, schema, cache, token, hash

❌ CẤM dùng tiếng Anh cho từ thông thường:
- "implement" → dùng "triển khai"
- "approach" → dùng "cách làm" hoặc "hướng"
- "consideration" → dùng "điểm cần lưu ý"
- "trade-off" → dùng "đánh đổi"
- "safety" → dùng "an toàn"
- "performance" → dùng "hiệu năng"

Viết tự nhiên như developer Việt Nam nói chuyện."""
            user_prompt = f"""Yêu cầu: {request}

Thông tin từ codebase:
{chr(10).join(context_results) if context_results else "Không tìm thấy thông tin liên quan"}

Hãy phân tích:
1. Những file/hàm nào liên quan đến yêu cầu này?
2. Cấu trúc code hiện tại như thế nào?
3. Những điểm nào cần thay đổi?

Chỉ nói về những gì BẠN THỰC SỰ THẤY trong codebase. Không đề xuất "kỹ thuật tiên tiến" hay "thực hành tốt nhất" chung chung."""
        else:
            system_prompt = """You are Agent A - a code analysis expert.
Task: Analyze the codebase based on RAG context and user's request.
Only use actual information from the codebase, DO NOT guess."""
            user_prompt = f"""Request: {request}

Codebase context:
{chr(10).join(context_results) if context_results else "No relevant context found"}

Analyze:
1. Which files/functions are related to this request?
2. What is the current code structure?
3. What needs to be changed?

Only discuss what you ACTUALLY SEE in the codebase. Don't suggest generic "advanced techniques" or "best practices"."""

        try:
            analysis = self.llm_caller_a(system_prompt, user_prompt)
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            analysis = "Unable to analyze codebase"

        return {
            **state,
            "codebase_context": context_results,
            "identified_files": list(identified_files),
            "agent_a_analysis": analysis,
            "messages": [f"[Agent A - Phân tích codebase]\n{analysis}"]
        }

    def propose_changes(self, state: PlanningState) -> PlanningState:
        """
        Node 2: Agent A proposes concrete changes.
        MUST reference actual files from analysis step.
        """
        request = state["request"]
        analysis = state.get("agent_a_analysis", "")
        identified_files = state.get("identified_files", [])
        codebase_context = state.get("codebase_context", [])
        language = state.get("language", "english")

        logger.info("[Planning] Agent A proposing changes...")

        if language == 'vietnamese':
            system_prompt = """Bạn là Agent A - chuyên gia lập kế hoạch code.
Nhiệm vụ: Đề xuất CỤ THỂ những thay đổi cần làm.
Quy tắc QUAN TRỌNG:
- Phải chỉ rõ file thật từ codebase
- Không đề xuất điều gì chung chung
- Mỗi bước phải có file + hàm cụ thể

⚠️⚠️⚠️ QUY TẮC NGÔN NGỮ QUAN TRỌNG ⚠️⚠️⚠️
BẮT BUỘC trả lời HOÀN TOÀN bằng tiếng Việt!

✅ CHỈ được dùng tiếng Anh cho:
- Tên file, tên hàm, tên class, tên biến
- Từ khóa code (if, for, return...)
- Thuật ngữ KHÔNG CÓ từ Việt: API, database, schema, cache

❌ CẤM dùng tiếng Anh cho từ thông thường:
- "implement" → "triển khai"
- "approach" → "cách làm"
- "performance" → "hiệu năng"
- "scaling" → "mở rộng"

Viết tự nhiên như developer Việt Nam nói chuyện."""
            user_prompt = f"""Yêu cầu: {request}

Phân tích trước đó:
{analysis}

File liên quan: {', '.join(identified_files) if identified_files else 'Chưa xác định'}

Thông tin codebase:
{chr(10).join(codebase_context[:2]) if codebase_context else "Không có"}

Đề xuất kế hoạch CỤ THỂ:
1. File nào cần sửa? Hàm nào?
2. Thay đổi gì ở mỗi file?
3. Thứ tự thực hiện?

Format:
## Kế hoạch thay đổi

### Bước 1: [Tên]
- File: [đường dẫn cụ thể]
- Thay đổi: [mô tả cụ thể]
- Lý do: [tại sao]

### Bước 2: ...

KHÔNG được nói "có thể", "nên", "tiên tiến" - chỉ nói CỤ THỂ làm gì."""
        else:
            system_prompt = """You are Agent A - a code planning expert.
Task: Propose CONCRETE changes to be made.
IMPORTANT rules:
- Must reference actual files from codebase
- No generic suggestions
- Each step must have specific file + function"""
            user_prompt = f"""Request: {request}

Previous analysis:
{analysis}

Related files: {', '.join(identified_files) if identified_files else 'Not identified'}

Codebase context:
{chr(10).join(codebase_context[:2]) if codebase_context else "None"}

Propose a CONCRETE plan:
1. Which files need changes? Which functions?
2. What changes in each file?
3. Order of implementation?

Format:
## Change Plan

### Step 1: [Name]
- File: [specific path]
- Change: [specific description]
- Reason: [why]

### Step 2: ...

DO NOT say "could", "should", "advanced" - only say SPECIFICALLY what to do."""

        try:
            proposal = self.llm_caller_a(system_prompt, user_prompt)
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            proposal = "Unable to generate proposal"

        return {
            **state,
            "agent_a_proposal": proposal,
            "messages": [f"[Agent A - Đề xuất]\n{proposal}"]
        }

    def review_and_refine(self, state: PlanningState) -> PlanningState:
        """
        Node 3: Agent B reviews and refines the proposal.
        Focus on feasibility and missing details.
        """
        request = state["request"]
        proposal = state.get("agent_a_proposal", "")
        analysis = state.get("agent_a_analysis", "")
        identified_files = state.get("identified_files", [])
        codebase_context = state.get("codebase_context", [])
        language = state.get("language", "english")

        logger.info("[Planning] Agent B reviewing proposal...")

        if language == 'vietnamese':
            system_prompt = """Bạn là Agent B - chuyên gia review code.
Nhiệm vụ: Xem xét đề xuất của Agent A và bổ sung/cải tiến.
Quy tắc:
- Kiểm tra xem đề xuất có khả thi không
- Có bỏ sót file/hàm nào không?
- Có vấn đề gì có thể xảy ra không?

⚠️⚠️⚠️ QUY TẮC NGÔN NGỮ QUAN TRỌNG ⚠️⚠️⚠️
BẮT BUỘC trả lời HOÀN TOÀN bằng tiếng Việt!

✅ CHỈ được dùng tiếng Anh cho:
- Tên file, tên hàm, tên class, tên biến
- Từ khóa code (if, for, return...)
- Thuật ngữ KHÔNG CÓ từ Việt: API, database, schema, cache

❌ CẤM dùng tiếng Anh cho từ thông thường:
- "implement" → "triển khai"
- "approach" → "cách làm"
- "performance" → "hiệu năng"
- "trade-off" → "đánh đổi"

Viết tự nhiên như developer Việt Nam nói chuyện."""
            user_prompt = f"""Yêu cầu gốc: {request}

Đề xuất của Agent A:
{proposal}

File đã xác định: {', '.join(identified_files) if identified_files else 'Chưa có'}

Thông tin codebase:
{chr(10).join(codebase_context[:2]) if codebase_context else "Không có"}

Xem xét và bổ sung:
1. Đề xuất có khả thi không? Tại sao?
2. Có thiếu file/hàm nào không?
3. Có vấn đề tiềm ẩn nào không?
4. Đề xuất cải tiến (nếu có)

Format:
## Xem xét của Agent B

### Điểm tốt:
- ...

### Điểm cần bổ sung:
- ...

### Vấn đề tiềm ẩn:
- ...

### Đề xuất cải tiến:
- ..."""
        else:
            system_prompt = """You are Agent B - a code review expert.
Task: Review Agent A's proposal and add improvements.
Rules:
- Check if proposal is realistic
- Any missing files/functions?
- Any potential issues?"""
            user_prompt = f"""Original request: {request}

Agent A's proposal:
{proposal}

Identified files: {', '.join(identified_files) if identified_files else 'None'}

Codebase context:
{chr(10).join(codebase_context[:2]) if codebase_context else "None"}

Review and add:
1. Is the proposal feasible? Why?
2. Any missing files/functions?
3. Any potential issues?
4. Suggested improvements (if any)

Format:
## Agent B's Review

### Good points:
- ...

### Missing items:
- ...

### Potential issues:
- ...

### Suggested improvements:
- ..."""

        try:
            review = self.llm_caller_b(system_prompt, user_prompt)
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            review = "Unable to generate review"

        return {
            **state,
            "agent_b_review": review,
            "messages": [f"[Agent B - Review]\n{review}"]
        }

    def validate_proposal(self, state: PlanningState) -> PlanningState:
        """
        Node 4: Validate that the proposal is concrete and realistic.
        Reject proposals that are too abstract.
        """
        proposal = state.get("agent_a_proposal", "")
        review = state.get("agent_b_review", "")
        identified_files = state.get("identified_files", [])

        logger.info("[Planning] Validating proposal...")

        issues = []

        # Check 1: Does proposal reference actual files?
        if not identified_files:
            issues.append("Không có file cụ thể nào được xác định từ codebase")

        # Check 2: Does proposal have concrete steps?
        proposal_lower = proposal.lower()
        abstract_keywords = [
            "advanced", "best practice", "modern", "industry standard",
            "could consider", "might want to", "possibly", "perhaps",
            "tiên tiến", "hiện đại", "có thể xem xét", "nên cân nhắc"
        ]
        for keyword in abstract_keywords:
            if keyword in proposal_lower:
                issues.append(f"Đề xuất chứa từ chung chung: '{keyword}'")

        # Check 3: Does it have file paths?
        has_file_reference = (
            '/' in proposal or
            '.py' in proposal or
            '.ts' in proposal or
            '.tsx' in proposal or
            '.js' in proposal
        )
        if not has_file_reference:
            issues.append("Đề xuất không chỉ rõ đường dẫn file cụ thể")

        validation_passed = len(issues) == 0

        return {
            **state,
            "validation_passed": validation_passed,
            "validation_issues": issues
        }

    def finalize_plan(self, state: PlanningState) -> PlanningState:
        """
        Node 5: Merge proposals into final plan.
        """
        request = state["request"]
        proposal = state.get("agent_a_proposal", "")
        review = state.get("agent_b_review", "")
        identified_files = state.get("identified_files", [])
        validation_passed = state.get("validation_passed", True)
        validation_issues = state.get("validation_issues", [])
        language = state.get("language", "english")

        logger.info("[Planning] Finalizing plan...")

        if language == 'vietnamese':
            if not validation_passed:
                final_plan = f"""## Kế hoạch cần điều chỉnh

⚠️ Đề xuất chưa đủ cụ thể. Vấn đề:
{chr(10).join(f'- {issue}' for issue in validation_issues)}

### Yêu cầu gốc:
{request}

### File liên quan (từ codebase):
{chr(10).join(f'- {f}' for f in identified_files) if identified_files else '- Chưa xác định được file cụ thể'}

### Đề xuất hiện tại:
{proposal}

### Xem xét:
{review}

---
Cần làm rõ hơn: file cụ thể nào, hàm nào, thay đổi gì?"""
            else:
                final_plan = f"""## Kế hoạch cuối cùng

### Yêu cầu:
{request}

### File sẽ thay đổi:
{chr(10).join(f'- {f}' for f in identified_files) if identified_files else '- Xem chi tiết bên dưới'}

### Kế hoạch chi tiết (Agent A):
{proposal}

### Bổ sung từ xem xét (Agent B):
{review}

---
✅ Kế hoạch đã được kiểm tra và sẵn sàng thực hiện."""
        else:
            if not validation_passed:
                final_plan = f"""## Plan Needs Adjustment

⚠️ Proposal is not concrete enough. Issues:
{chr(10).join(f'- {issue}' for issue in validation_issues)}

### Original request:
{request}

### Related files (from codebase):
{chr(10).join(f'- {f}' for f in identified_files) if identified_files else '- No specific files identified'}

### Current proposal:
{proposal}

### Review:
{review}

---
Need clarification: which specific files, functions, and changes?"""
            else:
                final_plan = f"""## Final Plan

### Request:
{request}

### Files to change:
{chr(10).join(f'- {f}' for f in identified_files) if identified_files else '- See details below'}

### Detailed plan (Agent A):
{proposal}

### Review additions (Agent B):
{review}

---
✅ Plan has been validated and is ready to execute."""

        return {
            **state,
            "final_plan": final_plan,
            "messages": [f"[Kế hoạch cuối cùng]\n{final_plan}"]
        }
