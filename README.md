# Mini RAG: Intelligent Document Search & Analysis

## Project Overview

Mini RAG is a Retrieval-Augmented Generation (RAG) application built
using Streamlit and LangChain that enables users to upload documents,
preprocess them, generate semantic embeddings, index them in a vector
database, and retrieve relevant information efficiently.

Repository: https://github.com/Anuska2103/Mini_Rag

## Problem Statement

Traditional document search systems rely heavily on exact keyword
matching and often fail to retrieve contextually relevant information.
Mini RAG demonstrates the evolution from keyword-based retrieval to
embedding-powered semantic retrieval.

# Week 1 Scope

## Features Implemented

-   TXT document upload and preview
-   Text cleaning and preprocessing
-   Document statistics generation
-   Keyword search with highlighting
-   TF-IDF based semantic search
-   Cosine similarity scoring

# Week 2 Scope

## Features Implemented

-   Support for TXT and PDF documents
-   PDF text extraction using PyPDF
-   Metadata generation for document records
-   Chunk generation with overlap
-   JSON export of processed chunks
-   Schema-based chunk validation

# Week 3 Scope

## LangChain Integration

LangChain components were integrated to build a production-style RAG
pipeline.

### Recursive Chunking

``` python
from langchain_text_splitters import RecursiveCharacterTextSplitter
```

Configuration: - Chunk Size: 1000 - Chunk Overlap: 200 - Start index
tracking enabled

### Embedding Generation

Implemented in:

    src/embedding_service.py

Model Used:

    sentence-transformers/all-mpnet-base-v2

Configuration:

``` python
HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-mpnet-base-v2",
    encode_kwargs={"normalize_embeddings": True},
)
```

Capabilities: - Single text embedding - Batch embedding generation -
Normalized embeddings for retrieval

### Vector Database Integration

Implemented in:

    src/vector_store.py

Features: - Chroma collection creation - Persistent vector storage -
Metadata storage - Similarity retrieval - Collection reset

### Document Indexing Pipeline

Implemented in:

    src/indexer.py

Workflow: 1. Load chunk records 2. Generate embeddings 3. Attach
metadata 4. Store vectors in Chroma 5. Prepare retrieval pipeline

### Embedding Validation

Implemented in:

    tests/test_embedding_smoke.py

Validation: - Model loading - Embedding generation - Dimension
consistency - Batch embedding checks

## Tools & Libraries Used

  Library                    Purpose
  -------------------------- ------------------------------
  Streamlit                  User interface
  LangChain                  RAG orchestration
  LangChain HuggingFace      Embedding integration
  LangChain Chroma           Chroma integration
  LangChain Text Splitters   Recursive chunking
  ChromaDB                   Vector database
  Sentence Transformers      Embedding generation
  Transformers               Model backend
  PyPDF                      PDF text extraction
  Scikit-learn               TF-IDF and cosine similarity
  NumPy                      Numerical operations
  Pandas                     Data processing

## Setup

``` bash
git clone https://github.com/Anuska2103/Mini_Rag.git
cd Mini_Rag
python -m venv venv
```

Windows:

``` bash
venv\Scripts\activate
```

Linux/macOS:

``` bash
source venv/bin/activate
```

Install dependencies:

``` bash
pip install -r requirements.txt
```

## Run Application

``` bash
streamlit run app.py
```

## Folder Structure

``` text
Mini_Rag/
├── app.py
├── requirements.txt
├── README.md
├── data/
├── outputs/
├── src/
│   ├── chunking.py
│   ├── document_loader.py
│   ├── embedding_service.py
│   ├── indexer.py
│   ├── schemas.py
│   ├── text_cleaning.py
│   ├── txt_processing.py
│   └── vector_store.py
├── tests/
│   └── test_embedding_smoke.py
└── venv/
```

## Current Limitations

-   OCR support for scanned PDFs is unavailable.
-   LLM-based answer generation is not implemented.
-   Hybrid retrieval is not supported.
-   Multi-document conversational memory is unavailable.

## Future Enhancements

-   Integrate LLMs for answer generation.
-   Add conversational memory.
-   Implement hybrid retrieval.
-   Support OCR for scanned PDFs.
-   Add Docker support.
-   Enable cloud deployment.

## Version History

  Version   Milestone
  --------- ------------------------------------------
  v1.0      Week 1 -- Traditional Retrieval
  v1.1      Week 2 -- Document Processing Pipeline
  v1.2      Week 3 -- Embeddings and Vector Indexing

## License

Educational and learning purposes.
