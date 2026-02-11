import os

os.makedirs("cache", exist_ok=True)

import importlib

from dotenv import load_dotenv
from flask import Flask

import fund
from src.config import setup_urllib3_ssl
from src.database import Database
from src.routes import (
    set_db,
    set_get_lan_fund,
    auth_bp,
    admin_bp,
    api_bp,
    pages_bp,
)

# 加载环境变量与网络配置
load_dotenv()
setup_urllib3_ssl()

app = Flask(__name__)
app.secret_key = "luobobo"
db = Database()


def get_lan_fund(user_id=None):
    """创建 LanFund 实例（统一 reload 与构造）。user_id 为 None 时使用文件模式。"""
    importlib.reload(fund)
    return fund.LanFund(user_id=user_id, db=db)


# 注入到路由包，供各 Blueprint 使用
set_db(db)
set_get_lan_fund(get_lan_fund)

# 注册 Blueprint（url_prefix 为空，路径与原先一致）
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(api_bp)
app.register_blueprint(pages_bp)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8311)
