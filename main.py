import logging
from typing import Optional

from config_manager import ConfigManager
from llm_manager import LLMManager
from prompt_generator import PromptGenerator


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def get_user_input() -> tuple[str, list[str]]:
    """Get task, input text, and variables from user"""
    task = input("Enter your task: ")


    variables = []
    if input("Do you want to specify variables? (y/n): ").lower() == 'y':
        logger.info("Enter variable names (empty line to finish):")
        while True:
            var = input("> ")
            if not var:
                break
            variables.append(var)

    return task, variables


def get_variable_values(variables: set[str]) -> dict:
    """Get values for variables from user"""
    variable_values = {}
    for variable in variables:
        value = input(f"Enter value for variable {variable}: ")
        variable_values[variable] = value
    return variable_values


def main():

    try:
        # Configure LLM
        config_manager = ConfigManager()
        provider, config = config_manager.configure_llm()

        chat_engine = LLMManager.create_llm(provider, config)

        # Create prompt generator
        generator = PromptGenerator(chat_engine)

        # Get user input
        task, variables = get_user_input()

        # Generate prompt
        result, found_variables = generator.generate_prompt(task, variables)
        logger.info("\nGenerated Prompt:\n%s", result)

        # Ask if user wants to generate an answer
        if input(
            "\nDo you want to generate an answer with this prompt? (y/n): ").lower() == 'y':
            variable_values = None
            if found_variables:
                logger.info(
                    "\nPrompt contains variables. Please provide values:")
                variable_values = get_variable_values(found_variables)

            answer = generator.generate_answer(result, variable_values)
            logger.info("\nGenerated Answer:\n%s", answer)

    except Exception as e:
        logger.error("Error in prompt generation: %s", str(e))
        return 1

    return 0


if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger(__name__)
    exit(main())