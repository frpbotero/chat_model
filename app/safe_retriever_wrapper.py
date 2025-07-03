"""safe_retriever_wrapper.py – robusto + fallback multi‑keywords

Melhorias:
• Se MMR não encontra nada, executa busca vetorial **por palavra‑chave**
  ("pagamento", "modalidade", etc.) e agrega os melhores chunks.
• Mantém filtro ≥2 palavras distintas na soma final.
• Nunca propaga exceções → devolve [] em último caso.
"""
from typing import List, Dict
from collections import defaultdict
from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document
from qdrant_client.http.exceptions import UnexpectedResponse

from rag import vectorstore

# 1) Vetorial MMR primário
retriever_mmr = vectorstore.as_retriever(
    search_type="mmr", search_kwargs={"k": 10, "fetch_k": 64}
)

_STOP = {
    "a", "as", "o", "os", "de", "do", "da", "das", "dos", "e", "em", "para", "pelo", "pela",
    "quais", "qual", "que", "um", "uma", "aceitas", "aceita", "tipo", "tipos"
}

# ---------- helpers --------------------------------------

def _significant_words(query: str) -> List[str]:
    return [w.lower() for w in query.split() if w.lower() not in _STOP and len(w) > 2]


def _keyword_union_search(query: str, k: int = 5) -> List[Document]:
    """Busca vetorial por **cada** palavra‑chave e devolve top‑k mais citados."""
    keywords = _significant_words(query)
    if not keywords:
        return []

    bucket: Dict[str, tuple[int, Document]] = defaultdict(lambda: (0, None))
    for w in keywords:
        try:
            docs = vectorstore.similarity_search(w, k=30)  # 30 docs por palavra
        except Exception:
            continue
        for d in docs:
            key = d.metadata.get("id") or d.page_content[:64]
            count, _ = bucket[key]
            bucket[key] = (count + 1, d)

    # Mantém somente docs citados por ≥2 palavras diferentes
    filtered = [(c, d) for c, d in bucket.values() if c >= 2]
    filtered.sort(key=lambda t: t[0], reverse=True)
    return [d for _, d in filtered][:k]


class SafeRetriever(BaseRetriever):
    """Retriever defensivo: MMR → fallback por palavras‑chave → []."""

    def _get_relevant_documents(self, query: str) -> List[Document]:
        # Coleção vazia?
        if vectorstore.client.count(collection_name=vectorstore.collection_name, exact=True).count == 0:
            return []

        # 1) Vetorial MMR
        try:
            docs = retriever_mmr.invoke(query)
            if docs:
                return docs[:5]
        except UnexpectedResponse:
            pass  # continua

        # 2) Busca por união de palavras‑chave
        docs_kw = _keyword_union_search(query, k=5)
        if docs_kw:
            return docs_kw

        # 3) Nada encontrado
        return []

    async def aget_relevant_documents(self, query: str) -> List[Document]:
        return self._get_relevant_documents(query)
