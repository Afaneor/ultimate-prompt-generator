from unittest.mock import Mock

import pytest
from llama_index.core.chat_engine import SimpleChatEngine
from llama_index.core.llms import MockLLM

from upg.config.manager import ConfigManager
from upg.config.types import (
    AnthropicConfig,
    AppConfig,
    LLMProvider,
    OpenAIConfig,
)


@pytest.fixture
def temp_config_dir(tmp_path):
    """Create a temporary config directory"""
    return tmp_path / 'config'


@pytest.fixture
def config_manager(temp_config_dir):
    """Create a ConfigManager instance with temporary directory"""
    return ConfigManager(config_dir=str(temp_config_dir))


@pytest.fixture
def mock_llm():
    """Create a MockLLM instance"""
    return MockLLM(max_tokens=10)


@pytest.fixture
def mock_chat_engine(mock_llm):
    """Create a SimpleChatEngine with MockLLM"""
    return SimpleChatEngine.from_defaults(llm=mock_llm)


@pytest.fixture
def mock_llm_manager(mock_chat_engine):
    """Create a mock LLM manager"""
    manager = Mock()
    manager.create_llm.return_value = mock_chat_engine
    return manager


@pytest.fixture
def openai_config():
    """Create a sample OpenAI configuration"""
    return OpenAIConfig(
        api_key='test-openai-key', model='gpt-4o', temperature=1.0
    )


@pytest.fixture
def anthropic_config():
    """Create a sample Anthropic configuration"""
    return AnthropicConfig(
        api_key='test-anthropic-key',
        model='claude-3-5-sonnet-20241022',
        temperature=1.0,
    )


@pytest.fixture
def app_config(openai_config, anthropic_config):
    """Create a sample application configuration"""
    return AppConfig(
        default_provider=LLMProvider.OPENAI,
        providers={'openai': openai_config, 'anthropic': anthropic_config},
    )
