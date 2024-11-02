import re
import logging
from typing import List, Optional, Set, Tuple
from llama_index.core.base.llms.types import ChatMessage

from core_prompts.metaprompt import metaprompt
from core_prompts.floatingprompt import remove_floating_variables_prompt

logger = logging.getLogger(__name__)


class PromptGenerator:
    def __init__(self, chat_engine):
        self.chat = chat_engine
        self.metaprompt_template = metaprompt

    @staticmethod
    def extract_between_tags(tag: str, string: str, strip: bool = False) -> \
    List[str]:
        ext_list = re.findall(f"<{tag}>(.+?)</{tag}>", string, re.DOTALL)
        if strip:
            ext_list = [e.strip() for e in ext_list]
        return ext_list

    @staticmethod
    def remove_empty_tags(text: str) -> str:
        return re.sub(r'\n<(\w+)>\s*</\1>\n', '', text, flags=re.DOTALL)

    @staticmethod
    def strip_last_sentence(text: str) -> str:
        sentences = text.split('. ')
        if sentences[-1].startswith("Let me know"):
            sentences = sentences[:-1]
            result = '. '.join(sentences)
            if result and not result.endswith('.'):
                result += '.'
            return result
        return text

    @staticmethod
    def extract_variables(prompt: str) -> Set[str]:
        pattern = r'{([^}]+)}'
        variables = re.findall(pattern, prompt)
        return set(variables)

    def find_free_floating_variables(self, prompt: str) -> List[str]:
        variable_usages = re.findall(r'\{\$[A-Z0-9_]+\}', prompt)

        free_floating_variables = []
        for variable in variable_usages:
            preceding_text = prompt[:prompt.index(variable)]
            open_tags = set()

            i = 0
            while i < len(preceding_text):
                if preceding_text[i] == '<':
                    if i + 1 < len(preceding_text) and preceding_text[
                        i + 1] == '/':
                        closing_tag = preceding_text[i + 2:].split('>', 1)[0]
                        open_tags.discard(closing_tag)
                        i += len(closing_tag) + 3
                    else:
                        opening_tag = preceding_text[i + 1:].split('>', 1)[0]
                        open_tags.add(opening_tag)
                        i += len(opening_tag) + 2
                else:
                    i += 1

            if not open_tags:
                free_floating_variables.append(variable)

        return free_floating_variables

    def remove_inapt_floating_variables(self, prompt: str) -> str:
        message = self.chat.chat(
            remove_floating_variables_prompt.replace("{$PROMPT}", prompt),
            chat_history=[]
        ).response
        return self.extract_between_tags("rewritten_prompt", message)[0]

    def generate_prompt(self, task: str, variables: List[str] = None) -> Tuple[
        str, Set[str]]:
        logger.info(f"Generating prompt for task: {task}")

        if variables is None:
            variables = []

        variable_string = "\n".join(
            "{$" + var.upper() + "}" for var in variables)
        logger.debug(f"Variable string: {variable_string}")

        prompt = self.metaprompt_template.replace("{{TASK}}", task)

        assistant_partial = "<Inputs>"
        if variable_string:
            assistant_partial += f"\n{variable_string}\n</Inputs>\n<Instructions Structure>"

        try:
            response = self.chat.chat(
                prompt,
                chat_history=[
                    ChatMessage(content=assistant_partial, role="assistant")]
            ).response
            logger.debug(f"Raw LLM response: {response}")

            extracted_prompt = self.extract_prompt(response)
            found_variables = self.extract_variables(response)

            # Handle floating variables
            floating_variables = self.find_free_floating_variables(
                extracted_prompt)
            if floating_variables:
                logger.info(f"Found floating variables: {floating_variables}")
                extracted_prompt = self.remove_inapt_floating_variables(
                    extracted_prompt)

            logger.info("Successfully generated prompt")
            return extracted_prompt, found_variables

        except Exception as e:
            logger.error(f"Error generating prompt: {str(e)}")
            raise

    def extract_prompt(self, metaprompt_response: str) -> str:
        between_tags = \
        self.extract_between_tags("Instructions", metaprompt_response)[0]
        cleaned_prompt = between_tags[:1000] + self.strip_last_sentence(
            self.remove_empty_tags(
                self.remove_empty_tags(between_tags[1000:]).strip()
            ).strip()
        )
        return cleaned_prompt

    def generate_answer(self, prompt: str,
                        variable_values: Optional[dict] = None) -> str:
        if variable_values:
            for var, value in variable_values.items():
                prompt = prompt.replace("{" + var + "}", value)

        try:
            response = self.chat.chat(prompt, chat_history=[]).response
            return response
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            raise