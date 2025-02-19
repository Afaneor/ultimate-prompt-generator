import json
import logging
from pathlib import Path

from pydantic import ValidationError

from upg.config.types import (
    AnthropicConfig,
    AppConfig,
    BaseLLMConfig,
    LLMProvider,
    OpenAIConfig,
    StoredPrompt,
)

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages application configuration and provider settings"""

    def __init__(self, config_dir: str | None = None):
        if config_dir is None:
            config_dir = Path.home() / '.config' / 'upg'
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / 'config.json'
        self.config: AppConfig = self._load_config()

    def _load_config(self) -> AppConfig:
        """Load configuration from file or create default"""
        if not self.config_dir.exists():
            self.config_dir.mkdir(parents=True)

        if not self.config_file.exists():
            return AppConfig(cache_dir=str(self.config_dir))

        try:
            with open(self.config_file) as f:
                data = json.load(f)
                return AppConfig(**data)
        except (json.JSONDecodeError, ValidationError) as e:
            logger.error(f'Error loading config file: {e}')
            return AppConfig(cache_dir=str(self.config_dir))

    def save_config(self) -> None:
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config.model_dump(), f, indent=2)
            logger.info('Configuration saved successfully')
        except Exception as e:
            logger.error(f'Error saving configuration: {e}')
            raise

    def get_provider_config(
        self, provider: str | LLMProvider
    ) -> BaseLLMConfig | None:
        """Get configuration for specific provider"""
        if isinstance(provider, LLMProvider):
            provider = provider.value
        return self.config.providers.get(provider)

    def set_provider_config(
        self,
        provider: str | LLMProvider,
        config: dict | BaseLLMConfig,
    ) -> None:
        """Set configuration for specific provider"""
        if isinstance(provider, LLMProvider):
            provider = provider.value

        if isinstance(config, dict):
            config_class = {
                LLMProvider.OPENAI.value: OpenAIConfig,
                LLMProvider.ANTHROPIC.value: AnthropicConfig,
            }.get(provider, BaseLLMConfig)

            try:
                config = config_class(**config)
            except ValidationError as e:
                logger.error(
                    f'Invalid configuration for provider {provider}: {e}'
                )
                raise

        self.config.providers[provider] = config
        self.save_config()

    def configure_provider(
        self, provider: str | LLMProvider
    ) -> tuple[str, BaseLLMConfig]:
        """Interactive provider configuration"""
        if isinstance(provider, LLMProvider):
            provider = provider.value

        config_class = {
            LLMProvider.OPENAI.value: OpenAIConfig,
            LLMProvider.ANTHROPIC.value: AnthropicConfig,
        }.get(provider)

        if not config_class:
            raise ValueError(f'Unsupported provider: {provider}')

        api_key = input(f'Enter {provider} API key: ').strip()
        default_model = config_class.default_model()

        model_input = input(
            f"Enter model name (press Enter for default '{default_model}'): "
        ).strip()

        model = model_input if model_input else default_model

        config = config_class(api_key=api_key, model=model, temperature=1.0)

        self.set_provider_config(provider, config)
        return provider, config

    def save_prompt(
        self,
        name: str,
        content: str,
        variables: list[str],
        description: str | None = None,
        tags: list[str] | None = None,
    ) -> StoredPrompt:
        """Save a prompt to configuration"""
        prompt = StoredPrompt(
            name=name,
            content=content,
            variables=variables,
            description=description,
            tags=tags or [],
        )

        if name in self.config.stored_prompts:
            prompt.created_at = self.config.stored_prompts[name].created_at

        self.config.stored_prompts[name] = prompt
        self.save_config()
        return prompt

    def get_prompt(self, name: str) -> StoredPrompt | None:
        """Retrieve a stored prompt by name"""
        return self.config.stored_prompts.get(name)

    def list_prompts(self) -> list[StoredPrompt]:
        """List all stored prompts"""
        return list(self.config.stored_prompts.values())

    def delete_prompt(self, name: str) -> bool:
        """Delete a stored prompt"""
        if name in self.config.stored_prompts:
            del self.config.stored_prompts[name]
            self.save_config()
            return True
        return False

    def search_prompts(
        self, query: str, tags: list[str] | None = None
    ) -> list[StoredPrompt]:
        """Search prompts by name, description or tags"""
        query = query.lower()
        results = []

        for prompt in self.config.stored_prompts.values():
            if query in prompt.name.lower() or (
                prompt.description and query in prompt.description.lower()
            ):
                if tags and not all(tag in prompt.tags for tag in tags):
                    continue
                results.append(prompt)

        return results
