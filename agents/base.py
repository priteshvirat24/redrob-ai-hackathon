"""
Base Agent interface.
Standardizes agent inputs, outputs, and LLM provider access.
"""

from abc import ABC, abstractmethod
from pydantic import BaseModel
from intelligence.llm.providers import ProviderRegistry, BaseLLMProvider
import logging

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    def __init__(self, provider_name: str = "freellm"):
        self.provider: BaseLLMProvider = ProviderRegistry.get(provider_name)
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def run(self, *args, **kwargs):
        """Execute the agent's core task."""
        pass
