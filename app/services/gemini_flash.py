from ..config import Settings

from ..schemas import (
    OutlineResponse,
    PromptRequest,
    PanelOutline,
)


def _clean_text(text: str) -> str:
    return " ".join(text.strip().split())


def _split_story_events(story_prompt: str) -> list[str]:
    """
    Break the user's story into meaningful events.
    These events become the foundation for panel continuity.
    """

    text = _clean_text(story_prompt)

    if not text:
        return []

    # First try normal sentences.
    sentences = [
        part.strip()
        for part in text.replace("!", ".")
        .replace("?", ".")
        .split(".")
        if part.strip()
    ]

    if len(sentences) >= 2:
        return sentences

    # If the user entered one long sentence,
    # split it at common story connectors.
    connectors = [
        " and then ",
        " then ",
        " after that ",
        " when ",
        " while ",
        " but ",
        " because ",
        " so ",
        " until ",
        " before ",
        " after ",
    ]

    parts = [text]

    for connector in connectors:
        new_parts = []

        for part in parts:
            pieces = part.split(connector)

            if len(pieces) == 1:
                new_parts.append(part)
            else:
                new_parts.extend(
                    piece.strip()
                    for piece in pieces
                    if piece.strip()
                )

        parts = new_parts

    return parts


def _build_story_arc(
    events: list[str],
    panel_count: int
) -> list[str]:

    if not events:
        return []

    # Exactly the requested number of events.
    if len(events) == panel_count:
        return events

    # If there are fewer events than panels,
    # distribute the existing story naturally.
    if len(events) < panel_count:

        result = list(events)

        while len(result) < panel_count:

            if len(result) == 1:
                result.append(
                    "The main character reacts to the situation "
                    "and decides what to do next."
                )
            else:
                result.insert(
                    -1,
                    "The main character continues the action "
                    "from the previous event and moves closer "
                    "to the goal."
                )

        return result[:panel_count]

    # If there are more events than panels,
    # combine nearby events while preserving order.
    result = []

    total = len(events)

    for panel_index in range(panel_count):

        start = round(
            panel_index * total / panel_count
        )

        end = round(
            (panel_index + 1) * total / panel_count
        )

        group = events[start:end]

        if not group:
            group = [
                events[
                    min(start, total - 1)
                ]
            ]

        result.append(
            " ".join(group)
        )

    return result


def _make_title(
    event: str,
    panel_number: int,
    panel_count: int
) -> str:

    text = event.lower()

    if panel_number == 1:
        return "The Beginning"

    if any(
        word in text
        for word in [
            "problem",
            "danger",
            "dark",
            "attack",
            "storm",
            "missing",
            "lost",
            "disappear",
            "disappeared",
        ]
    ):
        return "The Trouble Begins"

    if any(
        word in text
        for word in [
            "enter",
            "enters",
            "arrive",
            "arrives",
            "discover",
            "discovers",
            "find",
            "finds",
        ]
    ):
        return "The Discovery"

    if any(
        word in text
        for word in [
            "follow",
            "follows",
            "search",
            "searches",
            "look",
            "looks",
            "travel",
            "travels",
            "go",
            "goes",
        ]
    ):
        return "Following the Clue"

    if any(
        word in text
        for word in [
            "fight",
            "fights",
            "battle",
            "challenge",
            "obstacle",
            "guardian",
            "dangerous",
        ]
    ):
        return "The Challenge"

    if any(
        word in text
        for word in [
            "solve",
            "solves",
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
        return "The Turning Point"

    if any(
        word in text
        for word in [
            "finally",
            "returns",
            "return",
            "restores",
            "complete",
            "completed",
            "safe",
            "success",
            "wins",
        ]
    ):
        return "Hope Restored"

    if panel_number == panel_count:
        return "The Resolution"

    return "The Next Step"


def _make_scene_description(
    character: str,
    setting: str,
    event: str,
    previous_event: str | None
) -> str:

    if previous_event:

        return (
            f"Continuing directly from the previous panel, "
            f"{character} remains in {setting}. "
            f"The previous event was: {previous_event}. "
            f"Now the story moves forward as {event}."
        )

    return (
        f"{character} begins the story in {setting}. "
        f"The opening story event is: {event}."
    )


def _make_image_prompt(
    request: PromptRequest,
    event: str,
    scene_description: str,
    previous_event: str | None
) -> str:

    continuity = ""

    if previous_event:
        continuity = (
            f"The previous panel showed: {previous_event}. "
            "Continue naturally from that moment. "
        )

    return (
        f"Create a comic book panel for the story. "
        f"Main character: {request.character_name}. "
        f"Setting: {request.setting}. "
        f"Exact event that must be shown: {event}. "
        f"{continuity}"
        f"Scene continuity: {scene_description} "
        "Show the exact action, characters, important objects, "
        "location, and emotional situation described by the story. "
        "Do not replace the event with a generic adventure scene. "
        "Keep the main character's appearance consistent with "
        "previous panels. "
        f"Art style: {request.art_style}. "
        f"Tone: {request.tone}. "
        f"Audience: {request.audience}. "
        "Clear visual storytelling, expressive poses, "
        "detailed environment, strong composition, "
        "family-friendly comic illustration."
    )


def generate_outline(
    request: PromptRequest,
    settings: Settings
) -> OutlineResponse:

    character = request.character_name
    setting = request.setting

    story_prompt = _clean_text(
        request.story_prompt
    )

    events = _split_story_events(
        story_prompt
    )

    story_arc = _build_story_arc(
        events,
        request.panel_count
    )

    if not story_arc:

        story_arc = [
            (
                f"{character} begins an adventure in "
                f"{setting} and discovers that something "
                "important is about to happen."
            )
        ]

    panels = []

    previous_event = None

    for index, event in enumerate(story_arc):

        panel_number = index + 1

        title = _make_title(
            event,
            panel_number,
            len(story_arc)
        )

        scene_description = _make_scene_description(
            character,
            setting,
            event,
            previous_event
        )

        image_prompt = _make_image_prompt(
            request,
            event,
            scene_description,
            previous_event
        )

        panels.append(
            PanelOutline(
                panel_number=panel_number,
                title=title,
                scene_description=scene_description,
                image_prompt=image_prompt,
            )
        )

        previous_event = event

    return OutlineResponse(
        panels=panels
    )