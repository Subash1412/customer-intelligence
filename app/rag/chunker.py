def chunk_text(
    text: str,
    page_number: int,
    chunk_size: int = 1800,
    overlap: int = 250,
) -> list[dict]:

    paragraphs = [
        p.strip()
        for p in text.split(". ")
        if p.strip()
    ]

    chunks = []

    current = ""

    for paragraph in paragraphs:

        candidate = (
            f"{current}. {paragraph}"
            if current
            else paragraph
        )

        if len(candidate) <= chunk_size:
            current = candidate
            continue

        if current:
            chunks.append(
                {
                    "content": current,
                    "page_number": page_number,
                }
            )

        overlap_text = (
            current[-overlap:]
            if current
            else ""
        )

        current = (
            f"{overlap_text} {paragraph}"
        ).strip()

    if current:
        chunks.append(
            {
                "content": current,
                "page_number": page_number,
            }
        )

    return chunks