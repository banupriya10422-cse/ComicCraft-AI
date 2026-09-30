from google import genai
from google.genai import types

from ..config import Settings
from ..schemas import (
    OutlineResponse,
    PromptRequest,
    PanelOutline,
    PanelStory,
    StoryResponse,
)


def generate_story(
    request: PromptRequest,
    outline: OutlineResponse,
    settings: Settings
) -> StoryResponse:

    panels = []

    for panel in outline.panels:
        panels.append(
            PanelStory(
                panel_number=panel.panel_number,
                title=panel.title,
                scene_description=panel.scene_description,
                caption=panel.title,
                narration=panel.scene_description,
                dialogue=[],
                image_prompt=panel.image_prompt,
            )
        )

    return StoryResponse(panels=panels)