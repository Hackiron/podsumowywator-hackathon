from agents import Agent, Runner, function_tool
from src.prompt import SUMMARIZER_PROMPT
from loguru import logger


@function_tool
async def summarizer_agent_tool(messages: str):
    """
    A tool that summarizes the messages.

    Args:
        messages: The messages to summarize as a string.

    Returns:
        The summary of the messages.
    """
    summarizer_agent = Agent(
        name="Summarizer",
        instructions=SUMMARIZER_PROMPT,
        model="gpt-4.1-mini",
    )

    logger.info(f"Tool Summarizing messages: {messages}")

    result = await Runner.run(
        summarizer_agent,
        messages,
    )

    return result.final_output
