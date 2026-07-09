class SourceFormatter:

    @staticmethod
    def format_sources(docs):

        sources = []

        for doc in docs:

            metadata = doc.metadata

            sources.append(
                {
                    "file": metadata.get("source_file", "Unknown"),
                    "page": metadata.get("page_number", "N/A"),
                    "chunk_id": metadata.get("chunk_id", "N/A"),
                    "chunk_index": metadata.get("chunk_index", "N/A"),
                    "preview": (
                        doc.page_content[:200] + "..."
                        if len(doc.page_content) > 200
                        else doc.page_content
                    ),
                }
            )

        return sources