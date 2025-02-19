import logging
from collections.abc import Callable
from typing import Any

from llama_index.core.chat_engine import SimpleChatEngine
from llama_index.llms.anthropic import Anthropic
from llama_index.llms.openai import OpenAI

from upg.config.types import BaseLLMConfig, LLMProvider

logger = logging.getLogger(__name__)


class LLMManager:
    """Manages LLM provider instances and configurations"""

    _llm_factories: dict[str, Callable[[BaseLLMConfig], Any]] = {
        LLMProvider.OPENAI.value: lambda config: OpenAI(
            api_key=config.api_key,
            model=config.model,
            temperature=config.temperature,
        ),
        LLMProvider.ANTHROPIC.value: lambda config: Anthropic(
            api_key=config.api_key,
            model=config.model,
            temperature=config.temperature,
        ),
    }

    @classmethod
    def create_llm(
        cls, provider: str, config: BaseLLMConfig
    ) -> SimpleChatEngine:
        """
        Create a chat engine instance for the specified provider

        Args:
            provider: LLM provider name
            config: Provider configuration

        Returns:
            SimpleChatEngine instance

        Raises:
            ValueError: If provider is not supported
            Exception: If creation fails
        """
        logger.info(
            f'Creating LLM for provider: {provider} with model: {config.model}'
        )

        try:
            factory = cls._llm_factories.get(provider)
            if not factory:
                raise ValueError(f'Unsupported LLM provider: {provider}')

            llm = factory(config)
            return SimpleChatEngine.from_defaults(llm=llm)

        except Exception as e:
            logger.error(f'Error creating LLM instance: {e}')
            raise

    @classmethod
    def supported_providers(cls) -> list[str]:
        """Returns list of supported LLM providers"""
        return list(cls._llm_factories.keys())
