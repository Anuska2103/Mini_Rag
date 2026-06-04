from pathlib import Path
import json
import logging

from .document_loader import load_document_text
from .text_cleaning import clean_document_records

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def chunk_text(text, chunk_size=1000, overlap=200):
    chunks = []

    try:
        if not text:
            return chunks

        start = 0

        while start < len(text):
            end = start + chunk_size

            chunk = text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            start += chunk_size - overlap

        logger.info(f"Created {len(chunks)} chunks")

        return chunks

    except Exception as e:
        logger.error(f"Chunking failed: {e}")
        return []


def chunk_records(records, chunk_size=1000, overlap=200):
    all_chunks = []

    try:
        for record in records:

            chunks = chunk_text(
                record["text"],
                chunk_size,
                overlap
            )

            for i, chunk in enumerate(chunks, start=1):

                all_chunks.append(
                    {
                        "source_file": record["source_file"],
                        "file_type": record["file_type"],
                        "page_number": record["page_number"],
                        "chunk_id": f"{record['source_file']}_{record['page_number']}_{i}",
                        "chunk_no": i,
                        "char_count": len(chunk),
                        "text": chunk,
                    }
                )

        logger.info(f"Total chunks created: {len(all_chunks)}")

        return all_chunks

    except Exception as e:
        logger.error(f"Record chunking failed: {e}")
        return []


def build_chunks_from_file(file_path, chunk_size=1000, overlap=200):

    try:
        records = load_document_text(file_path)

        cleaned_records = clean_document_records(records)

        return chunk_records(
            cleaned_records,
            chunk_size,
            overlap
        )

    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        return []


def export_chunks_json(chunks, output_file):

    try:
        output_path = Path(output_file)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(
                chunks,
                file,
                indent=4,
                ensure_ascii=False
            )

        logger.info(f"Chunks saved to {output_file}")

    except Exception as e:
        logger.error(f"Export failed: {e}")