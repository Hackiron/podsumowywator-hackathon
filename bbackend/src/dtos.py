from pydantic import BaseModel, Field


class Message(BaseModel):
    username: str
    message: str


class SummaryRequest(BaseModel):
    messages: list[Message]
    channel_id: str = Field(alias="channelId")
    thread_id: str = Field(alias="threadId")
