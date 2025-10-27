"""
Language-specific instructions for AI agents.
"""


class LanguageInstructions:
    """Provides language-specific instructions for agents."""
    
    @staticmethod
    def get_vietnamese_instructions() -> str:
        """Get Vietnamese language instructions."""
        return """

IMPORTANT LANGUAGE RULES:
- Respond ENTIRELY in Vietnamese
- Use PURE Vietnamese - NO English words mixed in (except technical terms that have no Vietnamese equivalent)
- Talk naturally like a Vietnamese developer"""
    
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

