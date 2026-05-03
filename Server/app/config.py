"""项目配置模块。"""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Config:
    """Flask 配置类，统一管理数据库、模型与存储目录。"""

    MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "123456")
    MYSQL_DB = os.getenv("MYSQL_DB", "db_enterprise_qa")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "enterprise-qa-secret")
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    OLLAMA_LLM_MODEL = os.getenv("OLLAMA_LLM_MODEL", "qwen3:4b")
    OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "qwen3-embedding:4b")
    CHROMA_PERSIST_DIR = os.getenv(
        "CHROMA_PERSIST_DIR", str(BASE_DIR / "storage" / "chroma")
    )
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", str(BASE_DIR / "storage" / "uploads"))
    AUTO_CREATE_TABLES = os.getenv("AUTO_CREATE_TABLES", "false").lower() == "true"

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/"
        f"{MYSQL_DB}?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_AS_ASCII = False
