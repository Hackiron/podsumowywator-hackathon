import uuid
from src.dtos import Message
from loguru import logger


class MessageMemory:
    """In-memory storage for messages that need to be shared between tools."""

    _messages: dict[str, list[Message]] = {}

    @classmethod
    def store_messages(cls, messages: list[Message]) -> str:
        messages_uuid = str(uuid.uuid4())
        cls._messages[messages_uuid] = messages
        logger.info(f"Stored {len(messages)} messages with UUID: {messages_uuid}")
        return messages_uuid

    @classmethod
    def get_messages(cls, messages_uuid: str) -> list[Message]:
        try:
            messages = cls._messages[messages_uuid]
            logger.info(
                f"Retrieved {len(messages)} messages with UUID: {messages_uuid}"
            )
            return messages
        except KeyError:
            logger.error(f"No messages found with UUID: {messages_uuid}")
            raise KeyError(f"No messages found with UUID: {messages_uuid}")

    @classmethod
    def delete_messages(cls, messages_uuid: str) -> None:
        if messages_uuid in cls._messages:
            del cls._messages[messages_uuid]
            logger.info(f"Deleted messages with UUID: {messages_uuid}")
        else:
            logger.warning(
                f"Attempted to delete non-existent messages with UUID: {messages_uuid}"
            )
