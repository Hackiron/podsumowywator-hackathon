from agents import Agent, Runner, function_tool
from src.prompts.image_description_prompt import IMAGE_DESCRIPTION_PROMPT
from loguru import logger
from src.dtos import ConversationContext
from agents import RunContextWrapper


@function_tool
async def describe_image(
    wrapper_context: RunContextWrapper[ConversationContext], image_url: str
) -> str:
    """
    Describe an image for given URL. This operation is slow and expensive, should be used only when necessary to answer the question.

    Args:
        image_url: The URL of the image to describe.

    Returns:
        A description of the image.
    """
    logger.info(f"Describing image: {image_url}")
    image_description_agent = Agent(
        name="Image Description",
        instructions=IMAGE_DESCRIPTION_PROMPT,
        model=wrapper_context.context.config.image_description_model,
    )

    result = await Runner.run(
        image_description_agent,
        image_url,
    )

    logger.info(f"Image description: {result.final_output}")
    return result.final_output
