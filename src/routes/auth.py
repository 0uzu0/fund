# -*- coding: UTF-8 -*-
from flask import Blueprint, request, render_template, redirect, url_for, jsonify, session

from loguru import logger

from src.auth import (
    login_required,
    login_user,
    logout_user,
    create_remember_token,
    verify_remember_token,
)
from src.routes import get_db

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    db = get_db()
    if request.method == 'GET':
        remember_token = request.cookies.get('remember_token')
        if remember_token:
            try:
                result = verify_remember_token(remember_token, db.get_user_by_username)
                if result:
                    user_id, username, admin = result
                    login_user(user_id, username, is_admin=admin)
                    return redirect(url_for('pages.get_fund'))
            except Exception as e:
                logger.error(f"Auto-login failed: {e}")
        return render_template('login.html', register_disabled=True)

    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    remember_me = request.form.get('remember_me') == '1'

    if not username or not password:
        return render_template('login.html', error='请输入用户名和密码', register_disabled=True)

    success, user_id = db.verify_password(username, password)
    if success:
        user = db.get_user_by_id(user_id)
        login_user(user_id, username, is_admin=bool(user.get('is_admin', 0)))
        response = redirect(url_for('pages.get_fund'))
        if remember_me:
            user = db.get_user_by_username(username)
            remember_token = create_remember_token(username, user['password_hash'])
            response.set_cookie('remember_token', remember_token, max_age=7 * 24 * 60 * 60, httponly=True, samesite='Lax')
        return response
    return render_template('login.html', error='用户名或密码错误', register_disabled=True)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return redirect(url_for('auth.login', register_disabled=1))
    return redirect(url_for('auth.login', register_disabled=1))


@auth_bp.route('/logout')
def logout():
    logout_user()
    response = redirect(url_for('auth.login'))
    response.set_cookie('remember_token', '', max_age=0)
    return response


@auth_bp.route('/api/auth/me', methods=['GET'])
def api_auth_me():
    if not session.get('user_id'):
        return jsonify({'error': 'unauthorized'}), 401
    return jsonify({
        'username': session.get('username', ''),
        'is_admin': bool(session.get('is_admin', False)),
    })


@auth_bp.route('/api/auth/logout', methods=['POST'])
def api_auth_logout():
    logout_user()
    response = jsonify({'success': True})
    response.set_cookie('remember_token', '', max_age=0)
    return response


@auth_bp.route('/api/auth/login', methods=['POST'])
def api_auth_login():
    db = get_db()
    try:
        data = request.get_json() or {}
        username = (data.get('username') or '').strip()
        password = data.get('password', '')
        remember_me = data.get('remember_me', False)

        if not username or not password:
            return jsonify({'success': False, 'message': '请输入用户名和密码'}), 400

        success, user_id = db.verify_password(username, password)
        if not success:
            return jsonify({'success': False, 'message': '用户名或密码错误'}), 401

        user = db.get_user_by_id(user_id)
        login_user(user_id, username, is_admin=bool(user.get('is_admin', 0)))

        response = jsonify({
            'success': True,
            'username': username,
            'is_admin': bool(user.get('is_admin', 0)),
        })
        if remember_me:
            u = db.get_user_by_username(username)
            remember_token = create_remember_token(username, u['password_hash'])
            response.set_cookie('remember_token', remember_token, max_age=7 * 24 * 60 * 60, httponly=True, samesite='Lax')
        return response
    except Exception as e:
        logger.error(f"API login failed: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
