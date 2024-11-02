import json
import logging
from dataclasses import asdict
from typing import Dict, Optional, Union, Type
from pathlib import Path

from config_types import OpenAIConfig, AnthropicConfig, BaseLLMConfig, \
    LLMProvider

logger = logging.getLogger(__name__)

LLMConfigType = Union[OpenAIConfig, AnthropicConfig]


class ConfigManager:
    _config_classes: Dict[str, Type[BaseLLMConfig]] = {
        LLMProvider.OPENAI.value: OpenAIConfig,
        LLMProvider.ANTHROPIC.value: AnthropicConfig,
    }

    def __init__(self, config_path: str = "llm_config.json"):
        self.config_path = Path(config_path)
        self.configs: Dict[str, dict] = self._load_configs()

    def _load_configs(self) -> Dict[str, dict]:
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.error(f"Error loading config file: {self.config_path}")
                return {}
        return {}

    def _dict_to_config(self, provider: str,
                        config_dict: dict) -> LLMConfigType:
        config_class = self._config_classes[provider]
        # Ensure temperature is always 1.0 when loading from file
        config_dict['temperature'] = 1.0
        return config_class(**config_dict)

    def save_config(self, provider: str, config: LLMConfigType) -> None:
        self.configs[provider] = asdict(config)
        with open(self.config_path, 'w') as f:
            json.dump(self.configs, f, indent=2)
        logger.info(f"Saved configuration for {provider}")

    def get_config(self, provider: str) -> Optional[LLMConfigType]:
        config_dict = self.configs.get(provider)
        if config_dict:
            return self._dict_to_config(provider, config_dict)
        return None

    def configure_llm(self) -> tuple[str, LLMConfigType]:
        """Interactive LLM configuration"""
        logger.info("Available LLM providers: %s",
                    ", ".join(LLMProvider.list_providers()))

        while True:
            provider = input("Select LLM provider: ").lower()
            if provider in LLMProvider.list_providers():
                break
            logger.error("Invalid provider. Please choose from: %s",
                         ", ".join(LLMProvider.list_providers()))

        existing_config = self.get_config(provider)
        if existing_config:
            use_existing = input(
                "Found existing configuration. Use it? (y/n): ").lower() == 'y'
            if use_existing:
                return provider, existing_config

        config_class = self._config_classes[provider]
        default_model = config_class.default_model()

        api_key = input("Enter API key: ").strip()

        # Model input with default
        model_input = input(
            f"Enter model name (press Enter for default '{default_model}'): ").strip()
        model = model_input if model_input else default_model

        config = config_class(
            api_key=api_key,
            model=model,
            temperature=1.0  # Fixed temperature value
        )

        self.save_config(provider, config)
        return provider, config