from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .routes import router


BASE_DIR = Path(
    __file__
).resolve().parent.parent

STATIC_DIR = (
    BASE_DIR / "static"
)

settings = get_settings()


app = FastAPI(
    title=settings.app_name,

    description=(
        "AI Comic Story Creator "
        "using Gemini and "
        "Hugging Face image generation."
    ),

    version="1.0.0",
)


app.mount(
    "/static",
    StaticFiles(
        directory=str(STATIC_DIR)
    ),
    name="static",
)


app.include_router(
    router
)