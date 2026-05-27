import streamlit as st
from src.txt_processing import read_text_file,basic_clean_text, keyword_search,count_text_stats, split_into_paragraphs, highlight_text, semantic_search
st.title("Mini rag char with Document")

st.write("""Upload a .txt document and search for keywords or sentences inside the file.
    The app will:
    - Preview uploaded text
    - Count words
    - Count paragraphs
    - Search matching paragraphs""")

#file upload

upload_file = st.file_uploader("Upload TXT File", type=["txt"])
if upload_file is None:
    st.warning("File not uploaded please upload a txt file")
    st.stop()

#read file 
text = read_text_file(upload_file)

# Clean text 
cleaned_text = basic_clean_text(text)

st.subheader("Text preview")
st.text_area('Preview', cleaned_text[:2000], height=250, disabled=True)

#extracting the summary 0
stats = count_text_stats(cleaned_text)


paragraphs = split_into_paragraphs(cleaned_text)

word_count = stats["words"]
characters = stats["characters"]
sentences = stats["sentences"]
paragraph_count = len(paragraphs)

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


# ----------------------
# Ask a Question (semantic)
# ----------------------
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