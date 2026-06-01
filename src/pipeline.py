"""
RAG pipeline — the system under evaluation.

Mirrors Build 1's retrieve → generate pattern. Kept in this repo so the
eval harness is fully standalone with no cross-repo imports.

The pipeline is deliberately kept thin: its job here is to be the thing being
evaluated, not to showcase retrieval engineering. See Build 1 (rag-pipeline)
for that implementation and its design commentary.
"""
import chromadb
from openai import OpenAI

from .ingest import CHROMA_PATH, COLLECTION_NAME, EMBED_MODEL

GENERATION_MODEL = "gpt-4.1-nano"

SYSTEM_PROMPT = (
    "You are a SOC analyst assistant. Answer questions using ONLY the provided context. "
    "Cite the source document filename for every claim you make. "
    "If the context does not contain sufficient information to answer, say so explicitly — "
    "do not invent facts."
)


def retrieve(query: str, top_k: int = 3) -> list[dict]:
    """Embed query and return top_k chunks by cosine similarity."""
    oai = OpenAI()
    try:
        chroma = chromadb.PersistentClient(path=CHROMA_PATH)
        collection = chroma.get_collection(COLLECTION_NAME)
    except Exception:
        raise RuntimeError(
            f"Vector store not found at '{CHROMA_PATH}/'. Run: python main.py ingest"
        )

    response = oai.embeddings.create(model=EMBED_MODEL, input=[query])
    query_embedding = response.data[0].embedding

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    return [
        {
            "chunk_id": results["ids"][0][i],
            "source": results["metadatas"][0][i]["source"],
            "text": results["documents"][0][i],
            "distance": round(results["distances"][0][i], 4),
        }
        for i in range(len(results["ids"][0]))
    ]


def _format_context(chunks: list[dict]) -> str:
    return "\n\n".join(
        f"[{i}] (source: {chunk['source']})\n{chunk['text']}"
        for i, chunk in enumerate(chunks, 1)
    )


def generate(query: str, chunks: list[dict]) -> dict:
    """Inject retrieved chunks into prompt and return grounded response."""
    oai = OpenAI()
    context = _format_context(chunks)
    user_message = f"Context:\n{context}\n\nQuestion: {query}"

    completion = oai.chat.completions.create(
        model=GENERATION_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.1,
    )

    return {
        "response": completion.choices[0].message.content,
        "sources_used": sorted({c["source"] for c in chunks}),
        "retrieved_chunks": chunks,
    }
