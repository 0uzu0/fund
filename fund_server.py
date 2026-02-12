import os

os.makedirs("cache", exist_ok=True)

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
    """
    创建 LanFund 实例（统一构造）。
    user_id 为 None 时使用文件模式。
    
    注意：移除了 importlib.reload，因为：
    1. 每次请求都 reload 模块效率低
    2. 可能导致状态不一致
    3. 生产环境通常不需要热重载
    如需热重载，应在开发环境使用专门的开发服务器
    """
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
