"""Flask 应用工厂模块。"""

from pathlib import Path

from flask import Flask

from app.blueprints import register_blueprints
from app.config import Config
from app.extensions import cors, db, jwt
from app.utils.response import api_error


def create_app() -> Flask:
    """创建 Flask 应用并注册扩展、蓝图与异常处理。"""

    app = Flask(__name__)
    app.config.from_object(Config)

    Path(app.config["UPLOAD_DIR"]).mkdir(parents=True, exist_ok=True)
    Path(app.config["CHROMA_PERSIST_DIR"]).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    register_blueprints(app)
    register_error_handlers(app)

    with app.app_context():
        if app.config["AUTO_CREATE_TABLES"]:
            db.create_all()

    return app


def register_error_handlers(app: Flask) -> None:
    """注册统一异常返回，便于前端统一处理。"""

    @app.errorhandler(404)
    def handle_not_found(_error):
        return api_error("请求的资源不存在", 404)

    @app.errorhandler(500)
    def handle_server_error(error):
        app.logger.exception("服务内部异常: %s", error)
        return api_error("服务内部异常，请稍后重试", 500)
