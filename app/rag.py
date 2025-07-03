from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance
import os

QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
COLLECTION_NAME = "base_conhecimento"
EMBED_MODEL_NAME = "intfloat/multilingual-e5-small"
VECTOR_SIZE = 384  # dimensão do modelo E5-small

client = QdrantClient(url=QDRANT_URL, prefer_grpc=False, timeout=30, check_compatibility=False)

# cria a coleção se ainda não existir
if COLLECTION_NAME not in [c.name for c in client.get_collections().collections]:
    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )

embedder = HuggingFaceEmbeddings(model_name=EMBED_MODEL_NAME)

vectorstore = QdrantVectorStore(
    client=client,
    collection_name=COLLECTION_NAME,
    embedding=embedder,   # ✅ parâmetro correto
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

