from agents import Agent, Runner
from typing import Any
from src.tools.read_through_cache import ReadThroughCache
from src.config_loader import load_config
from src.tools.orchestrator_tools import get_orchestrator_tools
from src.dtos import SummaryRequest, ConversationContext
from src.prompts.orchestrator_prompt import ORCHESTRATOR_PROMPT
from loguru import logger
from datetime import datetime


class OrchestratorAgent:
    def __init__(self, cache: ReadThroughCache):
        self.config = load_config()
        self.agent = Agent(
            name="Orchestrator",
            instructions=ORCHESTRATOR_PROMPT.format(
                main_language=self.config.main_language
            ),
            model=self.config.orchestrator_model,
            tools=get_orchestrator_tools(cache),
        )

    async def get_summary(self, summary_request: SummaryRequest) -> dict[str, Any]:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        channel_id = summary_request.channel_id
        thread_id = summary_request.thread_id

        conversation_context = ConversationContext(
            current_date=current_time,
            config=self.config,
        )
        logger.info(f"Conversation context: {conversation_context}")

        messages_string = "\n".join(
            [
                f"{message.created_at} {message.username}: {message.message}"
                for message in summary_request.messages
            ]
        )
        logger.info(f"Orchestrator agent input: {messages_string}")
        result = await Runner.run(
            starting_agent=self.agent,
            input=f"Thread ID: {thread_id}\nChannel ID: {channel_id}\nCurrent time: {current_time}\nMessages: {messages_string}",
            context=conversation_context,
        )
        logger.info(f"Orchestrator agent result: {result.final_output}")
        return {"message": result.final_output}
