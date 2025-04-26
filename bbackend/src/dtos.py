from pydantic import BaseModel, Field
from src.config_loader import Config


class Message(BaseModel):
    username: str
    message: str
    images: list[str]


class SummaryRequest(BaseModel):
    messages: list[Message]
    channel_id: str = Field(alias="channelId")
    thread_id: str = Field(alias="threadId")


class ConversationContext(BaseModel):
    current_date: str
    config: Config
