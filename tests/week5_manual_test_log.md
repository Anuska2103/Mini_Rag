# Week 5 Manual Test Log

## Scope
- PDF questions
- TXT questions
- Insufficient context
- Duplicate indexing
- Multiple documents
- Source display

## Test Log

| Test Case | Expected | Actual | Status | Remarks |
| --- | --- | --- | --- | --- |
| PDF questions | The app should answer questions from an uploaded PDF and cite the correct chunk source. | Not run in this session. | Pending | Verify after uploading a PDF in Streamlit. |
| TXT questions | The app should answer questions from an uploaded TXT file and return relevant context. | Not run in this session. | Pending | Verify after uploading a TXT file in Streamlit. |
| Insufficient context | The app should say no relevant information was found when the document does not contain the answer. | Not run in this session. | Pending | Check both RAG answer and search output. |
| Duplicate indexing | Re-indexing the same chunks should not create duplicate vector entries, and duplicate chunk IDs in the input should be skipped safely. | Covered by automated test: duplicate IDs are deduplicated before indexing and repeated indexing leaves one copy per ID. | Pass | See tests/test_indexer_duplicate_handling.py. |
| Multiple documents | Different uploaded documents should index into separate collections and not overwrite each other. | Not run in this session. | Pending | Verify using two different uploads. |
| Source display | Retrieved answers should show file name, page number, chunk ID, and preview text. | Not run in this session. | Pending | Confirm source cards are visible in the UI. |