from pathlib import Path
import re

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


def generate_image(
    prompt: str,
    output_dir: Path,
    filename_hint: str,
    settings: Settings
) -> str:

    if not settings.hf_token:
        raise RuntimeError(
            "HF_TOKEN is missing. "
            "Add your Hugging Face token to the .env file."
        )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    filename = (
        f"{safe_filename(filename_hint)}.png"
    )

    output_path = output_dir / filename

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
