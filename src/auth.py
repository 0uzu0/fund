# -*- coding: UTF-8 -*-

from functools import wraps

from flask import session, redirect, url_for, request
from loguru import logger


def login_required(f):
    """装饰器：要求用户登录才能访问"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            # 如果是API请求，返回JSON错误
            if request.path.startswith('/api/'):
                return {'success': False, 'message': '请先登录'}, 401
            # 否则重定向到登录页
            return redirect(url_for('login'))
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
            return redirect(url_for('login'))
        if not is_admin():
            if request.path.startswith('/api/'):
                return {'success': False, 'message': '需要管理员权限'}, 403
            return redirect(url_for('login'))
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
