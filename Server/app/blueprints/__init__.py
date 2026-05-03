"""蓝图注册模块。"""

from app.blueprints.admin import admin_bp
from app.blueprints.auth import auth_bp
from app.blueprints.chat import chat_bp
from app.blueprints.kb import kb_bp


def register_blueprints(app):
    """集中注册所有业务蓝图。"""

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(kb_bp)
    app.register_blueprint(chat_bp)
