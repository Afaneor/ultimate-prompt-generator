from upg.config.manager import ConfigManager
from upg.config.types import LLMProvider


def test_config_manager_init(config_manager, temp_config_dir):
    """Test ConfigManager initialization"""
    assert config_manager.config_dir == temp_config_dir
    assert config_manager.config_file == temp_config_dir / 'config.json'
    assert config_manager.config.default_provider == LLMProvider.OPENAI


def test_save_load_config(config_manager, openai_config):
    """Test saving and loading configuration"""
    # Save configuration
    config_manager.set_provider_config('openai', openai_config)

    # Verify file exists
    assert config_manager.config_file.exists()

    # Load in new manager
    new_manager = ConfigManager(config_dir=str(config_manager.config_dir))
    loaded_config = new_manager.get_provider_config('openai')

    assert loaded_config.api_key == openai_config.api_key
    assert loaded_config.model == openai_config.model
    assert loaded_config.temperature == openai_config.temperature


def test_invalid_config_file(temp_config_dir):
    """Test handling of invalid configuration file"""
    config_file = temp_config_dir / 'config.json'
    config_file.parent.mkdir(parents=True, exist_ok=True)

    # Write invalid JSON
    with open(config_file, 'w') as f:
        f.write('invalid json')

    # Should not raise error, returns default config
    manager = ConfigManager(config_dir=str(temp_config_dir))
    assert manager.config.default_provider == LLMProvider.OPENAI
    assert not manager.config.providers


def test_llm_provider_enum():
    """Test LLMProvider enum functionality"""
    assert LLMProvider.list_providers() == ['openai', 'anthropic']
    assert LLMProvider.get_default_model('openai') == 'gpt-4o'
    assert (
        LLMProvider.get_default_model('anthropic')
        == 'claude-3-5-sonnet-20241022'
    )
