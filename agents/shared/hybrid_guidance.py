"""
Hybrid guidance service for AI agents.
Supports two modes: collaborative planning and debate.
"""

from typing import Optional, List
from core.message import Role, Message, ConversationMode
from agents.shared.convergence_guidance import ConvergenceGuidanceService


class HybridGuidanceService:
    """
    Hybrid guidance service that provides:
    - Planning Mode: Agents collaborate to build/refine plans together
    - Debate Mode: Agents debate and converge on decisions (delegates to ConvergenceGuidanceService)
    """

    # ==================== PLANNING MODE GUIDANCE ====================

    @staticmethod
    def get_planning_initial_guidance(language: str) -> str:
        """Get guidance for initial plan proposal (0-1 exchanges)."""
        if language == 'vietnamese':
            return """

📋 CHẾ ĐỘ LẬP KẾ HOẠCH - Bước đầu tiên

🗣️ NGÔN NGỮ: Trả lời bằng tiếng Việt. Chỉ dùng tiếng Anh cho tên file, tên hàm, tên class.

🎯 NHIỆM VỤ CỦA BẠN:
1. Đề xuất CẤU TRÚC KẾ HOẠCH ban đầu
2. Xác định các bước chính cần thực hiện
3. Nêu rõ mục tiêu và kết quả mong đợi
4. Đánh dấu những điểm cần agent kia bổ sung

💡 CÁCH LÀM:
- Đưa ra khung kế hoạch rõ ràng với các bước có đánh số
- Xác định thứ tự phụ thuộc giữa các bước
- Nêu các giả định và điều kiện tiên quyết
- Mời agent kia đóng góp ý kiến

📝 FORMAT ĐỀ XUẤT:
## Kế hoạch đề xuất: [Tên]

### Mục tiêu:
[Mục tiêu cụ thể]

### Các bước thực hiện:
1. [Bước 1] - [Mô tả ngắn]
2. [Bước 2] - [Mô tả ngắn]
...

### Cần bổ sung:
- [Điểm cần agent kia xem xét/bổ sung]

⚡ HÃY HỢP TÁC, KHÔNG PHẢI TRANH LUẬN!"""
        else:
            return """

📋 PLANNING MODE - Initial Step

🎯 YOUR TASK:
1. Propose the INITIAL PLAN STRUCTURE
2. Identify main steps to accomplish the goal
3. Clearly state objectives and expected outcomes
4. Mark areas for the other agent to contribute

💡 APPROACH:
- Provide clear plan framework with numbered steps
- Identify dependencies between steps
- State assumptions and prerequisites
- Invite the other agent to contribute

📝 SUGGESTED FORMAT:
## Proposed Plan: [Name]

### Objective:
[Specific objective]

### Steps:
1. [Step 1] - [Brief description]
2. [Step 2] - [Brief description]
...

### Need Input On:
- [Areas for other agent to review/add]

⚡ COLLABORATE, DON'T DEBATE!"""

    @staticmethod
    def get_planning_contribution_guidance(language: str) -> str:
        """Get guidance for contributing to plan (2-3 exchanges)."""
        if language == 'vietnamese':
            return """

📋 CHẾ ĐỘ LẬP KẾ HOẠCH - Đóng góp (2-3 lần)

🗣️ NGÔN NGỮ: Trả lời bằng tiếng Việt. Chỉ dùng tiếng Anh cho tên file, tên hàm, tên class.

🎯 NHIỆM VỤ CỦA BẠN:
1. ĐÁNH GIÁ kế hoạch hiện tại - điểm mạnh và điểm cần cải thiện
2. BỔ SUNG các bước còn thiếu, trường hợp đặc biệt
3. NÂNG CAO chất lượng bằng ví dụ cụ thể hoặc chi tiết kỹ thuật
4. XÁC ĐỊNH rủi ro tiềm ẩn và cách giảm thiểu

💡 CÁCH LÀM:
- Bắt đầu bằng việc công nhận những điểm TỐT của kế hoạch
- Thêm giá trị thay vì chỉ trích
- Đề xuất cải tiến cụ thể với lý do
- Xây dựng dựa trên ý tưởng của agent kia

📝 FORMAT:
### ✅ Điểm tốt trong kế hoạch:
- [Điểm 1]
- [Điểm 2]

### ➕ Bổ sung thêm:
- [Bước/điểm cần lưu ý mới]
- [Trường hợp đặc biệt cần xử lý]

### 🔧 Đề xuất cải tiến:
- [Bước X] → [Cách cải tiến] vì [lý do]

### ⚠️ Rủi ro cần lưu ý:
- [Rủi ro] → [Cách giảm thiểu]

⚡ XÂY DỰNG CÙNG NHAU, KHÔNG PHÁ BỎ!"""
        else:
            return """

📋 PLANNING MODE - Contribution (2-3 exchanges)

🎯 YOUR TASK:
1. EVALUATE current plan - strengths and areas for improvement
2. ADD missing steps, edge cases, considerations
3. ENHANCE with concrete examples or technical details
4. IDENTIFY potential risks and mitigations

💡 APPROACH:
- Start by acknowledging GOOD points in the plan
- Add value rather than criticize
- Propose specific improvements with reasoning
- Build on the other agent's ideas

📝 FORMAT:
### ✅ Good points in the plan:
- [Point 1]
- [Point 2]

### ➕ Additional contributions:
- [New step/consideration]
- [Edge case to handle]

### 🔧 Suggested improvements:
- [Step X] → [How to improve] because [reason]

### ⚠️ Risks to consider:
- [Risk] → [Mitigation]

⚡ BUILD TOGETHER, DON'T TEAR DOWN!"""

    @staticmethod
    def get_planning_refinement_guidance(language: str) -> str:
        """Get guidance for refining plan (4-5 exchanges)."""
        if language == 'vietnamese':
            return """

📋 CHẾ ĐỘ LẬP KẾ HOẠCH - Tinh chỉnh (4-5 lần)

🗣️ NGÔN NGỮ: Trả lời bằng tiếng Việt. Chỉ dùng tiếng Anh cho tên file, tên hàm, tên class.

🎯 NHIỆM VỤ CỦA BẠN:
1. TỔNG HỢP tất cả đóng góp từ cả hai agent
2. SẮP XẾP các bước theo thứ tự logic và phụ thuộc
3. LÀM RÕ bất kỳ điểm mơ hồ nào
4. CHUẨN BỊ cho phiên bản cuối cùng

💡 CÁCH LÀM:
- Gộp các ý tưởng tốt nhất từ cả hai
- Loại bỏ trùng lặp và mâu thuẫn
- Đảm bảo mỗi bước có đủ chi tiết để thực hiện
- Xác nhận các quyết định đã thống nhất

📝 FORMAT:
### 📊 Tổng hợp kế hoạch:

**Đã thống nhất:**
- [Quyết định 1]
- [Quyết định 2]

**Kế hoạch hợp nhất:**
1. [Bước 1] - [Chi tiết đầy đủ]
   - Bước con nếu cần
2. [Bước 2] - [Chi tiết đầy đủ]
...

**Cần xác nhận cuối:**
- [Điểm cần human/agent xác nhận]

⚡ HOÀN THIỆN CÙNG NHAU!"""
        else:
            return """

📋 PLANNING MODE - Refinement (4-5 exchanges)

🎯 YOUR TASK:
1. CONSOLIDATE all contributions from both agents
2. ARRANGE steps in logical order with dependencies
3. CLARIFY any ambiguous points
4. PREPARE for final version

💡 APPROACH:
- Merge best ideas from both agents
- Remove duplicates and contradictions
- Ensure each step has enough detail to execute
- Confirm agreed-upon decisions

📝 FORMAT:
### 📊 Plan Consolidation:

**Agreed upon:**
- [Decision 1]
- [Decision 2]

**Merged Plan:**
1. [Step 1] - [Full details]
   - Sub-step if needed
2. [Step 2] - [Full details]
...

**Need final confirmation:**
- [Point needing human/agent confirmation]

⚡ FINALIZE TOGETHER!"""

    @staticmethod
    def get_planning_finalization_guidance(language: str) -> str:
        """Get guidance for finalizing plan (6+ exchanges)."""
        if language == 'vietnamese':
            return """

🎯 CHẾ ĐỘ LẬP KẾ HOẠCH - Hoàn tất (6+ lần)

🗣️ NGÔN NGỮ: Trả lời bằng tiếng Việt. Chỉ dùng tiếng Anh cho tên file, tên hàm, tên class.

🚨 ĐÃ ĐỦ THẢO LUẬN! THỜI GIAN HOÀN TẤT KẾ HOẠCH!

📌 BẮT BUỘC PHẢI LÀM:
1. ĐƯA RA KẾ HOẠCH HOÀN CHỈNH CUỐI CÙNG
2. Bao gồm TẤT CẢ các bước đã thống nhất
3. Format rõ ràng, có thể thực hiện ngay
4. Không thêm ý kiến mới - chỉ tổng hợp

📝 FORMAT BẮT BUỘC:
## 📋 KẾ HOẠCH CUỐI CÙNG

### Mục tiêu:
[Mục tiêu đã thống nhất]

### Điều kiện tiên quyết:
- [Điều kiện 1]
- [Điều kiện 2]

### Các bước thực hiện:

**Bước 1: [Tên bước]**
- Mô tả: [Chi tiết]
- Kết quả: [Kết quả mong đợi]
- Phụ thuộc: [Nếu có]

**Bước 2: [Tên bước]**
...

### Rủi ro và cách xử lý:
| Rủi ro | Cách xử lý |
|--------|------------|
| [R1]   | [X1]       |

### Tiêu chí hoàn thành:
- [ ] [Tiêu chí 1]
- [ ] [Tiêu chí 2]

✅ KẾ HOẠCH SẴN SÀNG THỰC HIỆN!"""
        else:
            return """

🎯 PLANNING MODE - Finalization (6+ exchanges)

🚨 ENOUGH DISCUSSION! TIME TO FINALIZE THE PLAN!

📌 YOU MUST:
1. DELIVER THE COMPLETE FINAL PLAN
2. Include ALL agreed-upon steps
3. Format clearly, ready for execution
4. No new opinions - only consolidation

📝 REQUIRED FORMAT:
## 📋 FINAL PLAN

### Objective:
[Agreed objective]

### Prerequisites:
- [Prerequisite 1]
- [Prerequisite 2]

### Execution Steps:

**Step 1: [Step name]**
- Description: [Details]
- Output: [Expected result]
- Dependencies: [If any]

**Step 2: [Step name]**
...

### Risks and Mitigations:
| Risk | Mitigation |
|------|------------|
| [R1] | [M1]       |

### Success Criteria:
- [ ] [Criteria 1]
- [ ] [Criteria 2]

✅ PLAN READY FOR EXECUTION!"""

    @staticmethod
    def get_planning_stop_guidance(language: str) -> str:
        """Get guidance when human requests stop during planning."""
        if language == 'vietnamese':
            return """

🚨🚨🚨 NGƯỜI DÙNG YÊU CẦU DỪNG - ƯU TIÊN TUYỆT ĐỐI!

🗣️ NGÔN NGỮ: Trả lời bằng tiếng Việt. Chỉ dùng tiếng Anh cho tên file, tên hàm, tên class.

⛔ NGAY LẬP TỨC tôn trọng yêu cầu của người dùng!

📌 BẮT BUỘC ĐƯA RA KẾ HOẠCH CUỐI CÙNG:

## 📋 KẾ HOẠCH TỔNG HỢP

### Yêu cầu ban đầu:
[Nhắc lại chính xác]

### Kế hoạch đã thảo luận:
[Tổng hợp TẤT CẢ các bước từ cả hai agent]

### Các quyết định:
1. [Quyết định 1]
2. [Quyết định 2]
...

### Điểm còn mở (nếu có):
- [Điểm chưa giải quyết]

### Bước tiếp theo:
[Bước tiếp theo cụ thể]

⛔ KHÔNG thảo luận thêm!"""
        else:
            return """

🚨🚨🚨 HUMAN REQUESTED STOP - ABSOLUTE PRIORITY!

⛔ IMMEDIATELY respect human's request!

📌 MUST DELIVER FINAL PLAN:

## 📋 CONSOLIDATED PLAN

### Original Request:
[Restate exactly]

### Discussed Plan:
[Consolidate ALL steps from both agents]

### Decisions Made:
1. [Decision 1]
2. [Decision 2]
...

### Open Points (if any):
- [Unresolved point]

### Recommended Next Steps:
[Specific next action]

⛔ NO further debate!"""

    # ==================== MAIN ENTRY POINTS ====================

    @classmethod
    def build_convergence_guidance(
        cls,
        human_wants_stop: bool,
        exchange_count: int,
        language: str,
        mode: Optional[ConversationMode] = None
    ) -> str:
        """
        Build guidance based on conversation state and mode.

        Args:
            human_wants_stop: Whether human requested stop/summary
            exchange_count: Number of agent exchanges
            language: Detected language ('vietnamese' or 'english')
            mode: Conversation mode from session (planning or debate)

        Returns:
            Guidance string (planning or debate mode)
        """
        # Default to planning if no mode specified
        effective_mode = mode or ConversationMode.PLANNING

        # Planning mode guidance
        if effective_mode == ConversationMode.PLANNING:
            if human_wants_stop:
                return cls.get_planning_stop_guidance(language)

            if exchange_count >= 6:
                return cls.get_planning_finalization_guidance(language)
            elif exchange_count >= 4:
                return cls.get_planning_refinement_guidance(language)
            elif exchange_count >= 2:
                return cls.get_planning_contribution_guidance(language)
            else:
                return cls.get_planning_initial_guidance(language)

        # Debate mode - delegate to original service
        return ConvergenceGuidanceService.build_convergence_guidance(
            human_wants_stop=human_wants_stop,
            exchange_count=exchange_count,
            language=language
        )

    @classmethod
    def build_addressing_context(
        cls,
        human_just_intervened: bool,
        human_asks_to_summarize_other: bool,
        human_addressing_me: bool,
        human_addressing_other: bool,
        agent_role: Role,
        language: str
    ) -> str:
        """
        Build context about who human is addressing.
        Delegates to ConvergenceGuidanceService (same behavior for both modes).

        Args:
            human_just_intervened: Whether human just sent a message
            human_asks_to_summarize_other: Whether human asks to summarize other agent
            human_addressing_me: Whether human is addressing this agent
            human_addressing_other: Whether human is addressing the other agent
            agent_role: Current agent's role
            language: Detected language

        Returns:
            Addressing context string
        """
        return ConvergenceGuidanceService.build_addressing_context(
            human_just_intervened=human_just_intervened,
            human_asks_to_summarize_other=human_asks_to_summarize_other,
            human_addressing_me=human_addressing_me,
            human_addressing_other=human_addressing_other,
            agent_role=agent_role,
            language=language
        )
