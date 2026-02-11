# -*- coding: UTF-8 -*-

import hashlib
from functools import wraps

from flask import session, redirect, url_for, request
from loguru import logger


def create_remember_token(username, password_hash):
    """生成「记住我」cookie 的 token。password_hash 为数据库中的密码哈希。"""
    token_hash = hashlib.sha256(f"{username}:{password_hash}".encode()).hexdigest()
    return f"{username}:{token_hash}"


def verify_remember_token(remember_token, get_user_by_username):
    """
    验证「记住我」token。若有效返回 (user_id, username, is_admin)，否则返回 None。
    get_user_by_username: 接收 username，返回 user 字典（含 id, password_hash, is_admin）。
    """
    if not remember_token:
        return None
    parts = remember_token.split(":")
    if len(parts) != 2:
        return None
    username, token_hash = parts
    user = get_user_by_username(username) if get_user_by_username else None
    if not user:
        return None
    expected = hashlib.sha256(f"{username}:{user['password_hash']}".encode()).hexdigest()
    if token_hash != expected:
        return None
    return (user["id"], username, bool(user.get("is_admin", 0)))


def login_required(f):
    """装饰器：要求用户登录才能访问"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            # 如果是API请求，返回JSON错误
            if request.path.startswith('/api/'):
                return {'success': False, 'message': '请先登录'}, 401
            # 否则重定向到登录页
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)

    return decorated_function


def get_current_user_id():
    """获取当前登录用户的ID

    Returns:
        int or None
    """
    return session.get('user_id')


def get_current_username():
    """获取当前登录用户的用户名

    Returns:
        str or None
    """
    return session.get('username')


def is_admin():
    """当前登录用户是否为管理员（由登录时从数据库写入 session）"""
    return session.get('is_admin', False)


def admin_required(f):
    """装饰器：仅管理员可访问"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.path.startswith('/api/'):
                return {'success': False, 'message': '请先登录'}, 401
            return redirect(url_for('auth.login'))
        if not is_admin():
            if request.path.startswith('/api/'):
                return {'success': False, 'message': '需要管理员权限'}, 403
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)

    return decorated_function


def login_user(user_id, username, is_admin=False):
    """登录用户，设置 session

    Args:
        user_id: 用户ID
        username: 用户名
        is_admin: 是否管理员，默认 False
    """
    session['user_id'] = user_id
    session['username'] = username
    session['is_admin'] = bool(is_admin)
    logger.info(f"User logged in: {username} (ID: {user_id}, admin={is_admin})")


def logout_user():
    """登出用户，清除session"""
    username = session.get('username', 'Unknown')
    session.clear()
    logger.info(f"User logged out: {username}")
