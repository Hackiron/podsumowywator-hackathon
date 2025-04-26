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
from firecrawl import FirecrawlApp
from src.prompts.web_summarizer_prompt import WEB_SUMMARIZER_PROMPT


async def _summarize_markdown(markdown_content: str, config: Config) -> str:
    """Summarize the given markdown content"""

    summarize_markdown_agent = Agent(
        name="Summarize Markdown",
        instructions=WEB_SUMMARIZER_PROMPT,
        model=config.web_summarizer_model,
    )

    agent_input = f"Input: {markdown_content}"

    result = await Runner.run(
        summarize_markdown_agent,
        agent_input,
    )
    logger.info(f"Summarize markdown agent result: {result.final_output}")

    return result.final_output


async def _scrape_url_with_firecrawl(url: str) -> str:
    """Use Firecrawl to scrape the given URL and return markdown content"""
    try:
        app = FirecrawlApp()

        scrape_result = app.scrape_url(url, formats=["markdown"])
        return scrape_result.markdown
    except Exception as e:
        logger.error(f"Error scraping URL with Firecrawl: {str(e)}")
        raise


@function_tool
async def summarize_webpage_content(
    wrapper_context: RunContextWrapper[ConversationContext],
    page_link: str,
) -> str:
    """
    Summarize a webpage content. This operation should be used only when necessary to answer the precise question.

    Args:
        page_link: The link of the webpage to summarize. Often starts with http or https.

    Returns:
        The webpage content summary.
    """
    logger.info(f"Scraping webpage: {page_link}")

    markdown_content = await _scrape_url_with_firecrawl(page_link)
    logger.info(f"Successfully scraped webpage: {page_link}")
    logger.info(f"Summarizing webpage: {page_link}")
    summary = await _summarize_markdown(
        markdown_content, wrapper_context.context.config
    )
    logger.info(f"Successfully summarized webpage: {page_link}")
    return summary


async def main_t():
    config = load_config()
    markdown_content = await _scrape_url_with_firecrawl("https://www.acidcave.net/")
    summary = await _summarize_markdown(markdown_content, config)


if __name__ == "__main__":
    import asyncio
    import dotenv

    dotenv.load_dotenv()
    asyncio.run(main_t())
