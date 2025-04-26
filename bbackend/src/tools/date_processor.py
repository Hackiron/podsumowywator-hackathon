from agents import Agent, Runner, function_tool
from src.prompts.date_processor_prompt import DATE_PROCESSOR_PROMPT
from loguru import logger
from src.memory import MessageMemory
from src.dtos import ConversationContext
from agents import RunContextWrapper


@function_tool
async def date_processor_agent_tool(
    wrapper_context: RunContextWrapper[ConversationContext], thread_id: str
) -> str | None:
    """
    Check whether the last user message contains a date range and return it in ISO format.

    Args:
        thread_id: The id of the thread to check.
    Returns:
        The date range in ISO format or None if no date range is found.
    """
    logger.info(f"Using date processor tool for thread {thread_id}")
    messages = MessageMemory.get_thread(thread_id)

    if len(messages) == 0:
        return None

    last_message = messages[-1]
    date_processor_agent = Agent(
        name="Date Processor",
        instructions=DATE_PROCESSOR_PROMPT,
        model=wrapper_context.context.config.date_processor_model,
    )

    agent_input = f"Current date: {wrapper_context.context.current_date}\nInput: {last_message.message}"
    logger.info(f"Date processor agent input: {agent_input}")

    result = await Runner.run(
        date_processor_agent,
        agent_input,
    )
    logger.info(f"Date processor agent result: {result.final_output}")

    return result.final_output
