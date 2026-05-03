"""Chat and session endpoints."""

import json

from flask import Blueprint, Response, request, stream_with_context
from flask_jwt_extended import jwt_required

from app.models import QaMessage, QaSession
from app.services import RagService
from app.utils.decorators import get_current_user
from app.utils.response import api_error, api_success

chat_bp = Blueprint("chat", __name__, url_prefix="/api/chat")


def _stream_event(event: str, data=None, message=None) -> str:
    """Serialize one NDJSON stream event."""

    payload = {"event": event}
    if data is not None:
        payload["data"] = data
    if message is not None:
        payload["message"] = message
    return json.dumps(payload, ensure_ascii=False) + "\n"


@chat_bp.get("/sessions")
@jwt_required()
def get_sessions():
    """Return the current user's session list."""

    current_user = get_current_user()
    sessions = (
        QaSession.query.filter_by(user_id=current_user.id)
        .order_by(QaSession.last_question_at.desc())
        .all()
    )
    return api_success([session.to_dict() for session in sessions])


@chat_bp.get("/messages")
@jwt_required()
def get_messages():
    """Return messages for a specific session."""

    session_id = request.args.get("sessionId", type=int)
    current_user = get_current_user()
    session = QaSession.query.filter_by(id=session_id, user_id=current_user.id).first()
    if not session:
        return api_error("会话不存在或无权访问", 404)

    messages = QaMessage.query.filter_by(session_id=session.id).order_by(QaMessage.id.asc()).all()
    data = []
    for message in messages:
        item = message.to_dict()
        item["sources"] = json.loads(message.sources_json or "[]")
        data.append(item)
    return api_success(data)


@chat_bp.post("/ask")
@jwt_required()
def ask_question():
    """Submit a question and return the final answer."""

    payload = request.get_json(silent=True) or {}
    knowledge_base_id = payload.get("knowledgeBaseId")
    question = (payload.get("question") or "").strip()
    session_id = payload.get("sessionId")
    current_user = get_current_user()

    if not knowledge_base_id:
        return api_error("请选择知识库")
    if not question:
        return api_error("请输入问题内容")

    try:
        result = RagService.ask(
            user_id=current_user.id,
            knowledge_base_id=int(knowledge_base_id),
            question=question,
            session_id=session_id,
        )
        return api_success(result, "问答完成")
    except Exception as error:
        return api_error(f"问答失败：{error}")


@chat_bp.post("/ask/stream")
@jwt_required()
def ask_question_stream():
    """Submit a question and stream the answer incrementally."""

    payload = request.get_json(silent=True) or {}
    knowledge_base_id = payload.get("knowledgeBaseId")
    question = (payload.get("question") or "").strip()
    session_id = payload.get("sessionId")
    current_user = get_current_user()

    if not knowledge_base_id:
        return api_error("请选择知识库")
    if not question:
        return api_error("请输入问题内容")

    def generate():
        try:
            for event in RagService.ask_stream(
                user_id=current_user.id,
                knowledge_base_id=int(knowledge_base_id),
                question=question,
                session_id=session_id,
            ):
                yield _stream_event(
                    event=event.get("event", "message"),
                    data=event.get("data"),
                    message=event.get("message"),
                )
        except Exception as error:
            yield _stream_event("error", message=f"问答失败：{error}")

    return Response(
        stream_with_context(generate()),
        mimetype="application/x-ndjson",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
