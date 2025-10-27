"""
OpenAI-compatible AI Agent implementation.
Works with OpenAI API and any OpenAI-compatible endpoints.
"""

import logging
from openai import OpenAI

from agents.shared.llm_agent_base import LLMAgentBase
from core.message import Role


logger = logging.getLogger(__name__)


class OpenAIAgent(LLMAgentBase):
    """
    AI Agent powered by OpenAI or OpenAI-compatible APIs.
    
    Supports:
    - OpenAI models: gpt-4, gpt-3.5-turbo, etc.
    - OpenAI-compatible endpoints (set custom base_url)
    
    Configuration:
    - openai_api_key: API key for OpenAI or compatible service
    - openai_base_url: (Optional) Base URL for API endpoint. Defaults to OpenAI's official endpoint.
    - model: Model name (e.g., "gpt-4", "gpt-3.5-turbo")
    """
    
    def __init__(self, role: Role, db, config: dict = None):
        super().__init__(role, db, config)
        
        # Configure OpenAI client
        self.api_key = config.get("openai_api_key")
        self.base_url = config.get("openai_base_url")  # Optional, defaults to OpenAI
        self.model = config.get("model", "gpt-5")  # Default to GPT-5
        
        # Create OpenAI client
        client_kwargs = {"api_key": self.api_key}
        if self.base_url:
            client_kwargs["base_url"] = self.base_url
        
        self.client = OpenAI(**client_kwargs)
        
        logger.info(
            f"Initialized {self.role.value} with OpenAI-compatible model {self.model}"
            + (f" at {self.base_url}" if self.base_url else "")
        )
    
    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """
        Call OpenAI or OpenAI-compatible API to generate a response.
        
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
            max_tokens=None,  # Allow detailed responses
            temperature=0.9,  # Higher temperature for more varied, spirited debate
            top_p=0.95  # Allow more diverse responses
        )
        
        return response.choices[0].message.content.strip()

