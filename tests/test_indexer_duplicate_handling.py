import json
import tempfile
import unittest
from pathlib import Path

from src import indexer


class FakeChroma:
    def __init__(self):
        self.stored_ids = set()
        self.delete_calls = []
        self.add_calls = []

    def delete(self, ids=None, **_kwargs):
        ids = list(ids or [])
        self.delete_calls.append(ids)
        for chunk_id in ids:
            self.stored_ids.discard(chunk_id)


def fake_add_chunks(chroma, chunks, ids=None, metadatas=None):
    ids = list(ids or [])
    assert len(ids) == len(set(ids)), "duplicate ids passed to add_chunks"

    overlap = set(ids) & chroma.stored_ids
    assert not overlap, f"duplicate ids still present before add: {sorted(overlap)}"

    chroma.add_calls.append(
        {
            "chunks": list(chunks),
            "ids": ids,
            "metadatas": list(metadatas or []),
        }
    )
    chroma.stored_ids.update(ids)


class IndexerDuplicateHandlingTest(unittest.TestCase):
    def test_duplicate_ids_are_deduplicated_and_reindexed_cleanly(self):
        fake_chroma = FakeChroma()

        with tempfile.TemporaryDirectory() as tmp_dir:
            json_path = Path(tmp_dir) / "chunks.json"
            payload = [
                {
                    "chunk_id": "doc_1_1",
                    "source_file": "doc.txt",
                    "file_type": "txt",
                    "page_number": 1,
                    "chunk_index": 1,
                    "text": "Alpha chunk",
                    "metadata": {"char_length": 11, "start_char": 0, "end_char": 11, "avg_char_value": 88.0},
                },
                {
                    "chunk_id": "doc_1_1",
                    "source_file": "doc.txt",
                    "file_type": "txt",
                    "page_number": 1,
                    "chunk_index": 1,
                    "text": "Alpha chunk duplicate",
                    "metadata": {"char_length": 22, "start_char": 0, "end_char": 22, "avg_char_value": 88.0},
                },
                {
                    "chunk_id": "doc_1_2",
                    "source_file": "doc.txt",
                    "file_type": "txt",
                    "page_number": 1,
                    "chunk_index": 2,
                    "text": "Beta chunk",
                    "metadata": {"char_length": 10, "start_char": 12, "end_char": 22, "avg_char_value": 89.0},
                },
            ]
            json_path.write_text(json.dumps(payload), encoding="utf-8")

            original_get_chroma = indexer.get_chroma
            original_reset_collection = indexer.reset_collection
            original_add_chunks = indexer.add_chunks

            try:
                indexer.get_chroma = lambda *args, **kwargs: fake_chroma
                indexer.reset_collection = lambda *args, **kwargs: fake_chroma
                indexer.add_chunks = fake_add_chunks

                indexer.index_chunks_from_json(str(json_path), collection_name="test_collection", reset=False)
                indexer.index_chunks_from_json(str(json_path), collection_name="test_collection", reset=False)
            finally:
                indexer.get_chroma = original_get_chroma
                indexer.reset_collection = original_reset_collection
                indexer.add_chunks = original_add_chunks

        self.assertEqual(len(fake_chroma.add_calls), 2)
        self.assertEqual(fake_chroma.add_calls[0]["ids"], ["doc_1_1", "doc_1_2"])
        self.assertEqual(fake_chroma.add_calls[1]["ids"], ["doc_1_1", "doc_1_2"])
        self.assertEqual(fake_chroma.stored_ids, {"doc_1_1", "doc_1_2"})
        self.assertEqual(fake_chroma.delete_calls[0], ["doc_1_1", "doc_1_2"])
        self.assertEqual(fake_chroma.delete_calls[1], ["doc_1_1", "doc_1_2"])


if __name__ == "__main__":
    unittest.main()