"""
LLM Provider Registry.
Allows seamless switching between different LLM backends (OpenAI, Gemini, FreeLLM Proxy, Local).
"""

from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Dict, Type
import os
import json
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)


class BaseLLMProvider(ABC):
    @abstractmethod
    def chat_completion(self, system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
        pass

    @abstractmethod
    def structured_completion(self, system_prompt: str, user_prompt: str, response_format: Type[BaseModel]) -> BaseModel | None:
        pass


class OpenAIProvider(BaseLLMProvider):
    def __init__(self, base_url: str = None, api_key: str = None, model: str = "gpt-4-turbo"):
        self.client = OpenAI(base_url=base_url, api_key=api_key or os.getenv("OPENAI_API_KEY", "dummy_key"))
        self.model = model

    def chat_completion(self, system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API Error: {e}")
            return ""

    def structured_completion(self, system_prompt: str, user_prompt: str, response_format: Type[BaseModel]) -> BaseModel | None:
        try:
            system_prompt += f"\n\nYou MUST return raw valid JSON matching this schema: {json.dumps(response_format.model_json_schema())}"
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
            )
            raw = response.choices[0].message.content
            return response_format.model_validate_json(raw)
        except Exception as e:
            logger.error(f"OpenAI Structured API Error: {e}")
            return None


class FreeLLMProvider(OpenAIProvider):
    """Specific subclass for the Hackathon's free LLM proxy."""
    def __init__(self):
        super().__init__(
            base_url=os.getenv("LLM_BASE_URL", "http://localhost:3001/v1"),
            api_key=os.getenv("LLM_API_KEY", "freellmapi-e85c66fc2196ebfe9c13738a3c93d5630af813e3a865cf4c"),
            model=os.getenv("LLM_MODEL", "-auto")
        )
        
    def structured_completion(self, system_prompt: str, user_prompt: str, response_format: Type[BaseModel]) -> BaseModel | None:
        try:
            return super().structured_completion(system_prompt, user_prompt, response_format)
        except Exception as e:
            logger.error(f"FreeLLM Connection Error, using fallback mock: {e}")
            # Generate empty mock data that matches the schema just to keep the DAG alive
            schema = response_format.model_json_schema()
            mock_data = {}
            for prop, details in schema.get("properties", {}).items():
                if details.get("type") == "array":
                    mock_data[prop] = ["Mocked Data"]
                elif details.get("type") == "boolean":
                    mock_data[prop] = True
                else:
                    mock_data[prop] = "Mocked Data"
            return response_format(**mock_data)

    def chat_completion(self, system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
        try:
            return super().chat_completion(system_prompt, user_prompt, temperature)
        except Exception as e:
            logger.error(f"FreeLLM Connection Error, using fallback mock: {e}")
            return "This is a mock LLM explanation generated because the LLM proxy is unreachable."



class ProviderRegistry:
    _providers: Dict[str, BaseLLMProvider] = {}
    _default: str = "freellm"

    @classmethod
    def register(cls, name: str, provider: BaseLLMProvider):
        cls._providers[name] = provider

    @classmethod
    def get(cls, name: str = None) -> BaseLLMProvider:
        name = name or cls._default
        if name not in cls._providers:
            raise ValueError(f"Provider {name} not found in registry.")
        return cls._providers[name]


# Auto-register default providers
ProviderRegistry.register("freellm", FreeLLMProvider())
ProviderRegistry.register("openai", OpenAIProvider())
