from agents import Agent, Runner
from typing import Any
from src.config_loader import load_config
from src.tools.tools import TOOLS
from src.dtos import SummaryRequest
from src.prompts.orchestrator_prompt import ORCHESTRATOR_PROMPT
from loguru import logger
from datetime import datetime


class OrchestratorAgent:
    def __init__(self):
        config = load_config()
        self.agent = Agent(
            name="Orchestrator",
            instructions=ORCHESTRATOR_PROMPT,
            model=config.orchestrator_model,
            tools=TOOLS,
        )

    async def get_summary(self, summary_request: SummaryRequest) -> dict[str, Any]:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        channel_id = summary_request.channel_id
        messages_string = "\n".join(
            [
                f"{message.username}: {message.message}"
                for message in summary_request.messages
            ]
        )
        logger.info(f"Orchestrator agent input: {messages_string}")
        result = await Runner.run(
            self.agent,
            f"Channel ID: {channel_id}\Current time: {current_time}\nMessages: {messages_string}",
        )
        logger.info(f"Orchestrator agent result: {result.final_output}")
        return {"message": result.final_output}
