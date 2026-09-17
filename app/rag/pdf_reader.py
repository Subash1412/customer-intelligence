from pathlib import Path

from pypdf import PdfReader


def read_pdf(
    file_path: Path,
) -> list[dict]:

    reader = PdfReader(
        str(file_path)
    )

    pages = []

    for index, page in enumerate(
        reader.pages
    ):
        text = page.extract_text()

        if not text:
            continue

        cleaned = " ".join(
            text.split()
        )

        if not cleaned:
            continue

        pages.append(
            {
                "page_number": index + 1,
                "text": cleaned,
            }
        )

    return pages