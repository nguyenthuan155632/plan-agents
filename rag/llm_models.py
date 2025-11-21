"""
LLM Models module
Contains custom LLM implementations for Ollama and GLM
"""
import requests
import ollama
from langchain_core.language_models.llms import LLM
from langchain_core.outputs import Generation, LLMResult
from typing import Optional, List


class OllamaLLM(LLM):
    """Custom LLM class for Ollama integration"""

    def __init__(self, model: str = "qwen2.5-coder:7b", base_url: str = "http://localhost:11434", temperature: float = 0.7, num_predict: int = 8000):
        super().__init__()
        self._model = model
        self._base_url = base_url
        self._temperature = temperature
        self._num_predict = num_predict

    @property
    def _llm_type(self) -> str:
        return "ollama"

    @property
    def model(self) -> str:
        return self._model

    @property
    def base_url(self) -> str:
        return self._base_url

    @property
    def temperature(self) -> float:
        return self._temperature

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """Call the Ollama API"""
        try:
            response = ollama.chat(
                model=self._model,
                messages=[{"role": "user", "content": prompt}],
                options={
                    "temperature": self._temperature,
                    "num_predict": self._num_predict,  # Maximum number of tokens to generate
                    "stop": stop
                }
            )
            return response["message"]["content"]
        except Exception as e:
            raise Exception(f"Ollama API error: {str(e)}")

    def _generate(self, prompts: List[str], stop: Optional[List[str]] = None) -> LLMResult:
        """Generate responses for multiple prompts"""
        generations = []
        for prompt in prompts:
            text = self._call(prompt, stop)
            generations.append([Generation(text=text)])

        return LLMResult(generations=generations)


class GLMLLM(LLM):
    """Custom LLM class for GLM (Z.AI) integration"""

    def __init__(self, model: str = "glm-4.5-air", api_key: str = "", 
                 base_url: str = "https://api.z.ai/api/coding/paas/v4",
                 temperature: float = 0.7, max_tokens: int = 32768):
        super().__init__()
        self._model = model
        self._api_key = api_key
        self._base_url = base_url
        self._temperature = temperature
        self._max_tokens = max_tokens

    @property
    def _llm_type(self) -> str:
        return "glm"

    @property
    def model(self) -> str:
        return self._model

    @property
    def api_key(self) -> str:
        return self._api_key

    @property
    def base_url(self) -> str:
        return self._base_url

    @property
    def temperature(self) -> float:
        return self._temperature

    @property
    def max_tokens(self) -> int:
        return self._max_tokens

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """Call the GLM API"""
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self._api_key}",
                "Accept-Language": "en-US,en"
            }
            
            data = {
                "model": self._model,
                "messages": [
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                "max_tokens": self._max_tokens,
                "temperature": self._temperature,
                "thinking": {
                    "type": "enabled"
                }
            }
            
            if stop:
                data["stop"] = stop

            response = requests.post(
                f"{self._base_url}/chat/completions",
                headers=headers,
                json=data
            )
            
            response.raise_for_status()
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                raise Exception("Invalid response format from GLM API")
                
        except requests.exceptions.Timeout as e:
            raise Exception(f"GLM API timeout - the request took too long. This is normal for complex queries. Please try again or use a simpler query.")
        except requests.exceptions.RequestException as e:
            raise Exception(f"GLM API request error: {str(e)}")
        except Exception as e:
            raise Exception(f"GLM API error: {str(e)}")

    def _generate(self, prompts: List[str], stop: Optional[List[str]] = None) -> LLMResult:
        """Generate responses for multiple prompts"""
        generations = []
        for prompt in prompts:
            text = self._call(prompt, stop)
            generations.append([Generation(text=text)])

        return LLMResult(generations=generations)

