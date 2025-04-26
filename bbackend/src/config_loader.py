from dataclasses import dataclass
import json
from src.const import CONFIG_PATH


@dataclass
class Config:
    summarizer_model: str
    orchestrator_model: str
    image_description_model: str
    date_processor_model: str
    api_base_url: str
    timeout_seconds: int


def load_config() -> Config:
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)
    return Config(**config)
