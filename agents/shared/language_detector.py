"""
Language detection service for AI agents.
"""

import re


class LanguageDetector:
    """Detects whether text is in Vietnamese or English."""
    
    # Vietnamese-specific characters (comprehensive)
    VIETNAMESE_CHARS_PATTERN = r'[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ]'
    
    # Common Vietnamese words (comprehensive, case insensitive)
    VIETNAMESE_WORDS = {
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
    }
    
    @classmethod
    def detect(cls, text: str) -> str:
        """
        Detect if the text is in Vietnamese or English.
        
        Args:
            text: Text to analyze
            
        Returns:
            'vietnamese' or 'english'
        """
        # Count Vietnamese characters
        vietnamese_count = len(re.findall(cls.VIETNAMESE_CHARS_PATTERN, text))
        
        # If ANY Vietnamese characters found, it's Vietnamese
        if vietnamese_count > 0:
            return 'vietnamese'
        
        # Normalize and split text
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        # Count Vietnamese words
        vietnamese_word_count = sum(1 for word in words if word in cls.VIETNAMESE_WORDS)
        
        # If more than 5% of words are Vietnamese OR at least 2 Vietnamese words found, assume Vietnamese
        if len(words) > 0 and (vietnamese_word_count / len(words) > 0.05 or vietnamese_word_count >= 2):
            return 'vietnamese'
        
        return 'english'

