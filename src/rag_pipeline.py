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

    def answer_question(self, question, k=5):

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