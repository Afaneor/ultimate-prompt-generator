import logging
from llama_index.core.chat_engine import SimpleChatEngine
from llama_index.legacy.llms import Anthropic
from llama_index.llms.openai import OpenAI
from typing import Dict, Callable

from config_manager import LLMConfigType
from config_types import LLMProvider

logger = logging.getLogger(__name__)


class LLMManager:
    _llm_factories: Dict[str, Callable] = {
        LLMProvider.OPENAI.value: lambda config: OpenAI(
            api_key=config.api_key,
            model=config.model,
            temperature=config.temperature
        ),
        LLMProvider.ANTHROPIC.value: lambda config: Anthropic(
            api_key=config.api_key,
            model=config.model,
            temperature=config.temperature
        ),
    }

    @classmethod
    def create_llm(cls, provider: str, config: LLMConfigType):
        logger.info(
            f"Creating LLM for provider: {provider} with model: {config.model}")

        factory = cls._llm_factories.get(provider)
        if not factory:
            raise ValueError(f"Unsupported LLM provider: {provider}")

        llm = factory(config)
        return SimpleChatEngine.from_defaults(llm=llm)
