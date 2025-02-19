import logging
import re
from dataclasses import dataclass

from llama_index.core.base.llms.types import ChatMessage
from llama_index.core.chat_engine import SimpleChatEngine

logger = logging.getLogger(__name__)


@dataclass
class GeneratorResult:
    """Result of prompt generation"""

    prompt: str
    variables: set[str]
    raw_response: str | None = None


class PromptGenerator:
    """Generates and manages prompts for LLM interactions"""

    def __init__(
        self,
        chat_engine: SimpleChatEngine,
        metaprompt_path: str | None = None,
    ):
        """
        Initialize prompt generator

        Args:
            chat_engine: LLM chat engine instance
            metaprompt_path: Path to custom metaprompt template
        """
        self.chat = chat_engine
        self.metaprompt_template = self._load_metaprompt(metaprompt_path)

    def _load_metaprompt(self, path: str | None = None) -> str:
        """Load metaprompt template from file or use default"""
        if path:
            try:
                with open(path) as f:
                    return f.read()
            except Exception as e:
                logger.error(f'Error loading metaprompt template: {e}')
                raise
        return self._get_default_metaprompt()

    @staticmethod
    def _get_default_metaprompt() -> str:
        """Returns default metaprompt template"""
        # Import here to avoid circular imports
        from upg.core.prompts.metaprompt import metaprompt

        return metaprompt

    @staticmethod
    def extract_between_tags(
        tag: str, string: str, strip: bool = False
    ) -> list[str]:
        """Extract content between XML tags"""
        ext_list = re.findall(f'<{tag}>(.+?)</{tag}>', string, re.DOTALL)
        if strip:
            ext_list = [e.strip() for e in ext_list]
        return ext_list

    @staticmethod
    def remove_empty_tags(text: str) -> str:
        """
        Remove empty XML tags from text

        Args:
            text: Input text

        Returns:
            Text with empty tags removed
        """
        # Сначала удаляем теги с пробелами внутри
        text = re.sub(r'<(\w+)>\s*</\1>', '', text)
        # Затем удаляем пустые строки
        lines = [line for line in text.split('\n') if line.strip()]
        return '\n'.join(lines)

    @staticmethod
    def strip_last_sentence(text: str) -> str:
        """Remove last sentence if it starts with 'Let me know'"""
        sentences = text.split('. ')
        if sentences[-1].startswith('Let me know'):
            sentences = sentences[:-1]
            result = '. '.join(sentences)
            if result and not result.endswith('.'):
                result += '.'
            return result
        return text

    @staticmethod
    def extract_variables(prompt: str) -> set[str]:
        """Extract variable names from prompt"""
        pattern = r'{([^}]+)}'
        variables = re.findall(pattern, prompt)
        return set(variables)

    def find_free_floating_variables(self, prompt: str) -> list[str]:
        """
        Find variables that are not properly contained within XML tags

        Args:
            prompt: Generated prompt text

        Returns:
            List of free-floating variable names
        """
        variable_usages = re.findall(r'\{\$[A-Z0-9_]+\}', prompt)
        free_floating_variables = []

        for variable in variable_usages:
            preceding_text = prompt[: prompt.index(variable)]
            open_tags = set()

            i = 0
            while i < len(preceding_text):
                if preceding_text[i] == '<':
                    if (
                        i + 1 < len(preceding_text)
                        and preceding_text[i + 1] == '/'
                    ):
                        closing_tag = preceding_text[i + 2 :].split('>', 1)[0]
                        open_tags.discard(closing_tag)
                        i += len(closing_tag) + 3
                    else:
                        opening_tag = preceding_text[i + 1 :].split('>', 1)[0]
                        open_tags.add(opening_tag)
                        i += len(opening_tag) + 2
                else:
                    i += 1

            if not open_tags:
                free_floating_variables.append(variable)

        return free_floating_variables

    def remove_inapt_floating_variables(self, prompt: str) -> str:
        """
        Remove or fix inappropriately used floating variables

        Args:
            prompt: Generated prompt text

        Returns:
            Cleaned prompt text
        """
        from ..core.prompts.floatingprompt import (
            remove_floating_variables_prompt,
        )

        message = self.chat.chat(
            remove_floating_variables_prompt.replace('{$PROMPT}', prompt),
            chat_history=[],
        ).response

        return self.extract_between_tags('rewritten_prompt', message)[0]

    def generate_prompt(
        self, task: str, variables: list[str] | None = None
    ) -> GeneratorResult:
        """
        Generate prompt for given task and variables

        Args:
            task: Task description
            variables: Optional list of variable names

        Returns:
            GeneratorResult with prompt and found variables

        Raises:
            Exception: If prompt generation fails
        """
        logger.info(f'Generating prompt for task: {task}')

        if variables is None:
            variables = []

        # Format variables with proper casing
        variable_string = '\n'.join(f'{{${var.upper()}}}' for var in variables)

        # Replace task in metaprompt
        prompt = self.metaprompt_template.replace('{{TASK}}', task)

        # Create assistant partial response
        assistant_partial = '<Inputs>'
        if variable_string:
            assistant_partial += (
                f'\n{variable_string}\n</Inputs>\n<Instructions Structure>'
            )

        try:
            response = self.chat.chat(
                prompt,
                chat_history=[
                    ChatMessage(content=assistant_partial, role='assistant')
                ],
            ).response

            logger.debug(f'Raw LLM response: {response}')

            extracted_prompt = self.extract_prompt(response)
            found_variables = self.extract_variables(response)

            # Handle floating variables
            floating_variables = self.find_free_floating_variables(
                extracted_prompt
            )
            if floating_variables:
                logger.info(f'Found floating variables: {floating_variables}')
                extracted_prompt = self.remove_inapt_floating_variables(
                    extracted_prompt
                )

            return GeneratorResult(
                prompt=extracted_prompt,
                variables=found_variables,
                raw_response=response,
            )

        except Exception as e:
            logger.error(f'Error generating prompt: {str(e)}', exc_info=True)
            raise

    def extract_prompt(self, metaprompt_response: str) -> str:
        """
        Extract final prompt from metaprompt response

        Args:
            metaprompt_response: Raw response from LLM

        Returns:
            Cleaned and processed prompt
        """
        between_tags = self.extract_between_tags(
            'Instructions', metaprompt_response
        )[0]
        cleaned_prompt = between_tags[:1000] + self.strip_last_sentence(
            self.remove_empty_tags(
                self.remove_empty_tags(between_tags[1000:]).strip()
            ).strip()
        )
        return cleaned_prompt

    def generate_answer(
        self, prompt: str, variable_values: dict[str, str] | None = None
    ) -> str:
        """
        Generate answer using the prompt and variable values

        Args:
            prompt: Generated prompt
            variable_values: Optional dictionary of variable values

        Returns:
            Generated answer

        Raises:
            Exception: If answer generation fails
        """
        if variable_values:
            for var, value in variable_values.items():
                prompt = prompt.replace('{' + var + '}', value)

        try:
            response = self.chat.chat(prompt, chat_history=[]).response
            return response
        except Exception as e:
            logger.error(f'Error generating answer: {str(e)}')
            raise
