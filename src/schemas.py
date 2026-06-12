"""Shared schema definitions for extracted document text, exported chunks,
and vector records stored in Chroma.

This module provides TypedDict shapes used across the project for JSON
export/import and for referencing how vectors and chunk metadata are stored
in the vector database.
"""

from __future__ import annotations

from typing import Any, Dict, List, NotRequired, TypedDict


class DocumentTextItem(TypedDict):
    """One page/section of raw text extracted from a source document."""

    source_file: str
    file_type: str
    page_number: int | None
    text: str


class ChunkMetadata(TypedDict):
    """Provenance metadata stored inside every ChunkExportItem."""

    file_type: str
    page_number: int | None
    start_char: int
    end_char: int
    char_length: int
    avg_char_value: float


class ChunkExportItem(TypedDict):
    """Schema for an exported chunk (JSON export / import).

    Written by chunking.chunk_records and read by indexer.index_chunks_from_json.
    All char-position details live inside `metadata`; the top-level fields are
    the stable identifiers used for deduplication and retrieval.
    """

    chunk_id: str          # "{source_file}_{page_number}_{chunk_index}"
    source_file: str
    file_type: str
    page_number: int | None
    chunk_index: int       # 1-based position within the page/record
    char_count: int        # convenience copy of metadata.char_length
    text: str
    metadata: ChunkMetadata


class ChromaVectorItem(TypedDict):
    """Schema representing a vector record as stored in Chroma.

    `id` is the Chroma document ID (== chunk_id).
    `vector` is the embedding produced by embedding_service.
    All other fields are stored as Chroma metadata.
    """

    id: str                              # Chroma document ID  (== chunk_id)
    vector: List[float]
    chunk_id: str                        # provenance link back to ChunkExportItem
    source_file: NotRequired[str]
    file_type: NotRequired[str]
    page_number: NotRequired[int | None]
    chunk_index: NotRequired[int]
    start_char: NotRequired[int]
    end_char: NotRequired[int]
    char_length: NotRequired[int]
    avg_char_value: NotRequired[float]
    text: NotRequired[str]
    embedding_model: NotRequired[str]
    embedding_dimensions: NotRequired[int]
    created_at: NotRequired[str]