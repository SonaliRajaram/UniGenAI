from backend.rag.vector_store import search

def retrieve_context(query: str) -> str:
    results = search(query)
    return "\n\n".join(results)
