import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def read_text_file(uploaded_file):

    try:
        return uploaded_file.read().decode("utf-8")

    except Exception as e:

        print("Error:", e)

        return "Error reading file"

def basic_clean_text(text):
    
    try:
        lines = [ln.strip() for ln in text.splitlines()]

        paragraphs = []
        current = []
        for ln in lines:
            if ln == "":
                if current:
                    paragraphs.append(" ".join(current))
                    current = []
            else:
                current.append(ln)

        if current:
            paragraphs.append(" ".join(current))

        return "\n\n".join(paragraphs)
    except Exception as e:
        print(f"basic_clean_text error: {e}")
        return ""

def count_text_stats(text):
    try:
        characters = len(text)
        words = len(text.split())
        sentences = text.count(".") + text.count("!") + text.count("?")

        return {
            "characters": characters,
            "words": words,
            "sentences": sentences,
        }
    except Exception as e:
        print(f"count_text_stats error: {e}")
        return {"characters": 0, "words": 0, "sentences": 0}

def split_into_paragraphs(text):
    try:
        paragraphs = text.split("\n\n")

        clean_paras = []
        for p in paragraphs:
            p = p.strip()
            if p:
                clean_paras.append(p)

        return clean_paras
    except Exception as e:
        print(f"split_into_paragraphs error: {e}")
        return []


def keyword_search(text, query):
    try:
        paragraphs = split_into_paragraphs(text)
        matches = []

        q = query.strip()
        if not q:
            return []

        
        if " " in q:
            pattern = re.compile(re.escape(q), re.IGNORECASE)
        else:
            pattern = re.compile(r"\b" + re.escape(q) + r"\b", re.IGNORECASE)

        for para in paragraphs:
            if pattern.search(para):
                matches.append(para)

        return matches
    except Exception as e:
        print(f"keyword_search error: {e}")
        return []

def highlight_text(text, query):
    try:
        if not query:
            return text

        # Simple case-insensitive highlight using regex
        esc = re.escape(query)
        pattern = re.compile(esc, re.IGNORECASE)

        def _repl(m):
            return f"<mark>{m.group(0)}</mark>"

        return pattern.sub(_repl, text)
    except Exception as e:
        print(f"highlight_text error: {e}")
        return text
    


#sematic search
def semantic_search(text, query):

    
    paragraphs = split_into_paragraphs(text)

    
    all_text = [query] + paragraphs

    vectorizer = TfidfVectorizer()

    vectors = vectorizer.fit_transform(all_text)    
    query_vector = vectors[0]
    paragraph_vectors = vectors[1:]

    
    similarities = cosine_similarity(
        query_vector,
        paragraph_vectors
    )[0]

    
    results = []

    for i, score in enumerate(similarities):

        # similarity threshold
        if score > 0.1:

            results.append({
                "paragraph": paragraphs[i],
                "score": score
            })

    # Sort best matches first
    results = sorted(
        results,
        key=lambda x: x["score"],
        reverse=True
    )

    return results