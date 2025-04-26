from agents import RunContextWrapper, function_tool
from src.dtos import Message
from loguru import logger
import requests
from src.config_loader import load_config
from urllib.parse import urljoin
from src.memory import MessageMemory
from src.dtos import ConversationContext
from pydantic import ValidationError


def _load_messages_from_api(
    channel_id: str, start_date: str, end_date: str
) -> list[Message]:
    config = load_config()

    url = urljoin(config.api_base_url, "/matchenatinderze")

    params = {"channelId": channel_id, "startDate": start_date, "endDate": end_date}

    try:
        response = requests.get(url, params=params, timeout=config.timeout_seconds)
        response.raise_for_status()

        messages_data = response.json()

        return [
            Message(username=msg["username"], message=msg["message"])
            for msg in messages_data
        ]

    except ValidationError as e:
        logger.error(f"Pydantic validation error: {e.errors()}")
        raise
    except KeyError as e:
        logger.error(f"Missing required field in message data: {e}")
        raise ValueError(f"Message data missing required field: {e}")
    except requests.RequestException as e:
        logger.error(f"Failed to load messages from API: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Other error: {str(e)}")
        raise


def _load_mock_messages(
    channel_id: str, start_date: str, end_date: str
) -> list[Message]:
    """Load mock messages for testing purposes."""
    return [
        Message(username="John", message="Hello, how are you?"),
        Message(username="Jane", message="I'm good, thank you!"),
    ]


@function_tool
def load_messages(
    wrapper_context: RunContextWrapper[ConversationContext],
    channel_id: str,
    start_date: str,
    end_date: str,
) -> str:
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
    messages = _load_messages_from_api(channel_id, start_date, end_date)
    logger.info(f"Loaded {len(messages)} messages")

    # Store messages in memory
    messages_uuid = MessageMemory.store_messages(messages)

    return messages_uuid
