"""
Language-specific instructions for AI agents.
"""


class LanguageInstructions:
    """Provides language-specific instructions for agents."""
    
    @staticmethod
    def get_vietnamese_instructions() -> str:
        """Get Vietnamese language instructions."""
        return """

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
- "scaling" → dùng "mở rộng"
- "backoff" → dùng "chờ"
- "detect" → dùng "phát hiện"
- "degradation" → dùng "suy giảm"
- "gradual" → dùng "từ từ"
- "automatic" → dùng "tự động"

Viết tự nhiên như developer Việt Nam nói chuyện."""
    
    @staticmethod
    def get_english_instructions() -> str:
        """Get English language instructions."""
        return """

IMPORTANT LANGUAGE RULES:
- Respond ENTIRELY in English
- Use natural, conversational English"""
    
    @classmethod
    def get_instructions(cls, language: str) -> str:
        """
        Get language instructions based on detected language.
        
        Args:
            language: 'vietnamese' or 'english'
            
        Returns:
            Language instructions string
        """
        if language == 'vietnamese':
            return cls.get_vietnamese_instructions()
        else:
            return cls.get_english_instructions()

