from pathlib import Path
import re
import textwrap

from PIL import Image, ImageDraw, ImageFont
from huggingface_hub import InferenceClient

from ..config import Settings


def safe_filename(value: str) -> str:
    value = re.sub(
        r"[^a-zA-Z0-9_-]+",
        "-",
        value
    )
    value = value.strip("-")
    return value[:80] or "panel"


def _get_font(size: int):
    """
    Try a few common fonts.
    Fall back to Pillow's default font if none are available.
    """
    font_paths = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibri.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
    ]

    for font_path in font_paths:
        path = Path(font_path)

        if path.exists():
            try:
                return ImageFont.truetype(
                    str(path),
                    size
                )
            except Exception:
                pass

    return ImageFont.load_default()


def _create_local_fallback(
    prompt: str,
    output_path: Path,
):
    """
    Create a local comic-style storyboard panel.

    This is used when the external image provider cannot
    generate an image, for example when its credits are exhausted.
    """

    width = 768
    height = 768

    image = Image.new(
        "RGB",
        (width, height),
        "#f5f1ff"
    )

    draw = ImageDraw.Draw(image)

    # Outer comic frame
    draw.rectangle(
        [20, 20, width - 20, height - 20],
        outline="#202033",
        width=8
    )

    # Inner scene area
    draw.rounded_rectangle(
        [55, 55, width - 55, 520],
        radius=24,
        fill="#ffffff",
        outline="#6d43df",
        width=5
    )

    # Simple comic sun
    draw.ellipse(
        [90, 90, 190, 190],
        fill="#ffd86b",
        outline="#202033",
        width=4
    )

    # Simple hills / environment
    draw.polygon(
        [
            (60, 500),
            (220, 350),
            (360, 500),
        ],
        fill="#b9e3c6",
        outline="#202033"
    )

    draw.polygon(
        [
            (280, 500),
            (500, 320),
            (730, 500),
        ],
        fill="#9fd1b0",
        outline="#202033"
    )

    # Simple character figure
    center_x = 385

    draw.ellipse(
        [
            center_x - 45,
            245,
            center_x + 45,
            335,
        ],
        fill="#ffd8b5",
        outline="#202033",
        width=4
    )

    draw.rectangle(
        [
            center_x - 50,
            335,
            center_x + 50,
            455,
        ],
        fill="#7650d8",
        outline="#202033",
        width=4
    )

    draw.line(
        [
            center_x - 45,
            370,
            center_x - 110,
            425,
        ],
        fill="#202033",
        width=7
    )

    draw.line(
        [
            center_x + 45,
            370,
            center_x + 110,
            425,
        ],
        fill="#202033",
        width=7
    )

    draw.line(
        [
            center_x - 25,
            455,
            center_x - 55,
            505,
        ],
        fill="#202033",
        width=7
    )

    draw.line(
        [
            center_x + 25,
            455,
            center_x + 55,
            505,
        ],
        fill="#202033",
        width=7
    )

    # Title
    title_font = _get_font(32)

    draw.text(
        (80, 545),
        "ComicCraft Storyboard",
        font=title_font,
        fill="#202033"
    )

    # Prompt/event text
    body_font = _get_font(22)

    clean_prompt = " ".join(
        prompt.strip().split()
    )

    wrapped = textwrap.wrap(
        clean_prompt,
        width=52
    )

    y = 600

    for line in wrapped[:6]:
        draw.text(
            (80, y),
            line,
            font=body_font,
            fill="#343448"
        )

        y += 30

    # Fallback notice
    small_font = _get_font(17)

    draw.text(
        (80, 735),
        "Local fallback panel",
        font=small_font,
        fill="#6d43df"
    )

    image.save(
        output_path,
        format="PNG"
    )


def generate_image(
    prompt: str,
    output_dir: Path,
    filename_hint: str,
    settings: Settings
) -> str:

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    filename = (
        f"{safe_filename(filename_hint)}.png"
    )

    output_path = output_dir / filename

    # Try Hugging Face first.
    if settings.hf_token:
        try:
            client = InferenceClient(
                provider=settings.hf_provider,
                api_key=settings.hf_token,
                timeout=180,
            )

            image = client.text_to_image(
                prompt=prompt,
                model=settings.hf_image_model,
                negative_prompt=(
                    "blurry, low quality, distorted face, "
                    "extra limbs, malformed hands, watermark, "
                    "logo, unreadable text"
                ),
                width=settings.image_width,
                height=settings.image_height,
                num_inference_steps=settings.image_steps,
                guidance_scale=settings.image_guidance,
            )

            image.save(output_path)

            return str(output_path)

        except Exception as error:
            error_text = str(error).lower()

            # Hugging Face credit/payment exhaustion.
            if (
                "402" in error_text
                or "payment required" in error_text
                or "depleted" in error_text
                or "credits" in error_text
            ):
                print(
                    "Hugging Face image credits are unavailable. "
                    "Using local ComicCraft fallback panel."
                )

            else:
                print(
                    "Hugging Face image generation failed. "
                    f"Using local fallback panel. Error: {error}"
                )

    else:
        print(
            "HF_TOKEN is missing. "
            "Using local ComicCraft fallback panel."
        )

    # Local fallback keeps the comic pipeline working.
    _create_local_fallback(
        prompt,
        output_path
    )

    return str(output_path)