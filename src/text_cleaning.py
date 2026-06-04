from __future__ import annotations

import re


def clean_text(text: str) -> str:
   

    if not text:
        return ""

    # Replace multiple spaces/tabs with a single space
    text = re.sub(r"[ \t]+", " ", text)

    # Replace 3 or more newlines with 2 newlines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Remove leading/trailing whitespace
    text = text.strip()

    return text


def clean_document_records(records: list[dict]) -> list[dict]:
    """
    Clean the text field of each document record.
    """

    cleaned_records = []

    for record in records:
        cleaned_record = record.copy()
        cleaned_record["text"] = clean_text(record["text"])
        cleaned_records.append(cleaned_record)

    return cleaned_records