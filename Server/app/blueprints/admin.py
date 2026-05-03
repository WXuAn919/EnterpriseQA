"""管理员后台接口。"""

from flask import Blueprint

from app.models import SysUser
from app.services import DashboardService
from app.utils.decorators import role_required
from app.utils.response import api_success

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@admin_bp.get("/users")
@role_required(["admin"])
def get_users():
    """获取系统用户列表。"""

    users = SysUser.query.order_by(SysUser.id.asc()).all()
    return api_success([user.to_dict() for user in users])


@admin_bp.get("/dashboard")
@role_required(["admin"])
def get_dashboard():
    """获取后台首页统计数据。"""

    return api_success(DashboardService.get_dashboard_data())
