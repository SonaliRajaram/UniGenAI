from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

# In-memory store (simple & fast)
DOCUMENTS = []
EMBEDDINGS = []


def add_documents(texts):
    embeddings = model.encode(texts)

    for text, emb in zip(texts, embeddings):
        DOCUMENTS.append(text)
        EMBEDDINGS.append(emb)


def search(query, top_k=5):
    if not DOCUMENTS:
        return []

    query_emb = model.encode([query])[0]

    scores = []
    for idx, emb in enumerate(EMBEDDINGS):
        score = np.dot(query_emb, emb)
        scores.append((score, DOCUMENTS[idx]))

    scores.sort(reverse=True, key=lambda x: x[0])
    return [doc for _, doc in scores[:top_k]]
