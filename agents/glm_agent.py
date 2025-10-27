"""
GLM AI Agent implementation using z.ai models.
Supports GLM-4.6 and GLM-4.5-air models.
"""

import logging
from openai import OpenAI

from agents.shared.llm_agent_base import LLMAgentBase
from core.message import Role


logger = logging.getLogger(__name__)


class GLMAgent(LLMAgentBase):
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
        self.model = config.get("model", "glm-4.6")  # Default to GLM-4.5
        
        # Create OpenAI client with z.ai endpoint
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
        logger.info(f"Initialized {self.role.value} with model {self.model}")
    
    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """
        Call GLM API via OpenAI-compatible interface to generate a response.
        
        Args:
            system_prompt: The system prompt
            user_prompt: The user prompt
            
        Returns:
            Generated response text
            
        Raises:
            Exception: If the API call fails
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=None,  # Allow detailed arguments
            temperature=0.9,  # Higher temperature for more varied, spirited debate
            top_p=0.95  # Allow more diverse responses
        )
        
        return response.choices[0].message.content.strip()
