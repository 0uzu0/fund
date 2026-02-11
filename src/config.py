# -*- coding: UTF-8 -*-
"""公共配置与网络初始化（SSL/urllib3），供 fund.py 与 fund_server.py 共用。"""

import urllib3

# 统一 SSL 密码套件，避免请求时报错
_DEFAULT_CIPHERS = ":".join([
    "ECDHE+AESGCM",
    "ECDHE+CHACHA20",
    "ECDHE-RSA-AES128-SHA",
    "ECDHE-RSA-AES256-SHA",
    "RSA+AESGCM",
    "AES128-SHA",
    "AES256-SHA",
])


def setup_urllib3_ssl():
    """禁用 urllib3 警告并设置默认密码套件。在应用/脚本入口调用一次即可。"""
    urllib3.disable_warnings()
    urllib3.util.ssl_.DEFAULT_CIPHERS = _DEFAULT_CIPHERS
