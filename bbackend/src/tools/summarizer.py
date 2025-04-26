from agents import Agent, Runner, function_tool
from src.prompts.summarizer_prompt import SUMMARIZER_PROMPT
from loguru import logger
from src.memory import MessageMemory
from src.dtos import Message, ConversationContext, Image
from agents import RunContextWrapper
from src.tools.summarizer_tools import SUMMARIZER_TOOLS


def _images_to_string(images: list[Image]) -> str:
    return "\n".join(
        [f"url: {img.url}\nextension: {img.extension}\n" for img in images]
    )


def _messages_to_string(messages: list[Message]) -> str:
    return "\n".join(
        [
            f"{msg.username}: {msg.message}\n{_images_to_string(msg.images)}\n"
            for msg in messages
        ]
    )


@function_tool
async def summarizer_agent_tool(
    wrapper_context: RunContextWrapper[ConversationContext],
    messages_uuid: str,
    query: str | None = None,
):
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
        model=wrapper_context.context.config.summarizer_model,
        tools=SUMMARIZER_TOOLS,
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
        context=wrapper_context.context,
    )

    logger.info(f"Summarizer agent result: {result.final_output}")
    return result.final_output
