import logging
from typing import List, Sequence

from langchain_huggingface import HuggingFaceEmbeddings

from config import MODEL_NAME

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Loading embedding model | model=%s normalize_embeddings=True", MODEL_NAME)

embedding_model = HuggingFaceEmbeddings(
    model_name=MODEL_NAME,
    encode_kwargs={"normalize_embeddings": True},
)

logger.info("Embedding model loaded | model=%s", MODEL_NAME)


def embed_text(text: str) -> List[float]:
    """Embed a single string and return a normalised float vector."""
    logger.debug("embed_text called | text_length=%d", len(text))

    try:
        vector = list(embedding_model.embed_query(text))
        logger.debug("embed_text complete | dimensions=%d", len(vector))
        return vector
    except Exception as exc:
        logger.error("embed_text failed | text_length=%d error=%s", len(text), exc)
        raise


def embed_texts(texts: Sequence[str]) -> List[List[float]]:
    """Embed a batch of strings and return a list of normalised float vectors."""
    logger.info("embed_texts called | batch_size=%d", len(texts))

    try:
        vectors = [list(v) for v in embedding_model.embed_documents(list(texts))]
        logger.info("embed_texts complete | batch_size=%d dimensions=%d", len(vectors), len(vectors[0]) if vectors else 0)
        return vectors
    except Exception as exc:
        logger.error("embed_texts failed | batch_size=%d error=%s", len(texts), exc)
        raise