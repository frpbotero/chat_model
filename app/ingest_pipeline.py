"""ingest_pipeline.py – versão compatível com langchain‑community 0.3+ e qdrant‑client 1.7.x

Recursos:
- Controle de versão dos documentos
- Backup de versões antigas em coleção histórica
- Remoção opcional de versões anteriores
- Restauração de versões específicas
- Criação automática de coleções (principal + histórico)
- Evita erro 404 consultando stats antes de buscar
"""
from __future__ import annotations

from pathlib import Path
import datetime
from typing import List

from langchain_core.documents import Document
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    CSVLoader,
)
from langchain_community.document_loaders import UnstructuredMarkdownLoader as MarkdownHeaderLoader
from langchain.text_splitter import MarkdownHeaderTextSplitter
from splitters import RecursiveSplitter, TokenSplitter
from rag import vectorstore as _vectorstore  # store único criado em rag.py

from qdrant_client.http.models import (
    Filter,
    FieldCondition,
    MatchValue,
    VectorParams,
    Distance,
)

# ───────────────────────── Config ─────────────────────────
REMOVE_OLD_VERSIONS = True
SAVE_VERSION_HISTORY = True
VERSION_HISTORY_COLLECTION = "historico_ingestao"
EMBED_DIM = 384  # mesmo modelo E5‑small
# ──────────────────────────────────────────────────────────

# ─────────────────── Garantir coleções ───────────────────
vs_client = _vectorstore.client
for col in (_vectorstore.collection_name, VERSION_HISTORY_COLLECTION):
    if col not in [c.name for c in vs_client.get_collections().collections]:
        vs_client.recreate_collection(
            collection_name=col,
            vectors_config=VectorParams(size=EMBED_DIM, distance=Distance.COSINE),
        )
# ──────────────────────────────────────────────────────────

# Helpers --------------------------------------------------

def normalize(text: str) -> str:
    return " ".join(line.strip() for line in text.splitlines() if line.strip())


def enrich(doc: Document, file_path: str, version: str) -> Document:
    return Document(
        page_content=doc.page_content,
        metadata={
            **doc.metadata,
            "source_file": Path(file_path).name,
            "version": version,
            "ingested_at": datetime.datetime.utcnow().isoformat(),
        },
    )


def load_documents(path: str, version: str) -> List[Document]:
    ext = Path(path).suffix.lower()
    if ext == ".pdf":
        loader = PyPDFLoader(path)
    elif ext == ".md":
        loader = MarkdownHeaderLoader(path)
    elif ext == ".txt":
        loader = TextLoader(path)
    elif ext == ".csv":
        loader = CSVLoader(path)
    else:
        raise ValueError(f"Tipo de arquivo não suportado: {ext}")

    raw_docs = loader.load()
    return [enrich(Document(page_content=normalize(d.page_content), metadata=d.metadata), path, version) for d in raw_docs]


def select_splitter(file_path: str):
    ext = Path(file_path).suffix.lower()
    if ext == ".md":
        return MarkdownHeaderTextSplitter(headers_to_split_on=[("#", "h1"), ("##", "h2"), ("###", "h3")], strip_headers=True)
    elif ext == ".csv":
        return TokenSplitter.chunk_fixed_size_100_25()
    else:
        return RecursiveSplitter.chunk_recursive_100_15()

# Filtros --------------------------------------------------

def _filter_source(name: str) -> Filter:
    return Filter(must=[FieldCondition(key="source_file", match=MatchValue(value=name))])


def _filter_source_version(name: str, version: str) -> Filter:
    return Filter(
        must=[
            FieldCondition(key="source_file", match=MatchValue(value=name)),
            FieldCondition(key="version", match=MatchValue(value=version)),
        ]
    )

# Backup / remoção / restauração ---------------------------

# def backup_old_versions(store, file_path: str):
#     name = Path(file_path).name
#     # evita 404: só busca se houver pontos
#     stats = store.client.get_collection_stats(collection_name=store.collection_name)
#     if stats.points_count == 0:
#         return
#     old_docs = store.similarity_search("*", k=100, filter=_filter_source(name))
#     if not old_docs:
#         return
#     hist = _vectorstore
#     hist.collection_name = VERSION_HISTORY_COLLECTION
#     hist.add_documents(old_docs)
#     print(f"📦 Backup: {len(old_docs)} chunks → {VERSION_HISTORY_COLLECTION}")


# def remove_old_versions(store, file_path: str):
#     name = Path(file_path).name
#     store.client.delete(collection_name=store.collection_name, points_selector=_filter_source(name))
#     print(f"🗑️ Removido conteúdo antigo de {name}")


def restore_from_history(file_path: str, version: str):
    name = Path(file_path).name
    hist = _vectorstore
    hist.collection_name = VERSION_HISTORY_COLLECTION
    stats = hist.client.get_collection_stats(collection_name=VERSION_HISTORY_COLLECTION)
    if stats.points_count == 0:
        print("⚠️ Histórico vazio.")
        return
    docs = hist.similarity_search("*", k=200, filter=_filter_source_version(name, version))
    if not docs:
        print("⚠️ Versão não encontrada.")
        return
    main = _vectorstore
    # backup_old_versions(main, file_path)
    # remove_old_versions(main, file_path)
    main.add_documents(docs)
    print(f"✅ Restaurado {len(docs)} chunks → coleção principal")

# Pipeline -------------------------------------------------

def chunk_and_ingest(docs: List[Document], file_path: str):
    splitter = select_splitter(file_path)
    chunks = splitter.split_documents(docs)
    store = _vectorstore

    # if REMOVE_OLD_VERSIONS:
    #     if SAVE_VERSION_HISTORY:
        #     backup_old_versions(store, file_path)
        # remove_old_versions(store, file_path)

    store.add_documents(chunks)
    print(f"✅ {len(chunks)} chunks ingeridos")


def ingest_file(file_path: str, version: str = "v1"):
    print(f"\n📥 Ingestão: {file_path}  (versão {version})")
    docs = load_documents(file_path, version)
    chunk_and_ingest(docs, file_path)


# CLI ------------------------------------------------------
if __name__ == "__main__":
    ingest_file("to_ingest/Module 3.pdf", version="v1")
    # restore_from_history("to_ingest/Module 3.pdf", version="v0.9")
