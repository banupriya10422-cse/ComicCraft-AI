from datetime import datetime, timezone
from pathlib import Path
import uuid

from fastapi import (
    APIRouter,
    Form,
    HTTPException,
    Request,
)

from fastapi.responses import (
    FileResponse,
    HTMLResponse,
)

from fastapi.templating import (
    Jinja2Templates,
)

from .config import get_settings

from .schemas import (
    ImageTestRequest,
    PromptRequest,
)

from .services.exporters import (
    save_pdf,
)

from .services.gemini_flash import (
    generate_outline,
)

from .services.gemini_pro import (
    generate_story,
)

from .services.image_generator import (
    generate_image,
)

from .services.layout_builder import (
    build_comic_layout,
)

from .storage import (
    get_comic,
    save_comic,
)


router = APIRouter()

templates = Jinja2Templates(
    directory="templates"
)


BASE_DIR = Path(__file__).resolve().parent.parent

STATIC_DIR = BASE_DIR / "static"

PANELS_DIR = (
    STATIC_DIR / "panels"
)

EXPORTS_DIR = (
    STATIC_DIR / "exports"
)


def generate_complete_comic(
    request_data: PromptRequest
):

    settings = get_settings()

    # --------------------------------
    # STEP 1
    # Generate structured outline
    # --------------------------------

    outline = generate_outline(
        request_data,
        settings
    )

    # --------------------------------
    # STEP 2
    # Generate story
    # --------------------------------

    story = generate_story(
        request_data,
        outline,
        settings
    )

    # --------------------------------
    # STEP 3
    # Generate images
    # --------------------------------

    comic_id = uuid.uuid4().hex

    image_paths = []

    for panel in story.panels:

        filename_hint = (
            f"{comic_id}-panel-"
            f"{panel.panel_number}"
        )

        image_path = generate_image(
            prompt=panel.image_prompt,
            output_dir=PANELS_DIR,
            filename_hint=filename_hint,
            settings=settings,
        )

        image_paths.append(
            image_path
        )

    # --------------------------------
    # STEP 4
    # Build browser layout
    # --------------------------------

    layout = build_comic_layout(
        story=story,
        image_paths=image_paths,
        static_root=STATIC_DIR,
    )

    # --------------------------------
    # STEP 5
    # Build PDF panels
    # --------------------------------

    pdf_panels = []

    for panel, image_path in zip(
        story.panels,
        image_paths
    ):

        pdf_panel = panel.model_copy(
            update={
                "image_path": image_path
            }
        )

        pdf_panels.append(
            pdf_panel
        )

    # --------------------------------
    # STEP 6
    # Export PDF
    # --------------------------------

    pdf_filename = (
        f"comiccraft-{comic_id}.pdf"
    )

    pdf_path = save_pdf(
        panels=pdf_panels,
        request=request_data,
        output_dir=EXPORTS_DIR,
        filename=pdf_filename,
    )

    # --------------------------------
    # STEP 7
    # Store comic
    # --------------------------------

    from .schemas import ComicRecord

    record = ComicRecord(
        comic_id=comic_id,
        created_at=datetime.now(
            timezone.utc
        ).isoformat(),
        request=request_data,
        panels=layout,
        pdf_path=pdf_path,
    )

    save_comic(record)

    return record


@router.get(
    "/",
    response_class=HTMLResponse
)
async def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
    )


@router.post(
    "/generate",
    response_class=HTMLResponse
)
async def generate(
    request: Request,

    story_prompt: str = Form(...),

    character_name: str = Form(...),

    setting: str = Form(...),

    tone: str = Form(...),

    art_style: str = Form(...),
):

    try:

        data = PromptRequest(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
        )

        comic = generate_complete_comic(
            data
        )

        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={
                "comic": comic
            },
        )

    except Exception as exc:

        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={
                "error": str(exc)
            },
            status_code=500,
        )


@router.post(
    "/generate-comic/json"
)
async def generate_comic_json(
    payload: PromptRequest
):

    try:

        comic = generate_complete_comic(
            payload
        )

        return {
            "success": True,

            "comic_id": comic.comic_id,

            "created_at": comic.created_at,

            "panels": [
                panel.model_dump()
                for panel in comic.panels
            ],

            "pdf_url": (
                f"/download/"
                f"{comic.comic_id}"
            ),

            "success_url": (
                f"/export-success/"
                f"{comic.comic_id}"
            ),
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        ) from exc


@router.post(
    "/test-image"
)
async def test_image(
    payload: ImageTestRequest
):

    try:

        settings = get_settings()

        image_id = uuid.uuid4().hex

        image_path = generate_image(
            prompt=payload.prompt,
            output_dir=PANELS_DIR,
            filename_hint=f"test-{image_id}",
            settings=settings,
        )

        relative_path = Path(
            image_path
        ).relative_to(
            STATIC_DIR
        )

        image_url = (
            "/static/"
            + str(relative_path)
            .replace("\\", "/")
        )

        return {
            "success": True,
            "image_url": image_url,
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        ) from exc


@router.get(
    "/download/{comic_id}"
)
async def download_comic(
    comic_id: str
):

    comic = get_comic(
        comic_id
    )

    if not comic:

        raise HTTPException(
            status_code=404,
            detail="Comic not found."
        )

    pdf_path = Path(
        comic.pdf_path
    )

    if not pdf_path.exists():

        raise HTTPException(
            status_code=404,
            detail="PDF file no longer exists."
        )

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=pdf_path.name,
    )


@router.get(
    "/export-success/{comic_id}",
    response_class=HTMLResponse
)
async def export_success(
    request: Request,
    comic_id: str
):

    comic = get_comic(
        comic_id
    )

    if not comic:

        raise HTTPException(
            status_code=404,
            detail="Comic not found."
        )

    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={
            "comic": comic
        },
    )


@router.get(
    "/health"
)
async def health():

    return {
        "status": "ok",
        "service": "ComicCraft"
    }