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


def generate_outline(
    request: PromptRequest,
    settings: Settings
) -> OutlineResponse:

    panels = []

    scenes = [
        (
            "A New Beginning",
            f"{request.character_name} begins an adventure in {request.setting}.",
        ),
        (
            "The Challenge",
            f"{request.character_name} discovers an unexpected challenge.",
        ),
        (
            "A Clever Idea",
            f"{request.character_name} thinks of a creative way to solve the problem.",
        ),
        (
            "The Big Moment",
            f"{request.character_name} puts the plan into action.",
        ),
        (
            "A Happy Ending",
            f"{request.character_name} succeeds and finishes the adventure on a positive note.",
        ),
    ]

    for i, (title, scene) in enumerate(
        scenes[:settings.panel_count],
        start=1
    ):
        panels.append(
            PanelOutline(
                panel_number=i,
                title=title,
                scene_description=scene,
                image_prompt=(
                    f"{request.character_name} in {request.setting}, "
                    f"{scene} "
                    f"Style: {request.art_style}. "
                    f"Tone: {request.tone}. "
                    "Family-friendly comic illustration."
                ),
            )
        )

    return OutlineResponse(panels=panels)
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