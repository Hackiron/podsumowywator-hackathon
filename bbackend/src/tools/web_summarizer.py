from datetime import datetime
from agents import Agent, Runner, function_tool
from loguru import logger
from src.dtos import ConversationContext
from agents import RunContextWrapper
import requests
from src.config_loader import load_config, Config
from urllib.parse import urljoin
import os
from dotenv import load_dotenv
from firecrawl import AsyncFirecrawlApp
from src.prompts.web_summarizer_prompt import WEB_SUMMARIZER_PROMPT


async def _summarize_markdown(markdown_content: str, config: Config) -> str:
    """Summarize the given markdown content"""

    summarize_markdown_agent = Agent(
        name="Summarize Markdown",
        instructions=WEB_SUMMARIZER_PROMPT,
        model=config.web_summarizer_model,
    )

    agent_input = f"Input: {markdown_content}"
    logger.info(f"Summarize markdown agent input: {agent_input}")

    result = await Runner.run(
        summarize_markdown_agent,
        agent_input,
    )
    logger.info(f"Summarize markdown agent result: {result.final_output}")

    return markdown_content


async def _scrape_url_with_firecrawl(url: str) -> str:
    """Use Firecrawl to scrape the given URL and return markdown content"""
    try:
        app = AsyncFirecrawlApp()

        scrape_result = await app.scrape_url(url, formats=["markdown"])
        print(scrape_result.markdown)
        return scrape_result.markdown
    except Exception as e:
        logger.error(f"Error scraping URL with Firecrawl: {str(e)}")
        raise


@function_tool
async def summarize_webpage_content(
    wrapper_context: RunContextWrapper[ConversationContext],
    url: str,
) -> str:
    """
    Summarize a webpage content. This operation is slow and expensive, should be used only when necessary to answer the precise question.

    Args:
        url: The URL of the webpage to summarize.

    Returns:
        The webpage content summary.
    """
    logger.info(f"Scraping webpage: {url}")

    markdown_content = await _scrape_url_with_firecrawl(url)
    logger.info(f"Successfully scraped webpage: {url}")
    logger.info(f"Summarizing webpage: {url}")
    summary = await _summarize_markdown(markdown_content)
    logger.info(f"Successfully summarized webpage: {url}")
    return summary


if __name__ == "__main__":
    import asyncio
    import dotenv

    dotenv.load_dotenv()
    url = "https://www.acidcave.net/"
    asyncio.run(_scrape_url_with_firecrawl(url))
