from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class LLMProvider(str, Enum):
    """Supported LLM providers"""

    OPENAI = 'openai'
    ANTHROPIC = 'anthropic'

    @classmethod
    def list_providers(cls) -> list[str]:
        """Returns list of available providers"""
        return [provider.value for provider in cls]

    @classmethod
    def get_default_model(cls, provider: str | None) -> str:
        """Returns default model for given provider"""
        defaults = {
            cls.OPENAI.value: 'gpt-4o',
            cls.ANTHROPIC.value: 'claude-3-5-sonnet-20241022',
        }
        return defaults.get(provider, '')


class BaseLLMConfig(BaseModel):
    """Base configuration for LLM providers"""

    api_key: str = Field(..., description='API key for the provider')
    model: str = Field(..., description='Model name')
    temperature: float = Field(
        default=1.0,
        ge=0.0,
        le=2.0,
        description='Temperature for model responses',
    )


class OpenAIConfig(BaseLLMConfig):
    """OpenAI specific configuration"""

    @classmethod
    def default_model(cls) -> str:
        return 'gpt-4o'


class AnthropicConfig(BaseLLMConfig):
    """Anthropic specific configuration"""

    @classmethod
    def default_model(cls) -> str:
        return 'claude-3-5-sonnet-20241022'


class StoredPrompt(BaseModel):
    """Stored prompt configuration"""

    name: str = Field(..., description='Unique name/identifier for the prompt')
    description: str | None = Field(
        None, description='Optional description of the prompt'
    )
    content: str = Field(..., description='The actual prompt content')
    variables: list[str] = Field(
        default_factory=list,
        description='List of variable names used in the prompt',
    )
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    tags: list[str] = Field(
        default_factory=list, description='Optional tags for categorization'
    )


class AppConfig(BaseModel):
    """Global application configuration"""

    default_provider: LLMProvider = Field(default=LLMProvider.OPENAI)
    providers: dict[str, BaseLLMConfig] = Field(default_factory=dict)
    cache_dir: str | None = Field(default=None)
    stored_prompts: dict[str, StoredPrompt] = Field(
        default_factory=dict,
        description='Dictionary of stored prompts indexed by name',
    )

    class Config:
        use_enum_values = True
