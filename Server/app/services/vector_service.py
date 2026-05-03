"""Chroma 向量索引服务。"""

import json

from flask import current_app
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

from app.models import KbChunk, KbDocument


class VectorStoreService:
    """封装 Chroma 与 Ollama Embedding 的常用操作。"""

    COLLECTION_NAME = "enterprise_qa_collection"

    @classmethod
    def _get_embeddings(cls):
        """初始化 Ollama 嵌入模型。"""

        return OllamaEmbeddings(
            model=current_app.config["OLLAMA_EMBED_MODEL"],
            base_url=current_app.config["OLLAMA_BASE_URL"],
        )

    @classmethod
    def _get_vector_store(cls):
        """获取本地持久化 Chroma 实例。"""

        return Chroma(
            collection_name=cls.COLLECTION_NAME,
            embedding_function=cls._get_embeddings(),
            persist_directory=current_app.config["CHROMA_PERSIST_DIR"],
        )

    @classmethod
    def remove_document_vectors(cls, document_id: int):
        """删除某个文档在 Chroma 中的已有向量，防止重复索引。"""

        vector_store = cls._get_vector_store()
        try:
            vector_store._collection.delete(where={"document_id": document_id})
        except Exception:
            return

    @classmethod
    def index_document(cls, document: KbDocument):
        """将数据库中的切片重新写入 Chroma。"""

        vector_store = cls._get_vector_store()
        cls.remove_document_vectors(document.id)

        chunks = (
            KbChunk.query.filter_by(document_id=document.id)
            .order_by(KbChunk.sequence.asc())
            .all()
        )
        if not chunks:
            return

        texts = [chunk.content for chunk in chunks]
        metadatas = []
        ids = []
        for chunk in chunks:
            chunk_meta = json.loads(chunk.meta_json or "{}")
            chunk_meta.update(
                {
                    "document_id": document.id,
                    "document_title": document.title,
                    "knowledge_base_id": document.knowledge_base_id,
                    "source": document.original_name,
                    "chunk_id": chunk.id,
                }
            )
            metadatas.append(chunk_meta)
            ids.append(chunk.vector_id)

        vector_store.add_texts(texts=texts, metadatas=metadatas, ids=ids)

    @classmethod
    def similarity_search(cls, knowledge_base_id: int, query: str, k: int = 4):
        """按知识库范围执行相似度检索。"""

        vector_store = cls._get_vector_store()
        return vector_store.similarity_search(
            query=query,
            k=k,
            filter={"knowledge_base_id": knowledge_base_id},
        )
