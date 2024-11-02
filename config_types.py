from dataclasses import dataclass
from enum import Enum

class LLMProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"

    @classmethod
    def list_providers(cls) -> list[str]:
        return [provider.value for provider in cls]

    @classmethod
    def get_default_model(cls, provider: str) -> str:
        defaults = {
            cls.OPENAI.value: "gpt-4o",
            cls.ANTHROPIC.value: "claude-3-5-sonnet-20241022"
        }
        return defaults.get(provider, "")

@dataclass
class BaseLLMConfig:
    api_key: str
    model: str
    temperature: float = 1.0

@dataclass
class OpenAIConfig(BaseLLMConfig):
    @classmethod
    def default_model(cls) -> str:
        return "gpt-4o"

@dataclass
class AnthropicConfig(BaseLLMConfig):
    @classmethod
    def default_model(cls) -> str:
        return "claude-3-5-sonnet-20241022"