"""问答与会话接口。"""

import json

from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.models import QaMessage, QaSession
from app.services import RagService
from app.utils.decorators import get_current_user
from app.utils.response import api_error, api_success

chat_bp = Blueprint("chat", __name__, url_prefix="/api/chat")


@chat_bp.get("/sessions")
@jwt_required()
def get_sessions():
    """查询当前用户的历史会话列表。"""

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
    """查询指定会话下的问答消息。"""

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
    """提交问题并返回知识库问答结果。"""

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
