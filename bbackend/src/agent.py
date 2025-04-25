from agents import Agent, Runner
from typing import Any
from src.config_loader import load_config
from src.tools.tools import TOOLS
from src.dtos import SummaryRequest
from src.prompt import ORCHESTRATOR_PROMPT


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
        text = "\n".join(
            [
                f"{message.username}: {message.message}"
                for message in summary_request.messages
            ]
        )
        result = await Runner.run(
            self.agent,
            f"{text}",
        )

        return {"summary": result.final_output}
