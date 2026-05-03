"""RAG 问答服务。"""

import json
import time
from datetime import datetime

from flask import current_app
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from app.extensions import db
from app.models import KnowledgeBase, QaMessage, QaSession
from app.services.vector_service import VectorStoreService


class RagService:
    """负责会话管理、向量检索与模型回答生成。"""

    @classmethod
    def _get_llm(cls):
        """初始化 Ollama 对话模型。"""

        return ChatOllama(
            model=current_app.config["OLLAMA_LLM_MODEL"],
            base_url=current_app.config["OLLAMA_BASE_URL"],
            temperature=0.2,
        )

    @staticmethod
    def _build_prompt():
        """构造约束型问答提示词，确保模型只基于知识库回答。"""

        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    (
                        "你是企业内部知识库问答助手。"
                        "请仅基于提供的知识库片段回答问题。"
                        "如果知识库没有明确答案，请直接回答“未检索到相关信息，请补充知识库内容或调整提问方式”。"
                        "回答要简洁、专业，并优先使用中文。"
                    ),
                ),
                (
                    "human",
                    "知识库片段如下：\n{context}\n\n用户问题：{question}",
                ),
            ]
        )

    @classmethod
    def _get_or_create_session(cls, user_id: int, knowledge_base_id: int, session_id=None):
        """获取已有会话，或根据第一条问题创建新会话。"""

        if session_id:
            return QaSession.query.filter_by(id=session_id, user_id=user_id).first()

        knowledge_base = KnowledgeBase.query.get(knowledge_base_id)
        title = f"{knowledge_base.name}问答会话" if knowledge_base else "知识库会话"
        session = QaSession(
            user_id=user_id,
            knowledge_base_id=knowledge_base_id,
            title=title,
            last_question_at=datetime.utcnow(),
        )
        db.session.add(session)
        db.session.commit()
        return session

    @classmethod
    def ask(cls, user_id: int, knowledge_base_id: int, question: str, session_id=None):
        """执行完整的 RAG 问答流程，并落库历史消息。"""

        session = cls._get_or_create_session(user_id, knowledge_base_id, session_id)
        if not session:
            raise ValueError("会话不存在或无权访问")

        start_time = time.time()
        docs = VectorStoreService.similarity_search(knowledge_base_id, question, k=4)

        sources = []
        context_blocks = []
        for index, doc in enumerate(docs, start=1):
            metadata = doc.metadata or {}
            excerpt = doc.page_content[:160]
            sources.append(
                {
                    "documentName": metadata.get("document_title") or metadata.get("source"),
                    "source": metadata.get("source"),
                    "chunkId": metadata.get("chunk_id"),
                    "excerpt": excerpt,
                }
            )
            context_blocks.append(f"[片段{index}] {doc.page_content}")

        if not context_blocks:
            answer = "未检索到相关信息，请补充知识库内容或调整提问方式。"
        else:
            prompt = cls._build_prompt()
            chain = prompt | cls._get_llm()
            result = chain.invoke({"context": "\n\n".join(context_blocks), "question": question})
            answer = getattr(result, "content", str(result))

        elapsed_ms = int((time.time() - start_time) * 1000)

        if session.title.endswith("问答会话"):
            session.title = question[:20] if len(question) <= 20 else f"{question[:20]}..."
        session.last_question_at = datetime.utcnow()

        qa_message = QaMessage(
            session_id=session.id,
            question=question,
            answer=answer,
            hit_chunks="\n\n".join(context_blocks),
            sources_json=json.dumps(sources, ensure_ascii=False),
            elapsed_ms=elapsed_ms,
        )
        db.session.add(qa_message)
        db.session.commit()

        return {
            "sessionId": session.id,
            "answer": answer,
            "sources": sources,
            "elapsedMs": elapsed_ms,
        }
