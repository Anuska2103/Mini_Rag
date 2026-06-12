import logging
import os
import shutil
from typing import Dict, List, Optional, Sequence
import streamlit as st  # 👈 Added to manage global file-locks
from langchain_chroma import Chroma
from .embedding_service import embedding_model as embedding_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_chroma(collection_name: str, persist_directory: str = "vector_store/chroma") -> Chroma:
    """Return a cached Chroma client bound to *collection_name* to prevent SQLite file locks."""
    logger.info("get_chroma | collection=%s persist_directory=%s", collection_name, persist_directory)

    # 🚨 FIX: Cache the database instance globally in Streamlit's state tracking
    state_key = f"chroma_client_{collection_name}_{persist_directory.replace('/', '_')}"
    
    if state_key not in st.session_state:
        logger.info("Creating fresh Chroma client thread for collection=%s", collection_name)
        st.session_state[state_key] = Chroma(
            collection_name=collection_name,
            persist_directory=persist_directory,
            embedding_function=embedding_client,
        )
    else:
        logger.info("Reusing existing cached Chroma client for collection=%s", collection_name)

    logger.info("get_chroma complete | collection=%s", collection_name)
    return st.session_state[state_key]


def add_chunks(
    chroma: Chroma,
    chunks: Sequence[str],
    ids: Optional[Sequence[str]] = None,
    metadatas: Optional[Sequence[Dict]] = None,
) -> None:
    """Embed and add *chunks* to an existing Chroma collection."""
    logger.info("add_chunks started | num_chunks=%d has_ids=%s has_metadatas=%s", len(chunks), ids is not None, metadatas is not None)

    try:
        chroma.add_texts(
            list(chunks),
            metadatas=list(metadatas) if metadatas is not None else None,
            ids=list(ids) if ids is not None else None,
        )
        logger.info("add_chunks complete | num_chunks=%d", len(chunks))
    except Exception as exc:
        logger.error("add_chunks failed | num_chunks=%d error=%s", len(chunks), exc)
        raise


def reset_collection(collection_name: str, persist_directory: str = "vector_store/chroma") -> Chroma:
    """Delete the persisted collection on disk and return a fresh Chroma client."""
    logger.info("reset_collection started | collection=%s persist_directory=%s", collection_name, persist_directory)

    # 🚨 FIX: Clear the cache key first so it doesn't try to link back to old deleted files
    state_key = f"chroma_client_{collection_name}_{persist_directory.replace('/', '_')}"
    if state_key in st.session_state:
        del st.session_state[state_key]

    if os.path.exists(persist_directory):
        logger.info("Removing existing persist directory | path=%s", persist_directory)
        try:
            shutil.rmtree(persist_directory)
            logger.info("Persist directory removed | path=%s", persist_directory)
        except Exception as e:
            logger.error("Failed to delete directory via rmtree. Force overriding. error=%s", e)
    else:
        logger.info("No existing persist directory found — nothing to remove | path=%s", persist_directory)

    chroma = get_chroma(collection_name, persist_directory=persist_directory)
    logger.info("reset_collection complete | collection=%s", collection_name)
    return chroma


def collection_exists(collection_name: str, persist_directory: str = "vector_store/chroma") -> bool:
    """Return True if *collection_name* can be opened without error."""
    logger.info("collection_exists check | collection=%s persist_directory=%s", collection_name, persist_directory)

    try:
        get_chroma(collection_name, persist_directory=persist_directory)
        logger.info("collection_exists result=True | collection=%s", collection_name)
        return True
    except Exception as exc:
        logger.warning("collection_exists result=False | collection=%s error=%s", collection_name, exc)
        return False
