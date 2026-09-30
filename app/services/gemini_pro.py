from ..config import Settings

from ..schemas import (
    OutlineResponse,
    PromptRequest,
    PanelStory,
    StoryResponse,
)


def _extract_event(
    scene_description: str
) -> str:
    """
    Extract the exact current story event
    from the outline scene description.
    """

    marker = (
        "The story moves forward as "
    )

    if marker in scene_description:
        event = scene_description.split(
            marker,
            1
        )[1].strip()

        return event.rstrip(".")

    marker = (
        "The opening story event is: "
    )

    if marker in scene_description:
        event = scene_description.split(
            marker,
            1
        )[1].strip()

        return event.rstrip(".")

    return scene_description.strip()


def _make_narration(
    request: PromptRequest,
    event: str,
    scene_description: str,
) -> str:

    character = request.character_name
    length = request.narration_length
    audience = request.audience

    # SHORT narration
    if length == "Short":
        return f"{event}."

    # DETAILED narration
    if length == "Detailed":

        if audience == "Children":
            return (
                f"{event}. "
                f"{character} sees what is happening "
                "and reacts to the situation."
            )

        if audience == "Young Readers":
            return (
                f"{event}. "
                f"{character} realizes that this moment "
                "is important and responds to what is happening."
            )

        if audience == "Adults":
            return (
                f"{event}. "
                f"{character} understands the significance "
                "of the moment and considers what to do next."
            )

        return (
            f"{event}. "
            f"{character} recognizes what is happening "
            "and responds to the situation."
        )

    # NORMAL narration
    if audience == "Children":
        return (
            f"{event}. "
            f"{character} reacts to what is happening."
        )

    if audience == "Young Readers":
        return (
            f"{event}. "
            f"{character} realizes that something important "
            "is happening and responds."
        )

    if audience == "Adults":
        return (
            f"{event}. "
            f"{character} understands what is happening "
            "and decides how to respond."
        )

    return (
        f"{event}. "
        f"{character} responds to what is happening "
        "and the story moves forward."
    )


def _make_dialogue(
    request: PromptRequest,
    event: str,
    panel_number: int,
    panel_count: int,
) -> list[str]:

    character = request.character_name
    text = event.lower()

    # Missing / lost object
    if any(
        word in text
        for word in [
            "missing",
            "lost",
            "gone",
            "disappear",
            "disappeared",
        ]
    ):

        if "page" in text:
            return [
                f"{character}: The final page is missing. "
                "Where could it have gone?"
            ]

        if "book" in text:
            return [
                f"{character}: Something is missing "
                "from the book."
            ]

        return [
            f"{character}: Something important is missing. "
            "We need to find it."
        ]

    # Discovery
    if any(
        word in text
        for word in [
            "discover",
            "discovers",
            "find",
            "finds",
            "found",
        ]
    ):

        return [
            f"{character}: I found it! "
            "This must be what we were looking for."
        ]

    # Entering / arriving
    if any(
        word in text
        for word in [
            "enter",
            "enters",
            "arrive",
            "arrives",
        ]
    ):

        if "library" in text:
            return [
                f"{character}: A hidden library! "
                "What secrets are waiting inside?"
            ]

        return [
            f"{character}: I wonder what "
            "we will discover here."
        ]

    # Following / searching
    if any(
        word in text
        for word in [
            "follow",
            "follows",
            "trail",
            "search",
            "searches",
            "look",
            "looks",
        ]
    ):

        return [
            f"{character}: Let's follow the clue "
            "and see where it leads."
        ]

    # Danger / challenge
    if any(
        word in text
        for word in [
            "danger",
            "dangerous",
            "fight",
            "fights",
            "battle",
            "challenge",
            "guardian",
            "obstacle",
            "storm",
        ]
    ):

        return [
            f"{character}: We have to face this "
            "and keep moving forward."
        ]

    # Saving / helping / protecting
    if any(
        word in text
        for word in [
            "save",
            "saves",
            "rescue",
            "rescues",
            "protect",
            "protects",
            "help",
            "helps",
        ]
    ):

        return [
            f"{character}: We have to help "
            "before it is too late."
        ]

    # Final panel
    if panel_number == panel_count:
        return [
            f"{character}: We did it together. "
            "Our story has a happy ending!"
        ]

    # First panel
    if panel_number == 1:
        return [
            f"{character}: Something is about to happen."
        ]

    # Safe fallback
    return [
        f"{character}: We need to figure out "
        "what to do next."
    ]


def generate_story(
    request: PromptRequest,
    outline: OutlineResponse,
    settings: Settings
) -> StoryResponse:

    panels = []

    panel_count = len(
        outline.panels
    )

    for panel in outline.panels:

        event = _extract_event(
            panel.scene_description
        )

        narration = _make_narration(
            request,
            event,
            panel.scene_description,
        )

        dialogue = _make_dialogue(
            request,
            event,
            panel.panel_number,
            panel_count,
        )

        panels.append(
            PanelStory(
                panel_number=panel.panel_number,
                title=panel.title,
                scene_description=panel.scene_description,
                caption=panel.title,
                narration=narration,
                dialogue=dialogue,
                image_prompt=panel.image_prompt,
            )
        )

    return StoryResponse(
        panels=panels
    )