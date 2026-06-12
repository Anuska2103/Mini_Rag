import unittest

from src.embedding_service import embed_text, embed_texts


class EmbeddingSmokeTest(unittest.TestCase):
    def test_single_embedding_smoke(self):
        text = "This is a short test sentence."
        vec = embed_text(text)

        print("Single vector length:", len(vec))
        self.assertIsInstance(vec, list)
        self.assertGreater(len(vec), 0)
        self.assertTrue(all(isinstance(x, (float, int)) for x in vec))

    def test_multiple_embeddings_smoke(self):
        texts = [
            "First chunk of text.",
            "Second chunk of text.",
            "Third chunk of text.",
        ]
        vecs = embed_texts(texts)

        print("Number of vectors:", len(vecs))
        self.assertIsInstance(vecs, list)
        self.assertEqual(len(vecs), len(texts))

        for i, v in enumerate(vecs):
            print(f"Vector {i} length:", len(v))
            self.assertIsInstance(v, list)
            self.assertGreater(len(v), 0)
            self.assertTrue(all(isinstance(x, (float, int)) for x in v))


if __name__ == "__main__":
    unittest.main()
