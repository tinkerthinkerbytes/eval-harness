"""
Embed corpus documents, chunk, and store in Chroma.

Uses the same paragraph-level chunking strategy as Build 1 (rag-pipeline) so that
retrieval quality is comparable across builds — the pipeline under evaluation here
is not meaningfully different from the one being harness-tested.
"""
import re
from collections import Counter
from pathlib import Path

import chromadb
from openai import OpenAI

EMBED_MODEL = "text-embedding-3-small"
CHUNK_MAX_CHARS = 500
CHROMA_PATH = ".chroma"
COLLECTION_NAME = "eval_corpus"


def load_docs(corpus_dir: str) -> list[dict]:
    docs = []
    for path in sorted(Path(corpus_dir).glob("*.md")):
        docs.append({"source": path.name, "text": path.read_text(encoding="utf-8")})
    return docs


def chunk_doc(source: str, text: str) -> list[dict]:
    """
    Paragraph-level chunking with sentence-boundary fallback for oversized paragraphs.
    Preserves semantic units (a paragraph is a coherent thought) while preventing
    chunks large enough to degrade embedding quality.
    """
    paragraphs = [p.strip() for p in re.split(r"\n\n+", text) if p.strip()]
    chunks = []
    for para in paragraphs:
        if len(para) <= CHUNK_MAX_CHARS:
            chunks.append(para)
        else:
            sentences = re.split(r"(?<=\.)\s+", para)
            current = ""
            for sent in sentences:
                if len(current) + len(sent) + 1 <= CHUNK_MAX_CHARS:
                    current = (current + " " + sent).strip()
                else:
                    if current:
                        chunks.append(current)
                    current = sent
            if current:
                chunks.append(current)

    return [
        {"chunk_id": f"{source}::{i}", "source": source, "text": chunk}
        for i, chunk in enumerate(chunks)
    ]


def embed_texts(texts: list[str], client: OpenAI) -> list[list[float]]:
    response = client.embeddings.create(model=EMBED_MODEL, input=texts)
    return [item.embedding for item in response.data]


def ingest(corpus_dir: str = "corpus") -> None:
    oai = OpenAI()
    chroma = chromadb.PersistentClient(path=CHROMA_PATH)

    try:
        chroma.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = chroma.create_collection(
        COLLECTION_NAME,
        metadata={"hf:space": "cosine"},
    )

    docs = load_docs(corpus_dir)
    if not docs:
        raise FileNotFoundError(f"No .md files found in {corpus_dir}/")

    all_chunks = []
    for doc in docs:
        all_chunks.extend(chunk_doc(doc["source"], doc["text"]))

    print(f"Ingesting {len(all_chunks)} chunks from {len(docs)} documents...")

    texts = [c["text"] for c in all_chunks]
    embeddings = embed_texts(texts, oai)

    collection.add(
        ids=[c["chunk_id"] for c in all_chunks],
        embeddings=embeddings,
        documents=texts,
        metadatas=[{"source": c["source"]} for c in all_chunks],
    )

    counts = Counter(c["source"] for c in all_chunks)
    for src, count in sorted(counts.items()):
        print(f"  {src}: {count} chunks")
    print(f"Done. Vector store at {CHROMA_PATH}/")
