# -*- coding: UTF-8 -*-
"""路由 Blueprint 包。使用前需在 fund_server 中调用 set_db(db) 与 set_get_lan_fund(get_lan_fund)。"""

_db = None
_get_lan_fund = None


def set_db(db):
    global _db
    _db = db


def set_get_lan_fund(fn):
    global _get_lan_fund
    _get_lan_fund = fn


def get_db():
    return _db


def get_get_lan_fund():
    return _get_lan_fund


from src.routes.auth import auth_bp
from src.routes.admin import admin_bp
from src.routes.api_routes import api_bp
from src.routes.pages import pages_bp

__all__ = [
    'set_db', 'set_get_lan_fund', 'get_db', 'get_get_lan_fund',
    'auth_bp', 'admin_bp', 'api_bp', 'pages_bp',
]
