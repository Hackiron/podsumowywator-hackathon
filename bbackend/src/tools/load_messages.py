from agents import function_tool
from src.dtos import Message
from loguru import logger
import requests
from src.config_loader import load_config
from urllib.parse import urljoin


def _load_messages_from_api(
    channel_id: str, start_date: str, end_date: str
) -> list[Message]:
    config = load_config()

    url = urljoin(config.api_base_url, "/matchenatinderze")

    params = {"channel_id": channel_id, "start_date": start_date, "end_date": end_date}

    try:
        response = requests.get(url, params=params, timeout=config.timeout_seconds)
        response.raise_for_status()

        messages_data = response.json()
        return [
            Message(username=msg["username"], message=msg["message"])
            for msg in messages_data
        ]
    except requests.RequestException as e:
        logger.error(f"Failed to load messages from API: {str(e)}")
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
    messages = _load_mock_messages(channel_id, start_date, end_date)
    return messages
