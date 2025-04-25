from agents import Agent, Runner
from typing import Dict, Any
from src.config_loader import load_config
from src.tools.tools import TOOLS
from src.dtos import SummaryRequest
from src.prompt import SUMMARIZER_PROMPT

class SummaryAgent:
    def __init__(self):
        config = load_config()
        self.agent = Agent(
            name="SummaryAssistant",
            instructions=SUMMARIZER_PROMPT,
            model=config.summarizer_model,
            tools=TOOLS,
        )

    async def get_summary(self, summary_request: SummaryRequest) -> Dict[str, Any]:
        text = "\n".join(
            [
                f"{message.username}: {message.message}"
                for message in summary_request.messages
            ]
        )
        result = await Runner.run(
            self.agent,
            f"Please provide a concise summary of the following text:\n\n{text}",
        )

        return {"summary": result.final_output}
