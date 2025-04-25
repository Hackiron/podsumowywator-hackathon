from dataclasses import dataclass
import json
from src.const import CONFIG_PATH


@dataclass
class Config:
    summarizer_model: str
    message_loader_model: str


def load_config() -> Config:
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)
    return Config(**config)
