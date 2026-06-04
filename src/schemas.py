"""Shared schema definitions for extracted document text."""

from __future__ import annotations

from typing import NotRequired, TypedDict


class DocumentTextItem(TypedDict):
    source_file: str
    file_type: str
    page_number: int | None
    text: str
