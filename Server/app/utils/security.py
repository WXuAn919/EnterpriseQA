"""安全相关工具方法。"""

import hashlib


def md5_text(raw_text: str) -> str:
    """对明文执行 MD5 哈希，用于教学项目密码处理。"""

    return hashlib.md5(raw_text.encode("utf-8")).hexdigest()


def verify_md5_password(raw_password: str, encrypted_password: str) -> bool:
    """校验前端传入密码与数据库中的 MD5 值是否一致。"""

    return md5_text(raw_password) == encrypted_password
