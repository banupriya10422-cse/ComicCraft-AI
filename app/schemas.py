from pydantic import BaseModel, Field, field_validator


class PromptRequest(BaseModel):
    story_prompt: str = Field(
        ...,
        min_length=5,
        max_length=2000
    )

    character_name: str = Field(
        ...,
        min_length=1,
        max_length=80
    )

    panel_count: int = Field(
        default=5,
        ge=3,
        le=9
    )

    setting: str = Field(
        default="Enchanted forest",
        min_length=1,
        max_length=120
    )

    tone: str = Field(
        default="Adventurous",
        min_length=1,
        max_length=50
    )

    art_style: str = Field(
        default="Comic book",
        min_length=1,
        max_length=80
    )

    audience: str = Field(
        default="General",
        min_length=1,
        max_length=30
    )

    narration_length: str = Field(
        default="Normal",
        min_length=1,
        max_length=30
    )

    @field_validator(
        "story_prompt",
        "character_name",
        "setting",
        "tone",
        "art_style",
        "audience",
        "narration_length"
    )
    @classmethod
    def validate_text(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Value cannot be empty.")

        return value


class ImageTestRequest(BaseModel):
    prompt: str = Field(
        ...,
        min_length=3,
        max_length=1500
    )


class PanelOutline(BaseModel):
    panel_number: int = Field(
        ...,
        ge=1
    )

    title: str

    scene_description: str

    image_prompt: str


class OutlineResponse(BaseModel):
    panels: list[PanelOutline]


class PanelStory(BaseModel):
    panel_number: int

    title: str

    scene_description: str

    caption: str

    narration: str

    dialogue: list[str] = Field(
        default_factory=list
    )

    image_prompt: str


class StoryResponse(BaseModel):
    panels: list[PanelStory]


class ComicPanel(BaseModel):
    panel_number: int

    title: str

    image_path: str

    scene_description: str

    caption: str

    narration: str

    dialogue: list[str] = Field(
        default_factory=list
    )

    image_prompt: str


class ComicRecord(BaseModel):
    comic_id: str

    created_at: str

    request: PromptRequest

    panels: list[ComicPanel]

    pdf_path: str