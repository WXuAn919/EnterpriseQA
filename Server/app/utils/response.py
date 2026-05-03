"""统一响应结构工具。"""

from flask import jsonify


def api_success(data=None, message="操作成功", status_code=200):
    """返回统一成功响应。"""

    return jsonify({"code": status_code, "message": message, "data": data}), status_code


def api_error(message="操作失败", status_code=400, data=None):
    """返回统一失败响应。"""

    return jsonify({"code": status_code, "message": message, "data": data}), status_code
