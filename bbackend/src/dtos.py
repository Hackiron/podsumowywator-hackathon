from pydantic import BaseModel
from typing import List


class Message(BaseModel):
    username: str
    message: str


class SummaryRequest(BaseModel):
    messages: List[Message]
