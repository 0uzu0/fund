# -*- coding: UTF-8 -*-
from flask import Blueprint, request, render_template, redirect, url_for, jsonify, session

from loguru import logger

from src.auth import login_required, admin_required, get_current_user_id, get_current_username
from src.routes import get_db

admin_bp = Blueprint('admin', __name__)


def _admin_users_context(users=None, error=None, success=None):
    db = get_db()
    if users is None:
        users = db.list_users()
    return {
        'users': users,
        'error': error,
        'success': success,
        'current_username': get_current_username(),
    }


def _render_admin_users_page(**context):
    from src.module_html import get_admin_users_page_html
    content = render_template('admin_users_content.html', **_admin_users_context(**context))
    return get_admin_users_page_html(
        content,
        username=get_current_username(),
        is_admin=True
    )


@admin_bp.route('/api/admin/users', methods=['GET'])
@login_required
@admin_required
def api_admin_users_list():
    db = get_db()
    try:
        users = db.list_users()
        out = []
        for u in users:
            out.append({
                'id': u['id'],
                'username': u['username'],
                'is_admin': bool(u.get('is_admin', 0)),
                'created_at': str(u.get('created_at', '')),
            })
        return jsonify({'users': out})
    except Exception as e:
        logger.error(f"API admin users list failed: {e}")
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/admin/users', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_users():
    db = get_db()
    if request.method == 'GET':
        return _render_admin_users_page()

    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    confirm_password = request.form.get('confirm_password', '')

    if not username or not password:
        return _render_admin_users_page(error='请输入用户名和密码')

    if len(username) < 3 or len(username) > 20:
        return _render_admin_users_page(error='用户名长度应为 3–20 个字符')

    if len(password) < 6:
        return _render_admin_users_page(error='密码长度至少为 6 个字符')

    if password != confirm_password:
        return _render_admin_users_page(error='两次输入的密码不一致')

    success, message, _ = db.create_user(username, password, is_admin=False)
    if success:
        return _render_admin_users_page(success=f'用户 {username} 已创建成功')
    return _render_admin_users_page(error=message)


@admin_bp.route('/admin/add-user', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_user():
    return redirect(url_for('admin.admin_users'))


@admin_bp.route('/admin/profile', methods=['GET'])
@login_required
@admin_required
def admin_profile():
    db = get_db()
    user = db.get_user_by_id(get_current_user_id())
    return render_template('admin_profile.html', username=user['username'] if user else '')


@admin_bp.route('/api/admin/delete-user', methods=['POST'])
@login_required
@admin_required
def api_admin_delete_user():
    db = get_db()
    try:
        data = request.json or {}
        user_id = data.get('user_id')
        username = (data.get('username') or '').strip()
        if user_id is None and not username:
            return jsonify({'success': False, 'message': '请提供 user_id 或 username'}), 400
        current_id = get_current_user_id()
        if user_id is not None and int(user_id) == current_id:
            return jsonify({'success': False, 'message': '不能删除当前登录账号'}), 400
        success, message = db.delete_user(user_id=user_id if user_id is not None else None, username=username or None)
        if success:
            return jsonify({'success': True, 'message': message})
        return jsonify({'success': False, 'message': message}), 400
    except Exception as e:
        logger.error(f"Admin delete user failed: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/api/admin/add-user', methods=['POST'])
@login_required
@admin_required
def api_admin_add_user():
    db = get_db()
    try:
        data = request.json or {}
        username = (data.get('username') or '').strip()
        password = data.get('password', '')

        if not username or not password:
            return jsonify({'success': False, 'message': '请输入用户名和密码'}), 400
        if len(username) < 3 or len(username) > 20:
            return jsonify({'success': False, 'message': '用户名长度应为 3–20 个字符'}), 400
        if len(password) < 6:
            return jsonify({'success': False, 'message': '密码长度至少为 6 个字符'}), 400

        success, message, user_id = db.create_user(username, password, is_admin=False)
        if success:
            return jsonify({'success': True, 'message': f'用户 {username} 已创建', 'user_id': user_id})
        return jsonify({'success': False, 'message': message}), 400
    except Exception as e:
        logger.error(f"Admin add user failed: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/api/admin/update-profile', methods=['POST'])
@login_required
@admin_required
def api_admin_update_profile():
    db = get_db()
    try:
        data = request.json or {}
        new_username = (data.get('new_username') or '').strip() or None
        new_password = (data.get('new_password') or '').strip() or None
        user_id = get_current_user_id()
        success, message = db.update_user_credentials(user_id, new_username=new_username, new_password=new_password)
        if not success:
            return jsonify({'success': False, 'message': message}), 400
        if new_username:
            session['username'] = new_username
        return jsonify({'success': True, 'message': message})
    except Exception as e:
        logger.error(f"Admin update profile failed: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
