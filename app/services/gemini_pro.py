from google import genai
from google.genai import types

from ..config import Settings
from ..schemas import (
    OutlineResponse,
    PromptRequest,
    StoryResponse,
)


def generate_story(
    request: PromptRequest,
    outline: OutlineResponse,
    settings: Settings
) -> StoryResponse:

    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. "
            "Add your Gemini API key to the .env file."
        )

    client = genai.Client(
        api_key=settings.gemini_api_key
    )

    outline_json = outline.model_dump_json(
        indent=2
    )

    prompt = f"""
Expand the following comic outline into a complete
panel-by-panel comic script.

MAIN CHARACTER:
{request.character_name}

SETTING:
{request.setting}

TONE:
{request.tone}

ART STYLE:
{request.art_style}

ORIGINAL STORY:
{request.story_prompt}

OUTLINE:
{outline_json}

REQUIREMENTS:

1. Keep exactly {settings.panel_count} panels.
2. Keep the same character and story continuity.
3. Do not change the order of the panels.
4. caption should be a short cinematic/environment caption.
5. narration should explain the important action or emotion.
6. dialogue should contain 0 to 3 short spoken lines.
7. image_prompt should be detailed enough for an image model.
8. Do not place dialogue text inside image_prompt.
9. Keep the comic family-friendly.
10. Make the final panel feel like a meaningful conclusion.
"""

    response = client.models.generate_content(
        model=settings.gemini_story_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=...,
        )
    )

    if not response.parsed:
        raise RuntimeError(
            "Gemini returned an empty comic story."
        )

    story = response.parsed

    if len(story.panels) != settings.panel_count:
        raise RuntimeError(
            f"Gemini generated {len(story.panels)} story panels "
            f"but {settings.panel_count} were required."
        )

    return story