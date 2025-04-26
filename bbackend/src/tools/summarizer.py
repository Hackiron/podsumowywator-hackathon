from agents import Agent, Runner, function_tool
from src.prompts.summarizer_prompt import SUMMARIZER_PROMPT
from loguru import logger
from src.memory import MessageMemory
from src.dtos import Message


def _messages_to_string(messages: list[Message]) -> str:
    return "\n".join([f"{msg.username}: {msg.message}" for msg in messages])


@function_tool
async def summarizer_agent_tool(messages_uuid: str, query: str | None = None):
    """
    A tool that summarizes the messages and answers to the query.
    It works on the messages that are stored in the memory by the load_messages tool.

    Args:
        messages_uuid: The uuid of the messages to summarize previously loaded by load_messages tool.
        query: The query that the summarizer should answer to. If None, will summarize the conversation.
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
    if query is None:
        query = "Summarize the conversation"

    logger.info(f"Summarizer tool query: {query}")
    logger.info(f"Summarizer tool messages: {messages_string}")

    input_text = f"Messages:\n{messages_string}\n\nQuery: {query}"

    result = await Runner.run(
        summarizer_agent,
        input_text,
    )

    logger.info(f"Summarizer agent result: {result.final_output}")
    return result.final_output
