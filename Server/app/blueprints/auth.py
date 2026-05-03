"""认证相关接口。"""

from flask import Blueprint, request
from flask_jwt_extended import create_access_token, jwt_required

from app.services import AuthService
from app.utils.decorators import get_current_user
from app.utils.response import api_error, api_success

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/login")
def login():
    """处理账号密码登录并返回 JWT。"""

    payload = request.get_json(silent=True) or {}
    username = (payload.get("username") or "").strip()
    password = (payload.get("password") or "").strip()

    if not username or not password:
        return api_error("用户名和密码不能为空")

    user = AuthService.authenticate(username, password)
    if not user:
        AuthService.record_login(username=username, status="failed")
        return api_error("用户名或密码错误", 401)

    AuthService.record_login(username=user.username, user_id=user.id, status="success")
    token = create_access_token(identity=str(user.id))
    return api_success(
        {
            "token": token,
            "role": user.role,
            "userInfo": user.to_dict(),
        },
        "登录成功",
    )


@auth_bp.get("/profile")
@jwt_required()
def profile():
    """返回当前登录用户资料。"""

    user = get_current_user()
    if not user:
        return api_error("用户不存在", 404)
    return api_success(user.to_dict())
