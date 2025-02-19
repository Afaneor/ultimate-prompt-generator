import logging

import click

from upg.config.manager import ConfigManager
from upg.config.types import LLMProvider
from upg.core.generator import PromptGenerator
from upg.core.llm import LLMManager

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool):
    """Configure logging level based on verbosity"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def cli(verbose: bool):
    """Ultimate Prompt Generator CLI"""
    setup_logging(verbose)


@cli.group()
def config():
    """Configure UPG settings"""
    pass


@config.command()
@click.option(
    '--provider',
    type=click.Choice(LLMProvider.list_providers()),
    help='LLM provider to configure',
)
@click.option('--api-key', help='API key for the provider')
@click.option('--model', help='Model name')
def provider(
    provider: str | None,
    api_key: str | None,
    model: str | None,
):
    """Configure provider settings"""
    try:
        config_manager = ConfigManager()

        if not provider:
            # Interactive mode
            provider = click.prompt(
                'Select provider',
                type=click.Choice(LLMProvider.list_providers()),
            )

        if not api_key:
            api_key = click.prompt(f'Enter {provider} API key', hide_input=True)

        if not model:
            default_model = LLMProvider.get_default_model(provider)
            model = click.prompt(
                'Enter model name', default=default_model, show_default=True
            )

        config_manager.set_provider_config(
            provider, {'api_key': api_key, 'model': model, 'temperature': 1.0}
        )

        click.echo(f'Configuration for {provider} saved successfully')

    except Exception as e:
        logger.error(f'Error configuring provider: {e}')
        raise click.ClickException(str(e)) from e


@config.command()
@click.argument('provider', type=click.Choice(LLMProvider.list_providers()))
def set_default(provider: str):
    """Set default LLM provider"""
    try:
        config_manager = ConfigManager()

        # Check if provider is configured
        if not config_manager.get_provider_config(provider):
            raise click.ClickException(
                f"Provider {provider} is not configured. Run 'upg config provider' first."  # noqa: E501
            )

        config_manager.config.default_provider = provider
        config_manager.save_config()
        click.echo(f'Default provider set to {provider}')

    except Exception as e:
        logger.error(f'Error setting default provider: {e}')
        raise click.ClickException(str(e)) from e


@config.command()
def show():
    """Show current configuration"""
    try:
        config_manager = ConfigManager()

        click.echo('\nCurrent Configuration:')
        click.echo('-' * 40)
        click.echo(
            f'Default Provider: {config_manager.config.default_provider}')
        click.echo('\nConfigured Providers:')

        for provider in LLMProvider.list_providers():
            provider_config = config_manager.get_provider_config(provider)
            if provider_config:
                click.echo(f'\n{provider.upper()}:')
                click.echo(f'  Model: {provider_config.model}')
                click.echo(f'  Temperature: {provider_config.temperature}')
                # Не показываем API ключ полностью в целях безопасности
                api_key = provider_config.api_key
                masked_key = f"{api_key[:8]}...{api_key[-4:]}" if len(
                    api_key) > 12 else "***"
                click.echo(f'  API Key: {masked_key}')

    except Exception as e:
        logger.error(f'Error showing configuration: {e}')
        raise click.ClickException(str(e)) from e


@cli.command()
@click.argument('task')
@click.option(
    '--provider',
    type=click.Choice(LLMProvider.list_providers()),
    help='LLM provider to use',
)
@click.option(
    '--variable', '-v', multiple=True, help='Variable names for the prompt'
)
@click.option(
    '--output',
    '-o',
    type=click.File('w'),
    help='Output file for the generated prompt',
)
@click.option(
    '--save',
    '-s',
    is_flag=True,
    help='Save the generated prompt for later use',
)
@click.option(
    '--name',
    help='Name for saved prompt (required if --save is used)',
)
@click.option(
    '--description',
    '-d',
    help='Description for saved prompt',
)
@click.option(
    '--tag',
    '-t',
    multiple=True,
    help='Tags for saved prompt',
)
def generate(
    task: str,
    provider: str | None,
    variable: tuple[str, ...],
    output,
    save: bool,
    name: str | None,
    description: str | None,
    tag: tuple[str, ...],
):
    """Generate a prompt for given task"""
    try:
        config_manager = ConfigManager()

        if not provider:
            provider = config_manager.config.default_provider

        provider_config = config_manager.get_provider_config(provider)
        if not provider_config:
            raise click.ClickException(
                f"Provider {provider} not configured. Run 'upg config' first."
            )

        chat_engine = LLMManager.create_llm(provider, provider_config)
        generator = PromptGenerator(chat_engine)

        result = generator.generate_prompt(task, list(variable))

        # Handle saving if requested
        if save:
            if name is None:
                name = click.prompt('Enter a name for the prompt')

            config_manager.save_prompt(
                name=name,
                content=result.prompt,
                variables=list(result.variables),
                description=description,
                tags=list(tag),
            )
            click.echo(f'\nPrompt saved as "{name}"')

        if output:
            output.write(result.prompt)
            click.echo(f'Prompt saved to {output.name}')
        else:
            click.echo('\nGenerated Prompt:')
            click.echo('-' * 40)
            click.echo(result.prompt)
            click.echo('-' * 40)

        if result.variables:
            click.echo('\nDetected variables:')
            for var in result.variables:
                click.echo(f'- {var}')

    except Exception as e:
        logger.error(f'Error generating prompt: {e}')
        raise click.ClickException(str(e)) from e


@cli.command()
@click.argument('prompt_source')
@click.option(
    '--provider',
    type=click.Choice(LLMProvider.list_providers()),
    help='LLM provider to use',
)
@click.option(
    '--var',
    '-v',
    multiple=True,
    nargs=2,
    help='Variable values in format: name value',
)
@click.option(
    '--output',
    '-o',
    type=click.File('w'),
    help='Output file for the generated answer',
)
@click.option(
    '--from-file',
    '-f',
    is_flag=True,
    help='Treat prompt_source as a file path instead of stored prompt name',
)
def answer(  # noqa: C901
    prompt_source: str, provider: str | None, var, output, from_file: bool
):
    """
    Generate answer for a prompt.

    PROMPT_SOURCE can be either a stored prompt name
    or a file path (if --from-file is used).
    """
    try:
        config_manager = ConfigManager()

        if not provider:
            provider = config_manager.config.default_provider

        provider_config = config_manager.get_provider_config(provider)
        if not provider_config:
            raise click.ClickException(
                f"Provider {provider} not configured. Run 'upg config' first."
            )

        # Get prompt content either from file or stored prompts
        if from_file:
            try:
                with open(prompt_source) as f:
                    prompt = f.read()
                stored_prompt = None
            except FileNotFoundError as e:
                raise click.ClickException(
                    f'File not found: {prompt_source}'
                ) from e
        else:
            stored_prompt = config_manager.get_prompt(prompt_source)
            if not stored_prompt:
                raise click.ClickException(
                    f'Stored prompt "{prompt_source}" not found. Use --from-file if you meant to read from a file.'  # noqa: E501
                )
            prompt = stored_prompt.content

        # Validate variables if using stored prompt
        if stored_prompt and stored_prompt.variables:
            provided_vars = {name for name, _ in var}
            required_vars = set(stored_prompt.variables)
            missing_vars = required_vars - provided_vars

            if missing_vars:
                # Prompt for missing variables interactively
                additional_vars = []
                for var_name in missing_vars:
                    value = click.prompt(f'Enter value for variable {var_name}')
                    additional_vars.append((var_name, value))
                var = list(var) + additional_vars

        chat_engine = LLMManager.create_llm(provider, provider_config)
        generator = PromptGenerator(chat_engine)

        # Convert variables tuple to dictionary
        variables = dict(var)

        # If using stored prompt, show prompt info
        if stored_prompt:
            click.echo('\nUsing stored prompt:')
            click.echo(f'Name: {stored_prompt.name}')
            if stored_prompt.description:
                click.echo(f'Description: {stored_prompt.description}')
            if stored_prompt.tags:
                click.echo(f'Tags: {", ".join(stored_prompt.tags)}')
            click.echo('-' * 40)

        answer = generator.generate_answer(prompt, variables)

        if output:
            output.write(answer)
            click.echo(f'Answer saved to {output.name}')
        else:
            click.echo('\nGenerated Answer:')
            click.echo('-' * 40)
            click.echo(answer)
            click.echo('-' * 40)

    except Exception as e:
        logger.error(f'Error generating answer: {e}')
        raise click.ClickException(str(e)) from e


@cli.group()
def prompts():
    """Manage stored prompts"""
    pass


@prompts.command(name='save')
@click.argument('name')
@click.argument('prompt_file', type=click.File('r'))
@click.option('--description', '-d', help='Description of the prompt')
@click.option('--tag', '-t', multiple=True, help='Tags for the prompt')
@click.option(
    '--variables', '-v', multiple=True, help='Variable names used in the prompt'
)
def save_prompt(
    name: str,
    prompt_file,
    description: str | None,
    tag: tuple[str, ...],
    variables: tuple[str, ...],
):
    """Save a prompt to configuration"""
    try:
        config_manager = ConfigManager()
        content = prompt_file.read()

        config_manager.save_prompt(
            name=name,
            content=content,
            description=description,
            tags=list(tag),
            variables=list(variables),
        )

        click.echo(f'Prompt "{name}" saved successfully')

    except Exception as e:
        logger.error(f'Error saving prompt: {e}')
        raise click.ClickException(str(e)) from e


@prompts.command(name='list')
@click.option('--tag', '-t', multiple=True, help='Filter by tags')
def list_prompts(tag: tuple[str, ...]):
    """List all stored prompts"""
    try:
        config_manager = ConfigManager()
        prompts = config_manager.list_prompts()

        if tag:
            prompts = [p for p in prompts if all(t in p.tags for t in tag)]

        if not prompts:
            click.echo('No prompts found')
            return

        click.echo('\nStored Prompts:')
        click.echo('-' * 40)

        for prompt in prompts:
            click.echo(f'\nName: {prompt.name}')
            if prompt.description:
                click.echo(f'Description: {prompt.description}')
            if prompt.tags:
                click.echo(f'Tags: {", ".join(prompt.tags)}')
            if prompt.variables:
                click.echo(f'Variables: {", ".join(prompt.variables)}')
            click.echo(f'Created: {prompt.created_at}')
            click.echo('-' * 40)

    except Exception as e:
        logger.error(f'Error listing prompts: {e}')
        raise click.ClickException(str(e)) from e


@prompts.command(name='show')
@click.argument('name')
def show_prompt(name: str):
    """Show a specific prompt"""
    try:
        config_manager = ConfigManager()
        prompt = config_manager.get_prompt(name)

        if not prompt:
            raise click.ClickException(f'Prompt "{name}" not found')

        click.echo(f'\nPrompt: {prompt.name}')
        click.echo('-' * 40)
        if prompt.description:
            click.echo(f'Description: {prompt.description}')
        if prompt.tags:
            click.echo(f'Tags: {", ".join(prompt.tags)}')
        if prompt.variables:
            click.echo(f'Variables: {", ".join(prompt.variables)}')
        click.echo('\nContent:')
        click.echo(prompt.content)
        click.echo('-' * 40)

    except Exception as e:
        logger.error(f'Error showing prompt: {e}')
        raise click.ClickException(str(e)) from e


@prompts.command(name='delete')
@click.argument('name')
@click.confirmation_option(
    prompt='Are you sure you want to delete this prompt?'
)
def delete_prompt(name: str):
    """Delete a stored prompt"""
    try:
        config_manager = ConfigManager()
        if config_manager.delete_prompt(name):
            click.echo(f'Prompt "{name}" deleted successfully')
        else:
            raise click.ClickException(f'Prompt "{name}" not found')

    except Exception as e:
        logger.error(f'Error deleting prompt: {e}')
        raise click.ClickException(str(e)) from e


@prompts.command(name='search')
@click.argument('query')
@click.option('--tag', '-t', multiple=True, help='Filter by tags')
def search_prompts(query: str, tag: tuple[str, ...]):
    """Search stored prompts"""
    try:
        config_manager = ConfigManager()
        prompts = config_manager.search_prompts(
            query, list(tag) if tag else None
        )

        if not prompts:
            click.echo('No matching prompts found')
            return

        click.echo('\nMatching Prompts:')
        click.echo('-' * 40)

        for prompt in prompts:
            click.echo(f'\nName: {prompt.name}')
            if prompt.description:
                click.echo(f'Description: {prompt.description}')
            if prompt.tags:
                click.echo(f'Tags: {", ".join(prompt.tags)}')
            if prompt.variables:
                click.echo(f'Variables: {", ".join(prompt.variables)}')
            click.echo('-' * 40)

    except Exception as e:
        logger.error(f'Error searching prompts: {e}')
        raise click.ClickException(str(e)) from e


if __name__ == '__main__':
    cli()
