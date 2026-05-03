"""认证服务模块。"""

from flask import request

from app.extensions import db
from app.models import SysLoginLog, SysUser
from app.utils.security import verify_md5_password


class AuthService:
    """处理登录校验、用户读取与登录日志记录。"""

    @staticmethod
    def authenticate(username: str, password: str):
        """校验用户名密码，返回用户对象或空值。"""

        user = SysUser.query.filter_by(username=username).first()
        if not user or user.status != "active":
            return None
        if not verify_md5_password(password, user.password):
            return None
        return user

    @staticmethod
    def get_user(user_id: int):
        """根据主键查询用户。"""

        return SysUser.query.get(user_id)

    @staticmethod
    def record_login(username: str, user_id=None, status="success"):
        """记录登录行为，用于后台首页统计。"""

        login_log = SysLoginLog(
            user_id=user_id,
            username=username,
            ip_address=request.headers.get("X-Forwarded-For", request.remote_addr),
            status=status,
        )
        db.session.add(login_log)
        db.session.commit()
