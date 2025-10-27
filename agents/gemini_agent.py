"""
Gemini AI Agent implementation using Google's Gemini API.
"""

import logging
import google.generativeai as genai

from agents.shared.llm_agent_base import LLMAgentBase
from core.message import Role


logger = logging.getLogger(__name__)


class GeminiAgent(LLMAgentBase):
    """
    AI Agent powered by Google Gemini models.
    
    Supports:
    - gemini-2.0-flash-exp: Latest Gemini 2.0 Flash (experimental, most capable)
    - gemini-1.5-flash: Gemini 1.5 Flash (fast and efficient)
    - gemini-1.5-pro: Gemini 1.5 Pro (more capable)
    """
    
    def __init__(self, role: Role, db, config: dict = None):
        super().__init__(role, db, config)
        
        # Configure Gemini
        self.api_key = config.get("gemini_api_key")
        self.model_name = config.get("model", "gemini-2.0-flash-exp")  # Default to Gemini 2.0 Flash
        
        # Initialize Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config={
                "temperature": 0.9,
                "top_p": 0.95,
                "max_output_tokens": None,
            }
        )
        
        logger.info(f"Initialized {self.role.value} with Gemini model {self.model_name}")
    
    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """
        Call Gemini API to generate a response.
        
        Args:
            system_prompt: The system prompt
            user_prompt: The user prompt
            
        Returns:
            Generated response text
            
        Raises:
            Exception: If the API call fails
        """
        # Combine system prompt and user prompt for Gemini (doesn't have separate system message)
        prompt = f"""{system_prompt}

{user_prompt}"""
        
        # Call Gemini API
        response = self.model.generate_content(
            prompt,
            safety_settings={
                'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
                'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
                'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
                'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE',
            }
        )
        
        # Check if response was blocked
        if not response.candidates or not response.candidates[0].content.parts:
            finish_reason = response.candidates[0].finish_reason if response.candidates else "UNKNOWN"
            logger.warning(f"Gemini response blocked. Finish reason: {finish_reason}")
            
            # Try again with simpler prompt
            simple_prompt = f"""You are {self.role.value}. 

Respond naturally and briefly (150-200 words)."""
            
            logger.info("Retrying with simplified prompt...")
            response = self.model.generate_content(
                simple_prompt,
                safety_settings={
                    'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
                    'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
                    'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
                    'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE',
                }
            )
        
        return response.text.strip()

