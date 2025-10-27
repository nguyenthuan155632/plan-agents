"""
Convergence guidance service for AI agents.
Provides dynamic prompts based on conversation state.
"""

from typing import Optional
from core.message import Role


class ConvergenceGuidanceService:
    """Service to generate convergence guidance based on conversation state."""
    
    @staticmethod
    def get_stop_guidance(language: str) -> str:
        """Get guidance when human requests stop/summary."""
        if language == 'vietnamese':
            return """

🚨🚨🚨 HUMAN YÊU CẦU DỪNG/TÓM TẮT - ƯU TIÊN TUYỆT ĐỐI!

⛔ KHÔNG ĐƯỢC TRANH LUẬN THÊM! Human đã ra lệnh.

🎯 BẮT BUỘC PHẢI LÀM:
1. NGAY LẬP TỨC tôn trọng yêu cầu của human
2. TỔNG KẾT TOÀN BỘ cuộc trò chuyện (100%)
3. Nhắc lại CHÍNH XÁC yêu cầu ban đầu của human
4. Liệt kê ĐẦY ĐỦ tất cả quyết định, code, schema đã thảo luận
5. Nếu có code: ĐƯA RA CODE HOÀN CHỈNH CUỐI CÙNG (merge cả ý của Agent A và B)
6. Nếu có schema/API: LIỆT KÊ ĐẦY ĐỦ tables, fields, endpoints
7. Nêu RÕ RÀNG tất cả trade-offs đã thảo luận
8. Đưa ra khuyến nghị cuối cùng rõ ràng

⛔ TUYỆT ĐỐI KHÔNG ĐƯỢC:
- Tranh luận thêm
- Đưa ra ý kiến mới
- Phản bác human
- Nói "nhưng..." hay "tuy nhiên..."

Format BẮT BUỘC:
📌 TÓM TẮT HOÀN CHỈNH - Những gì chúng tôi đã hoàn thành:

✅ Yêu cầu ban đầu: [Nhắc lại CHÍNH XÁC]

✅ Giải pháp cuối cùng:
[Code/Schema HOÀN CHỈNH - bao gồm TẤT CẢ details]

✅ Quyết định chung:
1. [Quyết định 1 - chi tiết]
2. [Quyết định 2 - chi tiết]
...

✅ Trade-offs đã thảo luận:
- [Trade-off 1]
- [Trade-off 2]
...

✅ Khuyến nghị cuối: [Rõ ràng, cụ thể]"""
        else:
            return """

🚨🚨🚨 HUMAN REQUESTED STOP/SUMMARY - ABSOLUTE PRIORITY!

⛔ NO MORE DEBATE! Human has commanded.

🎯 YOU MUST:
1. IMMEDIATELY respect human's request
2. SUMMARIZE THE ENTIRE conversation (100%)
3. Restate EXACTLY what human originally requested
4. List ALL decisions, code, schemas discussed in FULL DETAIL
5. If code: PROVIDE COMPLETE FINAL CODE (merge Agent A and B ideas)
6. If schema/API: LIST ALL tables, fields, endpoints in DETAIL
7. STATE CLEARLY all trade-offs discussed
8. Provide clear final recommendation

⛔ ABSOLUTELY DO NOT:
- Debate further
- Introduce new opinions
- Contradict human
- Say "but..." or "however..."

REQUIRED Format:
📌 COMPLETE SUMMARY - What we accomplished:

✅ Original Request: [Restate EXACTLY]

✅ Final Solution:
[COMPLETE Code/Schema - include ALL details]

✅ Key Decisions:
1. [Decision 1 - detailed]
2. [Decision 2 - detailed]
...

✅ Trade-offs Discussed:
- [Trade-off 1]
- [Trade-off 2]
...

✅ Final Recommendation: [Clear, specific]"""
    
    @staticmethod
    def get_conclusion_guidance(language: str) -> str:
        """Get guidance when 6+ exchanges (time to conclude)."""
        if language == 'vietnamese':
            return """

🚨 ĐÃ 6+ LẦN TRANH LUẬN: ĐÃ ĐỦ RỒI!

🎯 BẮT BUỘC: Đây là message CUỐI CÙNG của bạn. Hãy:
1. CHẤP NHẬN compromise và KẾT THÚC
2. TỔNG KẾT TOÀN BỘ cuộc trò chuyện (100% - không bỏ sót)
3. Nhắc lại yêu cầu ban đầu của human
4. Liệt kê TẤT CẢ quyết định đã thống nhất
5. Nếu có code: Đưa ra CODE HOÀN CHỈNH cuối cùng (merge tất cả ý tưởng tốt)
6. Nếu có schema/API: Liệt kê chi tiết tables, fields, endpoints
7. Nêu rõ trade-offs đã thảo luận
8. Đưa ra khuyến nghị cuối cùng

Format bắt buộc:
📌 TÓM TẮT - Những gì chúng tôi đã hoàn thành:

Yêu cầu ban đầu: [...]
Giải pháp cuối cùng: [Code/Schema đầy đủ]
Quyết định chung: [...]
Trade-offs: [...]
Khuyến nghị: [...]"""
        else:
            return """

🚨 6+ DEBATES: TIME TO CONCLUDE!

🎯 REQUIRED: This is your FINAL message. You must:
1. ACCEPT the compromise and CONCLUDE
2. SUMMARIZE the ENTIRE conversation
3. Restate the human's original request
4. List ALL agreed-upon decisions
5. If code: Include the COMPLETE FINAL CODE
6. If schema/API: List all tables, fields, endpoints in detail
7. Acknowledge all trade-offs discussed
8. Provide final recommendation

Required format:
📌 SUMMARY - What we accomplished:

Original Request: [...]
Final Solution: [Complete Code/Schema]
Key Decisions: [...]
Trade-offs: [...]
Recommendation: [...]"""
    
    @staticmethod
    def get_convergence_guidance(language: str) -> str:
        """Get guidance when 4-5 exchanges (prepare to wrap up)."""
        if language == 'vietnamese':
            return """

⚖️ 4-5 lần rồi: Bắt đầu tìm điểm chung và chuẩn bị kết thúc.
- Thừa nhận các điểm đúng của đối phương
- Đề xuất compromise
- Chuẩn bị cho message cuối (có thể là lần sau)
- Bắt đầu nghĩ về việc tổng kết"""
        else:
            return """

⚖️ 4-5 exchanges: Start finding middle ground and prepare to wrap up.
- Acknowledge valid points
- Propose compromise
- Prepare for final message (possibly next)
- Start thinking about summary"""
    
    @staticmethod
    def get_debate_guidance(language: str) -> str:
        """Get guidance when 2-3 exchanges (debate strongly)."""
        if language == 'vietnamese':
            return """

🔥 2-3 lần: TRANH LUẬN mạnh mẽ và KIÊN ĐỊNH!
- BẢO VỆ quan điểm ban đầu của bạn
- Challenge mạnh mẽ ý kiến đối phương
- Chỉ ra lỗ hổng trong lập luận của họ
- Đưa ra bằng chứng, ví dụ cụ thể để chứng minh quan điểm của BẠN
- ⚠️ KHÔNG đổi ý kiến dễ dàng - chỉ thừa nhận khi đối phương có điểm THỰC SỰ thuyết phục
- Có thể nói: "Tôi vẫn nghĩ...", "Tôi vẫn tin rằng...", "Nhưng quan điểm của tôi là..."
- ĐỪNG đồng ý chỉ vì lịch sự!"""
        else:
            return """

🔥 2-3 exchanges: DEBATE strongly and STAND YOUR GROUND!
- DEFEND your initial position
- Challenge their view strongly
- Point out flaws in their reasoning
- Provide evidence, concrete examples to prove YOUR point
- ⚠️ DON'T change your mind easily - only concede when they have TRULY compelling points
- Use phrases like: "I still think...", "I maintain that...", "But my position is..."
- DON'T agree just to be polite!"""
    
    @staticmethod
    def get_initial_guidance(language: str) -> str:
        """Get guidance for first exchange (establish position)."""
        if language == 'vietnamese':
            return """

💪 Lần đầu: Xác lập lập trường MẠNH MẼ và RÕ RÀNG!
- Trình bày quan điểm CỤ THỂ và KIÊN ĐỊNH của bạn
- Đưa ra lý do, bằng chứng rõ ràng
- Đừng ngại bất đồng MẠNH MẼ với đối phương
- Tạo nền tảng cho các lần tranh luận sau
- ⚠️ Đây là QUAN ĐIỂM của bạn - hãy TỰ TIN và KIÊN ĐỊNH với nó!"""
        else:
            return """

💪 First exchange: Establish your STRONG, CLEAR position!
- Present your SPECIFIC and FIRM perspective
- Provide clear reasoning and evidence
- Don't be afraid to STRONGLY disagree
- Set the foundation for future debates
- ⚠️ This is YOUR position - be CONFIDENT and FIRM with it!"""
    
    @staticmethod
    def get_summarize_other_context(agent_role: Role, language: str) -> str:
        """Get context when human asks agent to summarize the other agent's proposal."""
        other_agent_name = "Agent A" if agent_role == Role.AGENT_B else "Agent B"
        
        if language == 'vietnamese':
            return f"""

🎯🎯🎯 YÊU CẦU ĐẶC BIỆT: Human yêu cầu BẠN tóm tắt đề xuất của {other_agent_name}

BẮT BUỘC PHẢI LÀM:
1. Đọc KỸ toàn bộ conversation để hiểu đầy đủ đề xuất của {other_agent_name}
2. Tóm tắt ĐẦY ĐỦ và CHI TIẾT những gì {other_agent_name} đã nói
3. BAO GỒM:
   - Yêu cầu gốc của human
   - Tất cả các đề xuất kỹ thuật cụ thể (schema, tables, fields, code, architecture...)
   - Lý do và reasoning của {other_agent_name}
   - Trade-offs đã được đề cập
   - Quyết định cuối cùng
4. Format rõ ràng với sections
5. KHÔNG bỏ sót chi tiết quan trọng
6. KHÔNG chỉ tóm tắt ngắn gọn - phải ĐẦY ĐỦ và có GIÁ TRỊ

Format bắt buộc:
📌 TÓM TẮT ĐỀ XUẤT CỦA {other_agent_name.upper()}:

✅ Vấn đề ban đầu: [Nhắc lại chính xác]

✅ Đề xuất của {other_agent_name}:
[Chi tiết đầy đủ - schema/code/architecture/approach]

✅ Lý do và reasoning:
[Tại sao {other_agent_name} đề xuất như vậy]

✅ Trade-offs được đề cập:
[Ưu/nhược điểm của đề xuất]

✅ Quyết định cuối:
[Giải pháp được chọn và lý do]"""
        else:
            return f"""

🎯🎯🎯 SPECIAL REQUEST: Human asks YOU to summarize {other_agent_name}'s proposal

YOU MUST:
1. Read the ENTIRE conversation to fully understand {other_agent_name}'s proposal
2. Summarize COMPLETELY and IN DETAIL what {other_agent_name} said
3. INCLUDE:
   - Original human request
   - All technical proposals (schema, tables, fields, code, architecture...)
   - {other_agent_name}'s reasoning
   - Trade-offs mentioned
   - Final decision
4. Format clearly with sections
5. DO NOT skip important details
6. DO NOT just give a brief summary - must be COMPLETE and VALUABLE

Required format:
📌 SUMMARY OF {other_agent_name.upper()}'S PROPOSAL:

✅ Original Problem: [Restate exactly]

✅ {other_agent_name}'s Proposal:
[Full details - schema/code/architecture/approach]

✅ Reasoning:
[Why {other_agent_name} proposed this]

✅ Trade-offs Mentioned:
[Pros/cons of the proposal]

✅ Final Decision:
[Chosen solution and rationale]"""
    
    @staticmethod
    def get_addressing_context(addressing_me: bool, language: str) -> str:
        """Get context about who human is addressing."""
        if addressing_me:
            if language == 'vietnamese':
                return "\n\n🎯 LƯU Ý: Human đang nói TRỰC TIẾP với BẠN! Hãy trả lời câu hỏi/phản hồi của họ."
            else:
                return "\n\n🎯 NOTE: Human is addressing YOU directly! Respond to their question/feedback."
        else:
            if language == 'vietnamese':
                return "\n\n💬 Lưu ý: Human đang nói với agent kia, KHÔNG phải bạn. Hãy lắng nghe và chuẩn bị phản hồi khi đến lượt."
            else:
                return "\n\n💬 Note: Human is addressing the OTHER agent, not you. Listen and prepare to respond when it's your turn."
    
    @classmethod
    def build_convergence_guidance(
        cls,
        human_wants_stop: bool,
        exchange_count: int,
        language: str
    ) -> str:
        """
        Build convergence guidance based on conversation state.
        
        Args:
            human_wants_stop: Whether human requested stop/summary
            exchange_count: Number of agent exchanges
            language: Detected language ('vietnamese' or 'english')
            
        Returns:
            Convergence guidance string
        """
        # Highest priority: Human wants to stop
        if human_wants_stop:
            return cls.get_stop_guidance(language)
        
        # Based on exchange count
        if exchange_count >= 6:
            return cls.get_conclusion_guidance(language)
        elif exchange_count >= 4:
            return cls.get_convergence_guidance(language)
        elif exchange_count >= 2:
            return cls.get_debate_guidance(language)
        else:
            return cls.get_initial_guidance(language)
    
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
        if not human_just_intervened:
            return ""
        
        if human_asks_to_summarize_other:
            return cls.get_summarize_other_context(agent_role, language)
        elif human_addressing_me:
            return cls.get_addressing_context(True, language)
        elif human_addressing_other:
            return cls.get_addressing_context(False, language)
        
        return ""

