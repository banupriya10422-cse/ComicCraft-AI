from pathlib import Path

from ..schemas import (
    ComicPanel,
    StoryResponse,
)


def build_comic_layout(
    story: StoryResponse,
    image_paths: list[str],
    static_root: Path
) -> list[ComicPanel]:

    if len(story.panels) != len(image_paths):
        raise ValueError(
            "Every comic panel must have exactly one image."
        )

    layout = []

    for panel, image_path in zip(
        story.panels,
        image_paths
    ):

        path = Path(image_path)

        try:

            relative_path = path.relative_to(
                static_root
            )

        except ValueError:

            relative_path = path.name

        web_path = (
            "/static/"
            + str(relative_path).replace("\\", "/")
        )

        comic_panel = ComicPanel(
            panel_number=panel.panel_number,
            title=panel.title,
            image_path=web_path,
            scene_description=panel.scene_description,
            caption=panel.caption,
            narration=panel.narration,
            dialogue=panel.dialogue,
            image_prompt=panel.image_prompt,
        )

        layout.append(comic_panel)

    return layout