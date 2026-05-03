"""接口鉴权与角色校验装饰器。"""

from functools import wraps

from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from app.models import SysUser
from app.utils.response import api_error


def get_current_user():
    """从 JWT 中解析当前登录用户。"""

    user_id = get_jwt_identity()
    if not user_id:
        return None
    return SysUser.query.get(int(user_id))


def role_required(roles):
    """限制接口仅允许指定角色访问。"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user = get_current_user()
            if not user:
                return api_error("用户不存在或登录已失效", 401)
            if user.role not in roles:
                return api_error("当前账号无权访问该资源", 403)
            return func(*args, **kwargs)

        return wrapper

    return decorator
