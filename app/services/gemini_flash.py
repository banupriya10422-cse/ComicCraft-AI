from google import genai
from google.genai import types

from ..config import Settings
from ..schemas import (
    OutlineResponse,
    PromptRequest,
)


def generate_outline(
    request: PromptRequest,
    settings: Settings
) -> OutlineResponse:

    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. "
            "Add your Gemini API key to the .env file."
        )

    client = genai.Client(
        api_key=settings.gemini_api_key
    )

    prompt = f"""
Create a cohesive {settings.panel_count}-panel comic outline.

USER STORY IDEA:
{request.story_prompt}

MAIN CHARACTER:
{request.character_name}

SETTING:
{request.setting}

TONE:
{request.tone}

ART STYLE:
{request.art_style}

IMPORTANT REQUIREMENTS:

1. Return exactly {settings.panel_count} panels.
2. Keep the same main character throughout the entire story.
3. The story must have a clear beginning, middle and ending.
4. Give every panel a short title.
5. scene_description must explain what happens in the panel.
6. image_prompt must describe the visual scene in detail.
7. Do not put dialogue inside image_prompt.
8. Keep the story family-friendly.
9. Make the panels visually different but narratively connected.
"""

    response = client.models.generate_content(
        model=settings.gemini_outline_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=OutlineResponse,
        )
    )

    if not response.parsed:
        raise RuntimeError(
            "Gemini returned an empty comic outline."
        )

    outline = response.parsed

    if len(outline.panels) != settings.panel_count:
        raise RuntimeError(
            f"Gemini generated {len(outline.panels)} panels "
            f"but {settings.panel_count} were required."
        )

    return outline