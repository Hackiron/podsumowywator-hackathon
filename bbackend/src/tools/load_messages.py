from agents import function_tool
from src.dtos import Message
from loguru import logger


@function_tool
def load_messages(channel_id: str, start_date: str, end_date: str) -> list[Message]:
    """Load messages from a specified channel within a given date range.

    Args:
        channel_id (str): The unique identifier of the channel to load messages from.
        start_date (str): The start date in ISO format (YYYY-MM-DDTHH:MM:SS) to filter messages.
        end_date (str): The end date in ISO format (YYYY-MM-DDTHH:MM:SS) to filter messages.

    Returns:
        list[Message]: A list of messages from the channel within the date range.
    """
    logger.info(
        f"Loading messages from channel {channel_id} between {start_date} and {end_date}"
    )
    mocked_messages = [
        Message(username="John", message="Hello, how are you?"),
        Message(username="Jane", message="I'm good, thank you!"),
    ]
    return mocked_messages
