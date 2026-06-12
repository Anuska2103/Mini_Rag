
from pathlib import Path
import json
import logging

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .document_loader import load_document_text
from .text_cleaning import clean_document_records

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def chunk_records(
    records: list[dict],
    chunk_size: int = 1000,
    overlap: int = 200,
) -> list[dict]:

    logger.info(
        "chunk_records started | total_records=%d",
        len(records),
    )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        add_start_index=True,
    )

    all_chunks = []

    for record_idx, record in enumerate(records, start=1):

        source_file = record["source_file"]
        page_number = record["page_number"]
        file_type = record["file_type"]

        logger.info(
            "Processing record %d/%d | source=%s page=%s",
            record_idx,
            len(records),
            source_file,
            page_number,
        )

        document = Document(
            page_content=record["text"],
            metadata={
                "source_file": source_file,
                "page_number": page_number,
                "file_type": file_type,
            },
        )

        split_docs = splitter.split_documents([document])

        for i, doc in enumerate(split_docs, start=1):

            chunk_str = doc.page_content

            start_char = doc.metadata["start_index"]
            end_char = start_char + len(chunk_str)

            char_length = len(chunk_str)

            avg_char_value = (
                sum(ord(c) for c in chunk_str) / char_length
            ) if char_length else 0.0

            chunk = {
                "chunk_id": f"{source_file}_{page_number}_{i}",
                "source_file": source_file,
                "file_type": file_type,
                "page_number": page_number,
                "chunk_index": i,
                "char_count": char_length,
                "text": chunk_str,
                "metadata": {
                    "file_type": file_type,
                    "page_number": page_number,
                    "start_char": start_char,
                    "end_char": end_char,
                    "char_length": char_length,
                    "avg_char_value": avg_char_value,
                },
            }

            all_chunks.append(chunk)

    logger.info(
        "chunk_records complete | total_chunks=%d",
        len(all_chunks),
    )

    return all_chunks

def build_chunks_from_file(
    file_path: str,
    chunk_size: int = 1000,
    overlap: int = 200,
) -> list[dict]:

    logger.info(
        "build_chunks_from_file started | file_path=%s",
        file_path,
    )

    try:
        records = load_document_text(file_path)

    except Exception as exc:

        logger.error(
            "load_document_text failed | error=%s",
            exc,
        )

        return []

    try:
        cleaned_records = clean_document_records(records)

    except Exception as exc:

        logger.error(
            "clean_document_records failed | error=%s",
            exc,
        )

        return []

    try:
        chunks = chunk_records(
            cleaned_records,
            chunk_size,
            overlap,
        )

    except Exception as exc:

        logger.error(
            "chunk_records failed | error=%s",
            exc,
        )

        return []

    logger.info(
        "build_chunks_from_file complete | total_chunks=%d",
        len(chunks),
    )

    return chunks

def export_chunks_json(
    chunks: list[dict],
    output_file: str,
) -> None:

    output_path = Path(output_file)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as fh:

        json.dump(
            chunks,
            fh,
            indent=4,
            ensure_ascii=False,
        )

    logger.info(
        "Chunks exported to %s",
        output_file,
    )