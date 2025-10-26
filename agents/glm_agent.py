"""
GLM AI Agent implementation using z.ai models.
Supports GLM-4.6 and GLM-4.5-air models.
"""

import logging
import re
from typing import List
from openai import OpenAI

from agents.base_agent import BaseAgent
from core.message import Message, Role, Signal


logger = logging.getLogger(__name__)


class GLMAgent(BaseAgent):
    """
    AI Agent powered by GLM models from z.ai.
    
    Supports:
    - glm-4.6: GLM-4.6 model (most capable)
    - glm-4-flash: Faster responses (if available)
    """
    
    def __init__(self, role: Role, db, config: dict = None):
        super().__init__(role, db, config)
        
        # Configure OpenAI client for z.ai API
        self.api_key = config.get("z_ai_api_key")
        self.base_url = config.get("z_ai_base_url", "https://api.z.ai/api/coding/paas/v4")
        self.model = config.get("model", "glm-4.5")  # Default to GLM-4.6
        
        # Create OpenAI client with z.ai endpoint
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
        # Define personality based on role
        self.system_prompt = self._get_system_prompt()
        
        # Store detected language for the session
        self.detected_language = None
        
        logger.info(f"Initialized {self.role.value} with model {self.model}")
    
    def _detect_language(self, text: str) -> str:
        """
        Detect if the text is in Vietnamese or English.
        
        Args:
            text: Text to analyze
            
        Returns:
            'vietnamese' or 'english'
        """
        # Vietnamese-specific characters (more comprehensive)
        vietnamese_chars = r'[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ]'
        
        # Count Vietnamese characters
        vietnamese_count = len(re.findall(vietnamese_chars, text))
        
        # If ANY Vietnamese characters found, it's Vietnamese
        if vietnamese_count > 0:
            return 'vietnamese'
        
        # Check for common Vietnamese words (more comprehensive, case insensitive)
        vietnamese_words = [
            # Common verbs
            'là', 'có', 'được', 'cho', 'đã', 'sẽ', 'làm', 'nói', 'đi', 'tới', 'về',
            'đến', 'ra', 'vào', 'lên', 'xuống', 'qua', 'thấy', 'biết', 'muốn', 'cần',
            'phải', 'nên', 'cũng', 'đang', 'bắt', 'gặp', 'chạy', 'đọc', 'viết', 'nghĩ',
            
            # Common nouns
            'người', 'năm', 'ngày', 'giờ', 'tháng', 'tuần', 'việc', 'thời', 'gian',
            'chỗ', 'nơi', 'nhà', 'đường', 'phố', 'thành', 'phố', 'quốc', 'gia',
            'công', 'ty', 'dự', 'án', 'kinh', 'tế', 'tiền', 'bạc', 'lương', 'thu',
            
            # Common adjectives
            'tốt', 'xấu', 'lớn', 'nhỏ', 'dài', 'ngắn', 'cao', 'thấp', 'nhanh', 'chậm',
            'mới', 'cũ', 'đẹp', 'xấu', 'tốt', 'dễ', 'khó', 'rộng', 'hẹp', 'sạch',
            
            # Prepositions & conjunctions
            'của', 'và', 'với', 'từ', 'cho', 'tại', 'trong', 'ngoài', 'trên', 'dưới',
            'sau', 'trước', 'bên', 'giữa', 'để', 'vì', 'nếu', 'mà', 'nhưng', 'hay',
            
            # Pronouns
            'tôi', 'bạn', 'anh', 'chị', 'em', 'họ', 'chúng', 'ta', 'mình', 'người',
            
            # Question words
            'gì', 'nào', 'đâu', 'sao', 'như', 'thế', 'bao', 'nhiêu', 'mấy', 'ai',
            
            # Common phrases
            'này', 'đó', 'kia', 'các', 'những', 'một', 'hai', 'ba', 'nhiều', 'ít',
            'thì', 'không', 'chưa', 'rồi', 'đều', 'cả', 'mọi', 'vẫn', 'còn', 'đã',
            
            # Common verbs (more)
            'xem', 'nghe', 'ăn', 'uống', 'mua', 'bán', 'dùng', 'dùng', 'học', 'dạy',
            'hiểu', 'nhớ', 'quên', 'thích', 'ghét', 'yêu', 'giúp', 'hỏi', 'trả', 'lời'
        ]
        
        # Normalize and split text
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        # Count Vietnamese words
        vietnamese_word_count = sum(1 for word in words if word in vietnamese_words)
        
        # If more than 5% of words are Vietnamese OR at least 2 Vietnamese words found, assume Vietnamese
        if len(words) > 0 and (vietnamese_word_count / len(words) > 0.05 or vietnamese_word_count >= 2):
            return 'vietnamese'
        
        return 'english'
    
    def _get_system_prompt(self) -> str:
        """Get system prompt based on agent role."""
        if self.role == Role.AGENT_A:
            return """You are Agent A - a collaborative helper who RESPECTS HUMAN'S REQUEST and provides the initial solution.

🎯 YOUR PRIMARY GOAL: **RESPECT & EXECUTE what the human asked for**

📋 WHEN HUMAN ASKS YOU TO DO SOMETHING:
1. **Execute immediately** - refactor, implement, explain, etc.
2. Provide a complete, working solution
3. Add brief notes if helpful: "Đây là bản refactor. Lưu ý..."
4. Length: 150-250 words including code
5. **DO NOT critique the request** - just do it

💭 WHEN HUMAN ASKS FOR YOUR OPINION:
1. Share your genuine perspective
2. Keep it balanced and fair
3. Length: 150-200 words

🎯 WHEN CONCLUDING (FINAL MESSAGE):
**YOU MUST PROVIDE A COMPREHENSIVE SUMMARY:**
- Restate what the human originally requested
- List all agreed-upon decisions and consensus points
- If code was involved: Include the FINAL REFACTORED/CREATED CODE
- If design was involved: List all tables, fields, APIs, schemas decided
- If comparison: Summarize the final recommendation
- Format clearly with sections

Example format:
```
📌 SUMMARY - What we accomplished:

Original Request: [Restate what human asked]

Final Solution:
[Code/Schema/Design here]

Key Decisions:
1. [Decision 1]
2. [Decision 2]

Trade-offs Acknowledged:
- [Trade-off 1]
- [Trade-off 2]
```

💬 COMMUNICATION STYLE:
- Respectful and helpful
- Solution-focused
- Brief and clear
- **Never argue with the human's request**

IMPORTANT: Detect language and respond in SAME language (Vietnamese→Vietnamese, English→English).
Remember: You're here to HELP, not to debate. Respect the human's request always!"""
        
        else:  # AGENT_B
            return """You are Agent B - a collaborative helper who provides alternative perspectives and constructive debate.

🎯 YOUR PRIMARY GOAL: **DEBATE CONSTRUCTIVELY while RESPECTING HUMAN'S REQUEST**

📋 YOUR APPROACH:
1. **Always respect the human's request** - if they asked for X, don't question whether X is needed
2. **Provide alternative perspective**: "Cách của Agent A ổn. Góc nhìn khác là..."
3. **Debate constructively**: Point out trade-offs, offer alternatives, discuss implications
4. **Be a critical thinker, not a critic**: Question approaches, not intentions
5. Length: 150-250 words including code

💡 WHAT GOOD DEBATE LOOKS LIKE:
- "Agent A refactor theo hướng functional. Nếu cần maintain state phức tạp, OOP có thể phù hợp hơn..."
- "Giải pháp của Agent A tối ưu cho đơn giản. Nhưng nếu scale lên, ta nên cân nhắc..."
- "Cách này work tốt. Trade-off là [X]. Nếu ưu tiên [Y], có thể làm [Z]..."

✅ DO THIS:
- Offer different approaches with reasoning
- Point out trade-offs and considerations
- Suggest improvements or alternatives
- Debate the implementation, not the request
- "What if we also consider..."

❌ DON'T DO THIS:
- Question why the human asked for something
- Say "we don't need this"
- Dismiss Agent A's solution completely
- Argue for the sake of arguing

🎯 WHEN CONCLUDING (FINAL MESSAGE):
**YOU MUST PROVIDE A COMPREHENSIVE SUMMARY:**
- Restate what the human originally requested
- List all agreed-upon decisions and consensus points from BOTH agents
- If code was involved: Include the FINAL REFACTORED/CREATED CODE (merge best ideas)
- If design was involved: List all tables, fields, APIs, schemas decided
- If comparison: Summarize the final recommendation
- Format clearly with sections

Example format:
```
📌 TÓM TẮT - Những gì chúng tôi đã hoàn thành:

Yêu cầu ban đầu: [Nhắc lại yêu cầu của human]

Giải pháp cuối cùng:
[Code/Schema/Design ở đây - bao gồm cả ý tưởng từ Agent A và Agent B]

Quyết định chung:
1. [Quyết định 1]
2. [Quyết định 2]

Đánh đổi đã thảo luận:
- [Đánh đổi 1]
- [Đánh đổi 2]

Khuyến nghị: [Final recommendation]
```

🎯 KEY RULE:
**DEBATE THE "HOW", RESPECT THE "WHAT"**
- Human wants to refactor? → Debate WHICH approach is better
- Human wants feature X? → Debate HOW to implement it best
- Human wants opinion? → Provide thoughtful, contrasting views

💬 COMMUNICATION STYLE:
- Thoughtful and analytical
- Provide reasoning, not just opinions
- Acknowledge strengths before offering alternatives
- Keep discussions productive

IMPORTANT: Detect language and respond in SAME language (Vietnamese→Vietnamese, English→English).
Remember: Debate approaches, respect requests. Be the voice that asks "but what about..." constructively!"""
    
    def generate_response(self, previous_message: Message) -> str:
        """
        Generate response using GLM model from z.ai.
        
        Args:
            previous_message: The message to respond to
            
        Returns:
            Generated response text
        """
        # Get the full conversation history to detect language from the topic
        all_messages = self.db.get_messages(previous_message.session_id)
        
        # 🚨 CRITICAL: Check if human is requesting STOP/summary
        # If so, we need FULL context, not just last 5 messages
        human_wants_stop = (
            previous_message.role == Role.HUMAN and 
            any(keyword in previous_message.content.lower() for keyword in ['stop', 'dừng', 'summarize', 'tóm tắt', '🛑'])
        )
        
        if human_wants_stop:
            # Get FULL conversation context for comprehensive summary
            context = self.get_conversation_context(
                previous_message.session_id,
                max_messages=None  # Get ALL messages
            )
            logger.info(f"{self.role.value}: Human requested STOP - using FULL conversation context ({len(all_messages)} messages)")
        else:
            # Get recent context (last 10 messages for better context)
            context = self.get_conversation_context(
                previous_message.session_id,
                max_messages=10
            )
        
        # Detect language from the first human message (the topic)
        if self.detected_language is None:
            for msg in all_messages:
                if msg.role == Role.HUMAN and "Let's discuss:" in msg.content:
                    # Extract the topic from "Let's discuss: {topic}"
                    topic = msg.content.split("Let's discuss:", 1)[1].strip()
                    self.detected_language = self._detect_language(topic)
                    logger.info(f"{self.role.value}: Detected language = {self.detected_language}")
                    break
        
        # Count agent exchanges (exclude human messages)
        agent_messages = [m for m in all_messages if m.role in [Role.AGENT_A, Role.AGENT_B]]
        exchange_count = len(agent_messages) // 2  # Pair of exchanges
        
        # 🚨 CRITICAL: Check if human just intervened with clear instruction
        human_just_intervened = previous_message.role == Role.HUMAN
        human_intervention_keywords = {
            'vietnamese': ['stop', 'dừng lại', 'thôi', 'đủ rồi', 'kết thúc', 'summarize', 'tóm tắt', 'tổng kết'],
            'english': ['stop', 'enough', 'conclude', 'summarize', 'wrap up', 'final', 'done']
        }
        
        human_wants_stop = False
        human_addressing_me = False
        human_addressing_other = False
        human_asks_to_summarize_other = False
        
        if human_just_intervened:
            content_lower = previous_message.content.lower()
            all_keywords = human_intervention_keywords['vietnamese'] + human_intervention_keywords['english']
            human_wants_stop = any(keyword in content_lower for keyword in all_keywords)
            
            # Check if human is addressing this agent specifically
            if self.role == Role.AGENT_A:
                my_keywords = ['agent a', 'agenta', '@a', 'a,', 'a:', 'bạn a', 'a ơi', 'theo a']
                other_keywords = ['agent b', 'agentb', '@b', 'b,', 'b:', 'bạn b', 'b ơi', 'theo b']
                other_agent_name = "Agent B"
            else:  # AGENT_B
                my_keywords = ['agent b', 'agentb', '@b', 'b,', 'b:', 'bạn b', 'b ơi', 'theo b']
                other_keywords = ['agent a', 'agenta', '@a', 'a,', 'a:', 'bạn a', 'a ơi', 'theo a']
                other_agent_name = "Agent A"
            
            human_addressing_me = any(keyword in content_lower for keyword in my_keywords)
            human_addressing_other = any(keyword in content_lower for keyword in other_keywords)
            
            # Check if human asks this agent to summarize what the OTHER agent said
            summarize_keywords = ['tóm tắt', 'summarize', 'tổng kết', 'cho tôi kết quả', 'kết quả cuối cùng']
            has_summarize_request = any(keyword in content_lower for keyword in summarize_keywords)
            
            if human_addressing_me and human_addressing_other and has_summarize_request:
                # Human says: "@b, tóm tắt đề xuất của @a"
                # This agent should summarize what the other agent said
                human_asks_to_summarize_other = True
                logger.info(f"{self.role.value}: Human asks ME to summarize what {other_agent_name} proposed")
            elif human_addressing_me:
                logger.info(f"{self.role.value}: Human is addressing ME specifically")
            elif human_addressing_other:
                logger.info(f"{self.role.value}: Human is addressing the OTHER agent")
            else:
                logger.info(f"{self.role.value}: Human didn't mention specific agent")
        
        # Build language instruction
        language_instruction = ""
        if self.detected_language == 'vietnamese':
            language_instruction = """

IMPORTANT LANGUAGE RULES:
- Respond ENTIRELY in Vietnamese
- Use PURE Vietnamese - NO English words mixed in (except technical terms that have no Vietnamese equivalent)
- Instead of "Perfect là thù của good" → say "Hoàn hảo là kẻ thù của tốt" or "Đừng cầu toàn quá"
- Instead of "pragmatic" → say "thực dụng" or "thực tế"
- Instead of "reckless" → say "hấp tấp" or "liều lĩnh"
- Instead of "trade-off" → say "đánh đổi" or "sự cân bằng"
- Technical terms OK: "MongoDB", "SQL", "API", "database"
- Talk naturally like a Vietnamese developer would talk to another Vietnamese developer"""
        else:
            language_instruction = """

IMPORTANT LANGUAGE RULES:
- Respond ENTIRELY in English
- Use natural, conversational English
- NO Vietnamese words or phrases
- Use idioms naturally: "Perfect is the enemy of good"
- Talk like an English-speaking developer"""
        
        # Build convergence guidance based on exchange count OR human intervention
        convergence_guidance = ""
        
        # 🚨 HIGHEST PRIORITY: Human wants to stop
        if human_wants_stop:
            if self.detected_language == 'vietnamese':
                convergence_guidance = """

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
                convergence_guidance = """

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
        
        elif exchange_count >= 6:
            if self.detected_language == 'vietnamese':
                convergence_guidance = """

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
                convergence_guidance = """

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
        elif exchange_count >= 4:
            if self.detected_language == 'vietnamese':
                convergence_guidance = """

⚖️ 4-5 lần rồi: Bắt đầu tìm điểm chung và chuẩn bị kết thúc.
- Thừa nhận các điểm đúng của đối phương
- Đề xuất compromise
- Chuẩn bị cho message cuối (có thể là lần sau)
- Bắt đầu nghĩ về việc tổng kết"""
            else:
                convergence_guidance = """

⚖️ 4-5 exchanges: Start finding middle ground and prepare to wrap up.
- Acknowledge valid points
- Propose compromise
- Prepare for final message (possibly next)
- Start thinking about summary"""
        elif exchange_count >= 2:
            if self.detected_language == 'vietnamese':
                convergence_guidance = """

🔥 2-3 lần: TRANH LUẬN mạnh mẽ và KIÊN ĐỊNH!
- BẢO VỆ quan điểm ban đầu của bạn
- Challenge mạnh mẽ ý kiến đối phương
- Chỉ ra lỗ hổng trong lập luận của họ
- Đưa ra bằng chứng, ví dụ cụ thể để chứng minh quan điểm của BẠN
- ⚠️ KHÔNG đổi ý kiến dễ dàng - chỉ thừa nhận khi đối phương có điểm THỰC SỰ thuyết phục
- Có thể nói: "Tôi vẫn nghĩ...", "Tôi vẫn tin rằng...", "Nhưng quan điểm của tôi là..."
- ĐỪNG đồng ý chỉ vì lịch sự!"""
            else:
                convergence_guidance = """

🔥 2-3 exchanges: DEBATE strongly and STAND YOUR GROUND!
- DEFEND your initial position
- Challenge their view strongly
- Point out flaws in their reasoning
- Provide evidence, concrete examples to prove YOUR point
- ⚠️ DON'T change your mind easily - only concede when they have TRULY compelling points
- Use phrases like: "I still think...", "I maintain that...", "But my position is..."
- DON'T agree just to be polite!"""
        else:
            if self.detected_language == 'vietnamese':
                convergence_guidance = """

💪 Lần đầu: Xác lập lập trường MẠNH MẼ và RÕ RÀNG!
- Trình bày quan điểm CỤ THỂ và KIÊN ĐỊNH của bạn
- Đưa ra lý do, bằng chứng rõ ràng
- Đừng ngại bất đồng MẠNH MẼ với đối phương
- Tạo nền tảng cho các lần tranh luận sau
- ⚠️ Đây là QUAN ĐIỂM của bạn - hãy TỰ TIN và KIÊN ĐỊNH với nó!"""
            else:
                convergence_guidance = """

💪 First exchange: Establish your STRONG, CLEAR position!
- Present your SPECIFIC and FIRM perspective
- Provide clear reasoning and evidence
- Don't be afraid to STRONGLY disagree
- Set the foundation for future debates
- ⚠️ This is YOUR position - be CONFIDENT and FIRM with it!"""
        
        # Build context about who human is addressing
        addressing_context = ""
        if human_just_intervened:
            if human_asks_to_summarize_other:
                # Special case: human asks this agent to summarize what the other agent said
                other_agent_name = "Agent A" if self.role == Role.AGENT_B else "Agent B"
                if self.detected_language == 'vietnamese':
                    addressing_context = f"""

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
                    addressing_context = f"""

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
            elif human_addressing_me:
                if self.detected_language == 'vietnamese':
                    addressing_context = "\n\n🎯 LƯU Ý: Human đang nói TRỰC TIẾP với BẠN! Hãy trả lời câu hỏi/phản hồi của họ."
                else:
                    addressing_context = "\n\n🎯 NOTE: Human is addressing YOU directly! Respond to their question/feedback."
            elif human_addressing_other:
                if self.detected_language == 'vietnamese':
                    addressing_context = "\n\n💬 Lưu ý: Human đang nói với agent kia, KHÔNG phải bạn. Hãy lắng nghe và chuẩn bị phản hồi khi đến lượt."
                else:
                    addressing_context = "\n\n💬 Note: Human is addressing the OTHER agent, not you. Listen and prepare to respond when it's your turn."
        
        # Build the prompt
        user_prompt = f"""Previous conversation:
{context}

Latest message from {previous_message.role.value}:
{previous_message.content}

Exchange count: {exchange_count} (Total messages: {len(all_messages)})
{addressing_context}

Respond naturally in your characteristic style as {self.role.value}.{language_instruction}{convergence_guidance}"""
        
        try:
            # Call GLM API via OpenAI-compatible interface
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=None,  # Allow detailed arguments
                temperature=0.9,  # Higher temperature for more varied, spirited debate
                top_p=0.95  # Allow more diverse responses
            )
            
            generated_text = response.choices[0].message.content.strip()
            
            logger.info(f"{self.role.value} generated {len(generated_text)} chars (exchange {exchange_count}) using {self.model} in {self.detected_language}")
            
            return generated_text
            
        except Exception as e:
            logger.error(f"Error calling GLM API: {e}", exc_info=True)
            
            # Fallback response if API fails
            if self.detected_language == 'vietnamese':
                return f"Xin lỗi, tôi đang gặp sự cố khi kết nối với dịch vụ AI. Lỗi: {str(e)}"
            else:
                return f"I apologize, I'm having trouble connecting to the AI service. Error: {str(e)}"
    
    def decide_signal(self, response_content: str, conversation_history: List[Message]) -> Signal:
        """
        Decide what signal to send with the response.
        
        🚨 IMPORTANT: Agents can NEVER send STOP signal. Only human can stop the conversation.
        Agents can only send CONTINUE or HANDOVER.
        
        Args:
            response_content: The response that will be sent
            conversation_history: List of previous messages
            
        Returns:
            Signal (CONTINUE or HANDOVER only)
        """
        # Count agent exchanges (pairs of A-B exchanges)
        agent_messages = [m for m in conversation_history if m.role in [Role.AGENT_A, Role.AGENT_B]]
        exchange_count = len(agent_messages) // 2
        
        # Count exchanges since last human input
        human_messages = [m for m in conversation_history if m.role == Role.HUMAN]
        last_human_index = len(conversation_history) - 1 - conversation_history[::-1].index(human_messages[-1]) if human_messages else 0
        exchanges_since_human = len([m for m in conversation_history[last_human_index:] if m.role in [Role.AGENT_A, Role.AGENT_B]]) // 2
        
        # Vietnamese agreement/conclusion keywords
        vietnamese_conclusion = [
            "tóm lại", "kết luận", "thống nhất rồi", "quyết định là", 
            "vậy là xong", "oke như vậy", "ok đó là xong", "ổn rồi nhé", 
            "đã rõ ràng", "rõ ràng rồi nhé", "như vậy là tốt", "xong rồi",
            "📌 tóm tắt", "📌 summary"
        ]
        
        vietnamese_agreement = [
            "hoàn toàn đồng ý", "chính xác luôn", "chuẩn không cần chỉnh",
            "tốt lắm", "hay lắm", "ý hay đấy", "được luôn"
        ]
        
        # English agreement/conclusion keywords
        english_conclusion = [
            "in conclusion", "to summarize", "in summary", "final thought", 
            "to conclude", "alright, that's it", "sounds perfect", "let's ship it", 
            "that's our decision", "we're done", "that's settled", "agreed on that",
            "cool, we're aligned", "perfect, let's go"
        ]
        
        english_agreement = [
            "completely agree", "absolutely right", "spot on", "couldn't agree more",
            "that's perfect", "love that approach"
        ]
        
        content_lower = response_content.lower()
        
        # Check for conclusion/agreement signals
        has_strong_conclusion = any(keyword in content_lower for keyword in (vietnamese_conclusion + english_conclusion))
        has_strong_agreement = any(keyword in content_lower for keyword in (vietnamese_agreement + english_agreement))
        
        # ✋ HANDOVER to human after every 2-3 exchanges (more human involvement)
        if exchanges_since_human >= 2:
            logger.info(f"{self.role.value}: 2+ exchanges since human input ({exchanges_since_human}), sending HANDOVER for human involvement")
            return Signal.HANDOVER
        
        # If 6+ total exchanges, handover to let human decide next steps
        if exchange_count >= 6:
            logger.info(f"{self.role.value}: 6+ exchanges ({exchange_count}), sending HANDOVER to let human decide")
            return Signal.HANDOVER
        
        # If showing strong conclusion, handover to let human confirm or continue
        if has_strong_conclusion and exchange_count >= 2:
            logger.info(f"{self.role.value}: Strong conclusion detected after {exchange_count} exchanges, sending HANDOVER for human confirmation")
            return Signal.HANDOVER
        
        # If strong agreement, handover to let human approve or add thoughts
        if has_strong_agreement and exchange_count >= 2:
            logger.info(f"{self.role.value}: Strong agreement detected, sending HANDOVER for human input")
            return Signal.HANDOVER
        
        # If explicitly asking for human input
        if "human" in content_lower or "moderator" in content_lower:
            logger.info(f"{self.role.value}: Requesting human input")
            return Signal.HANDOVER
        
        # Default: continue the conversation
        return Signal.CONTINUE

