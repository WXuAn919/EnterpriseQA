"""知识库管理接口。"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.models import KbDocument, KnowledgeBase
from app.services import DocumentService, VectorStoreService
from app.utils.decorators import get_current_user, role_required
from app.utils.response import api_error, api_success

kb_bp = Blueprint("knowledge_base", __name__, url_prefix="/api/kb")


@kb_bp.get("/list")
@jwt_required()
def get_knowledge_bases():
    """获取知识库列表，管理员与普通用户都可查看。"""

    knowledge_bases = KnowledgeBase.query.order_by(KnowledgeBase.id.asc()).all()
    return api_success([item.to_dict() for item in knowledge_bases])


@kb_bp.post("/create")
@role_required(["admin"])
def create_knowledge_base():
    """创建新的知识库。"""

    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "").strip()
    description = (payload.get("description") or "").strip()
    current_user = get_current_user()

    if not name:
        return api_error("知识库名称不能为空")
    if KnowledgeBase.query.filter_by(name=name).first():
        return api_error("知识库名称已存在")

    knowledge_base = KnowledgeBase(
        name=name,
        description=description,
        status="enabled",
        created_by=current_user.id,
    )
    from app.extensions import db

    db.session.add(knowledge_base)
    db.session.commit()
    return api_success(knowledge_base.to_dict(), "知识库创建成功")


@kb_bp.get("/documents")
@role_required(["admin"])
def get_documents():
    """按知识库查询文档列表。"""

    knowledge_base_id = request.args.get("knowledgeBaseId", type=int)
    query = KbDocument.query.order_by(KbDocument.id.desc())
    if knowledge_base_id:
        query = query.filter_by(knowledge_base_id=knowledge_base_id)
    return api_success([document.to_dict() for document in query.all()])


@kb_bp.post("/documents/upload")
@role_required(["admin"])
def upload_document():
    """上传文档、切片并建立向量索引。"""

    current_user = get_current_user()
    upload_file = request.files.get("file")
    title = request.form.get("title", "")
    knowledge_base_id = request.form.get("knowledgeBaseId", type=int)

    if not knowledge_base_id:
        return api_error("请选择所属知识库")
    if not upload_file:
        return api_error("请上传文档文件")

    try:
        document = DocumentService.create_document(
            upload_file=upload_file,
            title=title,
            knowledge_base_id=knowledge_base_id,
            user_id=current_user.id,
        )
        DocumentService.split_and_store_chunks(document)
        VectorStoreService.index_document(document)
        return api_success(document.to_dict(), "文档上传并索引成功")
    except Exception as error:
        if "document" in locals():
            DocumentService.mark_failed(document)
        return api_error(f"文档处理失败：{error}")


@kb_bp.post("/documents/reindex")
@role_required(["admin"])
def reindex_document():
    """重新构建指定文档或指定知识库的向量索引。"""

    payload = request.get_json(silent=True) or {}
    document_id = payload.get("documentId")
    knowledge_base_id = payload.get("knowledgeBaseId")

    if document_id:
        documents = KbDocument.query.filter_by(id=document_id).all()
    elif knowledge_base_id:
        documents = KbDocument.query.filter_by(knowledge_base_id=knowledge_base_id).all()
    else:
        return api_error("请提供 documentId 或 knowledgeBaseId")

    success_count = 0
    errors = []
    for document in documents:
        try:
            DocumentService.split_and_store_chunks(document)
            VectorStoreService.index_document(document)
            success_count += 1
        except Exception as error:
            DocumentService.mark_failed(document)
            errors.append({"documentId": document.id, "message": str(error)})

    return api_success(
        {"successCount": success_count, "errors": errors},
        "重建索引完成",
    )
