# LanFund - 基金与市场辅助工具

基金自选、持仓统计、市场行情与贵金属数据的一体化工具，支持 **Web 端** 与 **命令行（CLI）** 双模式，数据可多端同步。

---

## 功能概览

| 类型 | 说明 |
|------|------|
| **Web 服务** | Flask 后端，登录后使用；左侧导航多页面，持仓与配置按用户存储 |
| **CLI 客户端** | 本地运行 `fund.py`，通过账号与服务器同步自选与份额，支持 AI 分析 |
| **数据同步** | 添加/删除基金、设置份额、板块标注等均会同步到服务器（多设备一致） |

---

## 项目结构

```
fund/
├── fund_server.py      # Web 服务入口（Flask）
├── fund.py             # CLI 客户端入口
├── requirements.txt    # Python 依赖
├── cache/              # 本地缓存（DB、配置等）
│   ├── fund_data.db    # SQLite：用户、自选基金、持仓记录等
│   ├── fund_map.json   # CLI 本地/导出基金列表
│   └── user_account.json # CLI 服务器连接配置
├── src/
│   ├── auth.py         # 登录鉴权
│   ├── database.py     # 数据库与持仓记录
│   ├── module_html.py  # 各页面 HTML 模板
│   └── ai_analyzer.py  # AI 分析（可选）
├── static/             # 静态资源（CSS/JS/图标）
├── templates/          # 登录、管理后台等模板
└── imgs/               # 文档截图
```

---

## 安装与运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动 Web 服务

```bash
python fund_server.py
```

- 默认地址：`http://0.0.0.0:8311`
- 浏览器访问：`http://localhost:8311`（根路径会重定向到持仓基金页）
- **注册已关闭**：需由管理员在「用户管理」中创建账号后再登录

### 3. CLI 客户端（可选）

首次使用需先配置服务器连接：

```bash
python fund.py --init
# 或
python fund.exe --init
```

按提示输入：服务器地址（如 `http://localhost:8311`）、用户名、密码。配置会写入 `cache/user_account.json`，后续添加/删除基金、修改份额等会自动与服务器同步。

---

## Web 端功能

### 左侧导航页面

| 入口 | 路径 | 说明 |
|------|------|------|
| 📈 市场行情 | `/market` | 7×24 快讯等市场资讯 |
| 📊 市场指数 | `/market-indices` | 全球指数、成交量趋势、上证分时等 |
| 🥇 贵金属行情 | `/precious-metals` | 实时贵金属、分时金价、历史金价 |
| 💰 持仓基金 | `/portfolio` | 自选基金列表、估值走势图、加减仓、份额设置 |
| 📋 持仓记录 | `/position-records` | 加减仓记录列表，删除即撤销该次操作 |
| 🏢 行业板块 | `/sectors` | 板块涨跌、板块下基金查询 |
| ⚙ 用户管理 | `/admin/users` | 仅管理员：添加/删除用户、修改资料 |

### 持仓基金页（核心）

- **自选管理**：添加/删除基金、标注板块、删除板块标签
- **持仓数据**：持有份额、持仓成本（持仓份额 = 持有份额 × 持仓成本）、持仓金额、预估/实际收益、累计收益
- **累计收益修正**：支持“显示累计收益 = 现有累计收益 − 修正金额”
- **设置/修改份额**：弹窗内填写持有份额与每份成本，自动计算持仓份额
- **同步加仓/减仓**：按金额与买入/卖出时间同步，写入持仓记录；未填金额或未选时间会弹窗提醒
- **一键炫耀**：生成今日收益分享卡片，可截图
- **导出/导入**：导出基金列表 JSON，或上传 JSON 恢复配置

### 持仓记录页

- 列表字段：基金编号、基金名称、操作时间、操作方式（加仓/减仓）、加减仓金额
- **删除即撤销**：删除某条记录会恢复该次操作前的持仓（持有份额与成本）

### 用户与权限

- 登录/登出、可选「记住我」
- 管理员：用户管理、添加用户、删除用户（不可删管理员）、修改本人资料

---

## CLI 端功能

在配置好 `cache/user_account.json` 后，以下操作会与服务器同步。

| 命令 | 说明 |
|------|------|
| `python fund.py` | 拉取服务器配置并展示：快讯、板块、金价、指数、成交量、上证分时、自选估值等 |
| `python fund.py -a` | 添加基金（可多码逗号分隔） |
| `python fund.py -d` | 删除基金 |
| `python fund.py -m` | 修改持仓份额（持有份额/成本） |
| `python fund.py -e` | 为基金标注板块 |
| `python fund.py -u` | 删除基金板块标注 |
| `python fund.py -s` | 按板块关键词查询板块及旗下基金 |
| `python fund.py --init` | 初始化/重置服务器连接配置 |

### AI 分析（可选，需配置 LLM）

| 命令 | 说明 |
|------|------|
| `python fund.py -W` | 标准分析（约 1200–1600 字） |
| `python fund.py -f -W` / `-F -W` | 快速分析（约 400–500 字） |
| `python fund.py -D -W` / `--deep -W` | 深度研究（ReAct Agent，约 10000+ 字） |
| `python fund.py -o [目录]` | 将报告保存到指定目录（默认 `reports/`） |

需在 `.env` 或环境中配置 `LLM_API_KEY`、`LLM_API_BASE`、`LLM_MODEL`（OpenAI 兼容接口，如 Moonshot、DeepSeek 等）。

---

## 配置说明

### CLI 服务器配置

- 文件：`cache/user_account.json`
- 字段：`server_url`、`username`、`password`
- 通过 `python fund.py --init` 交互写入；服务器不可用时 CLI 可降级使用本地 `cache/fund_map.json`

### Web 环境变量

- 见 `.env.example`；如 Session 密钥等可按需配置

### AI 分析（.env）

```bash
LLM_API_KEY=your-api-key
LLM_API_BASE=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat
```

---

## 主要 API（供前端/CLI 调用）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/login` | 登录 |
| GET  | `/api/auth/me` | 当前用户信息 |
| GET  | `/api/fund/data` | 当前用户基金列表（含份额等） |
| POST | `/api/fund/add` | 添加基金 |
| POST | `/api/fund/delete` | 删除基金 |
| POST | `/api/fund/shares` | 更新持仓（持有份额、成本；可带 record 写入加减仓记录） |
| GET  | `/api/fund/position-records` | 持仓记录列表 |
| DELETE | `/api/fund/position-records/<id>` | 删除记录并撤销该次加减仓 |
| POST | `/api/fund/sector` | 标注板块 |
| POST | `/api/fund/sector/remove` | 删除板块标注 |
| GET  | `/api/fund/download` | 导出基金配置 JSON |
| POST | `/api/fund/upload` | 上传基金配置 JSON |
| GET  | `/api/fund/chart-data` | 基金估值趋势图数据 |
| GET  | `/api/gold/real-time` | 实时贵金属 |
| GET  | `/api/gold/history` | 黄金历史 |
| GET  | `/api/news/7x24` | 7×24 快讯 |
| GET  | `/api/indices/global` | 全球指数 |
| GET  | `/api/sectors` | 板块数据 |
| POST | `/api/client/fund/config` | 客户端拉取/推送配置（账号密码认证） |

---

## Docker 部署

```bash
# 构建
docker build -t lanfund .

# 运行（推荐挂载 cache 持久化）
docker run -d -p 8311:8311 --name lanfund -v $(pwd)/cache:/app/cache lanfund
```

访问：`http://localhost:8311`

---

## 打包为可执行文件

```bash
pyinstaller fund.spec
```

可执行文件输出在 `dist/`（如 `fund.exe`）。

---

## 依赖概览

- **Web/通用**：flask, python-dotenv, bcrypt, loguru, requests, tabulate, wcwidth, curl_cffi
- **AI 分析（可选）**：langchain, langchain-openai, langchain-core, ddgs, beautifulsoup4, lxml

详见 `requirements.txt`。

---

## 免责声明

本工具仅用于数据展示与个人记录，不构成任何投资建议。投资有风险，入市需谨慎。
