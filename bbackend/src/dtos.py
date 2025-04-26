from pydantic import BaseModel, Field
from src.config_loader import Config


class Image(BaseModel):
    url: str
    extension: str


class Message(BaseModel):
    username: str
    message: str
    images: list[Image]
    created_at: str = Field(alias="createdAt")


class SummaryRequest(BaseModel):
    messages: list[Message]
    channel_id: str = Field(alias="channelId")
    thread_id: str = Field(alias="threadId")


class ConversationContext(BaseModel):
    current_date: str
    config: Config
