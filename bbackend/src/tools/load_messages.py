from agents import RunContextWrapper, function_tool
from src.tools.read_through_cache import ReadThroughCache
from src.dtos import Message
from loguru import logger
from src.config_loader import load_config
from urllib.parse import urljoin
from src.memory import MessageMemory
from src.dtos import ConversationContext

def create_load_messages(cache: ReadThroughCache):
    @function_tool
    def load_messages(channel_id: str, start_date: str, end_date: str) -> str:
        """Load messages from a specified channel within a given date range and store them in memory.

        Args:
            channel_id (str): The unique identifier of the channel to load messages from.
            start_date (str): The start date in ISO format (YYYY-MM-DDTHH:MM:SS) to filter messages.
            end_date (str): The end date in ISO format (YYYY-MM-DDTHH:MM:SS) to filter messages.

        Returns:
            str: UUID for retrieving the messages later
        """
        logger.info(
            f"Loading messages from channel {channel_id} between {start_date} and {end_date}"
        )
        messages = cache.load(channel_id, start_date, end_date)
        logger.info(f"Loaded {len(messages)} messages")

        # Store messages in memory
        messages_uuid = MessageMemory.store_messages(messages)

        return messages_uuid

    return load_messages
