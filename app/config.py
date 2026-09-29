from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ComicCraft"

    gemini_api_key: str = ""

    hf_token: str = ""

    gemini_outline_model: str = "gemini-3-flash-preview"
    gemini_story_model: str = "gemini-3-flash-preview"
    
    hf_image_model: str = "black-forest-labs/FLUX.1-schnell"

    hf_provider: str = "auto"

    panel_count: int = 5

    image_width: int = 768

    image_height: int = 768

    image_steps: int = 4

    image_guidance: float = 3.5

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()