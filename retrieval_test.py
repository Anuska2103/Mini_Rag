"""
Standalone retrieval smoke-test.

Run from the project root:
    python retrieval_test.py

Output:  retrieval_test_results.md  (written next to this file)
"""

import logging
import os
import sys
from datetime import datetime
from typing import List, Optional

# ---------------------------------------------------------------------------
# Make sure `src` is importable when running from the project root
# ---------------------------------------------------------------------------
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.vector_store import get_chroma  # noqa: E402  (after sys.path patch)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("retrieval_test")

# ---------------------------------------------------------------------------
# Config — edit these freely
# ---------------------------------------------------------------------------
COLLECTION_NAME = "collection"
PERSIST_DIR     = os.path.join(ROOT_DIR, "vector_store", "chroma")
OUTPUT_MD       = os.path.join(ROOT_DIR, "retrieval_test_results.md")
TOP_K           = 3

QUERIES: List[str] = [
    "What is Technical skills?",
    "what is the educational Qualifications",
    "mention email address or id",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def simple_relevance_observation(query: str, text: str) -> str:
    """Keyword-overlap heuristic — quick sanity check, not a real metric."""
    q_words = {w.strip(".,'?\"").lower() for w in query.split()}
    t_words = {w.strip(".,'?\"").lower() for w in text.split()}
    common  = q_words & t_words
    if len(common) >= 2:
        return "Likely relevant (keyword overlap)"
    if len(common) == 1:
        return "Possibly relevant (single keyword match)"
    return "Unclear / possibly not relevant"


def _safe_page_content(doc) -> str:
    return getattr(doc, "page_content", None) or getattr(doc, "content", None) or str(doc)


def _safe_metadata(doc) -> dict:
    return getattr(doc, "metadata", None) or {}


def _fmt_score(score: Optional[float]) -> str:
    return f"{score:.6f}" if score is not None else "n/a"


def _meta_row(meta: dict) -> str:
    """Compact one-liner — mirrors every ChromaVectorItem field from schemas.py."""

    def _f(key, fmt=None):
        val = meta.get(key)
        if val is None:
            return "—"
        return f"{float(val):{fmt}}" if fmt else str(val)

    return (
        f"**id:** {_f('chunk_id')}  "
        f"**src:** {_f('source_file')}  "
        f"**type:** {_f('file_type')}  "
        f"**page:** {_f('page_number')}  "
        f"**idx:** {_f('chunk_index')}  "
        f"**chars:** {_f('char_length')} "
        f"[{_f('start_char')}–{_f('end_char')}]  "
        f"**avg_cp:** {_f('avg_char_value', '.1f')}"
    )


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run() -> None:
    logger.info("=" * 60)
    logger.info("Retrieval test started")
    logger.info("collection   : %s", COLLECTION_NAME)
    logger.info("persist_dir  : %s", PERSIST_DIR)
    logger.info("top_k        : %d", TOP_K)
    logger.info("queries      : %d", len(QUERIES))
    logger.info("output       : %s", OUTPUT_MD)
    logger.info("=" * 60)

    # ---- Connect to Chroma --------------------------------------------------
    logger.info("Connecting to Chroma vector store …")
    chroma = get_chroma(COLLECTION_NAME, persist_directory=PERSIST_DIR)
    logger.info("Chroma client ready")

    # ---- Markdown report header ---------------------------------------------
    lines: List[str] = [
        "# Retrieval Test Results\n\n",
        f"- **Generated:** {datetime.utcnow().isoformat()} UTC\n",
        f"- **Collection:** `{COLLECTION_NAME}`\n",
        f"- **Persist dir:** `{PERSIST_DIR}`\n",
        f"- **Top-K:** {TOP_K}\n",
        f"- **Queries:** {len(QUERIES)}\n\n",
        "---\n\n",
    ]

    # ---- Run each query -----------------------------------------------------
    for q_idx, query in enumerate(QUERIES, start=1):
        logger.info("─" * 50)
        logger.info("Query %d/%d | %r", q_idx, len(QUERIES), query)
        print(f"\n{'─'*60}\nQuery {q_idx}/{len(QUERIES)}: {query}")

        lines.append(f"## {q_idx}. `{query}`\n\n")

        # Search
        try:
            docs_and_scores = chroma.similarity_search_with_score(query, k=TOP_K)
            logger.info("similarity_search_with_score → %d results", len(docs_and_scores))
        except Exception as exc:
            logger.warning("Scored search unavailable (%s) — falling back", exc)
            raw = chroma.similarity_search(query, k=TOP_K)
            docs_and_scores = [(d, None) for d in raw]
            logger.info("similarity_search → %d results", len(docs_and_scores))

        if not docs_and_scores:
            logger.warning("No results for query %r", query)
            lines.append("_No results returned._\n\n---\n\n")
            continue

        # Results table (score + snippet only — keeps table readable)
        lines.append(
            "| Rank | Score | Relevance | Snippet (300 chars) |\n"
            "| ---: | ---: | --- | --- |\n"
        )

        combined: List[str] = []

        for rank, (doc, score) in enumerate(docs_and_scores, start=1):
            content   = _safe_page_content(doc)
            metadata  = _safe_metadata(doc)
            snippet   = content.replace("|", "\\|").replace("\n", " ")[:300]
            obs       = simple_relevance_observation(query, content)
            score_str = _fmt_score(score)

            # stdout
            print(
                f"  [{rank}] score={score_str}  "
                f"chunk={metadata.get('chunk_id', '?')}  "
                f"src={metadata.get('source_file', '?')}  "
                f"page={metadata.get('page_number', '?')}  "
                f"idx={metadata.get('chunk_index', '?')}"
            )
            print(f"       {snippet[:120]} …")

            logger.debug(
                "rank=%d score=%s chunk_id=%s source_file=%s page=%s "
                "chunk_index=%s char_length=%s start_char=%s end_char=%s avg_char_value=%s",
                rank, score_str,
                metadata.get("chunk_id"),
                metadata.get("source_file"),
                metadata.get("page_number"),
                metadata.get("chunk_index"),
                metadata.get("char_length"),
                metadata.get("start_char"),
                metadata.get("end_char"),
                metadata.get("avg_char_value"),
            )

            lines.append(f"| {rank} | {score_str} | {obs} | {snippet} |\n")
            combined.append(content)

        # Metadata detail block — one line per result, below the table
        lines.append("\n### Metadata detail\n\n")
        for rank, (doc, _score) in enumerate(docs_and_scores, start=1):
            meta = _safe_metadata(doc)
            lines.append(f"**Rank {rank}** — {_meta_row(meta)}  \n")

        # Overall observation for this query
        overall = simple_relevance_observation(query, " ".join(combined))
        lines.append(f"\n**Overall observation:** {overall}\n\n---\n\n")
        logger.info("Query %d done | overall=%r", q_idx, overall)

    # ---- Write MD -----------------------------------------------------------
    logger.info("Writing report → %s", OUTPUT_MD)
    with open(OUTPUT_MD, "w", encoding="utf-8") as fh:
        fh.writelines(lines)

    print(f"\n✓  Report written to: {OUTPUT_MD}")
    logger.info("Retrieval test complete")


if __name__ == "__main__":
    run()