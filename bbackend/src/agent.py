from agents import Agent, Runner
from typing import Dict, Any
from src.config_loader import load_config

class SummaryAgent:
    def __init__(self):
        config = load_config()
        self.agent = Agent(
            name="SummaryAssistant",
            instructions="""You are a helpful assistant specialized in summarizing text content.
            You provide clear, concise, and accurate summaries while maintaining the key points
            of the original content.""",
            model=config.summarizer_model
        )
        
    async def get_summary(self, text: str) -> Dict[str, Any]:
        """
        Get a summary of the provided text using the agent.
        
        Args:
            text (str): The text to summarize
            
        Returns:
            Dict[str, Any]: A dictionary containing the summary and metadata
        """
        result = await Runner.run(
            self.agent,
            f"Please provide a concise summary of the following text:\n\n{text}"
        )
        
        return {
            "summary": result.final_output
        }
