import re

from src.vector_store import get_chroma
from src.llm_service import LLMService
from src.source_formatter import SourceFormatter


class RAGPipeline:

    def __init__(
        self,
        collection_name="default",
        persist_directory="vector_store/chroma",
    ):

        self.db = get_chroma(
            collection_name=collection_name,
            persist_directory=persist_directory,
        )

        self.llm = LLMService()

    def _is_page_count_question(self, question):

        normalized = question.lower().strip()

        page_count_patterns = (
            r"\bhow many pages\b",
            r"\bnumber of pages\b",
            r"\bpage count\b",
            r"\bhow many page(s)?\b",
            r"\bpages does (this|the) document have\b",
        )

        return any(re.search(pattern, normalized) for pattern in page_count_patterns)

    def _load_collection_metadata(self):

        try:
            result = self.db.get(include=["metadatas", "documents"])
        except TypeError:
            result = self.db.get()

        return result or {}

    def _count_pages_from_collection(self):

        collection_data = self._load_collection_metadata()
        metadatas = collection_data.get("metadatas") or []

        page_numbers = {
            metadata.get("page_number")
            for metadata in metadatas
            if isinstance(metadata, dict) and metadata.get("page_number") is not None
        }

        if page_numbers:
            return len(page_numbers)

        if metadatas:
            return 1

        return None

    def _build_page_count_answer(self):

        page_count = self._count_pages_from_collection()

        if page_count is None:
            return None

        suffix = "s" if page_count != 1 else ""
        return f"This document has {page_count} page{suffix}."

    def answer_question(self, question, k=5):

        if self._is_page_count_question(question):

            page_count_answer = self._build_page_count_answer()

            if page_count_answer is not None:
                return {
                    "answer": page_count_answer,
                    "sources": [],
                    "context": "",
                }

        docs = self.db.similarity_search(
            question,
            k=k,
        )

        if len(docs) == 0:

            return {
                "answer": "No relevant information found.",
                "sources": [],
                "context": "",
            }

        context = "\n\n".join(
            doc.page_content
            for doc in docs
        )

        answer = self.llm.generate_answer(
            question,
            context,
        )

        if answer.startswith("Error generating response:"):
            answer = self._build_local_fallback_answer(docs)

        sources = SourceFormatter.format_sources(
            docs
        )

        return {
            "answer": answer,
            "sources": sources,
            "context": context,
        }

    def _build_local_fallback_answer(self, docs):
        first_doc = docs[0]
        preview = first_doc.page_content.strip()

        if len(preview) > 700:
            preview = preview[:700].rsplit(" ", 1)[0] + "..."

        return (
            "I couldn't reach Gemini, so I used the most relevant retrieved context instead. "
            f"\n\n{preview}"
        )