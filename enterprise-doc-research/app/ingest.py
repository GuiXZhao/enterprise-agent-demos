import io
from pathlib import Path

from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

from app.config import CHROMA_DIR, CHUNK_OVERLAP, CHUNK_SIZE
from app.llm import get_embeddings


def _read_bytes(filename: str, raw: bytes) -> str:
    name = filename.lower()
    if name.endswith(".txt"):
        for encoding in ("utf-8", "gbk"):
            try:
                return raw.decode(encoding)
            except UnicodeDecodeError:
                continue
        return raw.decode("utf-8", errors="ignore")
    if name.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(raw))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    raise ValueError(f"不支持的文件类型: {filename}")


def _split_documents(docs: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", "。", "；", " ", ""],
    )
    return splitter.split_documents(docs)


def get_vectorstore() -> Chroma | None:
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    if not any(CHROMA_DIR.iterdir()):
        return None
    return Chroma(
        persist_directory=str(CHROMA_DIR),
        embedding_function=get_embeddings(),
    )


def ingest_file(filename: str, raw: bytes) -> dict:
    text = _read_bytes(filename, raw)
    if not text.strip():
        raise ValueError(f"文件内容为空: {filename}")

    base_doc = Document(
        page_content=text,
        metadata={"source": filename, "doc_id": filename},
    )
    chunks = _split_documents([base_doc])
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = str(i)

    store = get_vectorstore()
    if store is None:
        CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        store = Chroma.from_documents(
            chunks,
            get_embeddings(),
            persist_directory=str(CHROMA_DIR),
        )
    else:
        store.add_documents(chunks)

    from app.retrieval import invalidate_retrieval_cache

    invalidate_retrieval_cache()
    return {
        "filename": filename,
        "chunk_count": len(chunks),
        "char_count": len(text),
    }


def ingest_path(path: Path) -> dict:
    return ingest_file(path.name, path.read_bytes())


def load_sample_docs() -> list[dict]:
    from app.config import SAMPLE_DOCS_DIR

    results = []
    if not SAMPLE_DOCS_DIR.exists():
        return results
    for file_path in sorted(SAMPLE_DOCS_DIR.glob("*.txt")):
        results.append(ingest_path(file_path))
    return results
