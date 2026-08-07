import json
import logging
from typing import Dict, List

from config import COLLECTION_NAME, VECTOR_PATH
from .vector_store import get_chroma, add_chunks, reset_collection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def index_chunks_from_json(
    json_path: str,
    collection_name: str = COLLECTION_NAME,
    persist_directory: str = VECTOR_PATH,
    reset: bool = False,
) -> None:
    """Read a chunks JSON file produced by chunking.export_chunks_json and
    upsert every chunk into a Chroma collection.

    The metadata stored per vector mirrors the ChromaVectorItem schema in
    schemas.py.
    """
    logger.info(
        "index_chunks_from_json started | json_path=%s collection=%s persist_dir=%s reset=%s",
        json_path, collection_name, persist_directory, reset,
    )

    # ------------------------------------------------------------------
    # Step 1 — load JSON
    # ------------------------------------------------------------------
    logger.info("Step 1/4 — loading chunks JSON | path=%s", json_path)
    try:
        with open(json_path, "r", encoding="utf-8") as fh:
            chunks = json.load(fh)
        logger.info("Step 1/4 complete | chunks_loaded=%d", len(chunks))
    except Exception as exc:
        logger.error("Failed to load chunks JSON | path=%s error=%s", json_path, exc)
        return

    # ------------------------------------------------------------------
    # Step 2 — parse into parallel lists expected by add_chunks
    # ------------------------------------------------------------------
    logger.info("Step 2/4 — parsing chunks into texts / ids / metadatas")

    texts: List[str] = []
    ids: List[str] = []
    metadatas: List[Dict] = []
    seen_ids: set[str] = set()
    duplicate_ids: List[str] = []

    for item_idx, item in enumerate(chunks):
        text = item.get("text")
        if not text:
            logger.warning("Skipping item %d — missing 'text' field | chunk_id=%s", item_idx, item.get("chunk_id"))
            continue

        chunk_id = item.get("chunk_id") or f"chunk-{item_idx}"
        if chunk_id in seen_ids:
            duplicate_ids.append(chunk_id)
            logger.warning("Skipping duplicate chunk_id in input | chunk_id=%s item_index=%d", chunk_id, item_idx)
            continue

        seen_ids.add(chunk_id)
        item_meta: dict = item.get("metadata") or {}

        # Build a flat metadata dict — all fields from ChromaVectorItem.
        # Use `is not None` so that 0 and False are preserved correctly.
        meta: Dict = {
            "chunk_id":      chunk_id,
            "source_file":   item.get("source_file"),
            "file_type":     item.get("file_type") if item.get("file_type") is not None else item_meta.get("file_type"),
            "page_number":   item.get("page_number") if item.get("page_number") is not None else item_meta.get("page_number"),
            "chunk_index":   item.get("chunk_index"),               # set by chunking.py (1-based)
            "char_length":   item_meta.get("char_length") if item_meta.get("char_length") is not None else item.get("char_count"),
            "start_char":    item_meta.get("start_char"),
            "end_char":      item_meta.get("end_char"),
            "avg_char_value": item_meta.get("avg_char_value"),
        }

        texts.append(text)
        ids.append(chunk_id)
        metadatas.append(meta)

        logger.debug(
            "Parsed item %d | chunk_id=%s source_file=%s page=%s chunk_index=%s",
            item_idx, chunk_id, meta["source_file"], meta["page_number"], meta["chunk_index"],
        )

    if duplicate_ids:
        logger.warning("Duplicate chunk ids skipped | duplicates=%d ids=%s", len(duplicate_ids), sorted(set(duplicate_ids)))

    logger.info("Step 2/4 complete | valid_chunks=%d (skipped=%d)", len(texts), len(chunks) - len(texts))

    if not texts:
        logger.warning("No valid chunks to index — aborting")
        return

    # ------------------------------------------------------------------
    # Step 3 — open (or reset) the Chroma collection
    # ------------------------------------------------------------------
    logger.info("Step 3/4 — preparing Chroma collection | collection=%s reset=%s", collection_name, reset)
    try:
        if reset:
            logger.info("Reset requested — deleting existing collection | collection=%s", collection_name)
            chroma = reset_collection(collection_name, persist_directory=persist_directory)
        else:
            chroma = get_chroma(collection_name, persist_directory=persist_directory)
        logger.info("Step 3/4 complete | collection=%s", collection_name)
    except Exception as exc:
        logger.error("Failed to prepare Chroma collection | collection=%s error=%s", collection_name, exc)
        return

    if ids and not reset:
        try:
            logger.info("Removing existing chunk ids before re-indexing | collection=%s ids=%d", collection_name, len(ids))
            chroma.delete(ids=ids)
        except Exception as exc:
            logger.warning("Failed to delete existing ids before indexing | collection=%s error=%s", collection_name, exc)

    # ------------------------------------------------------------------
    # Step 4 — embed and upsert
    # ------------------------------------------------------------------
    logger.info("Step 4/4 — embedding and indexing chunks | num_chunks=%d", len(texts))
    try:
        add_chunks(chroma, texts, ids=ids, metadatas=metadatas)
        logger.info("Step 4/4 complete | indexed=%d collection=%s", len(texts), collection_name)
    except Exception as exc:
        logger.error("add_chunks failed | collection=%s error=%s", collection_name, exc)
        return

    logger.info("index_chunks_from_json complete | collection=%s total_indexed=%d", collection_name, len(texts))


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Index a chunks JSON file into a Chroma vector store")
    parser.add_argument("json_path",                               help="Path to the chunks JSON file")
    parser.add_argument("--collection",   default="default",       help="Chroma collection name")
    parser.add_argument("--persist-dir",  default="vector_store/chroma", help="Chroma persist directory")
    parser.add_argument("--reset",        action="store_true",     help="Wipe the collection before indexing")

    args = parser.parse_args()

    logger.info(
        "CLI invocation | json_path=%s collection=%s persist_dir=%s reset=%s",
        args.json_path, args.collection, args.persist_dir, args.reset,
    )

    index_chunks_from_json(
        args.json_path,
        collection_name=args.collection,
        persist_directory=args.persist_dir,
        reset=args.reset,
    )