import chromadb
from chromadb.utils import embedding_functions
from typing import List, Optional, Union
import uuid
from pathlib import Path
from process_pdf import extract_text_from_pdf


class DocumentChunker:
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        self.collection = self.client.get_or_create_collection(
            name="document_chunks",
            embedding_function=self.embedding_fn
        )

    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        chunks, start = [], 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            if end < len(text):
                para_break = chunk.rfind("\n\n")
                sentence_break = max(chunk.rfind(". "), chunk.rfind("! "), chunk.rfind("? "))
                split = para_break if para_break != -1 else sentence_break
                if split != -1:
                    chunk, end = chunk[:split + 1], start + split + 1
            chunks.append(chunk.strip())
            start = end - overlap
        return [c for c in chunks if c]

    def add_document(self, text: str, metadata: Optional[dict] = None,
                     chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        chunks = self.chunk_text(text, chunk_size, overlap)
        ids = [str(uuid.uuid4()) for _ in chunks]
        metadatas = [{**(metadata or {}), "chunk_index": i, "total_chunks": len(chunks)}
                     for i in range(len(chunks))]
        self.collection.add(documents=chunks, ids=ids, metadatas=metadatas)
        return ids

    def search(self, query: str, n_results: int = 3,
               where: Optional[dict] = None) -> List[dict]:
        res = self.collection.query(query_texts=[query], n_results=n_results, where=where)
        return [
            {"text": res["documents"][0][i],
             "metadata": res["metadatas"][0][i],
             "id": res["ids"][0][i],
             "distance": res["distances"][0][i]}
            for i in range(len(res["documents"][0]))
        ]

    def process_pdfs(self, pdf_paths: Union[str, List[str]],
                     chunk_size: int = 1000, overlap: int = 200) -> None:
        if isinstance(pdf_paths, str):
            pdf_paths = [pdf_paths]

        for pdf in pdf_paths:
            path = Path(pdf)
            if not path.exists() or path.suffix.lower() != ".pdf":
                print(f"Skipping invalid file: {pdf}")
                continue

            text = extract_text_from_pdf(pdf)
            if not text:
                print(f"No text extracted from {pdf}")
                continue

            ids = self.add_document(text, {"source": str(pdf), "filename": path.name}, chunk_size, overlap)
            print(f"✅ {path.name}: {len(ids)} chunks")


if __name__ == "__main__":
    db = DocumentChunker()
    db.process_pdfs("path/to/your.pdf")

    for r in db.search("example query", n_results=2):
        print(f"- {r['text'][:80]}... ({r['distance']:.4f})")
