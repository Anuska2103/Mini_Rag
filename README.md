# Mini RAG: Intelligent Document Search & Analysis

## Project Overview

**Mini RAG** is a Retrieval-Augmented Generation (RAG) application built with Streamlit that enables users to upload text documents and intelligently search through them using both keyword-based and semantic search capabilities. The application provides a user-friendly interface for document analysis, including text statistics, paragraph extraction, and AI-powered question answering with confidence scoring.

---

## Problem Statement

Users often need to search through long text documents to find specific information. Traditional document search methods rely on exact keyword matching, which may miss relevant content that uses different terminology. Mini RAG solves this by:

- Enabling both **keyword-based search** (exact phrase matching)
- Providing **semantic search** (understanding meaning and context)
- Offering **document statistics** (word count, character count, sentence count)
- Allowing **interactive result navigation** with highlighted matches

This tool is ideal for researchers, students, and professionals who need to quickly extract and analyze information from text documents.

---

## Week 1 Scope

### Core Features Implemented

1. **Document Upload & Preview**
   - Upload `.txt` files through a simple UI
   - Display first 2000 characters of cleaned text

2. **Text Analysis**
   - Count total words, paragraphs, sentences, and characters
   - Display metrics in an easy-to-read dashboard format

3. **Keyword Search**
   - Search for specific keywords or phrases in the document
   - Navigate through multiple matching results
   - Highlight matching text with `<mark>` tags

4. **Semantic Search**
   - Ask natural language questions
   - Use TF-IDF vectorization and cosine similarity
   - Return best-matching paragraphs with confidence scores


---

## Tools & Libraries Used

| Tool/Library | Version | Purpose |
|---|---|---|
| **Streamlit** | 1.57.0 | Web app framework for interactive UI |
| **NumPy** | 2.4.6 | Numerical computing |
| **Pandas** | 3.0.3 | Data manipulation (optional enhancement) |
| **Scikit-learn** | 1.8.0 | TF-IDF vectorizer & cosine similarity |

| **Charset Normalizer** | 3.4.7 | Text encoding handling |

---

## Setup Instructions

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Step-by-Step Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Anuska2103/Mini_Rag.git
   cd Mini_Rag
   ```

2. **Create a Virtual Environment** (Recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate    # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify Installation**
   ```bash
   python -c "import streamlit; print('✓ Streamlit installed')"
   python -c "from sklearn.feature_extraction.text import TfidfVectorizer; print('✓ Scikit-learn installed')"
   ```

---

## How to Run the Streamlit App

### Launch the Application

```bash
streamlit run app.py
```

The app will start on `http://localhost:8501` (or another available port).

### Using the Application

1. **Upload a Document**
   - Click "Upload TXT File" and select a `.txt` file
   - The app will display a preview of the cleaned text

2. **View Document Statistics**
   - See word count, paragraph count, sentence count, and character count

3. **Keyword Search**
   - Enter a keyword or phrase in "Enter keyword or question"
   - Click "Search Document"
   - Navigate through results using Previous/Next buttons
   - Matched text is highlighted in yellow

4. **Semantic Search**
   - Scroll to "Ask a question about this document"
   - Enter a natural language question
   - Click "Ask Question" to find the most relevant paragraph
   - View the confidence score for the answer

---

## Folder Structure

```
Mini_Rag/
├── app.py                          # Main Streamlit application
├── demo_run.py                     # Demo script for testing functions
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── data/                           # Sample data folder
│   └── Artificial Intelligence is transfor.txt  # Example document
├── src/                            # Source code directory
│   ├── __pycache__/               # Python cache files
│   └── txt_processing.py          # Core text processing module
└── venv/                           # Virtual environment (local)
```

---

## Function Workflow & Documentation

### Core Module: `src/txt_processing.py`

#### 1. **`read_text_file(uploaded_file)`**
   - **Purpose**: Read uploaded text file from Streamlit file uploader
   - **Input**: Streamlit UploadedFile object
   - **Output**: Text string (UTF-8 decoded)
   - **Workflow**:
     ```
     uploaded_file → decode UTF-8 → return text
     ```
   - **Error Handling**: Returns "Error reading file" on exception

---

#### 2. **`basic_clean_text(text)`**
   - **Purpose**: Clean raw text by removing extra whitespace and normalizing paragraphs
   - **Input**: Raw text string
   - **Output**: Cleaned text with normalized paragraphs
   - **Workflow**:
     ```
     1. Split text into lines
     2. Strip whitespace from each line
     3. Group consecutive non-empty lines into paragraphs
     4. Join paragraphs with double newlines (\n\n)
     ```
   - **Example**:
     ```
     Input:  "Hello world\n\n\nHow are you?\nI am fine"
     Output: "Hello world\n\nHow are you? I am fine"
     ```

---

#### 3. **`count_text_stats(text)`**
   - **Purpose**: Calculate text statistics (word, character, sentence counts)
   - **Input**: Cleaned text string
   - **Output**: Dictionary with keys: `characters`, `words`, `sentences`
   - **Workflow**:
     ```
     1. Count total characters: len(text)
     2. Count words: split by whitespace and count
     3. Count sentences: count occurrences of . ! ?
     4. Return stats dictionary
     ```
   - **Usage**: Displays metrics in Streamlit dashboard

---

#### 4. **`split_into_paragraphs(text)`**
   - **Purpose**: Split cleaned text into individual paragraphs
   - **Input**: Cleaned text string
   - **Output**: List of paragraph strings
   - **Workflow**:
     ```
     1. Split text by double newlines (\n\n)
     2. Strip whitespace from each paragraph
     3. Filter out empty paragraphs
     4. Return list of paragraphs
     ```
   - **Used By**: `keyword_search()`, `semantic_search()`

---

#### 5. **`keyword_search(text, query)`**
   - **Purpose**: Find paragraphs containing exact keyword or phrase match
   - **Input**: Text string, query string
   - **Output**: List of matching paragraphs
   - **Workflow**:
     ```
     1. Split text into paragraphs
     2. Validate query is not empty
     3. Create regex pattern:
        - Single word: \bword\b (whole word match)
        - Multi-word: exact phrase (case-insensitive)
     4. Search each paragraph for pattern match
     5. Return list of matching paragraphs
     ```
   - **Example**:
     ```
     Query: "Python"
     Returns all paragraphs containing "Python" (case-insensitive)
     ```

---

#### 6. **`highlight_text(text, query)`**
   - **Purpose**: HTML-highlight matched query terms in text
   - **Input**: Text string, query string
   - **Output**: HTML string with `<mark>` tags around matches
   - **Workflow**:
     ```
     1. Escape special regex characters in query
     2. Create case-insensitive regex pattern
     3. Replace all matches with <mark>{match}</mark>
     4. Return HTML string
     ```
   - **Output Example**:
     ```html
     "Python is great" → "Python is <mark>great</mark>"
     ```

---

#### 7. **`semantic_search(text, question)`**
   - **Purpose**: Find paragraphs semantically similar to a question using TF-IDF + cosine similarity
   - **Input**: Text string, question string
   - **Output**: List of dictionaries with paragraph and similarity score
   - **Workflow**:
     ```
     1. Split text into paragraphs
     2. Combine [question] + [all paragraphs] into list
     3. Initialize TfidfVectorizer (converts text to numerical vectors)
     4. Transform all text into TF-IDF vectors
     5. Extract query vector (first vector)
     6. Extract paragraph vectors (remaining vectors)
     7. Calculate cosine similarity between query and each paragraph
     8. Filter results with similarity > 0.1 (threshold)
     9. Sort by similarity score (highest first)
     10. Return list of {paragraph, score} dictionaries
     ```
   - **Similarity Score**: Ranges from 0 (no match) to 1 (perfect match)
   - **Example**:
     ```python
     Question: "What is AI?"
     Returns: [
       {"paragraph": "AI is machine learning...", "score": 0.85},
       {"paragraph": "Artificial intelligence uses...", "score": 0.72}
     ]
     ```

---

### Main Application: `app.py`

**Application Flow**:

```
1. Display title and instructions
   ↓
2. File Upload
   ├─ Get uploaded file from user
   └─ Stop if no file
   ↓
3. Read & Clean
   ├─ read_text_file() → get raw text
   ├─ basic_clean_text() → normalize text
   └─ Display preview (first 2000 characters)
   ↓
4. Text Statistics
   ├─ count_text_stats() → get word/char/sentence counts
   ├─ split_into_paragraphs() → get paragraph list
   └─ Display metrics in 4-column dashboard
   ↓
5. Keyword Search
   ├─ Get user query
   ├─ On button click:
   │  ├─ Validate input
   │  ├─ keyword_search() → find matches
   │  └─ Store results in session state
   ├─ Display results with navigation
   └─ highlight_text() → show matches with highlighting
   ↓
6. Semantic Search
   ├─ Get user question
   ├─ On button click:
   │  ├─ Validate input
   │  ├─ semantic_search() → find best match
   │  └─ highlight_text() → highlight keywords
   └─ Display answer with confidence score
```

---

## Session State Variables

Streamlit maintains these session variables to preserve state across interactions:

| Variable | Type | Purpose |
|---|---|---|
| `current_result` | int | Current result index in keyword search results |
| `results` | list | List of matching paragraphs from keyword search |
| `query` | str | The current search query |

---

## Team Members and Roles

| Member | Role |
|---|---|
| Anuska2103 | Project Lead, Full Stack Developer |
| (Contributor slots open) | Backend/ML Development, UI/UX Enhancement |

---

## Known Limitations & Future Improvements

### Current Limitations

1. **Text-Only Input**
   - Currently supports `.txt` files only
   - No PDF, DOCX, or image document support

2. **Semantic Search Threshold**
   - Fixed 0.1 similarity threshold may miss relevant results
   - No user-configurable threshold

3. **No Persistent Storage**
   - Search results are not saved between sessions
   - No history or logging of searches

4. **Limited Context**
   - Semantic search returns single paragraphs
   - No multi-paragraph context expansion

5. **Performance**
   - TF-IDF vectorization not cached; recalculated on each search
   

6. **Language Support**
   - Optimized for English text
   - Limited support for non-Latin alphabets

### Next Steps (Future Roadmap)

- [ ] **Multi-format Support**: Add PDF, DOCX, and image OCR support
- [ ] **Batch Processing**: Process multiple documents simultaneously
- [ ] **Advanced Vectorization**: Integrate sentence-transformers or embeddings (e.g., OpenAI) for better semantic search
- [ ] **Caching**: Implement vector caching for improved performance
- [ ] **Persistent History**: Store and retrieve past searches
- [ ] **Export Results**: Save search results to CSV/JSON
- [ ] **Multi-language**: Support for non-English documents
- [ ] **Fine-tuned Models**: Train custom models for domain-specific search
- [ ] **API Development**: Expose functionality via REST API
- [ ] **Docker Containerization**: Streamlined deployment

---

## Running the Demo

For testing without the Streamlit UI, run the demo script:

```bash
python demo_run.py
```

This will test core functions with the sample document:
- Text statistics
- Paragraph splitting
- Keyword search

---

## Troubleshooting

| Issue | Solution |
|---|---|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| File upload fails | Ensure file is `.txt` encoding (UTF-8 recommended) |
| Semantic search is slow | Reduce document size or upgrade system specs |
| No results found | Try different keywords or simpler queries |
| App won't start | Check port 8501 is available or use `streamlit run app.py --server.port 8502` |

---

## License

This project is open source. Refer to LICENSE file for details.

---

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/YourFeature`)
3. Commit changes (`git commit -m 'Add YourFeature'`)
4. Push to branch (`git push origin feature/YourFeature`)
5. Open a Pull Request

---

## Contact & Support

For issues, questions, or suggestions:
- **GitHub Issues**: [Create an issue](https://github.com/Anuska2103/Mini_Rag/issues)
- **Project Repository**: https://github.com/Anuska2103/Mini_Rag

---

**Last Updated**: May 2026  
**Version**: 1.0.0
