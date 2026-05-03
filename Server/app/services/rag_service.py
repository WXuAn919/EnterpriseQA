"""RAG question answering service."""

import json
import time
from datetime import datetime

from flask import current_app
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from app.extensions import db
from app.models import KnowledgeBase, QaMessage, QaSession
from app.services.vector_service import VectorStoreService

DEFAULT_EMPTY_ANSWER = "未检索到相关信息，请补充知识库内容或调整提问方式。"


class RagService:
    """Handle session management, retrieval, and answer generation."""

    @classmethod
    def _get_llm(cls):
        """Create the Ollama chat model."""

        return ChatOllama(
            model=current_app.config["OLLAMA_LLM_MODEL"],
            base_url=current_app.config["OLLAMA_BASE_URL"],
            temperature=0.2,
        )

    @staticmethod
    def _build_prompt():
        """Build a constrained prompt so answers stay grounded in the KB."""

        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    (
                        "你是企业内部知识库问答助手。"
                        "请仅基于提供的知识库片段回答问题。"
                        "如果知识库没有明确信息，请直接回答"
                        f"“{DEFAULT_EMPTY_ANSWER}”。"
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
        """Fetch an existing session or create a new one."""

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

    @staticmethod
    def _serialize_context(docs):
        """Convert retrieved documents into prompt context and source metadata."""

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
        return sources, context_blocks

    @staticmethod
    def _normalize_chunk_text(chunk) -> str:
        """Extract plain text from a LangChain message chunk."""

        content = getattr(chunk, "content", "")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = []
            for item in content:
                if isinstance(item, str):
                    parts.append(item)
                elif isinstance(item, dict) and item.get("text"):
                    parts.append(item["text"])
            return "".join(parts)
        return str(content or "")

    @staticmethod
    def _finalize_session(session: QaSession, question: str) -> None:
        """Refresh session title and last activity time."""

        if session.title.endswith("问答会话"):
            session.title = question[:20] if len(question) <= 20 else f"{question[:20]}..."
        session.last_question_at = datetime.utcnow()

    @classmethod
    def _save_message(
        cls,
        session: QaSession,
        question: str,
        answer: str,
        context_blocks,
        sources,
        start_time: float,
    ):
        """Persist the generated answer and return the saved entity."""

        elapsed_ms = int((time.time() - start_time) * 1000)
        cls._finalize_session(session, question)

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
        return qa_message, elapsed_ms

    @classmethod
    def _prepare_qa(cls, user_id: int, knowledge_base_id: int, question: str, session_id=None):
        """Prepare session, retrieval context, and source metadata."""

        session = cls._get_or_create_session(user_id, knowledge_base_id, session_id)
        if not session:
            raise ValueError("会话不存在或无权访问")

        docs = VectorStoreService.similarity_search(knowledge_base_id, question, k=4)
        sources, context_blocks = cls._serialize_context(docs)
        return session, sources, context_blocks

    @classmethod
    def ask(cls, user_id: int, knowledge_base_id: int, question: str, session_id=None):
        """Run the standard non-streaming RAG pipeline."""

        start_time = time.time()
        session, sources, context_blocks = cls._prepare_qa(
            user_id=user_id,
            knowledge_base_id=knowledge_base_id,
            question=question,
            session_id=session_id,
        )

        if not context_blocks:
            answer = DEFAULT_EMPTY_ANSWER
        else:
            prompt = cls._build_prompt()
            chain = prompt | cls._get_llm()
            result = chain.invoke({"context": "\n\n".join(context_blocks), "question": question})
            answer = getattr(result, "content", str(result)).strip() or DEFAULT_EMPTY_ANSWER

        qa_message, elapsed_ms = cls._save_message(
            session=session,
            question=question,
            answer=answer,
            context_blocks=context_blocks,
            sources=sources,
            start_time=start_time,
        )

        return {
            "sessionId": session.id,
            "messageId": qa_message.id,
            "answer": answer,
            "sources": sources,
            "elapsedMs": elapsed_ms,
        }

    @classmethod
    def ask_stream(cls, user_id: int, knowledge_base_id: int, question: str, session_id=None):
        """Stream answer chunks while keeping the final message persisted."""

        start_time = time.time()
        session, sources, context_blocks = cls._prepare_qa(
            user_id=user_id,
            knowledge_base_id=knowledge_base_id,
            question=question,
            session_id=session_id,
        )

        yield {"event": "start", "data": {"sessionId": session.id}}
        yield {"event": "context", "data": {"sources": sources}}

        if not context_blocks:
            answer = DEFAULT_EMPTY_ANSWER
            yield {"event": "chunk", "data": answer}
        else:
            prompt = cls._build_prompt()
            chain = prompt | cls._get_llm()
            answer_parts = []
            for chunk in chain.stream(
                {"context": "\n\n".join(context_blocks), "question": question}
            ):
                text = cls._normalize_chunk_text(chunk)
                if not text:
                    continue
                answer_parts.append(text)
                yield {"event": "chunk", "data": text}

            answer = "".join(answer_parts).strip()
            if not answer:
                answer = DEFAULT_EMPTY_ANSWER
                yield {"event": "chunk", "data": answer}

        qa_message, elapsed_ms = cls._save_message(
            session=session,
            question=question,
            answer=answer,
            context_blocks=context_blocks,
            sources=sources,
            start_time=start_time,
        )

        yield {
            "event": "complete",
            "data": {
                "sessionId": session.id,
                "messageId": qa_message.id,
                "answer": answer,
                "sources": sources,
                "elapsedMs": elapsed_ms,
            },
        }
