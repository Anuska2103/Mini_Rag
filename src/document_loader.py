from __future__ import annotations
from pathlib import Path
from .schemas import DocumentTextItem


def load_text_file(file_path: str | Path) -> list[DocumentTextItem]:
    """Read a UTF-8 text file and return the expected list-of-dicts output."""

    path = Path(file_path)
    text = path.read_text(encoding="utf-8")

    return [
        {
            "source_file": path.name,
            "file_type": "txt",
            "page_number": None,
            "text": text,
        }
    ]


def load_pdf_file(file_path: str | Path) -> list[DocumentTextItem]:
    """Extract text page-by-page from a PDF file."""

    path = Path(file_path)

    try:
        from pypdf import PdfReader
    except Exception as exc:
        raise RuntimeError("PDF support requires the 'pypdf' package.") from exc

    reader = PdfReader(str(path))

    items: list[DocumentTextItem] = []
    for page_number, page in enumerate(reader.pages, start=1):
        items.append(
            {
                "source_file": path.name,
                "file_type": "pdf",
                "page_number": page_number,
                "text": page.extract_text() or "",
            }
        )

    return items


def load_document_text(file_path: str | Path) -> list[DocumentTextItem]:
    """Dispatch to TXT or PDF extraction based on the file extension."""

    suffix = Path(file_path).suffix.lower()

    match suffix:
        case ".txt":
            return load_text_file(file_path)
        case ".pdf":
            return load_pdf_file(file_path)
        case _:
            raise ValueError(f"Unsupported file type: {suffix or '<none>'}")



read_text_file = load_text_file
load_pdf = load_pdf_file
