"""项目核心数据模型定义。"""

from datetime import datetime

from app.extensions import db


class BaseModel:
    """基础模型混入类，为所有表提供通用时间字段。"""

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class SysUser(db.Model, BaseModel):
    """系统用户表，区分管理员与普通用户。"""

    __tablename__ = "sys_user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    real_name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(32), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")
    status = db.Column(db.String(20), nullable=False, default="active")

    login_logs = db.relationship("SysLoginLog", backref="user", lazy=True)

    def to_dict(self) -> dict:
        """返回脱敏后的用户信息。"""

        return {
            "id": self.id,
            "username": self.username,
            "realName": self.real_name,
            "role": self.role,
            "status": self.status,
            "createdAt": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }


class SysLoginLog(db.Model):
    """登录日志表，用于后台统计与行为追踪。"""

    __tablename__ = "sys_login_log"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("sys_user.id"), nullable=True)
    username = db.Column(db.String(50), nullable=False)
    ip_address = db.Column(db.String(64), nullable=True)
    status = db.Column(db.String(20), nullable=False, default="success")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class KnowledgeBase(db.Model, BaseModel):
    """知识库主表，管理知识库基础信息。"""

    __tablename__ = "kb_knowledge_base"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default="enabled")
    created_by = db.Column(db.Integer, db.ForeignKey("sys_user.id"), nullable=False)

    documents = db.relationship("KbDocument", backref="knowledge_base", lazy=True)

    def to_dict(self) -> dict:
        """返回知识库信息。"""

        return {
            "id": self.id,
            "name": self.name,
            "description": self.description or "",
            "status": self.status,
            "createdBy": self.created_by,
            "createdAt": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }


class KbDocument(db.Model, BaseModel):
    """文档表，记录上传文件及处理状态。"""

    __tablename__ = "kb_document"

    id = db.Column(db.Integer, primary_key=True)
    knowledge_base_id = db.Column(
        db.Integer, db.ForeignKey("kb_knowledge_base.id"), nullable=False
    )
    title = db.Column(db.String(150), nullable=False)
    original_name = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(20), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    process_status = db.Column(db.String(20), nullable=False, default="pending")
    chunk_count = db.Column(db.Integer, nullable=False, default=0)
    created_by = db.Column(db.Integer, db.ForeignKey("sys_user.id"), nullable=False)

    chunks = db.relationship(
        "KbChunk", backref="document", lazy=True, cascade="all, delete-orphan"
    )

    def to_dict(self) -> dict:
        """返回文档简要信息。"""

        return {
            "id": self.id,
            "knowledgeBaseId": self.knowledge_base_id,
            "title": self.title,
            "originalName": self.original_name,
            "fileType": self.file_type,
            "filePath": self.file_path,
            "processStatus": self.process_status,
            "chunkCount": self.chunk_count,
            "createdAt": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }


class KbChunk(db.Model, BaseModel):
    """文档切片表，用于追踪切片与向量索引的对应关系。"""

    __tablename__ = "kb_chunk"

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey("kb_document.id"), nullable=False)
    sequence = db.Column(db.Integer, nullable=False)
    vector_id = db.Column(db.String(100), nullable=False, unique=True)
    content = db.Column(db.Text, nullable=False)
    char_count = db.Column(db.Integer, nullable=False)
    meta_json = db.Column(db.Text, nullable=True)

    def to_dict(self) -> dict:
        """返回切片数据。"""

        return {
            "id": self.id,
            "documentId": self.document_id,
            "sequence": self.sequence,
            "vectorId": self.vector_id,
            "content": self.content,
            "charCount": self.char_count,
        }


class QaSession(db.Model, BaseModel):
    """问答会话表，存储用户与知识库的对话上下文。"""

    __tablename__ = "qa_session"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("sys_user.id"), nullable=False)
    knowledge_base_id = db.Column(
        db.Integer, db.ForeignKey("kb_knowledge_base.id"), nullable=False
    )
    title = db.Column(db.String(150), nullable=False)
    last_question_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    messages = db.relationship(
        "QaMessage", backref="session", lazy=True, cascade="all, delete-orphan"
    )

    def to_dict(self) -> dict:
        """返回会话摘要。"""

        return {
            "id": self.id,
            "userId": self.user_id,
            "knowledgeBaseId": self.knowledge_base_id,
            "title": self.title,
            "lastQuestionAt": self.last_question_at.strftime("%Y-%m-%d %H:%M:%S"),
            "createdAt": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }


class QaMessage(db.Model, BaseModel):
    """问答消息表，保存问题、答案及引用来源。"""

    __tablename__ = "qa_message"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("qa_session.id"), nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    hit_chunks = db.Column(db.Text, nullable=True)
    sources_json = db.Column(db.Text, nullable=True)
    elapsed_ms = db.Column(db.Integer, nullable=False, default=0)

    def to_dict(self) -> dict:
        """返回消息数据。"""

        return {
            "id": self.id,
            "sessionId": self.session_id,
            "question": self.question,
            "answer": self.answer,
            "hitChunks": self.hit_chunks,
            "sources": self.sources_json,
            "elapsedMs": self.elapsed_ms,
            "createdAt": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
