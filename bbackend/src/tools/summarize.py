from agents import Agent, Runner, function_tool
from src.prompt import SUMMARIZER_PROMPT
from loguru import logger
from src.memory import MessageMemory
from src.dtos import Message


def _messages_to_string(messages: list[Message]) -> str:
    return "\n".join([f"{msg.username}: {msg.message}" for msg in messages])


@function_tool
async def summarizer_agent_tool(messages_uuid: str):
    """
    A tool that summarizes the messages.

    Args:
        messages_uuid: The uuid of the messages to summarize.

    Returns:
        The summary of the messages.
    """
    # Retrieve messages from memory
    messages = MessageMemory.get_messages(messages_uuid)

    summarizer_agent = Agent(
        name="Summarizer",
        instructions=SUMMARIZER_PROMPT,
        model="gpt-4.1-mini",
    )

    messages_string = _messages_to_string(messages)
    logger.info(f"Tool Summarizing messages: {messages_string}")

    result = await Runner.run(
        summarizer_agent,
        messages_string,
    )

    logger.info(f"Summarizer agent result: {result.final_output}")

    return result.final_output
