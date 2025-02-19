import pytest

from upg.config.types import AnthropicConfig, OpenAIConfig
from upg.core.llm import LLMManager


def test_create_openai_llm():
    """Test creation of OpenAI LLM instance"""
    config = OpenAIConfig(api_key='test-key', model='gpt-4o', temperature=1.0)

    engine = LLMManager.create_llm('openai', config)
    assert engine is not None


def test_create_anthropic_llm():
    """Test creation of Anthropic LLM instance"""
    config = AnthropicConfig(
        api_key='test-key', model='claude-3-5-sonnet-20241022', temperature=1.0
    )

    engine = LLMManager.create_llm('anthropic', config)
    assert engine is not None


def test_unsupported_provider():
    """Test error handling for unsupported provider"""
    config = OpenAIConfig(
        api_key='test-key', model='test-model', temperature=1.0
    )

    with pytest.raises(ValueError) as exc_info:
        LLMManager.create_llm('unsupported', config)

    assert 'Unsupported LLM provider' in str(exc_info.value)
