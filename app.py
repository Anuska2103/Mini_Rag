from pathlib import Path

import streamlit as st

from src.chunking import build_chunks_from_file, export_chunks_json
from src.document_loader import load_document_text
from src.text_cleaning import clean_document_records
from src.txt_processing import basic_clean_text, keyword_search, count_text_stats, split_into_paragraphs, highlight_text, semantic_search
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

chunk_size = st.number_input("Chunk size (characters)", min_value=200, max_value=1200, value=1000, step=100)
overlap = st.number_input("Overlap (characters)", min_value=100, max_value=200, value=200, step=10)

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
    chunks = build_chunks_from_file(str(upload_path), chunk_size, overlap)
    export_chunks_json(chunks, "outputs/chunks_preview.json")
    st.session_state.chunks = chunks
    st.session_state.chunk_source = upload_file.name
    st.session_state.chunk_config = current_config

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
        with st.expander(f"Chunk {idx} ({chunk.get('char_count', 0)} chars)"):
            st.write(chunk.get("text", ""))

    preview_path = Path("outputs") / "chunks_preview.json"
    if preview_path.exists():
        st.download_button(
            "Download chunks_preview.json",
            data=preview_path.read_bytes(),
            file_name="chunks_preview.json",
            mime="application/json",
        )