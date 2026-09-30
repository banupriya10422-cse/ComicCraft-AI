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
        # Skip header on the cover page
        if self.page_no() == 1:
            return

        self.set_font(
            "Helvetica",
            "B",
            10
        )

        self.set_text_color(
            70,
            70,
            70
        )

        self.cell(
            0,
            7,
            "COMICCRAFT",
            align="R"
        )

        self.ln(5)

    def footer(self):
        self.set_y(-12)

        self.set_font(
            "Helvetica",
            "",
            8
        )

        self.set_text_color(
            120,
            120,
            120
        )

        self.cell(
            0,
            6,
            f"ComicCraft  |  Page {self.page_no()}",
            align="C"
        )


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
        margin=18
    )

    pdf.set_title(
        pdf_safe(
            f"{request.character_name} - ComicCraft"
        )
    )

    pdf.set_author(
        "ComicCraft"
    )

    # ==================================================
    # COVER PAGE
    # ==================================================

    pdf.add_page()

    pdf.set_fill_color(
        245,
        245,
        245
    )

    pdf.rect(
        0,
        0,
        210,
        297,
        style="F"
    )

    pdf.set_y(55)

    pdf.set_font(
        "Helvetica",
        "B",
        30
    )

    pdf.set_text_color(
        25,
        25,
        25
    )

    pdf.cell(
        0,
        15,
        "COMICCRAFT",
        align="C"
    )

    pdf.ln(18)

    pdf.set_font(
        "Helvetica",
        "B",
        22
    )

    pdf.multi_cell(
        0,
        11,
        pdf_safe(
            request.story_prompt
        ),
        align="C"
    )

    pdf.ln(18)

    pdf.set_font(
        "Helvetica",
        "",
        13
    )

    pdf.set_text_color(
        70,
        70,
        70
    )

    pdf.cell(
        0,
        8,
        pdf_safe(
            f"Featuring: {request.character_name}"
        ),
        align="C"
    )

    pdf.ln(8)

    pdf.cell(
        0,
        8,
        pdf_safe(
            f"Setting: {request.setting}"
        ),
        align="C"
    )

    pdf.ln(8)

    pdf.cell(
        0,
        8,
        pdf_safe(
            f"Tone: {request.tone}"
        ),
        align="C"
    )

    pdf.ln(8)

    pdf.cell(
        0,
        8,
        pdf_safe(
            f"Art Style: {request.art_style}"
        ),
        align="C"
    )

    pdf.ln(25)

    pdf.set_font(
        "Helvetica",
        "I",
        11
    )

    pdf.set_text_color(
        110,
        110,
        110
    )

    pdf.cell(
        0,
        8,
        "Created with ComicCraft",
        align="C"
    )

    # ==================================================
    # COMIC PANELS
    # ==================================================

    for panel in panels:

        pdf.add_page()

        # Make sure every panel starts from a predictable
        # position below the page header.
        pdf.set_y(25)

        # ----------------------------------------------
        # Panel heading
        # ----------------------------------------------

        pdf.set_fill_color(
            30,
            30,
            30
        )

        pdf.set_text_color(
            255,
            255,
            255
        )

        pdf.set_font(
            "Helvetica",
            "B",
            15
        )

        heading = pdf_safe(
            f"PANEL {panel.panel_number}  |  {panel.title}"
        )

        # Give the heading its own fixed-height block.
        pdf.cell(
            0,
            12,
            heading,
            fill=True,
            align="L"
        )

        # IMPORTANT:
        # Move the cursor below the complete heading
        # before placing the image.
        pdf.ln(12)

        # Extra gap between title and image.
        pdf.ln(5)

        # ----------------------------------------------
        # Panel image
        # ----------------------------------------------

        image_path = Path(
            panel.image_path
        )

        if image_path.exists():

            with Image.open(image_path) as image:
                width, height = image.size

            # Keep the image comfortably inside the page.
            max_width = 174
            max_height = 118

            scale = min(
                max_width / width,
                max_height / height
            )

            display_width = width * scale
            display_height = height * scale

            x_position = (
                210 - display_width
            ) / 2

            # Capture the current position AFTER
            # the heading and its spacing.
            y_position = pdf.get_y()

            # Image border
            pdf.set_draw_color(
                40,
                40,
                40
            )

            pdf.rect(
                x_position - 2,
                y_position - 2,
                display_width + 4,
                display_height + 4
            )

            pdf.image(
                str(image_path),
                x=x_position,
                y=y_position,
                w=display_width,
                h=display_height
            )

            # Move the cursor completely below
            # the image before writing any text.
            pdf.set_y(
                y_position
                + display_height
                + 10
            )

        else:
            # If an image is missing, leave a clear message
            # instead of allowing later content to overlap.
            pdf.set_font(
                "Helvetica",
                "I",
                10
            )

            pdf.set_text_color(
                150,
                0,
                0
            )

            pdf.cell(
                0,
                8,
                "Panel image could not be loaded.",
                align="C"
            )

            pdf.ln(12)

        # ----------------------------------------------
        # Scene description
        # ----------------------------------------------

        pdf.set_font(
            "Helvetica",
            "I",
            10
        )

        pdf.set_text_color(
            80,
            80,
            80
        )

        pdf.multi_cell(
            0,
            5,
            pdf_safe(
                panel.scene_description
            )
        )

        pdf.ln(4)

        # ----------------------------------------------
        # Caption
        # ----------------------------------------------

        if panel.caption:

            pdf.set_fill_color(
                235,
                235,
                235
            )

            pdf.set_text_color(
                30,
                30,
                30
            )

            pdf.set_font(
                "Helvetica",
                "B",
                11
            )

            pdf.multi_cell(
                0,
                7,
                pdf_safe(
                    panel.caption
                ),
                fill=True
            )

            pdf.ln(4)

        # ----------------------------------------------
        # Narration
        # ----------------------------------------------

        if panel.narration:

            pdf.set_font(
                "Helvetica",
                "",
                11
            )

            pdf.set_text_color(
                40,
                40,
                40
            )

            pdf.multi_cell(
                0,
                6,
                pdf_safe(
                    panel.narration
                )
            )

            pdf.ln(4)

        # ----------------------------------------------
        # Dialogue
        # ----------------------------------------------

        if panel.dialogue:

            pdf.set_fill_color(
                250,
                250,
                250
            )

            pdf.set_draw_color(
                80,
                80,
                80
            )

            pdf.set_text_color(
                30,
                30,
                30
            )

            pdf.set_font(
                "Helvetica",
                "B",
                11
            )

            pdf.cell(
                0,
                7,
                "DIALOGUE",
                fill=True
            )

            pdf.ln(7)

            pdf.set_font(
                "Helvetica",
                "",
                10
            )

            for line in panel.dialogue:

                pdf.multi_cell(
                    0,
                    6,
                    pdf_safe(
                        f'"{line}"'
                    )
                )

                pdf.ln(1)

            pdf.ln(2)

    # ==================================================
    # SAVE
    # ==================================================

    pdf.output(
        str(output_path)
    )

    return str(output_path)