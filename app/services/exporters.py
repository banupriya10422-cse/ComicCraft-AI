from pathlib import Path

from fpdf import FPDF
from PIL import Image

from ..schemas import (
    ComicPanel,
    PromptRequest,
)


def pdf_safe(text: str) -> str:

    return (
        text
        .encode("latin-1", "replace")
        .decode("latin-1")
    )


class ComicPDF(FPDF):

    def header(self):

        self.set_font(
            "Helvetica",
            "B",
            12
        )

        self.set_text_color(
            50,
            50,
            50
        )

        self.cell(
            0,
            8,
            "ComicCraft",
            align="R"
        )

        self.ln(10)


def save_pdf(
    panels: list[ComicPanel],
    request: PromptRequest,
    output_dir: Path,
    filename: str
) -> str:

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path = output_dir / filename

    pdf = ComicPDF()

    pdf.set_auto_page_break(
        auto=True,
        margin=15
    )

    pdf.set_title(
        pdf_safe(
            f"{request.character_name} - ComicCraft"
        )
    )

    for panel in panels:

        pdf.add_page()

        pdf.set_font(
            "Helvetica",
            "B",
            18
        )

        pdf.set_text_color(
            25,
            25,
            25
        )

        pdf.multi_cell(
            0,
            10,
            pdf_safe(
                f"Panel {panel.panel_number}: "
                f"{panel.title}"
            )
        )

        pdf.ln(3)

        image_path = Path(
            panel.image_path
        )

        if image_path.exists():

            with Image.open(image_path) as image:

                width, height = image.size

            max_width = 175
            max_height = 110

            scale = min(
                max_width / width,
                max_height / height
            )

            display_width = width * scale
            display_height = height * scale

            x_position = (
                210 - display_width
            ) / 2

            pdf.image(
                str(image_path),
                x=x_position,
                w=display_width,
                h=display_height
            )

            pdf.ln(5)

        pdf.set_font(
            "Helvetica",
            "I",
            10
        )

        pdf.multi_cell(
            0,
            6,
            pdf_safe(
                panel.scene_description
            )
        )

        pdf.ln(3)

        if panel.caption:

            pdf.set_font(
                "Helvetica",
                "B",
                11
            )

            pdf.multi_cell(
                0,
                6,
                pdf_safe(
                    "Caption: "
                    + panel.caption
                )
            )

            pdf.ln(2)

        pdf.set_font(
            "Helvetica",
            "",
            11
        )

        pdf.multi_cell(
            0,
            6,
            pdf_safe(
                panel.narration
            )
        )

        pdf.ln(3)

        if panel.dialogue:

            pdf.set_font(
                "Helvetica",
                "B",
                11
            )

            pdf.multi_cell(
                0,
                6,
                "Dialogue"
            )

            pdf.set_font(
                "Helvetica",
                "",
                11
            )

            for line in panel.dialogue:

                pdf.multi_cell(
                    0,
                    6,
                    pdf_safe(
                        f'"{line}"'
                    )
                )

            pdf.ln(2)

    pdf.output(
        str(output_path)
    )

    return str(output_path)