from datetime import datetime
from agents import Agent, Runner, function_tool
from src.prompts.image_description_prompt import IMAGE_DESCRIPTION_PROMPT
from loguru import logger
from src.dtos import ConversationContext
from agents import RunContextWrapper
import requests
from src.config_loader import load_config, Config
from urllib.parse import urljoin
from openai import OpenAI
import base64
from pathlib import Path
from src.const import BBACKEND_DIR


async def _get_image_mock(image_url: str, config: Config) -> str:
    """Mock function that loads example.jpg instead of making an API call"""
    try:
        example_path = BBACKEND_DIR / "examples/example.jpg"

        with open(example_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded_string

    except Exception as e:
        logger.error(f"Error loading mock image: {str(e)}")
        raise


async def _get_image(image_url: str, config: Config) -> str:
    endpoint = urljoin(config.api_base_url, "/nudes")

    try:
        response = requests.post(
            endpoint, json={"url": image_url}, timeout=config.timeout_seconds
        )
        response.raise_for_status()
        result = response.json()
        return result["base64"]
    except requests.RequestException as e:
        logger.error(f"Failed to send data to nudes API: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Other error: {str(e)}")
        raise


@function_tool
async def describe_image(
    wrapper_context: RunContextWrapper[ConversationContext],
    image_url: str,
    image_extension: str,
    question: str | None = None,
) -> str:
    """
    Describe an image for given URL. This operation should be used only when necessary to answer the precise question.

    Args:
        image_url: The URL of the image to describe.
        image_extension: The extension of the image.
        question: The question to the image that will focus the model attention when describing the image. If None, the image will be described in general.

    Returns:
        A description of the image.
    """
    if question is None:
        question = "Describe the image"

    logger.info(f"Describing image: {image_url} with question: {question}")

    # base64_image = await _get_image_mock(image_url, wrapper_context.context.config)
    base64_image = await _get_image(image_url, wrapper_context.context.config)

    client = OpenAI()
    response = client.responses.create(
        model=wrapper_context.context.config.image_description_model,
        instructions=IMAGE_DESCRIPTION_PROMPT,
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": question},
                    {
                        "type": "input_image",
                        "image_url": f"data:image/{image_extension};base64,{base64_image}",
                    },
                ],
            }
        ],
    )

    final_output = response.output_text

    # image_description_agent = Agent(
    #     name="Image Description",
    #     instructions=IMAGE_DESCRIPTION_PROMPT,
    #     model=wrapper_context.context.config.image_description_model,
    # )
    # result = await Runner.run(
    #     image_description_agent,
    #     image_url,
    # )

    logger.info(f"Image description: {final_output}")
    return final_output


if __name__ == "__main__":
    import asyncio
    import dotenv

    dotenv.load_dotenv()
    config = load_config()
    url = "https://cdn.discordapp.com/attachments/799677088609075212/1359422438642946120/rn_image_picker_lib_temp_faed8f7b-50bd-4480-a7ae-ac060036a547.jpg?ex=680dd5ce&is=680c844e&hm=b528422dc083bbf31752d5c22eef532e5bd95239fae2d5446b60d7b58ef3ef4e&"
    extension = "jpeg"
    asyncio.run(_get_image(url, config))
