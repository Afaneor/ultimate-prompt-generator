import pytest
from click.testing import CliRunner

from upg.cli.commands import cli


@pytest.fixture
def runner():
    """Create a CLI runner"""
    return CliRunner()


def test_config_provider_command(runner, temp_config_dir):
    """Test provider configuration command"""
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                'config',
                'provider',
                '--provider',
                'openai',
                '--api-key',
                'test-key',
                '--model',
                'gpt-4o',
            ],
        )

        assert result.exit_code == 0
        assert 'Configuration for openai saved successfully' in result.output


def test_set_default_provider(runner, temp_config_dir):
    """Test setting default provider"""
    with runner.isolated_filesystem():
        # First configure the provider
        result = runner.invoke(
            cli,
            [
                'config',
                'provider',
                '--provider',
                'openai',
                '--api-key',
                'test-key',
                '--model',
                'gpt-4o',
            ],
        )
        assert result.exit_code == 0

        # Then set it as default
        result = runner.invoke(
            cli,
            [
                'config',
                'set-default',
                'openai',
            ],
        )
        assert result.exit_code == 0
        assert 'Default provider set to openai' in result.output


def test_show_config(runner, temp_config_dir):
    """Test showing configuration"""
    with runner.isolated_filesystem():
        # First configure a provider
        result = runner.invoke(
            cli,
            [
                'config',
                'provider',
                '--provider',
                'openai',
                '--api-key',
                'test-key',
                '--model',
                'gpt-4o',
            ],
        )
        assert result.exit_code == 0

        # Then test show command
        result = runner.invoke(cli, ['config', 'show'])
        assert result.exit_code == 0
        assert 'Current Configuration' in result.output
        assert 'OPENAI' in result.output
        assert 'gpt-4o' in result.output


def test_config_provider_interactive(runner, temp_config_dir):
    """Test interactive provider configuration"""
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            ['config', 'provider'],
            input='openai\ntest-key\ngpt-4o\n',
        )
        assert result.exit_code == 0
        assert 'Configuration for openai saved successfully' in result.output


@pytest.mark.parametrize('provider', ['openai', 'anthropic'])
def test_config_provider_different_providers(runner, temp_config_dir, provider):
    """Test configuration with different providers"""
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                'config',
                'provider',
                '--provider',
                provider,
                '--api-key',
                'test-key',
                '--model',
                'test-model',
            ],
        )
        assert result.exit_code == 0
        assert f'Configuration for {provider} saved successfully' in result.output