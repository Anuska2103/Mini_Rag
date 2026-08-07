from pathlib import Path
import json
import logging
import re
from dotenv import load_dotenv
from config import CHUNK_SIZE, OVERLAP, VECTOR_PATH
from src.rag_pipeline import RAGPipeline
import streamlit as st

from src.chunking import build_chunks_from_file, export_chunks_json
from src.document_loader import load_document_text
from src.text_cleaning import clean_document_records
from src.txt_processing import basic_clean_text, keyword_search, count_text_stats, split_into_paragraphs, highlight_text, semantic_search
from src.indexer import index_chunks_from_json
from src.vector_store import get_chroma

load_dotenv()


st.title("Mini rag char with Document")

st.write("""Upload a .txt document and search for keywords or sentences inside the file.
    The app will:
    - Preview uploaded text
    - Count words
    - Count paragraphs
    - Search matching paragraphs""")

#file upload

upload_file = st.file_uploader("Upload TXT/PDF File", type=["txt", "pdf"])
if upload_file is None:
    st.warning("File not uploaded please upload a txt file")
    st.stop()

uploaded_bytes = upload_file.getvalue()
upload_dir = Path("outputs") / "uploads"
upload_dir.mkdir(parents=True, exist_ok=True)
upload_path = upload_dir / upload_file.name
upload_path.write_bytes(uploaded_bytes)

# set up logging
logger = logging.getLogger("mini_rag")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

# in-memory UI log buffer
if "ui_logs" not in st.session_state:
    st.session_state.ui_logs = []

def log(msg: str, level: str = "info"):
    """Log to terminal and append to Streamlit UI log buffer."""
    if level == "info":
        logger.info(msg)
    elif level == "error":
        logger.error(msg)
    elif level == "warning":
        logger.warning(msg)
    else:
        logger.debug(msg)

    st.session_state.ui_logs.append(f"{msg}")

def render_logs():
    logs_text = "\n".join(st.session_state.ui_logs[-200:])
    st.text_area("Process logs", value=logs_text, height=200)


def make_collection_name(filename: str) -> str:
    """Create a safe collection name from a filename."""
    name = Path(filename).stem
    # replace non-alphanumeric runs with underscore, trim, and lowercase
    name = re.sub(r"[^0-9a-zA-Z]+", "_", name).strip("_").lower()
    return name or "default"

#read file
records = load_document_text(upload_path)
cleaned_records = clean_document_records(records)
text = "\n\n".join(record.get("text", "") for record in cleaned_records)

# Clean text
cleaned_text = basic_clean_text(text)

st.subheader("Text preview")
st.text_area('Preview', cleaned_text[:1000], height=250, disabled=True)

#extracting the summary 0
stats = count_text_stats(cleaned_text)


paragraphs = split_into_paragraphs(cleaned_text)

word_count = stats["words"]
characters = stats["characters"]
sentences = stats["sentences"]
paragraph_count = len(paragraphs)
page_count = max(1, sum(1 for record in cleaned_records if record.get("page_number") is not None))

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Words", word_count)
with col2:
    st.metric("Paragraphs", paragraph_count)
with col3:
    st.metric("Sentences", sentences)
with col4:
    st.metric("Characters", characters)


query = st.text_input("Enter keyword or question")



if "current_result" not in st.session_state:
    st.session_state.current_result = 0

if "results" not in st.session_state:
    st.session_state.results = []

if "query" not in st.session_state:
    st.session_state.query = ""



if st.button("Search Document"):

    
    if not query.strip():

        st.error("Please enter a keyword or question.")

    else:

        # Search Results
        results = keyword_search(cleaned_text, query)

        # Store in session state
        st.session_state.results = results
        st.session_state.query = query
        st.session_state.current_result = 0



results = st.session_state.results

if len(results) > 0:

    current = st.session_state.current_result
    query = st.session_state.query

    st.subheader("🔍 Search Results")

    st.success(f"{len(results)} matching paragraph(s) found.")

    # Counter like PDF search
    st.write(f"### Result {current + 1}/{len(results)}")

    # Highlight matched text
    highlighted_para = highlight_text(
        results[current],
        query
    )

    st.markdown(
        highlighted_para,
        unsafe_allow_html=True
    )

    st.divider()

    # Navigation Buttons
    col1, col2 = st.columns(2)

    # Previous Button
    with col1:

        if st.button("⬅ Previous"):

            if current > 0:
                st.session_state.current_result -= 1

    # Next Button
    with col2:

        if st.button("Next ➡"):

            if current < len(results) - 1:
                st.session_state.current_result += 1



elif st.session_state.query != "":
    

    st.warning("No matching paragraph found.")



st.markdown("---")
st.subheader("Ask a question about this document")
question = st.text_input("Enter a question")

if st.button("Ask Question"):

    if not question or not question.strip():
        st.error("Please enter a question.")
    else:
        try:
            sem_results = semantic_search(cleaned_text, question)
        except Exception as e:
            st.error(f"Semantic search error: {e}")
            sem_results = []

        if not sem_results:
            st.warning("No answer found for your question.")
        else:
            top = sem_results[0]
            ans_para = top.get("paragraph", "")
            score = top.get("score", 0)

            st.write(f"**Confidence:** {score:.2f}")

            highlighted = highlight_text(ans_para, question)
            st.markdown(highlighted, unsafe_allow_html=True)


st.markdown("---")
st.subheader("Chunking preview")

chunk_size = st.number_input("Chunk size (characters)", min_value=200, max_value=1200, value=CHUNK_SIZE, step=100)
overlap = st.number_input("Overlap (characters)", min_value=100, max_value=200, value=OVERLAP, step=10)

if "chunks" not in st.session_state:
    st.session_state.chunks = []

if "chunk_source" not in st.session_state:
    st.session_state.chunk_source = ""

if "chunk_config" not in st.session_state:
    st.session_state.chunk_config = {}

current_config = {
    "source": upload_file.name,
    "chunk_size": int(chunk_size),
    "overlap": int(overlap),
}

if st.session_state.chunk_config != current_config:
    try:
        log("Starting chunking step: building chunks from file")
        chunks = build_chunks_from_file(str(upload_path), chunk_size, overlap)
        log(f"Chunking complete: {len(chunks)} chunks created")

        log("Exporting chunks to outputs/chunks_preview.json")
        export_chunks_json(chunks, "outputs/chunks_preview.json")
        log("Chunks exported to outputs/chunks_preview.json")

        st.session_state.chunks = chunks
        st.session_state.chunk_source = upload_file.name
        st.session_state.chunk_config = current_config
    except Exception as e:
        log(f"Chunking failed: {e}", level="error")
        st.error(f"Chunking failed: {e}")

if st.session_state.chunks:
    info_col1, info_col2, info_col3, info_col4, info_col5 = st.columns(5)
    with info_col1:
        st.metric("File", st.session_state.chunk_source)
    with info_col2:
        st.metric("Type", upload_path.suffix.lstrip(".") or "txt")
    with info_col3:
        st.metric("Characters", len(cleaned_text))
    with info_col4:
        st.metric("Pages", page_count)
    with info_col5:
        st.metric("Chunks", len(st.session_state.chunks))

    st.caption("First 5 chunks")
    for idx, chunk in enumerate(st.session_state.chunks[:5], start=1):
        # prefer metadata char_length, fall back to legacy char_count
        char_len = None
        if isinstance(chunk.get("metadata"), dict):
            char_len = chunk["metadata"].get("char_length")
        if char_len is None:
            char_len = chunk.get("char_count", 0)

        with st.expander(f"Chunk {idx} ({char_len} chars)"):
            st.write(chunk.get("text", ""))

    preview_path = Path("outputs") / "chunks_preview.json"
    if preview_path.exists():
        st.download_button(
            "Download chunks_preview.json",
            data=preview_path.read_bytes(),
            file_name="chunks_preview.json",
            mime="application/json",
        )

# --- Vector index controls ---
st.markdown("---")
st.subheader("Vector Index")

col_a, col_b = st.columns([3, 1])
with col_a:
    if st.button("Build / Rebuild Vector Index"):
        # perform indexing from outputs/chunks_preview.json
        preview_path = Path("outputs") / "chunks_preview.json"
        if not preview_path.exists():
            st.error("No chunks_preview.json found. Please generate chunks first.")
        else:
            try:
                collection_name = make_collection_name(upload_file.name)
                log(f"Starting indexing: loading chunks JSON and building embeddings/index into '{collection_name}'")
                index_chunks_from_json(
                    str(preview_path),
                    collection_name=collection_name,
                    persist_directory=VECTOR_PATH,
                    reset=True,
                )
                # count chunks from JSON
                with open(preview_path, "r", encoding="utf-8") as fh:
                    chunk_list = json.load(fh)
                total = len([c for c in chunk_list if c.get("text")])
                log(f"Indexing complete: {total} chunks indexed into collection '{collection_name}'")
                st.success(f"Indexing complete: {total} chunks indexed")
                st.session_state.last_indexed_count = total
            except Exception as e:
                log(f"Indexing failed: {e}", level="error")
                st.error(f"Indexing failed: {e}")

with col_b:
    indexed_count = st.session_state.get("last_indexed_count", None)
    st.metric("Indexed Chunks", indexed_count if indexed_count is not None else "-")

# ------------------------------
# Week 4 : RAG Question Answering
# ------------------------------

st.markdown("---")
st.subheader("Ask Questions using RAG")

rag_question = st.text_input(
    "Ask anything about the uploaded document",
    key="rag_question"
)

if st.button("Generate Answer"):

    if not rag_question.strip():
        st.error("Please enter a question.")

    else:

        try:
            collection_name = make_collection_name(upload_file.name)

            log(f"Generating answer from collection '{collection_name}'")

            pipeline = RAGPipeline(
                collection_name=collection_name,
                persist_directory=VECTOR_PATH
            )

            result = pipeline.answer_question(rag_question)
            answer_text = result["answer"]

            st.subheader("Answer")
            if answer_text.startswith("Error generating response:"):
                st.error(answer_text)
            else:
                st.success(answer_text)

            st.subheader("Sources")

            for source in result["sources"]:

                st.markdown(f"""
**File:** {source['file']}

**Page:** {source['page']}

**Chunk ID:** {source['chunk_id']}
                """)

                with st.expander("Preview"):

                    st.write(source["preview"])

            with st.expander("Retrieved Context"):

                st.write(result["context"])

            log("RAG answer generated successfully.")

        except Exception as e:

            log(f"RAG pipeline failed: {e}", level="error")
            st.error(f"RAG pipeline failed: {e}")
# Render UI logs at bottom
st.markdown("---")
st.subheader("Process Logs")
render_logs()