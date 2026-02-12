# -*- coding: UTF-8 -*-
"""Page HTML: market, news, admin, metals, indices, portfolio, position-records, sectors."""

from src.html.layout import (
    get_sidebar_menu_items_html,
    get_legacy_sidebar_html,
    get_top_navbar_html,
    get_lyrics_script,
)
from src.html.assets import get_css_style

def get_market_page_html(market_data, username=None, is_admin=False):
    """生成市场行情页面 - 使用卡片/图表布局"""
    css_style = get_css_style()
    sidebar_menu_html = get_sidebar_menu_items_html('market', is_admin)

    # 生成市场数据卡片
    market_cards = ''
    for key, data in market_data.items():
        card_id = "card-{}".format(key)
        icon = get_market_icon(key)
        market_cards += '''
        <div class="market-card" id="{card_id}">
            <div class="market-card-header">
                <h3 class="market-card-title">
                    <span class="card-icon">{icon}</span>
                    {title}
                </h3>
                <button class="card-toggle" onclick="toggleCard('{card_id}')">
                    <span>▼</span>
                </button>
            </div>
            <div class="market-card-content">
                {content}
            </div>
        </div>
        '''.format(card_id=card_id, icon=icon, title=data['title'], content=data['content'])

    username_display = ''
    if username:
        username_display += '<span class="nav-user">🍎 {username}</span>'.format(username=username)
        username_display += '<a href="/logout" class="nav-logout">退出登录</a>'

    html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>市场行情 - LanFund</title>
    <link rel="icon" href="/static/1.ico">
    {css_style}
    <link rel="stylesheet" href="/static/css/style.css">
    <style>
        body {{
            background-color: var(--terminal-bg);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }}

        /* 顶部导航栏 */
        .top-navbar {{
            background-color: var(--card-bg);
            color: var(--text-main);
            padding: 0.8rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border);
        }}

        .top-navbar-brand {{
            display: flex;
            align-items: center;
            flex: 0 0 auto;
        }}

        .top-navbar-quote {{
            flex: 1;
            text-align: center;
            font-size: 1rem;
            font-weight: 500;
            color: var(--text-main);
            font-style: italic;
            padding: 0 2rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            letter-spacing: 0.05em;
            transition: opacity 0.5s ease-in-out;
        }}

        .top-navbar-menu {{
            display: flex;
            gap: 1rem;
            align-items: center;
        }}

        .nav-user {{
            color: #3b82f6;
            font-weight: 500;
        }}

        .nav-logout {{
            color: #f85149;
            text-decoration: none;
            font-weight: 500;
        }}

        /* 主容器 */
        .main-container {{
            display: flex;
            flex: 1;
        }}

        /* 内容区域 */
        .content-area {{
            flex: 1;
            padding: 30px;
            overflow-y: auto;
        }}

        .page-header {{
            margin-bottom: 30px;
            text-align: center;
        }}

        .page-header h1 {{
            font-size: 2rem;
            font-weight: 700;
            margin: 0;
            border: none;
            text-decoration: none;
            background: linear-gradient(135deg, var(--accent), var(--down));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .page-header p {{
            color: var(--text-dim);
            margin-top: 10px;
            border: none;
            text-decoration: none;
        }}

        /* 市场行情网格布局 */
        .market-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            max-width: 1600px;
            margin: 0 auto;
        }}

        @media (max-width: 1200px) {{
            .market-grid {{
                grid-template-columns: 1fr;
            }}
        }}

        /* 市场卡片 */
        .market-card {{
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 12px;
            overflow: hidden;
            transition: all 0.3s ease;
        }}

        .market-card:hover {{
            border-color: var(--accent);
            box-shadow: 0 4px 20px rgba(59, 130, 246, 0.15);
        }}

        .market-card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 16px 20px;
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
            border-bottom: 1px solid var(--border);
            cursor: pointer;
            user-select: none;
        }}

        .market-card-title {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin: 0;
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--text-main);
        }}

        .card-icon {{
            font-size: 1.3rem;
        }}

        .card-toggle {{
            background: none;
            border: none;
            color: var(--text-dim);
            cursor: pointer;
            padding: 4px 8px;
            transition: transform 0.3s ease;
        }}

        .card-toggle.collapsed {{
            transform: rotate(-90deg);
        }}

        .market-card-content {{
            padding: 20px;
            max-height: 600px;
            overflow-y: auto;
            transition: all 0.3s ease;
            opacity: 1;
        }}

        /* 折叠状态：内容隐藏 */
        .market-card.collapsed .market-card-content {{
            display: none;
        }}

        /* 折叠状态：卡片收缩 */
        .market-card.collapsed {{
            max-height: 60px;
        }}

        /* 滚动条样式 */
        .market-card-content::-webkit-scrollbar {{
            width: 8px;
        }}

        .market-card-content::-webkit-scrollbar-track {{
            background: var(--terminal-bg);
        }}

        .market-card-content::-webkit-scrollbar-thumb {{
            background: var(--border);
            border-radius: 4px;
        }}

        .market-card-content::-webkit-scrollbar-thumb:hover {{
            background: var(--accent);
        }}

        @media (max-width: 768px) {{
            .main-container {{
                flex-direction: column;
            }}

            .sidebar {{
                width: 100%;
                border-right: none;
                border-bottom: 1px solid var(--border);
                padding: 10px 0;
            }}

            .sidebar-item {{
                padding: 10px 15px;
                font-size: 0.9rem;
            }}

            .content-area {{
                padding: 15px;
            }}

            /* 顶部导航栏两行布局 */
            .top-navbar {{
                flex-direction: row;
                flex-wrap: wrap;
                height: auto;
                padding: 0.5rem 1rem;
                align-items: center;
                border-bottom: none;
            }}

            .top-navbar > .top-navbar-brand {{
                order: 1;
                flex: 0 0 auto;
                padding-bottom: 0.5rem;
                border-bottom: 1px solid var(--border);
            }}

            .top-navbar-menu {{
                order: 1;
                flex: 0 0 auto;
                margin-left: auto;
                padding-bottom: 0.5rem;
                border-bottom: 1px solid var(--border);
            }}

            .top-navbar-quote {{
                order: 2;
                width: 100%;
                flex-basis: 100%;
                text-align: center;
                padding: 0.5rem 0;
                font-size: 0.8rem;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                border-top: 1px solid var(--border);
                margin-top: 0.5rem;
            }}
        }}
    </style>
</head>
<body>
    <!-- 顶部导航栏 -->
    <nav class="top-navbar">
        <div class="top-navbar-brand">
            <img src="/static/1.ico" alt="Logo" class="navbar-logo">
        </div>
        <div class="top-navbar-quote" id="lyricsDisplay">
            偶然与巧合, 舞动了蝶翼, 谁的心头风起 ————《如果我们不曾相遇》
        </div>
        <div class="top-navbar-menu">
            {username_display}
        </div>
    </nav>

    <!-- 主容器 -->
    <div class="main-container">
        <!-- 汉堡菜单按钮 (移动端) -->
        <button class="hamburger-menu" id="hamburgerMenu">
            <span></span>
            <span></span>
            <span></span>
        </button>

        <!-- 左侧导航栏 -->
        <div class="sidebar collapsed" id="sidebar">
            <div class="sidebar-toggle" id="sidebarToggle">▶</div>
            {sidebar_menu_html}
        </div>

        <!-- 内容区域 -->
        <div class="content-area">
            <!-- 页面标题 -->
            <div class="page-header">
                <h1>📊 市场行情</h1>
                <p>实时追踪全球市场动态</p>
            </div>

            <!-- 市场数据网格 -->
            <div class="market-grid">
                {market_cards}
            </div>
        </div>
    </div>

    <script>
        function toggleCard(cardId) {{
            const card = document.getElementById(cardId);
            const toggle = card.querySelector('.card-toggle');
            card.classList.toggle('collapsed');
            toggle.classList.toggle('collapsed');
        }}

        // 自动颜色化
        function autoColorize() {{
            const cells = document.querySelectorAll('.style-table td');
            cells.forEach(cell => {{
                const text = cell.textContent.trim();
                const cleanText = text.replace(/[%,亿万手]/g, '');
                const val = parseFloat(cleanText);

                if (!isNaN(val)) {{
                    if (text.includes('%') || text.includes('涨跌')) {{
                        if (text.includes('-')) {{
                            cell.classList.add('negative');
                        }} else if (val > 0) {{
                            cell.classList.add('positive');
                        }}
                    }} else if (text.startsWith('-')) {{
                        cell.classList.add('negative');
                    }} else if (text.startsWith('+')) {{
                        cell.classList.add('positive');
                    }}
                }}
            }});
        }}

        document.addEventListener('DOMContentLoaded', function() {{
            autoColorize();
        }});
    </script>
    <script src="/static/js/main.js"></script>
    <script>
        // 歌词轮播
        (function() {{
            const lyrics = [
                "偶然与巧合, 舞动了蝶翼, 谁的心头风起 ————《如果我们不曾相遇》",
                "如海上的浪花, 如深海的鱼, 浪与鱼相依 ————《鱼仔》",
                "阳光下的泡沫, 是彩色的, 一触就破 ————《泡沫》",
                "如果我变成回忆, 退出了这场生命 ————《如果我变成回忆》"
            ];
            let currentIndex = 0;
            const lyricsElement = document.getElementById('lyricsDisplay');

            function rotateLyrics() {{
                if (!lyricsElement) return;
                lyricsElement.style.opacity = '0';
                setTimeout(() => {{
                    currentIndex = (currentIndex + 1) % lyrics.length;
                    lyricsElement.textContent = lyrics[currentIndex];
                    lyricsElement.style.opacity = '1';
                }}, 500);
            }}

            setInterval(rotateLyrics, 10000);
        }})();
    </script>
</body>
</html>'''.format(css_style=css_style, username_display=username_display, market_cards=market_cards, sidebar_menu_html=sidebar_menu_html)
    return html


def get_news_page_html(news_content, username=None, is_admin=False):
    """生成7*24快讯页面 - 简洁布局"""
    css_style = get_css_style()
    sidebar_menu_html = get_sidebar_menu_items_html('market', is_admin)

    username_display = ''
    if username:
        username_display += '<span class="nav-user">🍎 {username}</span>'.format(username=username)
        username_display += '<a href="/logout" class="nav-logout">退出登录</a>'

    html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>7*24快讯 - LanFund</title>
    <link rel="icon" href="/static/1.ico">
    {css_style}
    <link rel="stylesheet" href="/static/css/style.css">
    <style>
        body {{
            background-color: var(--terminal-bg);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }}

        /* 顶部导航栏 */
        .top-navbar {{
            background-color: var(--card-bg);
            color: var(--text-main);
            padding: 0.8rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border);
        }}

        .top-navbar-brand {{
            display: flex;
            align-items: center;
            flex: 0 0 auto;
        }}

        .navbar-logo {{
            width: 32px;
            height: 32px;
        }}

        .top-navbar-quote {{
            flex: 1;
            text-align: center;
            font-size: 1rem;
            font-weight: 500;
            color: var(--text-main);
            font-style: italic;
            padding: 0 2rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            letter-spacing: 0.05em;
            transition: opacity 0.5s ease-in-out;
        }}

        .top-navbar-menu {{
            display: flex;
            gap: 1rem;
            align-items: center;
        }}

        .nav-logout {{
            color: #f85149;
            text-decoration: none;
            font-weight: 500;
        }}

        .nav-user {{
            color: #3b82f6;
            font-weight: 500;
        }}

        /* 主容器 */
        .main-container {{
            display: flex;
            flex: 1;
        }}

        /* 内容区域 */
        .content-area {{
            flex: 1;
            padding: 20px;
            overflow-y: auto;
        }}

        /* 隐藏滚动条但保留功能 */
        ::-webkit-scrollbar {{
            width: 6px;
            height: 6px;
        }}

        ::-webkit-scrollbar-track {{
            background: transparent;
        }}

        ::-webkit-scrollbar-thumb {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 3px;
        }}

        ::-webkit-scrollbar-thumb:hover {{
            background: rgba(255, 255, 255, 0.2);
        }}

        /* Firefox */
        * {{
            scrollbar-width: thin;
            scrollbar-color: rgba(255, 255, 255, 0.1) transparent;
        }}

        .page-header {{
            margin-bottom: 20px;
        }}

        .page-header h1 {{
            font-size: 1.8rem;
            margin: 0;
            color: var(--text-main);
        }}

        .page-header p {{
            margin: 5px 0 0;
            color: var(--text-dim);
        }}

        /* 快讯内容 */
        .news-content {{
            background-color: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 20px;
            max-height: calc(100vh - 200px);
            overflow-y: auto;
        }}

        /* 响应式设计 */
        @media (max-width: 768px) {{
            /* 汉堡菜单显示 */
            .hamburger-menu {{
                display: flex !important;
            }}

            .content-area {{
                padding: 15px;
            }}

            /* 顶部导航栏两行布局 */
            .top-navbar {{
                flex-direction: row;
                flex-wrap: wrap;
                height: auto;
                padding: 0.5rem 1rem;
                align-items: center;
                border-bottom: none;
            }}

            .top-navbar > .top-navbar-brand {{
                order: 1;
                flex: 0 0 auto;
                padding-bottom: 0.5rem;
                border-bottom: 1px solid var(--border);
            }}

            .top-navbar-menu {{
                order: 1;
                flex: 0 0 auto;
                margin-left: auto;
                padding-bottom: 0.5rem;
                border-bottom: 1px solid var(--border);
            }}

            .top-navbar-quote {{
                order: 2;
                width: 100%;
                flex-basis: 100%;
                text-align: center;
                padding: 0.5rem 0;
                font-size: 0.8rem;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                border-top: 1px solid var(--border);
                margin-top: 0.5rem;
            }}
        }}
    </style>
</head>
<body>
    <!-- 顶部导航栏 -->
    <nav class="top-navbar">
        <div class="top-navbar-brand">
            <img src="/static/1.ico" alt="Logo" class="navbar-logo">
        </div>
        <div class="top-navbar-quote" id="lyricsDisplay">
            偶然与巧合, 舞动了蝶翼, 谁的心头风起 ————《如果我们不曾相遇》
        </div>
        <div class="top-navbar-menu">
            {username_display}
        </div>
    </nav>

    <!-- 主容器 -->
    <div class="main-container">
        <!-- 汉堡菜单按钮 (移动端) -->
        <button class="hamburger-menu" id="hamburgerMenu">
            <span></span>
            <span></span>
            <span></span>
        </button>

        <!-- 左侧导航栏 -->
        <div class="sidebar collapsed" id="sidebar">
            <div class="sidebar-toggle" id="sidebarToggle">▶</div>
            {sidebar_menu_html}
        </div>

        <!-- 内容区域 -->
        <div class="content-area">
            <!-- 页面标题 -->
            <div class="page-header">
                <h1 style="display: flex; align-items: center;">
                    📰 7*24快讯
                    <button id="refreshBtn" onclick="refreshCurrentPage()" class="refresh-button" style="margin-left: 15px; padding: 8px 16px; background: var(--accent); color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 0.9rem; font-weight: 500; transition: all 0.2s ease; display: inline-flex; align-items: center; gap: 5px;">🔄 刷新</button>
                </h1>
                <p>实时追踪全球市场动态</p>
            </div>

            <!-- 快讯内容 -->
            <div class="news-content">
                {news_content}
            </div>
        </div>
    </div>

    <script src="/static/js/main.js"></script>
    <script src="/static/js/sidebar-nav.js"></script>
    <script>
        // 自动颜色化
        function autoColorize() {{
            const elements = document.querySelectorAll('[data-change]');
            elements.forEach(function(el) {{
                const change = parseFloat(el.getAttribute('data-change'));
                if (change > 0) {{
                    el.style.color = '#f44336';
                }} else if (change < 0) {{
                    el.style.color = '#4caf50';
                }}
            }});
        }}

        document.addEventListener('DOMContentLoaded', function() {{
            // 歌词轮播
            const lyrics = [
                '总要有一首我的歌, 大声唱过, 再看天地辽阔 ————《一颗苹果》',
                '苍狗又白云, 身旁有了你, 匆匆轮回又有何惧 ————《如果我们不曾相遇》',
                '活着其实很好, 再吃一颗苹果 ————《一颗苹果》',
                '偶然与巧合, 舞动了蝶翼, 谁的心头风起 ————《如果我们不曾相遇》'
            ];
            let currentLyricIndex = 0;
            const lyricsElement = document.getElementById('lyricsDisplay');

            // 随机选择初始歌词
            currentLyricIndex = Math.floor(Math.random() * lyrics.length);
            if (lyricsElement) {{
                lyricsElement.textContent = lyrics[currentLyricIndex];

                // 每10秒切换一次歌词
                setInterval(function() {{
                    // 淡出
                    lyricsElement.style.opacity = '0';

                    setTimeout(function() {{
                        // 切换歌词
                        currentLyricIndex = (currentLyricIndex + 1) % lyrics.length;
                        lyricsElement.textContent = lyrics[currentLyricIndex];

                        // 淡入
                        lyricsElement.style.opacity = '1';
                    }}, 500);
                }}, 10000);
            }}

            autoColorize();
        }});
    </script>
</body>
</html>'''.format(css_style=css_style, username_display=username_display, news_content=news_content, sidebar_menu_html=sidebar_menu_html)
    return html


def get_admin_users_page_html(admin_users_content, username=None, is_admin=True):
    """生成用户管理页面 - 与其它页面一致的左侧 sidebar 布局"""
    css_style = get_css_style()
    sidebar_menu_html = get_sidebar_menu_items_html('admin-users', is_admin)

    username_display = ''
    if username:
        username_display += '<span class="nav-user">🍎 {username}</span>'.format(username=username)
        username_display += '<a href="/logout" class="nav-logout">退出登录</a>'

    html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>用户管理 - LanFund</title>
    <link rel="icon" href="/static/1.ico">
    {css_style}
    <link rel="stylesheet" href="/static/css/style.css">
    <style>
        body {{ background-color: var(--terminal-bg); color: var(--text-main); min-height: 100vh; display: flex; flex-direction: column; }}
        .top-navbar {{ display: flex; align-items: center; justify-content: space-between; padding: 12px 20px; border-bottom: 1px solid var(--border); background: var(--card-bg); }}
        .main-container {{ display: flex; flex: 1; }}
        .content-area {{ flex: 1; padding: 20px; overflow-y: auto; }}
        .admin-users-page {{ max-width: 640px; margin: 0 auto; }}
    </style>
</head>
<body>
    <nav class="top-navbar">
        <div class="top-navbar-brand"><img src="/static/1.ico" alt="Logo" class="navbar-logo"></div>
        <div class="top-navbar-quote" id="lyricsDisplay">偶然与巧合, 舞动了蝶翼, 谁的心头风起 ————《如果我们不曾相遇》</div>
        <div class="top-navbar-menu">{username_display}</div>
    </nav>
    <div class="main-container">
        <button class="hamburger-menu" id="hamburgerMenu"><span></span><span></span><span></span></button>
        <div class="sidebar collapsed" id="sidebar">
            <div class="sidebar-toggle" id="sidebarToggle">▶</div>
            {sidebar_menu_html}
        </div>
        <div class="content-area">
            <div class="admin-users-page">
                {admin_users_content}
            </div>
        </div>
    </div>
    <script src="/static/js/main.js"></script>
    <script src="/static/js/sidebar-nav.js"></script>
</body>
</html>'''.format(
        css_style=css_style,
        username_display=username_display,
        sidebar_menu_html=sidebar_menu_html,
        admin_users_content=admin_users_content
    )
    return html


def get_precious_metals_page_html(metals_data, username=None, is_admin=False):
    """生成贵金属行情页面"""
    css_style = get_css_style()
    sidebar_menu_html = get_sidebar_menu_items_html('precious-metals', is_admin)

    username_display = ''
    if username:
        username_display += '<span class="nav-user">🍎 {username}</span>'.format(username=username)
        username_display += '<a href="/logout" class="nav-logout">退出登录</a>'

    html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>贵金属行情 - LanFund</title>
    <link rel="icon" href="/static/1.ico">
    {css_style}
    <link rel="stylesheet" href="/static/css/style.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        body {{
            background-color: var(--terminal-bg);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }}

        /* 顶部导航栏 */
        .top-navbar {{
            background-color: var(--card-bg);
            color: var(--text-main);
            padding: 0.8rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border);
        }}

        .top-navbar-brand {{
            display: flex;
            align-items: center;
            flex: 0 0 auto;
        }}

        .navbar-logo {{
            width: 32px;
            height: 32px;
        }}

        .top-navbar-quote {{
            flex: 1;
            text-align: center;
            font-size: 1rem;
            font-weight: 500;
            color: var(--text-main);
            font-style: italic;
            padding: 0 2rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            letter-spacing: 0.05em;
            transition: opacity 0.5s ease-in-out;
        }}

        .top-navbar-menu {{
            display: flex;
            gap: 1rem;
            align-items: center;
        }}

        .nav-logout {{
            color: #f85149;
            text-decoration: none;
            font-weight: 500;
        }}

        .nav-user {{
            color: #3b82f6;
            font-weight: 500;
        }}

        /* 主容器 */
        .main-container {{
            display: flex;
            flex: 1;
        }}

        /* 内容区域 */
        .content-area {{
            flex: 1;
            padding: 20px;
            overflow-y: auto;
        }}

        /* 隐藏滚动条但保留功能 */
        ::-webkit-scrollbar {{
            width: 6px;
            height: 6px;
        }}

        ::-webkit-scrollbar-track {{
            background: transparent;
        }}

        ::-webkit-scrollbar-thumb {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 3px;
        }}

        ::-webkit-scrollbar-thumb:hover {{
            background: rgba(255, 255, 255, 0.2);
        }}

        /* Firefox */
        * {{
            scrollbar-width: thin;
            scrollbar-color: rgba(255, 255, 255, 0.1) transparent;
        }}

        .page-header {{
            margin-bottom: 20px;
        }}

        .page-header h1 {{
            font-size: 1.8rem;
            margin: 0;
            color: var(--text-main);
        }}

        .page-header p {{
            margin: 5px 0 0;
            color: var(--text-dim);
        }}

        /* 贵金属网格布局 - 上下两栏 */
        .metals-grid {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 20px;
            max-width: 100%;
        }}

        .metal-card {{
            background-color: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 8px;
            overflow: hidden;
            width: 100%;
        }}

        .metal-card-realtime {{
            min-height: 200px;
        }}

        .metal-card-history {{
            min-height: 400px;
        }}

        .metal-card {{
            background-color: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 8px;
            overflow: hidden;
        }}

        .metal-card-header {{
            padding: 15px 20px;
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .metal-card-title {{
            font-size: 1.1rem;
            font-weight: 500;
            color: var(--text-main);
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .metal-card-content {{
            padding: 20px;
            max-height: 500px;
            overflow-y: auto;
        }}

        .chart-container {{
            position: relative;
            height: 400px;
            width: 100%;
        }}

        /* 确保表格容器支持横向滚动 */
        .metal-card-realtime .table-container {{
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
        }}

        .metal-card-realtime .style-table {{
            min-width: max-content;
            white-space: nowrap;
        }}

        /* 响应式设计 */
        @media (max-width: 768px) {{
            .metals-grid {{
                grid-template-columns: 1fr;
            }}

            .content-area {{
                padding: 15px;
            }}

            /* 顶部导航栏两行布局 */
            .top-navbar {{
                flex-direction: row;
                flex-wrap: wrap;
                height: auto;
                padding: 0.5rem 1rem;
                align-items: center;
                border-bottom: none;
            }}

            .top-navbar > .top-navbar-brand {{
                order: 1;
                flex: 0 0 auto;
                padding-bottom: 0.5rem;
                border-bottom: 1px solid var(--border);
            }}

            .top-navbar-menu {{
                order: 1;
                flex: 0 0 auto;
                margin-left: auto;
                padding-bottom: 0.5rem;
                border-bottom: 1px solid var(--border);
            }}

            .top-navbar-quote {{
                order: 2;
                width: 100%;
                flex-basis: 100%;
                text-align: center;
                padding: 0.5rem 0;
                font-size: 0.8rem;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                border-top: 1px solid var(--border);
                margin-top: 0.5rem;
            }}

            /* 汉堡菜单显示 */
            .hamburger-menu {{
                display: flex !important;
            }}

            .metal-card-history {{
                min-height: 300px;
            }}

            .chart-container {{
                height: 280px;
            }}
        }}
    </style>
</head>
<body>
    <!-- 顶部导航栏 -->
    <nav class="top-navbar">
        <div class="top-navbar-brand">
            <img src="/static/1.ico" alt="Logo" class="navbar-logo">
        </div>
        <div class="top-navbar-quote" id="lyricsDisplay">
            偶然与巧合, 舞动了蝶翼, 谁的心头风起 ————《如果我们不曾相遇》
        </div>
        <div class="top-navbar-menu">
            {username_display}
        </div>
    </nav>

    <!-- 主容器 -->
    <div class="main-container">
        <!-- 汉堡菜单按钮 (移动端) -->
        <button class="hamburger-menu" id="hamburgerMenu">
            <span></span>
            <span></span>
            <span></span>
        </button>

        <!-- 左侧导航栏 -->
        <div class="sidebar collapsed" id="sidebar">
            <div class="sidebar-toggle" id="sidebarToggle">▶</div>
            {sidebar_menu_html}
        </div>

        <!-- 内容区域 -->
        <div class="content-area">
            <!-- 页面标题 -->
            <div class="page-header">
                <h1 style="display: flex; align-items: center;">
                    🥇 贵金属行情
                    <button id="refreshBtn" onclick="refreshCurrentPage()" class="refresh-button" style="margin-left: 15px; padding: 8px 16px; background: var(--accent); color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 0.9rem; font-weight: 500; transition: all 0.2s ease; display: inline-flex; align-items: center; gap: 5px;">🔄 刷新</button>
                </h1>
                <p>实时追踪贵金属价格走势</p>
            </div>

            <!-- 贵金属网格 - 上下两栏布局 -->
            <div class="metals-grid">
                <!-- 实时贵金属 -->
                <div class="metal-card metal-card-realtime">
                    <div class="metal-card-header">
                        <h3 class="metal-card-title">
                            <span>⚡</span>
                            <span>实时贵金属</span>
                        </h3>
                    </div>
                    <div class="metal-card-content">
                        {real_time_content}
                    </div>
                </div>

                <!-- 分时黄金价格 -->
                <div class="metal-card metal-card-history">
                    <div class="metal-card-header">
                        <h3 class="metal-card-title">
                            <span>📊</span>
                            <span>分时黄金价格</span>
                        </h3>
                    </div>
                    <div class="metal-card-content">
                        <!-- Hidden div to store one day gold data for parsing -->
                        <div id="goldOneDayData" style="display:none;">
                            {one_day_content}
                        </div>
                        <div class="chart-container">
                            <canvas id="goldOneDayChart"></canvas>
                        </div>
                    </div>
                </div>

                <!-- 历史金价 -->
                <div class="metal-card metal-card-history">
                    <div class="metal-card-header">
                        <h3 class="metal-card-title">
                            <span>📈</span>
                            <span>历史金价</span>
                        </h3>
                    </div>
                    <div class="metal-card-content">
                        <!-- Hidden div to store history data for parsing -->
                        <div id="goldHistoryData" style="display:none;">
                            {history_content}
                        </div>
                        <div class="chart-container">
                            <canvas id="goldPriceChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="/static/js/main.js"></script>
    <script src="/static/js/sidebar-nav.js"></script>
    <script>
        // 自动颜色化
        function autoColorize() {{
            const elements = document.querySelectorAll('[data-change]');
            elements.forEach(function(el) {{
                const change = parseFloat(el.getAttribute('data-change'));
                if (change > 0) {{
                    el.style.color = '#f44336';
                }} else if (change < 0) {{
                    el.style.color = '#4caf50';
                }}
            }});
        }}

        // 解析历史金价数据并创建图表
        function createGoldChart() {{
            // 从隐藏的div中获取历史金价表格
            const historyContainer = document.getElementById('goldHistoryData');
            if (!historyContainer) return;

            const table = historyContainer.querySelector('table');
            if (!table) return;

            const rows = table.querySelectorAll('tbody tr');
            const labels = [];
            const prices = [];

            rows.forEach(row => {{
                const cells = row.querySelectorAll('td');
                if (cells.length >= 2) {{
                    labels.push(cells[0].textContent.trim());
                    prices.push(parseFloat(cells[1].textContent.trim()));
                }}
            }});

            // 创建图表
            const ctx = document.getElementById('goldPriceChart').getContext('2d');

            // 注册插件以在数据点上显示数值
            const dataLabelPlugin = {{
                id: 'dataLabelPlugin',
                afterDatasetsDraw(chart, args, options) {{
                    const {{ ctx }} = chart;
                    chart.data.datasets.forEach((dataset, datasetIndex) => {{
                        const meta = chart.getDatasetMeta(datasetIndex);
                        meta.data.forEach((datapoint, index) => {{
                            const value = dataset.data[index];
                            const x = datapoint.x;
                            const y = datapoint.y;

                            ctx.save();
                            ctx.fillStyle = '#f59e0b';
                            ctx.font = 'bold 11px sans-serif';
                            ctx.textAlign = 'center';
                            ctx.textBaseline = 'bottom';
                            ctx.fillText(value.toFixed(2), x, y - 5);
                            ctx.restore();
                        }});
                    }});
                }}
            }};

            new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: labels.reverse(),
                    datasets: [{{
                        label: '金价 (元/克)',
                        data: prices.reverse(),
                        borderColor: '#f59e0b',
                        backgroundColor: 'rgba(245, 158, 11, 0.1)',
                        fill: true,
                        tension: 0.4,
                        pointRadius: 4,
                        pointBackgroundColor: '#f59e0b',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2,
                        pointHoverRadius: 6
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            labels: {{
                                color: '#9ca3af'
                            }}
                        }}
                    }},
                    scales: {{
                        x: {{
                            ticks: {{
                                color: '#9ca3af'
                            }},
                            grid: {{
                                color: 'rgba(255, 255, 255, 0.1)'
                            }}
                        }},
                        y: {{
                            ticks: {{
                                color: '#9ca3af'
                            }},
                            grid: {{
                                color: 'rgba(255, 255, 255, 0.1)'
                            }}
                        }}
                    }}
                }},
                plugins: [dataLabelPlugin]
            }});
        }}

        // 解析分时黄金价格数据并创建图表
        function createGoldOneDayChart() {{
            // 从隐藏的div中获取分时黄金价格数据
            const oneDayContainer = document.getElementById('goldOneDayData');
            if (!oneDayContainer) return;

            const dataText = oneDayContainer.textContent.trim();
            if (!dataText || dataText === 'None' || dataText === '') return;

            let data;
            try {{
                data = JSON.parse(dataText);
            }} catch (e) {{
                console.error('Failed to parse gold one day data:', e);
                return;
            }}

            if (!data || !Array.isArray(data) || data.length === 0) return;

            const labels = [];
            const prices = [];

            data.forEach(item => {{
                if (item.date && item.price !== undefined) {{
                    // 只显示时间部分 (HH:MM:SS)
                    const timePart = item.date.split(' ')[1] || item.date;
                    labels.push(timePart);
                    prices.push(parseFloat(item.price));
                }}
            }});

            // 创建图表
            const ctx = document.getElementById('goldOneDayChart').getContext('2d');

            // 获取最新价格和时间用于图例显示
            let labelText = '金价 (元/克)';
            if (data.length > 0) {{
                const latestData = data[data.length - 1];
                const timePart = latestData.date.split(' ')[1] || latestData.date;
                labelText = `金价 (元/克)  最新: ¥${{latestData.price}}  ${{timePart}}`;
            }}

            new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: labels,
                    datasets: [{{
                        label: labelText,
                        data: prices,
                        borderColor: '#f59e0b',
                        backgroundColor: 'rgba(245, 158, 11, 0.1)',
                        fill: true,
                        tension: 0.4,
                        pointRadius: 0,
                        pointHoverRadius: 0
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            labels: {{
                                color: '#9ca3af'
                            }}
                        }},
                        tooltip: {{
                            enabled: true,
                            mode: 'index',
                            intersect: false
                        }}
                    }},
                    scales: {{
                        x: {{
                            ticks: {{
                                color: '#9ca3af',
                                maxTicksLimit: 12
                            }},
                            grid: {{
                                color: 'rgba(255, 255, 255, 0.1)'
                            }}
                        }},
                        y: {{
                            ticks: {{
                                color: '#9ca3af'
                            }},
                            grid: {{
                                color: 'rgba(255, 255, 255, 0.1)'
                            }}
                        }}
                    }},
                    interaction: {{
                        mode: 'nearest',
                        axis: 'x',
                        intersect: false
                    }}
                }}
            }});
        }}

        document.addEventListener('DOMContentLoaded', function() {{
            // 歌词轮播
            const lyrics = [
                '总要有一首我的歌, 大声唱过, 再看天地辽阔 ————《一颗苹果》',
                '苍狗又白云, 身旁有了你, 匆匆轮回又有何惧 ————《如果我们不曾相遇》',
                '活着其实很好, 再吃一颗苹果 ————《一颗苹果》',
                '偶然与巧合, 舞动了蝶翼, 谁的心头风起 ————《如果我们不曾相遇》'
            ];
            let currentLyricIndex = 0;
            const lyricsElement = document.getElementById('lyricsDisplay');

            // 随机选择初始歌词
            currentLyricIndex = Math.floor(Math.random() * lyrics.length);
            if (lyricsElement) {{
                lyricsElement.textContent = lyrics[currentLyricIndex];

                // 每10秒切换一次歌词
                setInterval(function() {{
                    // 淡出
                    lyricsElement.style.opacity = '0';

                    setTimeout(function() {{
                        // 切换歌词
                        currentLyricIndex = (currentLyricIndex + 1) % lyrics.length;
                        lyricsElement.textContent = lyrics[currentLyricIndex];

                        // 淡入
                        lyricsElement.style.opacity = '1';
                    }}, 500);
                }}, 10000);
            }}

            autoColorize();
            createGoldChart();
            createGoldOneDayChart();
        }});
    </script>
</body>
</html>'''.format(
        css_style=css_style,
        username_display=username_display,
        real_time_content=metals_data.get('real_time', ''),
        one_day_content=metals_data.get('one_day', ''),
        history_content=metals_data.get('history', ''),
        sidebar_menu_html=sidebar_menu_html
    )
    return html


def get_market_indices_page_html(market_charts=None, chart_data=None, timing_data=None, username=None, is_admin=False):
    """生成市场指数页面 - 上证分时、全球指数和成交量趋势"""
    css_style = get_css_style()
    sidebar_menu_html = get_sidebar_menu_items_html('market-indices', is_admin)
    import json

    username_display = ''
    if username:
        username_display += '<span class="nav-user">🍎 {username}</span>'.format(username=username)
        username_display += '<a href="/logout" class="nav-logout">退出登录</a>'

    # 准备图表数据JSON (optional, for future chart enhancements)
    indices_data_json = json.dumps(chart_data.get('indices', {'labels': [], 'prices': [], 'changes': []}) if chart_data else {'labels': [], 'prices': [], 'changes': []})
    volume_data_json = json.dumps(chart_data.get('volume', {'labels': [], 'total': [], 'sh': [], 'sz': [], 'bj': []}) if chart_data else {'labels': [], 'total': [], 'sh': [], 'sz': [], 'bj': []})

    # 准备上证分时数据JSON
    timing_data_json = json.dumps(timing_data if timing_data else {'labels': [], 'prices': [], 'change_pcts': [], 'change_amounts': [], 'volumes': [], 'amounts': []})

    # 生成市场指数HTML - 两行布局
    market_content = '''
        <!-- 市场指数区域 -->
        <div class="market-indices-section" style="padding: 30px;">
            <div class="page-header" style="margin-bottom: 25px;">
                <h1 style="font-size: 1.5rem; font-weight: 600; margin: 0; color: var(--text-main); display: flex; align-items: center;">
                    📊 市场指数
                    <button id="refreshBtn" onclick="refreshCurrentPage()" class="refresh-button" style="margin-left: 15px; padding: 8px 16px; background: var(--accent); color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 0.9rem; font-weight: 500; transition: all 0.2s ease; display: inline-flex; align-items: center; gap: 5px;">🔄 刷新</button>
                </h1>
            </div>

            <!-- 第一行：上证分时（全宽） -->
            <div class="timing-chart-row" style="margin-bottom: 20px;">
                <div class="chart-card" style="background-color: var(--card-bg); border: 1px solid var(--border); border-radius: 8px; overflow: hidden;">
                    <div class="chart-card-header" style="padding: 12px 15px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center;">
                        <h3 id="timingChartTitle" style="margin: 0; font-size: 1rem; color: var(--text-main);">📉 上证分时</h3>
                    </div>
                    <div class="chart-card-content" style="padding: 15px; height: 350px;">
                        <canvas id="timingChart"></canvas>
                    </div>
                </div>
            </div>

            <!-- 第二行：全球指数和成交量趋势 -->
            <div class="market-charts-grid">
                <!-- 全球指数 - 表格 -->
                <div class="chart-card" style="background-color: var(--card-bg); border: 1px solid var(--border); border-radius: 8px; overflow: hidden;">
                    <div class="chart-card-header" style="padding: 12px 15px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center;">
                        <h3 style="margin: 0; font-size: 1rem; color: var(--text-main);">🌍 全球指数</h3>
                    </div>
                    <div class="chart-card-content" style="padding: 15px; max-height: 400px; overflow-y: auto;">
                        {indices_content}
                    </div>
                </div>
                <!-- 成交量趋势 - 表格 -->
                <div class="chart-card" style="background-color: var(--card-bg); border: 1px solid var(--border); border-radius: 8px; overflow: hidden;">
                    <div class="chart-card-header" style="padding: 12px 15px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center;">
                        <h3 style="margin: 0; font-size: 1rem; color: var(--text-main);">📊 成交量趋势</h3>
                    </div>
                    <div class="chart-card-content" style="padding: 15px; max-height: 400px; overflow-y: auto;">
                        {volume_content}
                    </div>
                </div>
            </div>
        </div>
    '''.format(
        indices_content=market_charts.get('indices', ''),
        volume_content=market_charts.get('volume', '')
    )

    html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>市场指数 - LanFund</title>
    <link rel="icon" href="/static/1.ico">
    {css_style}
    <link rel="stylesheet" href="/static/css/style.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        body {{
            background-color: var(--terminal-bg);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }}

        /* 顶部导航栏 */
        .top-navbar {{
            background-color: var(--card-bg);
            color: var(--text-main);
            padding: 0.8rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border);
        }}

        .top-navbar-brand {{
            display: flex;
            align-items: center;
            flex: 0 0 auto;
        }}

        .top-navbar-quote {{
            flex: 1;
            text-align: center;
            font-size: 1rem;
            font-weight: 500;
            color: var(--text-main);
            font-style: italic;
            padding: 0 2rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            letter-spacing: 0.05em;
            transition: opacity 0.5s ease-in-out;
        }}

        .top-navbar-menu {{
            display: flex;
            gap: 1rem;
            align-items: center;
        }}

        .nav-user {{
            color: #3b82f6;
            font-weight: 500;
        }}

        .nav-logout {{
            color: #f85149;
            text-decoration: none;
            font-weight: 500;
        }}

        /* 主容器 */
        .main-container {{
            display: flex;
            flex: 1;
        }}

        /* 内容区域 */
        .content-area {{
            flex: 1;
            overflow-y: auto;
        }}

        /* 隐藏滚动条但保留功能 */
        ::-webkit-scrollbar {{
            width: 6px;
            height: 6px;
        }}

        ::-webkit-scrollbar-track {{
            background: transparent;
        }}

        ::-webkit-scrollbar-thumb {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 3px;
        }}

        ::-webkit-scrollbar-thumb:hover {{
            background: rgba(255, 255, 255, 0.2);
        }}

        /* Firefox */
        * {{
            scrollbar-width: thin;
            scrollbar-color: rgba(255, 255, 255, 0.1) transparent;
        }}

        .chart-card-content::-webkit-scrollbar {{
            width: 4px;
        }}

        .chart-card-content::-webkit-scrollbar-thumb {{
            background: rgba(255, 255, 255, 0.05);
        }}

        @media (max-width: 768px) {{
            /* 顶部导航栏两行布局 */
            .top-navbar {{
                flex-direction: row;
                flex-wrap: wrap;
                height: auto;
                padding: 0.5rem 1rem;
                align-items: center;
                border-bottom: none;
            }}

            .top-navbar > .top-navbar-brand {{
                order: 1;
                flex: 0 0 auto;
                padding-bottom: 0.5rem;
                border-bottom: 1px solid var(--border);
            }}

            .top-navbar-menu {{
                order: 1;
                flex: 0 0 auto;
                margin-left: auto;
                padding-bottom: 0.5rem;
                border-bottom: 1px solid var(--border);
            }}

            .top-navbar-quote {{
                order: 2;
                width: 100%;
                flex-basis: 100%;
                text-align: center;
                padding: 0.5rem 0;
                font-size: 0.8rem;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                border-top: 1px solid var(--border);
                margin-top: 0.5rem;
            }}

            .timing-chart-row .chart-card-content {{
                height: 250px;
            }}
        }}
    </style>
</head>
<body>
    <!-- 顶部导航栏 -->
    <div class="top-navbar">
        <div class="top-navbar-brand">
            <img src="/static/1.ico" alt="Logo" class="navbar-logo">
        </div>
        <div class="top-navbar-quote" id="lyricsDisplay">
            偶然与巧合, 舞动了蝶翼, 谁的心头风起 ————《如果我们不曾相遇》
        </div>
        <div class="top-navbar-menu">
            {username_display}
        </div>
    </div>

    <!-- 主容器 -->
    <div class="main-container">
        <!-- 汉堡菜单按钮 (移动端) -->
        <button class="hamburger-menu" id="hamburgerMenu">
            <span></span>
            <span></span>
            <span></span>
        </button>

        <!-- 左侧导航栏 -->
        <div class="sidebar collapsed" id="sidebar">
            <div class="sidebar-toggle" id="sidebarToggle">▶</div>
            {sidebar_menu_html}
        </div>

        <!-- 内容区域 -->
        <div class="content-area">
            {market_content}
        </div>
    </div>

    <script src="/static/js/main.js"></script>
    <script src="/static/js/sidebar-nav.js"></script>
    <script>
        // 上证分时数据
        const timingData = {timing_data_json};

        document.addEventListener('DOMContentLoaded', function() {{
            // 歌词轮播
            const lyrics = [
                '总要有一首我的歌, 大声唱过, 再看天地辽阔 ————《一颗苹果》',
                '苍狗又白云, 身旁有了你, 匆匆轮回又有何惧 ————《如果我们不曾相遇》',
                '活着其实很好, 再吃一颗苹果 ————《一颗苹果》',
                '偶然与巧合, 舞动了蝶翼, 谁的心头风起 ————《如果我们不曾相遇》'
            ];
            let currentLyricIndex = 0;
            const lyricsElement = document.getElementById('lyricsDisplay');

            // 随机选择初始歌词
            currentLyricIndex = Math.floor(Math.random() * lyrics.length);
            if (lyricsElement) {{
                lyricsElement.textContent = lyrics[currentLyricIndex];

                // 每10秒切换一次歌词
                setInterval(function() {{
                    // 淡出
                    lyricsElement.style.opacity = '0';

                    setTimeout(function() {{
                        // 切换歌词
                        currentLyricIndex = (currentLyricIndex + 1) % lyrics.length;
                        lyricsElement.textContent = lyrics[currentLyricIndex];

                        // 淡入
                        lyricsElement.style.opacity = '1';
                    }}, 500);
                }}, 10000);
            }}

            // 自动颜色化
            const cells = document.querySelectorAll('.style-table td');
            cells.forEach(cell => {{
                const text = cell.textContent.trim();
                const cleanText = text.replace(/[%,亿万手]/g, '');
                const val = parseFloat(cleanText);

                if (!isNaN(val)) {{
                    if (text.includes('%') || text.includes('涨跌')) {{
                        if (text.includes('-')) {{
                            cell.classList.add('negative');
                        }} else if (val > 0) {{
                            cell.classList.add('positive');
                        }}
                    }} else if (text.startsWith('-')) {{
                        cell.classList.add('negative');
                    }} else if (text.startsWith('+')) {{
                        cell.classList.add('positive');
                    }}
                }}
            }});

            // 初始化上证分时图表
            initTimingChart();
        }});

        // 上证分时图表 - 使用API返回的实际涨跌幅
        function initTimingChart() {{
            const ctx = document.getElementById('timingChart');
            if (!ctx || timingData.labels.length === 0) return;

            // 使用API返回的实际数据（已经处理好的）
            const changePercentages = timingData.change_pcts || [];
            const changeAmounts = timingData.change_amounts || [];  // 原始涨跌额数据
            const basePrice = timingData.prices[0];
            const lastPrice = timingData.prices[timingData.prices.length - 1];

            // 使用最后一个实际涨跌幅值
            const lastPct = changePercentages.length > 0 ? changePercentages[changePercentages.length - 1] : 0;
            const titleColor = lastPct >= 0 ? '#f44336' : '#4caf50';

            // 更新标题颜色 - 现在主要显示实际涨跌幅
            const titleElement = document.getElementById('timingChartTitle');
            if (titleElement) {{
                titleElement.style.color = titleColor;
                titleElement.innerHTML = '📉 上证分时 <span style="font-size:0.9em;">' +
                    (lastPct >= 0 ? '+' : '-') + Math.abs(lastPct).toFixed(2) + '% (' + lastPrice.toFixed(2) + ')</span>';
            }}

            // 保存图表实例到全局变量，方便后续更新
            window.timingChartInstance = new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: timingData.labels,
                    datasets: [{{
                        label: '涨跌幅 (%)',
                        data: changePercentages,
                        borderColor: function(context) {{
                            // 动态返回颜色：>0% 红色，<0% 绿色，=0% 灰色
                            const index = context.dataIndex;
                            if (index === undefined || index < 0) return '#9ca3af';
                            const pct = changePercentages[index];
                            return pct > 0 ? '#f44336' : (pct < 0 ? '#4caf50' : '#9ca3af');
                        }},
                        segment: {{
                            borderColor: function(context) {{
                                // 根据线段的结束点判断颜色
                                const pct = changePercentages[context.p1DataIndex];
                                return pct > 0 ? '#f44336' : (pct < 0 ? '#4caf50' : '#9ca3af');
                            }}
                        }},
                        backgroundColor: function(context) {{
                            const chart = context.chart;
                            const {{ctx, chartArea}} = chart;
                            if (!chartArea) return null;
                            // 根据当前最新涨跌幅判断整体涨跌来设置背景色
                            const lastPct = changePercentages[changePercentages.length - 1];
                            const color = lastPct >= 0 ? '244, 67, 54' : '76, 175, 80';
                            const gradient = ctx.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
                            gradient.addColorStop(0, 'rgba(' + color + ', 0.2)');
                            gradient.addColorStop(1, 'rgba(' + color + ', 0.0)');
                            return gradient;
                        }},
                        fill: true,
                        tension: 0.4,
                        pointRadius: 0,
                        pointHoverRadius: 4,
                        borderWidth: 2
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {{
                        mode: 'index',
                        intersect: false,
                    }},
                    plugins: {{
                        legend: {{
                            display: true,
                            position: 'top',
                            labels: {{
                                font: {{ size: 11 }},
                                boxWidth: 12,
                                generateLabels: function(chart) {{
                                    const lastPct = changePercentages[changePercentages.length - 1];
                                    const color = lastPct >= 0 ? '#ff4d4f' : '#52c41a';
                                    return [{{
                                        text: '涨跌幅: ' + (lastPct >= 0 ? '+' : '-') + Math.abs(lastPct).toFixed(2) + '% (' + lastPrice.toFixed(2) + ')',
                                        fillStyle: color,
                                        strokeStyle: color,
                                        fontColor: color,
                                        lineWidth: 2,
                                        hidden: false,
                                        index: 0
                                    }}];
                                }}
                            }}
                        }},
                        tooltip: {{
                            callbacks: {{
                                title: function(context) {{
                                    return '时间: ' + context[0].label;
                                }},
                                label: function(context) {{
                                    const index = context.dataIndex;
                                    const pct = changePercentages[index];
                                    const price = timingData.prices[index];
                                    const changeAmt = changeAmounts[index];  // 使用原始涨跌额数据
                                    const volume = timingData.volumes ? timingData.volumes[index] : 0;
                                    const amount = timingData.amounts ? timingData.amounts[index] : 0;
                                    return [
                                        '涨跌幅: ' + (pct >= 0 ? '+' : '-') + Math.abs(pct).toFixed(2) + '%',
                                        '上证指数: ' + price.toFixed(2),
                                        '涨跌额: ' + (changeAmt >= 0 ? '+' : '-') + Math.abs(changeAmt).toFixed(2),
                                        '成交量: ' + volume.toFixed(0) + '万手',
                                        '成交额: ' + amount.toFixed(2) + '亿'
                                    ];
                                }}
                            }}
                        }},
                        datalabels: {{
                            display: false
                        }}
                    }},
                    scales: {{
                        x: {{
                            ticks: {{
                                color: '#9ca3af',
                                font: {{ size: 10 }},
                                maxTicksLimit: 6
                            }},
                            grid: {{
                                color: 'rgba(255, 255, 255, 0.1)'
                            }}
                        }},
                        y: {{
                            title: {{
                                display: true,
                                text: '涨跌幅 (%)',
                                color: '#9ca3af',
                                font: {{ size: 11 }}
                            }},
                            ticks: {{
                                color: '#9ca3af',
                                callback: function(value) {{
                                    return (value >= 0 ? '+' : '-') + Math.abs(value).toFixed(2) + '%';
                                }}
                            }},
                            grid: {{
                                color: 'rgba(255, 255, 255, 0.1)'
                            }}
                        }}
                    }}
                }}
            }});
        }}
    </script>
</body>
</html>'''.format(
        css_style=css_style,
        username_display=username_display,
        market_content=market_content,
        timing_data_json=timing_data_json,
        sidebar_menu_html=sidebar_menu_html
    )
    return html


def get_portfolio_page_html(fund_content, fund_map, fund_chart_data=None, fund_chart_info=None, username=None, is_admin=False):
    """生成持仓基金页面"""
    css_style = get_css_style()
    sidebar_menu_html = get_sidebar_menu_items_html('portfolio', is_admin)
    import json

    username_display = ''
    if username:
        username_display += '<span class="nav-user">🍎 {username}</span>'.format(username=username)
        username_display += '<a href="/logout" class="nav-logout">退出登录</a>'

    # 准备估值趋势图数据JSON
    fund_chart_data_json = json.dumps(fund_chart_data if fund_chart_data else {'labels': [], 'growth': [], 'net_values': []})
    fund_chart_info_json = json.dumps(fund_chart_info if fund_chart_info else {})

    html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>持仓基金 - LanFund</title>
    <link rel="icon" href="/static/1.ico">
    {css_style}
    <link rel="stylesheet" href="/static/css/style.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        body {{
            background-color: var(--terminal-bg);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }}

        /* 顶部导航栏 */
        .top-navbar {{
            background-color: var(--card-bg);
            color: var(--text-main);
            padding: 0.8rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border);
        }}

        .top-navbar-brand {{
            display: flex;
            align-items: center;
            flex: 0 0 auto;
        }}

        .top-navbar-quote {{
            flex: 1;
            text-align: center;
            font-size: 1rem;
            font-weight: 500;
            color: var(--text-main);
            font-style: italic;
            padding: 0 2rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            letter-spacing: 0.05em;
            transition: opacity 0.5s ease-in-out;
        }}

        .top-navbar-menu {{
            display: flex;
            gap: 1rem;
            align-items: center;
        }}

        .nav-user {{
            color: #3b82f6;
            font-weight: 500;
        }}

        .nav-logout {{
            color: #f85149;
            text-decoration: none;
            font-weight: 500;
        }}

        /* 主容器 */
        .main-container {{
            display: flex;
            flex: 1;
        }}

        /* 内容区域 */
        .content-area {{
            flex: 1;
            padding: 30px;
            overflow-y: auto;
        }}

        .portfolio-header {{
            margin-bottom: 20px;
        }}

        .portfolio-header h1 {{
            font-size: 1.5rem;
            font-weight: 600;
            margin: 0;
            color: var(--text-main);
        }}

        .portfolio-header p {{
            color: var(--text-dim);
            margin: 5px 0 0;
            font-size: 0.9rem;
        }}

        .operations-panel {{
            background: rgba(102, 126, 234, 0.05);
            border: 1px solid rgba(102, 126, 234, 0.1);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 30px;
        }}

        .operation-group {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }}

        .fund-content {{
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 12px;
            overflow: hidden;
        }}

        .portfolio-tab {{
            padding: 8px 16px;
            border: 1px solid var(--border);
            border-radius: 8px;
            background: var(--card-bg);
            color: var(--text-main);
            cursor: pointer;
            font-size: 0.9rem;
        }}

        .portfolio-tab:hover {{
            background: rgba(59, 130, 246, 0.15);
            border-color: var(--accent);
        }}

        .portfolio-tab.active {{
            background: var(--accent);
            border-color: var(--accent);
            color: #fff;
        }}

        .portfolio-tab-new {{
            border-style: dashed;
        }}

        .portfolio-tab-group {{
            background: rgba(59, 130, 246, 0.08);
            border-color: rgba(59, 130, 246, 0.35);
        }}

        .portfolio-tab-group:hover {{
            background: rgba(59, 130, 246, 0.18);
        }}

        .portfolio-tab-group.active {{
            background: rgba(59, 130, 246, 0.25);
            border-color: var(--accent);
        }}

        @media (max-width: 768px) {{
            .main-container {{
                flex-direction: column;
            }}

            .sidebar {{
                width: 100%;
                border-right: none;
                border-bottom: 1px solid var(--border);
                padding: 10px 0;
            }}

            .sidebar-item {{
                padding: 10px 15px;
                font-size: 0.9rem;
            }}

            .content-area {{
                padding: 15px;
            }}

            /* 顶部导航栏两行布局 */
            .top-navbar {{
                flex-direction: row;
                flex-wrap: wrap;
                height: auto;
                padding: 0.5rem 1rem;
                align-items: center;
                border-bottom: none;
            }}

            .top-navbar > .top-navbar-brand {{
                order: 1;
                flex: 0 0 auto;
                padding-bottom: 0.5rem;
                border-bottom: 1px solid var(--border);
            }}

            .top-navbar-menu {{
                order: 1;
                flex: 0 0 auto;
                margin-left: auto;
                padding-bottom: 0.5rem;
                border-bottom: 1px solid var(--border);
            }}

            .top-navbar-quote {{
                order: 2;
                width: 100%;
                flex-basis: 100%;
                text-align: center;
                padding: 0.5rem 0;
                font-size: 0.8rem;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                border-top: 1px solid var(--border);
                margin-top: 0.5rem;
            }}

            .market-charts-grid {{
                grid-template-columns: 1fr;
                gap: 15px;
            }}

            .chart-card {{
                min-height: auto;
            }}

            .chart-card-content {{
                max-height: 200px;
            }}

            .chart-card h3 {{
                font-size: 0.9rem;
            }}
        }}

        @media (max-width: 1024px) {{
            .market-charts-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}

        /* 基金选择器容器 */
        .fund-selector-wrapper {{
            position: relative;
            display: flex;
            align-items: center;
            flex: 1;
            min-width: 200px;
            max-width: 500px;
        }}

        /* 输入框样式 - 隐藏原生箭头 */
        #fundSelector {{
            flex: 1;
            width: 100%;
            min-width: 150px;
            padding: 6px 32px 6px 12px;
            background: var(--card-bg);
            color: var(--text-main);
            border: 1px solid var(--border);
            border-radius: 6px;
            font-size: var(--font-size-md);
            line-height: 1.5;
            /* 隐藏原生datalist箭头 */
            appearance: none;
            -webkit-appearance: none;
            -moz-appearance: none;
        }}

        /* 隐藏Webkit浏览器的下拉按钮 */
        #fundSelector::-webkit-calendar-picker-indicator {{
            opacity: 0;
            display: none;
        }}

        /* 输入框焦点样式 */
        #fundSelector:focus {{
            outline: none;
            border-color: #3b82f6;
            box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
        }}

        /* 清除按钮 */
        .input-clear-btn {{
            position: absolute;
            right: 8px;
            top: 50%;
            transform: translateY(-50%);
            display: flex;
            align-items: center;
            justify-content: center;
            width: 16px;
            height: 16px;
            border-radius: 50%;
            background-color: #9ca3af;
            color: #fff !important;
            font-size: var(--font-size-xs) !important;
            font-weight: bold;
            cursor: pointer;
            opacity: 0;
            transition: opacity 0.2s ease, background-color 0.2s ease;
            z-index: 2;
        }}

        /* 有内容且hover时显示清除按钮 */
        .fund-selector-wrapper.has-value:hover .input-clear-btn {{
            opacity: 1;
        }}

        .input-clear-btn:hover {{
            background-color: #6b7280;
        }}

        /* 基金选择器下拉箭头 */
        .fund-selector-dropdown-arrow {{
            position: absolute;
            right: 8px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-dim);
            font-size: var(--font-size-xs);
            pointer-events: none;
            transition: transform 0.2s ease;
        }}

        .fund-selector-wrapper:hover .fund-selector-dropdown-arrow {{
            color: var(--text-main);
        }}

        /* 清除按钮位置调整 */
        .input-clear-btn {{
            right: 24px; /* 为箭头留出空间 */
        }}

        /* 基金选择列表项 */
        .fund-chart-selector-item {{
            padding: 12px;
            margin-bottom: 8px;
            cursor: pointer;
            border-radius: 6px;
            transition: background-color 0.2s ease;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .fund-chart-selector-item:hover {{
            background-color: rgba(59, 130, 246, 0.1);
        }}

        .fund-chart-selector-item .fund-code {{
            font-weight: 600;
            color: var(--text-main);
            min-width: 70px;
        }}

        .fund-chart-selector-item .fund-name {{
            flex: 1;
            color: var(--text-dim);
        }}

        .fund-chart-selector-item.is-default {{
            background-color: rgba(59, 130, 246, 0.15);
            border-left: 3px solid #3b82f6;
        }}

        /* 移动端优化 */
        @media (max-width: 768px) {{
            #fundSelector {{
                font-size: var(--font-size-lg); /* 防止iOS自动缩放 */
                padding: 8px 36px 8px 12px;
            }}

            .input-clear-btn {{
                width: 20px;
                height: 20px;
                font-size: var(--font-size-sm);
                right: 26px;
            }}

            .fund-selector-dropdown-arrow {{
                font-size: var(--font-size-sm);
                right: 10px;
            }}

            .fund-chart-selector-item {{
                padding: 16px 12px; /* 增大点击区域 */
            }}

            #fundChartSelectorModal .sector-modal-content {{
                width: 95%;
                max-height: 85vh;
            }}
        }}
    </style>
</head>
<body>
    <!-- 顶部导航栏 -->
    <nav class="top-navbar">
        <div class="top-navbar-brand">
            <img src="/static/1.ico" alt="Logo" class="navbar-logo">
        </div>
        <div class="top-navbar-quote" id="lyricsDisplay">
            偶然与巧合, 舞动了蝶翼, 谁的心头风起 ————《如果我们不曾相遇》
        </div>
        <div class="top-navbar-menu">
            {username_display}
        </div>
    </nav>

    <!-- 主容器 -->
    <div class="main-container">
        <!-- 汉堡菜单按钮 (移动端) -->
        <button class="hamburger-menu" id="hamburgerMenu">
            <span></span>
            <span></span>
            <span></span>
        </button>

        <!-- 左侧导航栏 -->
        <div class="sidebar collapsed" id="sidebar">
            <div class="sidebar-toggle" id="sidebarToggle">▶</div>
            {sidebar_menu_html}
        </div>

        <!-- 内容区域 -->
        <div class="content-area">
            <!-- 页面标题 -->
            <div class="portfolio-header">
                <h1>
                    💼 持仓基金
                    <button id="refreshBtn" onclick="refreshCurrentPage()" class="refresh-button">🔄 刷新</button>
                </h1>
            </div>

            <!-- Refresh button styling -->
            <style>
                .refresh-button {{
                    margin-left: 15px;
                    padding: 8px 16px;
                    background: var(--accent);
                    color: white;
                    border: none;
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 0.9rem;
                    font-weight: 500;
                    transition: all 0.2s ease;
                    display: inline-flex;
                    align-items: center;
                    gap: 5px;
                }}
                .refresh-button:hover {{
                    background: #2563eb;
                    transform: translateY(-1px);
                }}
                .refresh-button:disabled {{
                    background: #6b7280;
                    cursor: not-allowed;
                    transform: none;
                }}
                .portfolio-header h1 {{
                    display: flex;
                    align-items: center;
                }}
            </style>

            <!-- 免责声明 -->
            <div style="margin-bottom: 20px; padding: 12px 15px; background: rgba(255, 193, 7, 0.1); border: 1px solid rgba(255, 193, 7, 0.3); border-radius: 8px; font-size: 0.85rem; color: var(--text-dim);">
                <p style="margin: 0; line-height: 1.5;">
                    <strong style="color: #ffc107;">⚠️ 免责声明</strong>：
                    预估收益根据您输入的持仓份额与实时估值计算得出，仅供参考。
                    实际收益以基金公司最终结算为准，可能因份额确认时间、分红方式、费用扣除等因素存在偏差。
                    投资有风险，入市需谨慎。
                </p>
            </div>

            <!-- 基金估值趋势图 -->
            <div id="fundChartContainer" class="chart-card" style="background-color: var(--card-bg); border: 1px solid var(--border); border-radius: 8px; overflow: hidden; margin-bottom: 20px;">
                <div class="chart-card-header" style="padding: 12px 15px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center;">
                    <div style="display: flex; align-items: center; gap: 15px; flex-wrap: wrap;">
                        <h3 id="fundChartTitle" style="margin: 0; font-size: 1rem; color: var(--text-main); flex-shrink: 0;">📈 基金估值</h3>
                        <div class="fund-selector-wrapper" id="fundSelectorWrapper" style="flex: 1; min-width: 280px; max-width: 100%;">
                            <input type="text" id="fundSelector" placeholder="选择或搜索基金代码/名称..." autocomplete="off" readonly>
                            <span id="fundSelectorClear" class="input-clear-btn">✕</span>
                            <span class="fund-selector-dropdown-arrow" id="fundSelectorArrow">▼</span>
                        </div>
                    </div>
                </div>
                <div class="chart-card-content" style="padding: 15px; height: 300px;">
                    <canvas id="fundChart"></canvas>
                </div>
            </div>

            <!-- 基金内容（含持有/自选/分组 tab 与分页，由 fund_content 内 portfolio-with-tabs 提供） -->
            <div class="fund-content">
                {fund_content}
            </div>
        </div>
    </div>

    <!-- 新建分组弹窗 -->
    <div class="sector-modal" id="newGroupModal">
        <div class="sector-modal-content" style="max-width: 360px;">
            <div class="sector-modal-header">新建分组</div>
            <div style="padding: 16px 20px;">
                <label style="display: block; font-size: var(--font-size-base); color: var(--text-dim); margin-bottom: 8px;">分组名称</label>
                <input type="text" id="newGroupName" placeholder="例如：科技板块" class="sector-modal-search" style="width: 100%; margin-bottom: 0;">
            </div>
            <div class="sector-modal-footer">
                <button class="btn btn-secondary" onclick="closeNewGroupModal()">取消</button>
                <button class="btn btn-primary" onclick="submitNewGroup()">创建</button>
            </div>
        </div>
    </div>

    <!-- Modals (复用现有模态框) -->
    <div class="sector-modal" id="sectorModal">
        <div class="sector-modal-content">
            <div class="sector-modal-header">选择板块</div>
            <input type="text" class="sector-modal-search" id="sectorSearch" placeholder="搜索板块名称...">
            <div id="sectorCategories"></div>
            <div class="sector-modal-footer">
                <button class="btn btn-secondary" onclick="closeSectorModal()">取消</button>
                <button class="btn btn-primary" onclick="confirmSector()">确定</button>
            </div>
        </div>
    </div>

    <div class="sector-modal" id="fundSelectionModal">
        <div class="sector-modal-content">
            <div class="sector-modal-header" id="fundSelectionTitle">选择基金</div>
            <input type="text" class="sector-modal-search" id="fundSelectionSearch" placeholder="搜索基金代码或名称...">
            <div id="fundSelectionList" style="max-height: 400px; overflow-y: auto;"></div>
            <div class="sector-modal-footer">
                <button class="btn btn-secondary" onclick="closeFundSelectionModal()">取消</button>
                <button class="btn btn-primary" id="fundSelectionConfirmBtn" onclick="confirmFundSelection()">确定</button>
            </div>
        </div>
    </div>

    <div class="confirm-dialog" id="confirmDialog">
        <div class="confirm-dialog-content">
            <h3 id="confirmTitle" class="confirm-title"></h3>
            <p id="confirmMessage" class="confirm-message"></p>
            <div class="confirm-actions">
                <button class="btn btn-secondary" onclick="closeConfirmDialog()">取消</button>
                <button class="btn btn-primary" id="confirmBtn">确定</button>
            </div>
        </div>
    </div>

    <!-- 基金图表选择模态框 -->
    <div class="sector-modal" id="fundChartSelectorModal">
        <div class="sector-modal-content" style="max-width: 500px;">
            <div class="sector-modal-header">选择基金</div>
            <input type="text" class="sector-modal-search" id="fundChartSelectorSearch" placeholder="搜索基金代码或名称...">
            <div id="fundChartSelectorList" style="max-height: 400px; overflow-y: auto;">
                <!-- 基金列表将通过JS动态生成 -->
            </div>
            <div class="sector-modal-footer">
                <button class="btn btn-secondary" onclick="closeFundChartSelectorModal()">取消</button>
            </div>
        </div>
    </div>

    <!-- 份额设置弹窗 -->
    <div class="sector-modal" id="sharesModal">
        <div class="sector-modal-content" style="max-width: 420px;">
            <div class="sector-modal-header">设置持仓份额</div>
            <div style="padding: 20px;">
                <div style="margin-bottom: 15px;">
                    <label style="display: block; margin-bottom: 8px; color: var(--text-main); font-weight: 500;">基金代码</label>
                    <div id="sharesModalFundCode" style="padding: 10px; background: rgba(59, 130, 246, 0.1); border-radius: 6px; color: #3b82f6; font-weight: 600; font-family: monospace;"></div>
                </div>
                <div style="margin-bottom: 15px;">
                    <label for="sharesModalHoldingUnits" style="display: block; margin-bottom: 8px; color: var(--text-main); font-weight: 500;">持有份额</label>
                    <input type="number" id="sharesModalHoldingUnits" step="0.01" min="0" placeholder="请输入持有份额"
                           oninput="if(window.updateSharesModalResult) window.updateSharesModalResult()"
                           style="width: 100%; padding: 10px 12px; border: 1px solid var(--border); border-radius: 6px; font-size: var(--font-size-md); background: var(--card-bg); color: var(--text-main);">
                </div>
                <div style="margin-bottom: 15px;">
                    <label for="sharesModalCostPerUnit" style="display: block; margin-bottom: 8px; color: var(--text-main); font-weight: 500;">持仓成本（每份成本）</label>
                    <input type="number" id="sharesModalCostPerUnit" step="0.0001" min="0" placeholder="请输入每份成本"
                           oninput="if(window.updateSharesModalResult) window.updateSharesModalResult()"
                           style="width: 100%; padding: 10px 12px; border: 1px solid var(--border); border-radius: 6px; font-size: var(--font-size-md); background: var(--card-bg); color: var(--text-main);">
                </div>
                <div style="margin-bottom: 8px; padding: 10px; background: var(--border); border-radius: 6px;">
                    <strong id="sharesModalResult" style="display: block; color: var(--text-main); font-family: var(--font-mono);">0.00</strong>
                </div>
            </div>
            <div class="sector-modal-footer">
                <button class="btn btn-secondary" onclick="closeSharesModal()">取消</button>
                <button class="btn btn-primary" onclick="confirmShares()">确定</button>
            </div>
        </div>
    </div>

    <!-- 同步加仓弹窗 -->
    <div id="addPositionModal" class="sector-modal">
        <div class="sector-modal-content add-position-modal-content" style="max-width: 420px;">
            <div class="sector-modal-header" style="display: flex; align-items: center; justify-content: space-between;">
                <span>同步加仓</span>
                <button type="button" onclick="closeAddPositionModal()" style="background: none; border: none; font-size: var(--font-size-xl); color: var(--text-dim); cursor: pointer; padding: 0 4px;">×</button>
            </div>
            <div style="padding: 16px 20px;">
                <div class="add-position-tip" style="display: none; background: #fef3c7; color: #92400e; padding: 8px 12px; border-radius: 8px; margin-bottom: 12px; font-size: var(--font-size-base);">
                    <span id="addPositionTipText"></span>
                    <button type="button" onclick="this.parentElement.style.display='none'" style="float: right; background: none; border: none; cursor: pointer; color: #92400e;">×</button>
                </div>
                <div style="margin-bottom: 12px;">
                    <div id="addPositionFundName" style="font-size: var(--font-size-lg); font-weight: 600; color: var(--text-main);"></div>
                    <div id="addPositionFundCode" style="font-size: var(--font-size-sm); color: var(--text-dim); margin-top: 2px;"></div>
                </div>
                <div style="margin-bottom: 12px; padding: 10px 12px; background: var(--border); border-radius: 8px;">
                    <span style="font-size: var(--font-size-base); color: var(--text-dim);">最新净值</span><span id="addPositionNetValueDate" style="font-size: var(--font-size-sm); color: var(--text-dim); margin-left: 4px;"></span><span id="addPositionNetValue" style="font-weight: 600; color: var(--text-main); margin-left: 6px;"></span>
                    <span id="addPositionNetValuePct" style="font-size: var(--font-size-base); margin-left: 6px;"></span>
                </div>
                <div style="margin-bottom: 12px;">
                    <label style="display: block; font-size: var(--font-size-base); font-weight: 500; color: var(--text-main); margin-bottom: 6px;">同步加仓金额</label>
                    <div style="display: flex; align-items: center; border: 1px solid var(--border); border-radius: 8px; background: var(--card-bg);">
                        <span style="padding: 10px 12px; color: var(--text-dim);">¥</span>
                        <input type="number" id="addPositionAmount" step="0.01" min="0" placeholder="已买入金额" style="flex: 1; padding: 10px 0; border: none; background: none; font-size: var(--font-size-md); color: var(--text-main);" oninput="if(window.updateAddPositionFee) window.updateAddPositionFee()">
                    </div>
                </div>
                <div style="margin-bottom: 12px;">
                    <label style="display: block; font-size: var(--font-size-base); font-weight: 500; color: var(--text-main); margin-bottom: 6px;">买入费率</label>
                    <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                        <label style="display: inline-flex; align-items: center; cursor: pointer; font-size: var(--font-size-base); color: var(--text-main);"><input type="radio" name="addPositionFeeRate" value="0" checked style="margin-right: 4px;">0.0%</label>
                        <label style="display: inline-flex; align-items: center; cursor: pointer; font-size: var(--font-size-base); color: var(--text-main);"><input type="radio" name="addPositionFeeRate" value="0.1" style="margin-right: 4px;">0.1%</label>
                        <label style="display: inline-flex; align-items: center; cursor: pointer; font-size: var(--font-size-base); color: var(--text-main);"><input type="radio" name="addPositionFeeRate" value="0.15" style="margin-right: 4px;">0.15%</label>
                    </div>
                </div>
                <div style="margin-bottom: 12px; font-size: var(--font-size-sm); color: var(--text-dim);">
                    估算手续费 <span id="addPositionFee">0.00</span> 元
                </div>
                <div style="margin-bottom: 12px;">
                    <label style="display: block; font-size: var(--font-size-base); font-weight: 500; color: var(--text-main); margin-bottom: 6px;">原平台买入时间</label>
                    <div id="addPositionTimeDisplay" onclick="openAddPositionTimePicker()" style="padding: 10px 12px; border: 1px solid var(--border); border-radius: 8px; background: var(--card-bg); color: var(--text-main); cursor: pointer; display: flex; align-items: center; justify-content: space-between;">
                        <span id="addPositionTimeText" style="font-size: var(--font-size-md);">请选择时间</span>
                        <span style="color: var(--text-dim);">▼</span>
                    </div>
                </div>
            </div>
            <div class="sector-modal-footer">
                <button class="btn btn-secondary" onclick="closeAddPositionModal()">取消</button>
                <button type="button" id="addPositionConfirmBtn" class="btn btn-primary" onclick="confirmAddPosition()">确认</button>
            </div>
        </div>
    </div>
    <div id="addPositionTimePicker" style="display: none; position: fixed; inset: 0; z-index: 10002; align-items: center; justify-content: center; pointer-events: none;">
        <div class="sector-modal-content" style="max-width: 378px; width: 90%; pointer-events: auto; box-shadow: 0 4px 20px rgba(0,0,0,0.2); padding: 0 18px 14px;">
            <div style="display: flex; align-items: center; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid var(--border); margin-bottom: 10px;">
                <button type="button" onclick="closeAddPositionTimePicker()" style="background: none; border: none; color: var(--accent); font-size: var(--font-size-lg); cursor: pointer;">取消</button>
                <span style="font-weight: 600; color: var(--text-main); font-size: var(--font-size-lg);">加仓时间</span>
                <button type="button" onclick="confirmAddPositionTime()" style="background: none; border: none; color: var(--accent); font-size: var(--font-size-lg); cursor: pointer;">确认</button>
            </div>
            <div id="addPositionTimeOptions" style="overflow-y: auto; max-height: 320px; padding: 4px 0;"></div>
        </div>
    </div>
    <div id="addPositionTimePickerOverlay" onclick="closeAddPositionTimePicker()" style="display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.4); z-index: 10001;"></div>
    <div id="reducePositionModal" class="sector-modal">
        <div class="sector-modal-content" style="max-width: 420px;">
            <div class="sector-modal-header" style="display: flex; align-items: center; justify-content: space-between;">
                <span>同步减仓</span>
                <button type="button" onclick="closeReducePositionModal()" style="background: none; border: none; font-size: var(--font-size-xl); color: var(--text-dim); cursor: pointer; padding: 0 4px;">×</button>
            </div>
            <div style="padding: 16px 20px;">
                <div style="margin-bottom: 12px;">
                    <div id="reducePositionFundName" style="font-size: var(--font-size-lg); font-weight: 600; color: var(--text-main);"></div>
                    <div id="reducePositionFundCode" style="font-size: var(--font-size-sm); color: var(--text-dim); margin-top: 2px;"></div>
                </div>
                <div style="margin-bottom: 12px; padding: 10px 12px; background: var(--border); border-radius: 8px;">
                    <span style="font-size: var(--font-size-base); color: var(--text-dim);">当前净值</span><span id="reducePositionNetValue" style="font-weight: 600; color: var(--text-main); margin-left: 8px;"></span>
                    <span style="font-size: var(--font-size-sm); color: var(--text-dim); margin-left: 8px;">持有份额</span><span id="reducePositionHoldingUnits" style="font-weight: 500; margin-left: 4px;"></span>
                </div>
                <div style="margin-bottom: 12px;">
                    <label style="display: block; font-size: var(--font-size-base); font-weight: 500; color: var(--text-main); margin-bottom: 6px;">减仓份额</label>
                    <div style="display: flex; align-items: center; border: 1px solid var(--border); border-radius: 8px; background: var(--card-bg);">
                        <input type="number" id="reducePositionUnits" step="0.01" min="0" placeholder="请输入减仓份额" style="flex: 1; padding: 10px 12px; border: none; background: none; font-size: var(--font-size-md); color: var(--text-main);">
                    </div>
                </div>
                <div style="margin-bottom: 12px;">
                    <label style="display: block; font-size: var(--font-size-base); font-weight: 500; color: var(--text-main); margin-bottom: 6px;">原平台卖出时间</label>
                    <div id="reducePositionTimeDisplay" onclick="openReducePositionTimePicker()" style="padding: 10px 12px; border: 1px solid var(--border); border-radius: 8px; background: var(--card-bg); color: var(--text-main); cursor: pointer; display: flex; align-items: center; justify-content: space-between;">
                        <span id="reducePositionTimeText" style="font-size: var(--font-size-md);">请选择时间</span>
                        <span style="color: var(--text-dim);">▼</span>
                    </div>
                </div>
            </div>
            <div class="sector-modal-footer">
                <button class="btn btn-secondary" onclick="closeReducePositionModal()">取消</button>
                <button type="button" id="reducePositionConfirmBtn" class="btn btn-primary" onclick="confirmReducePosition()">确认</button>
            </div>
        </div>
    </div>
    <div id="reducePositionTimePicker" style="display: none; position: fixed; inset: 0; z-index: 10002; align-items: center; justify-content: center; pointer-events: none;">
        <div class="sector-modal-content" style="max-width: 378px; width: 90%; pointer-events: auto; box-shadow: 0 4px 20px rgba(0,0,0,0.2); padding: 0 18px 14px;">
            <div style="display: flex; align-items: center; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid var(--border); margin-bottom: 10px;">
                <button type="button" onclick="closeReducePositionTimePicker()" style="background: none; border: none; color: var(--accent); font-size: var(--font-size-lg); cursor: pointer;">取消</button>
                <span style="font-weight: 600; color: var(--text-main); font-size: var(--font-size-lg);">卖出时间</span>
                <button type="button" onclick="confirmReducePositionTime()" style="background: none; border: none; color: var(--accent); font-size: var(--font-size-lg); cursor: pointer;">确认</button>
            </div>
            <div id="reducePositionTimeOptions" style="overflow-y: auto; max-height: 320px; padding: 4px 0;"></div>
        </div>
    </div>
    <div id="reducePositionTimePickerOverlay" onclick="closeReducePositionTimePicker()" style="display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.4); z-index: 10001;"></div>

    <script src="/static/js/main.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            // 导入基金列表：若 main.js 未挂载则在此提供回退，确保持仓页导入可用
            if (typeof window.uploadFundMap !== 'function') {{
                window.uploadFundMap = async function(file) {{
                    if (!file) {{ alert('请选择文件'); return; }}
                    if (!file.name.endsWith('.json')) {{ alert('只支持JSON文件'); return; }}
                    const formData = new FormData();
                    formData.append('file', file);
                    try {{
                        const response = await fetch('/api/fund/upload', {{ method: 'POST', body: formData }});
                        const result = await response.json();
                        if (result.success) {{ alert(result.message); location.reload(); }} else {{ alert(result.message); }}
                    }} catch (e) {{ alert('上传失败: ' + e.message); }}
                }};
            }}
            // 自动颜色化
            const cells = document.querySelectorAll('.style-table td');
            cells.forEach(cell => {{
                const text = cell.textContent.trim();
                const cleanText = text.replace(/[%,亿万手]/g, '');
                const val = parseFloat(cleanText);

                if (!isNaN(val)) {{
                    if (text.includes('%') || text.includes('涨跌')) {{
                        if (text.includes('-')) {{
                            cell.classList.add('negative');
                        }} else if (val > 0) {{
                            cell.classList.add('positive');
                        }}
                    }} else if (text.startsWith('-')) {{
                        cell.classList.add('negative');
                    }} else if (text.startsWith('+')) {{
                        cell.classList.add('positive');
                    }}
                }}
            }});

            // 歌词轮播
            const lyrics = [
                '总要有一首我的歌, 大声唱过, 再看天地辽阔 ————《一颗苹果》',
                '苍狗又白云, 身旁有了你, 匆匆轮回又有何惧 ————《如果我们不曾相遇》',
                '活着其实很好, 再吃一颗苹果 ————《一颗苹果》',
                '偶然与巧合, 舞动了蝶翼, 谁的心头风起 ————《如果我们不曾相遇》'
            ];
            let currentLyricIndex = 0;
            const lyricsElement = document.getElementById('lyricsDisplay');

            // 随机选择初始歌词
            currentLyricIndex = Math.floor(Math.random() * lyrics.length);
            if (lyricsElement) {{
                lyricsElement.textContent = lyrics[currentLyricIndex];

                // 每10秒切换一次歌词
                setInterval(function() {{
                    // 淡出
                    lyricsElement.style.opacity = '0';

                    setTimeout(function() {{
                        // 切换歌词
                        currentLyricIndex = (currentLyricIndex + 1) % lyrics.length;
                        lyricsElement.textContent = lyrics[currentLyricIndex];

                        // 淡入
                        lyricsElement.style.opacity = '1';
                    }}, 500);
                }}, 10000);
            }}

            // 初始化基金估值趋势图
            initFundChartSelector();
            initFundChart();
        }});

        // 持仓页：表格更新前先拉取份额数据，保证「持有基金」与持仓统计能正确显示
        async function ensureFundDataLoaded() {{
            if (window.fundSharesData !== undefined) return;
            try {{
                const r = await fetch('/api/fund/data');
                if (!r.ok) return;
                const fundData = await r.json();
                window.fundSharesData = {{}};
                window.fundHoldingData = {{}};
                window.fundSectorsData = {{}};
                for (const [code, data] of Object.entries(fundData)) {{
                    if (data.shares != null) window.fundSharesData[code] = parseFloat(data.shares) || 0;
                    if (data.holding_units != null && data.cost_per_unit != null) window.fundHoldingData[code] = {{ holding_units: parseFloat(data.holding_units) || 0, cost_per_unit: parseFloat(data.cost_per_unit) || 1 }};
                    else if (window.fundSharesData[code] != null) window.fundHoldingData[code] = {{ holding_units: window.fundSharesData[code], cost_per_unit: 1 }};
                    if (data.sectors && data.sectors.length) window.fundSectorsData[code] = data.sectors;
                }}
            }} catch (e) {{}}
        }}

        // 基金估值趋势数据和选择器
        let fundChartData = {fund_chart_data_json};
        let fundChartInfo = {fund_chart_info_json};

        // 基金图表选择器相关变量
        let fundChartSelectorFunds = [];
        let selectedFundCode = null;

        function initFundChartSelector() {{
            const selector = document.getElementById('fundSelector');
            const clearBtn = document.getElementById('fundSelectorClear');
            const wrapper = document.getElementById('fundSelectorWrapper');

            if (!selector || !fundChartInfo || Object.keys(fundChartInfo).length === 0) {{
                const container = document.getElementById('fundChartContainer');
                if (container) {{
                    container.style.display = 'none';
                }}
                return;
            }}

            // 转换基金信息为数组
            fundChartSelectorFunds = Object.entries(fundChartInfo).map(([code, info]) => ({{
                code: code,
                name: info.name,
                is_default: info.is_default || false
            }}));

            // 设置默认值
            const defaultFund = fundChartSelectorFunds.find(f => f.is_default);
            if (defaultFund) {{
                selector.value = `${{defaultFund.code}} - ${{defaultFund.name}}`;
                selectedFundCode = defaultFund.code;
            }}

            // 点击输入框打开模态框
            const openModal = () => {{
                renderFundChartSelectorList(fundChartSelectorFunds);
                document.getElementById('fundChartSelectorModal').classList.add('active');
                setTimeout(() => {{
                    const searchInput = document.getElementById('fundChartSelectorSearch');
                    if (searchInput) searchInput.focus();
                }}, 100);
            }};

            selector.addEventListener('click', openModal);

            // 清空按钮
            if (clearBtn && wrapper) {{
                const updateClearButtonVisibility = () => {{
                    if (selector.value.trim()) {{
                        wrapper.classList.add('has-value');
                    }} else {{
                        wrapper.classList.remove('has-value');
                    }}
                }};

                clearBtn.addEventListener('click', function(e) {{
                    e.preventDefault();
                    e.stopPropagation();
                    selector.value = '';
                    selectedFundCode = null;
                    updateClearButtonVisibility();
                }});

                updateClearButtonVisibility();
            }}
        }}

        // 渲染基金选择列表
        function renderFundChartSelectorList(funds) {{
            const listContainer = document.getElementById('fundChartSelectorList');
            if (!listContainer) return;

            if (funds.length === 0) {{
                listContainer.innerHTML = '<div style="text-align: center; padding: 40px; color: var(--text-dim);">未找到匹配的基金</div>';
                return;
            }}

            listContainer.innerHTML = funds.map(fund => `
                <div class="fund-chart-selector-item ${{fund.is_default ? 'is-default' : ''}}"
                     onclick="selectFundForChart('${{fund.code}}')">
                    <div class="fund-code">${{fund.code}}</div>
                    <div class="fund-name">${{fund.name}}</div>
                    ${{fund.is_default ? '<span style="color: #3b82f6; font-size: var(--font-size-sm);">⭐ 默认</span>' : ''}}
                </div>
            `).join('');
        }}

        // 选择基金并更新图表
        function selectFundForChart(fundCode) {{
            const fund = fundChartSelectorFunds.find(f => f.code === fundCode);
            if (!fund) return;

            const selector = document.getElementById('fundSelector');
            selector.value = `${{fund.code}} - ${{fund.name}}`;
            selectedFundCode = fund.code;

            const wrapper = document.getElementById('fundSelectorWrapper');
            if (wrapper) wrapper.classList.add('has-value');

            closeFundChartSelectorModal();
            loadFundChartData(fundCode);
        }}

        // 关闭模态框
        function closeFundChartSelectorModal() {{
            const modal = document.getElementById('fundChartSelectorModal');
            if (modal) modal.classList.remove('active');

            const searchInput = document.getElementById('fundChartSelectorSearch');
            if (searchInput) searchInput.value = '';
        }}

        // 搜索功能和模态框事件
        document.addEventListener('DOMContentLoaded', function() {{
            // 搜索过滤
            const searchInput = document.getElementById('fundChartSelectorSearch');
            if (searchInput) {{
                searchInput.addEventListener('input', function() {{
                    const keyword = this.value.toLowerCase().trim();
                    if (!keyword) {{
                        renderFundChartSelectorList(fundChartSelectorFunds);
                        return;
                    }}
                    const filtered = fundChartSelectorFunds.filter(fund =>
                        fund.code.includes(keyword) ||
                        fund.name.toLowerCase().includes(keyword)
                    );
                    renderFundChartSelectorList(filtered);
                }});
            }}

            // 点击背景关闭
            const modal = document.getElementById('fundChartSelectorModal');
            if (modal) {{
                modal.addEventListener('click', function(e) {{
                    if (e.target === modal) {{
                        closeFundChartSelectorModal();
                    }}
                }});
            }}
        }});

        function initFundChart() {{
            if (!fundChartData.labels || fundChartData.labels.length === 0) {{
                return;
            }}

            const ctx = document.getElementById('fundChart');
            if (!ctx) return;

            const growthData = fundChartData.growth || [];
            const netValues = fundChartData.net_values || [];
            const lastGrowth = growthData.length > 0 ? growthData[growthData.length - 1] : 0;
            const lastNetValue = netValues.length > 0 ? netValues[netValues.length - 1] : 0;

            // 更新标题
            const titleEl = document.getElementById('fundChartTitle');
            if (titleEl) {{
                const color = lastGrowth > 0 ? '#f44336' : (lastGrowth < 0 ? '#4caf50' : '#9ca3af');
                titleEl.innerHTML = `📈 基金估值`;
            }}

            window.fundChartInstance = new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: fundChartData.labels,
                    datasets: [{{
                        label: '涨幅 (%)',
                        data: growthData,
                        borderColor: function(context) {{
                            const index = context.dataIndex;
                            if (index === undefined || index < 0) return '#9ca3af';
                            const pct = growthData[index];
                            return pct > 0 ? '#f44336' : (pct < 0 ? '#4caf50' : '#9ca3af');
                        }},
                        segment: {{
                            borderColor: function(context) {{
                                const pct = growthData[context.p1DataIndex];
                                return pct > 0 ? '#f44336' : (pct < 0 ? '#4caf50' : '#9ca3af');
                            }}
                        }},
                        backgroundColor: function(context) {{
                            const chart = context.chart;
                            const {{ctx, chartArea}} = chart;
                            if (!chartArea) return null;
                            const lastPct = growthData[growthData.length - 1];
                            const color = lastPct >= 0 ? '244, 67, 54' : '76, 175, 80';
                            const gradient = ctx.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
                            gradient.addColorStop(0, 'rgba(' + color + ', 0.2)');
                            gradient.addColorStop(1, 'rgba(' + color + ', 0.0)');
                            return gradient;
                        }},
                        fill: true,
                        tension: 0.4,
                        pointRadius: 0,
                        pointHoverRadius: 4,
                        borderWidth: 2
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {{
                        mode: 'index',
                        intersect: false,
                    }},
                    plugins: {{
                        legend: {{
                            display: true,
                            position: 'top',
                            labels: {{
                                font: {{ size: 11 }},
                                boxWidth: 12,
                                generateLabels: function(chart) {{
                                    const lastPct = growthData[growthData.length - 1];
                                    const color = lastPct >= 0 ? '#ff4d4f' : '#52c41a';
                                    return [{{
                                        text: '涨幅: ' + (lastPct >= 0 ? '+' : '-') + Math.abs(lastPct).toFixed(2) + '% | 净值: ' + lastNetValue.toFixed(4),
                                        fillStyle: color,
                                        strokeStyle: color,
                                        fontColor: color,
                                        lineWidth: 2,
                                        hidden: false,
                                        index: 0
                                    }}];
                                }}
                            }}
                        }},
                        tooltip: {{
                            callbacks: {{
                                title: function(context) {{
                                    return '时间: ' + context[0].label;
                                }},
                                label: function(context) {{
                                    const index = context.dataIndex;
                                    const growth = growthData[index];
                                    const netValue = netValues[index];
                                    const color = growth > 0 ? '#f44336' : (growth < 0 ? '#4caf50' : '#9ca3af');
                                    return [
                                        '涨幅: ' + (growth >= 0 ? '+' : '-') + Math.abs(growth).toFixed(2) + '%',
                                        '净值: ' + netValue.toFixed(4)
                                    ];
                                }}
                            }}
                        }}
                    }},
                    scales: {{
                        x: {{
                            ticks: {{
                                color: '#9ca3af',
                                font: {{ size: 10 }},
                                maxTicksLimit: 6
                            }},
                            grid: {{
                                color: 'rgba(255, 255, 255, 0.1)'
                            }}
                        }},
                        y: {{
                            title: {{
                                display: true,
                                text: '涨幅 (%)',
                                color: '#9ca3af',
                                font: {{ size: 11 }}
                            }},
                            ticks: {{
                                color: '#9ca3af',
                                callback: function(value) {{
                                    return (value >= 0 ? '+' : '-') + Math.abs(value).toFixed(2) + '%';
                                }}
                            }},
                            grid: {{
                                color: 'rgba(255, 255, 255, 0.1)'
                            }}
                        }}
                    }}
                }}
            }});
        }}

        async function loadFundChartData(fundCode) {{
            try {{
                const response = await fetch('/api/fund/chart-data?code=' + fundCode);
                const data = await response.json();

                // 更新全局数据
                fundChartData = data.chart_data;

                // 重新渲染图表
                const canvas = document.getElementById('fundChart');
                if (window.fundChartInstance) {{
                    window.fundChartInstance.destroy();
                }}
                initFundChart();

                // 保存用户偏好
                await fetch('/api/fund/chart-default', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ fund_code: fundCode }})
                }});
            }} catch (error) {{
                console.error('Failed to load fund chart data:', error);
            }}
        }}

        // 持仓 tab 切换与分页（每页 10 条，每个 tab 独立页码）
        const PORTFOLIO_PAGE_SIZE = 10;
        let portfolioCurrentTab = '';
        let portfolioPageByTab = {{}};
        let portfolioRowCountByTab = {{}};

        function portfolioGetVisibleRows() {{
            if (!portfolioCurrentTab || !portfolioCurrentTab.startsWith('group-')) return [];
            const tbody = document.querySelector('#portfolioTableWrap .table-container tbody');
            if (!tbody) return [];
            return Array.from(tbody.querySelectorAll('tr')).filter(tr => tr.getAttribute('data-code'));
        }}

        function portfolioRender() {{
            const rows = portfolioGetVisibleRows();
            const tab = portfolioCurrentTab;
            const total = (tab && portfolioRowCountByTab[tab] !== undefined) ? portfolioRowCountByTab[tab] : rows.length;
            const totalPages = Math.max(1, Math.ceil(total / PORTFOLIO_PAGE_SIZE));
            let page = (tab && portfolioPageByTab[tab]) ? portfolioPageByTab[tab] : 1;
            page = Math.min(Math.max(1, page), totalPages);
            if (tab) portfolioPageByTab[tab] = page;
            const start = (page - 1) * PORTFOLIO_PAGE_SIZE;
            const end = start + PORTFOLIO_PAGE_SIZE;
            rows.forEach((tr, i) => {{
                tr.style.display = (i >= start && i < end) ? '' : 'none';
            }});
            const paginationEl = document.getElementById('portfolioPagination');
            if (paginationEl) {{
                let html = '<span style="color:var(--text-dim);">共 ' + total + ' 条</span>';
                html += ' <button type="button" class="btn btn-secondary" onclick="portfolioSetPage(' + (page - 1) + ')" ' + (page <= 1 ? 'disabled' : '') + '>上一页</button>';
                html += ' <span style="min-width:80px;text-align:center;">第 ' + page + ' / ' + totalPages + ' 页</span>';
                html += ' <button type="button" class="btn btn-secondary" onclick="portfolioSetPage(' + (page + 1) + ')" ' + (page >= totalPages ? 'disabled' : '') + '>下一页</button>';
                paginationEl.innerHTML = html;
            }}
        }}

        function portfolioSetPage(p) {{
            if (!portfolioCurrentTab) return;
            portfolioPageByTab[portfolioCurrentTab] = p;
            portfolioRender();
        }}

        function portfolioSetTab(tab) {{
            portfolioCurrentTab = tab;
            const wrap = document.getElementById('portfolioTableWrap');
            if (wrap) wrap.setAttribute('data-current-tab', tab || '');
            document.querySelectorAll('#portfolioTabs .portfolio-tab').forEach(btn => {{
                btn.classList.toggle('active', btn.getAttribute('data-tab') === tab);
            }});
            const groupActionsWrap = document.getElementById('portfolioGroupActionsWrap');
            const tabBtnEl = document.querySelector('#portfolioTabs .portfolio-tab[data-tab="' + tab + '"]');
            const isDefaultTab = tabBtnEl && tabBtnEl.getAttribute('data-default') === '1';
            const opCols = document.querySelectorAll('#portfolioTableWrap .portfolio-op-col');
            const posCols = document.querySelectorAll('#portfolioTableWrap .portfolio-position-col');
            opCols.forEach(el => {{ el.style.display = isDefaultTab ? 'none' : ''; }});
            posCols.forEach(el => {{ el.style.display = isDefaultTab ? '' : 'none'; }});
            if (tab.startsWith('group-')) {{
                if (groupActionsWrap) groupActionsWrap.style.display = isDefaultTab ? 'none' : 'block';
                const delBtn = document.getElementById('portfolioDeleteGroupBtn');
                if (delBtn && !isDefaultTab) {{
                    delBtn.onclick = function() {{
                        if (!confirm('确定要删除该分组吗？')) return;
                        const gid = tab.replace('group-', '');
                        fetch('/api/fund/groups/' + gid, {{ method: 'DELETE' }}).then(r => r.json()).then(data => {{
                            if (data.success) location.reload(); else alert(data.message || '删除失败');
                        }}).catch(e => alert('删除失败: ' + e.message));
                    }};
                }}
            }} else {{
                if (groupActionsWrap) groupActionsWrap.style.display = 'none';
            }}
            const portfolioTbody = function() {{ return document.querySelector('#portfolioTableWrap .table-container tbody'); }};
            const tbody = portfolioTbody();
            if (tab && tab.startsWith('group-')) {{
                const gid = tab.replace('group-', '');
                const requestedTab = tab;
                if (tbody) tbody.innerHTML = '<tr><td colspan="10" style="text-align:center;color:var(--text-dim);padding:24px;">加载中...</td></tr>';
                fetch('/api/portfolio/table?group=' + encodeURIComponent(gid), {{ cache: 'no-store' }}).then(r => r.json()).then(async function(resp) {{
                    if (portfolioCurrentTab !== requestedTab) return;
                    await ensureFundDataLoaded();
                    const t = portfolioTbody();
                    if (t) {{
                        if (resp.success && resp.html !== undefined && resp.html !== null) {{
                            t.innerHTML = resp.html;
                            if (typeof resp.total === 'number') portfolioRowCountByTab[requestedTab] = resp.total;
                        }} else {{
                            t.innerHTML = '<tr><td colspan="10" style="text-align:center;color:var(--text-dim);padding:24px;">加载失败</td></tr>';
                            portfolioRowCountByTab[requestedTab] = 0;
                        }}
                    }}
                    requestAnimationFrame(function() {{ portfolioRender(); if (window.calculatePositionSummary) window.calculatePositionSummary(); }});
                }}).catch(async function() {{
                    if (portfolioCurrentTab !== requestedTab) return;
                    await ensureFundDataLoaded();
                    const t = portfolioTbody();
                    if (t) t.innerHTML = '<tr><td colspan="10" style="text-align:center;color:var(--text-dim);padding:24px;">加载失败</td></tr>';
                    portfolioRowCountByTab[requestedTab] = 0;
                    requestAnimationFrame(function() {{ portfolioRender(); if (window.calculatePositionSummary) window.calculatePositionSummary(); }});
                }});
            }} else {{
                portfolioRender();
            }}
        }}

        async function portfolioRemoveFundFromGroup(code) {{
            const tab = portfolioCurrentTab;
            if (!tab || !tab.startsWith('group-')) {{ alert('请先切换到分组'); return; }}
            if (!confirm('确定从该分组中移除该基金吗？')) return;
            const gid = tab.replace('group-', '');
            try {{
                const res = await fetch('/api/fund/groups/' + gid + '/funds/' + encodeURIComponent(code), {{ method: 'DELETE' }});
                const data = await res.json();
                if (data.success) {{
                    fetch('/api/portfolio/table?group=' + encodeURIComponent(gid), {{ cache: 'no-store' }}).then(r => r.json()).then(async function(resp) {{
                        await ensureFundDataLoaded();
                        const t = document.querySelector('#portfolioTableWrap .table-container tbody');
                        if (t && resp.success && resp.html != null) {{
                            t.innerHTML = resp.html;
                            if (typeof resp.total === 'number') portfolioRowCountByTab[portfolioCurrentTab] = resp.total;
                        }}
                        requestAnimationFrame(function() {{ portfolioRender(); if (window.calculatePositionSummary) window.calculatePositionSummary(); }});
                    }}).catch(async function() {{ await ensureFundDataLoaded(); requestAnimationFrame(function() {{ portfolioRender(); if (window.calculatePositionSummary) window.calculatePositionSummary(); }}); }});
                }} else alert(data.message || '移除失败');
            }} catch (e) {{ alert('移除失败: ' + e.message); }}
        }}

        window.portfolioRemoveFundFromGroup = portfolioRemoveFundFromGroup;

        let portfolioFundSuggestList = [];
        const portfolioSuggestMax = 12;

        function portfolioFetchFundList(cb) {{
            if (portfolioFundSuggestList.length > 0) {{ if (cb) cb(); return; }}
            fetch('/api/portfolio/fund-list', {{ cache: 'no-store' }}).then(r => r.json()).then(function(resp) {{
                if (resp.success && Array.isArray(resp.funds)) portfolioFundSuggestList = resp.funds;
                if (cb) cb();
            }}).catch(function() {{ if (cb) cb(); }});
        }}

        function portfolioShowSuggest(input, word) {{
            const listEl = document.getElementById('portfolioFundSuggestList');
            if (!listEl) return;
            word = (word || '').trim().toLowerCase();
            const filtered = word ? portfolioFundSuggestList.filter(function(f) {{
                return (f.code && f.code.indexOf(word) !== -1) || (f.name && f.name.toLowerCase().indexOf(word) !== -1);
            }}) : portfolioFundSuggestList.slice(0, portfolioSuggestMax);
            listEl.innerHTML = '';
            if (filtered.length === 0) {{ listEl.style.display = 'none'; return; }}
            filtered.slice(0, portfolioSuggestMax).forEach(function(f) {{
                const div = document.createElement('div');
                div.setAttribute('data-code', f.code);
                div.style.cssText = 'padding: 8px 12px; cursor: pointer; font-size: var(--font-size-base); color: var(--text-main); border-bottom: 1px solid var(--border);';
                div.textContent = f.code + '  ' + (f.name || '');
                div.addEventListener('mouseenter', function() {{ this.style.background = 'var(--hover-bg, rgba(59,130,246,0.1))'; }});
                div.addEventListener('mouseleave', function() {{ this.style.background = ''; }});
                div.addEventListener('mousedown', function(e) {{ e.preventDefault(); portfolioSelectSuggest(f.code); }});
                listEl.appendChild(div);
            }});
            listEl.style.display = 'block';
        }}

        function portfolioSelectSuggest(code) {{
            const input = document.getElementById('fundCodesInput');
            if (!input) return;
            const val = input.value;
            const comma = /[,，\\s]+/;
            const parts = val.split(comma).map(function(s) {{ return s.trim(); }});
            const lastPart = parts[parts.length - 1] || '';
            const beforeLast = val.substring(0, val.length - lastPart.length).replace(/[,，\\s]*$/, '');
            const newVal = beforeLast ? (beforeLast + (beforeLast ? ',' : '') + code) : code;
            input.value = newVal;
            document.getElementById('portfolioFundSuggestList').style.display = 'none';
            input.focus();
        }}

        function portfolioBindFundSuggest() {{
            const input = document.getElementById('fundCodesInput');
            const listEl = document.getElementById('portfolioFundSuggestList');
            if (!input || !listEl) return;
            input.addEventListener('focus', function() {{
                portfolioFetchFundList(function() {{
                    const val = input.value;
                    const parts = val.split(/[,，\\s]+/).map(function(s) {{ return s.trim(); }});
                    portfolioShowSuggest(input, parts[parts.length - 1] || '');
                }});
            }});
            input.addEventListener('input', function() {{
                const val = input.value;
                const parts = val.split(/[,，\\s]+/).map(function(s) {{ return s.trim(); }});
                portfolioShowSuggest(input, parts[parts.length - 1] || '');
            }});
            input.addEventListener('keydown', function(e) {{
                if (e.key === 'Escape') {{ listEl.style.display = 'none'; }}
            }});
            listEl.addEventListener('mousedown', function(e) {{ e.preventDefault(); }});
            document.addEventListener('click', function(e) {{
                if (input.contains(e.target) || listEl.contains(e.target)) return;
                listEl.style.display = 'none';
            }});
        }}

        async function portfolioAddByInput() {{
            const input = document.getElementById('fundCodesInput');
            if (!input) return;
            const codes = input.value.trim();
            if (!codes) {{ alert('请输入基金代码'); return; }}
            const tab = portfolioCurrentTab;
            if (tab && tab.startsWith('group-')) {{
                const gid = tab.replace('group-', '');
                const codeList = codes.split(/[,，\\s]+/).map(s => s.trim()).filter(Boolean);
                if (!codeList.length) {{ alert('请输入基金代码'); return; }}
                let anySuccess = false;
                for (const code of codeList) {{
                    try {{
                        const res = await fetch('/api/fund/groups/' + gid + '/funds', {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/json' }},
                            body: JSON.stringify({{ code: code }})
                        }});
                        const data = await res.json();
                        if (data.success) anySuccess = true;
                        else alert(code + ': ' + (data.message || '添加失败'));
                    }} catch (e) {{ alert(code + ' 添加失败: ' + e.message); }}
                }}
                input.value = '';
                if (anySuccess) {{
                    fetch('/api/portfolio/table?group=' + encodeURIComponent(gid), {{ cache: 'no-store' }}).then(r => r.json()).then(async function(resp) {{
                        await ensureFundDataLoaded();
                        const t = document.querySelector('#portfolioTableWrap .table-container tbody');
                        if (t && resp.success && resp.html != null) {{
                            t.innerHTML = resp.html;
                            if (typeof resp.total === 'number') portfolioRowCountByTab[portfolioCurrentTab] = resp.total;
                        }}
                        requestAnimationFrame(function() {{ portfolioRender(); if (window.calculatePositionSummary) window.calculatePositionSummary(); }});
                    }}).catch(async function() {{ await ensureFundDataLoaded(); requestAnimationFrame(function() {{ portfolioRender(); if (window.calculatePositionSummary) window.calculatePositionSummary(); }}); }});
                }}
                return;
            }}
        }}

        function openNewGroupModal() {{
            document.getElementById('newGroupName').value = '';
            document.getElementById('newGroupModal').classList.add('active');
        }}

        function closeNewGroupModal() {{
            document.getElementById('newGroupModal').classList.remove('active');
        }}

        async function submitNewGroup() {{
            const name = (document.getElementById('newGroupName').value || '').trim();
            if (!name) {{ alert('请输入分组名称'); return; }}
            try {{
                const res = await fetch('/api/fund/groups', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ name: name }})
                }});
                const data = await res.json();
                if (data.success && data.group_id) {{
                    closeNewGroupModal();
                    location.reload();
                }} else {{
                    alert(data.message || '创建失败');
                }}
            }} catch (e) {{
                alert('创建失败: ' + e.message);
            }}
        }}

        function portfolioSyncUrlFromTab(tab) {{
            const gid = tab ? tab.replace('group-', '') : '';
            const url = gid ? '/portfolio?group=' + encodeURIComponent(gid) : '/portfolio';
            if (location.search !== (gid ? '?group=' + encodeURIComponent(gid) : '')) {{
                history.replaceState({{ tab: tab }}, '', url);
            }}
        }}

        document.addEventListener('DOMContentLoaded', function() {{
            const tabsEl = document.getElementById('portfolioTabs');
            if (tabsEl) {{
                const params = new URLSearchParams(location.search);
                const groupParam = params.get('group');
                let tabToShow = '';
                if (groupParam !== null && groupParam !== '') {{
                    const btn = document.querySelector('#portfolioTabs .portfolio-tab[data-tab="group-' + groupParam + '"]');
                    if (btn) tabToShow = 'group-' + groupParam;
                }}
                if (!tabToShow) {{
                    const activeTab = document.querySelector('#portfolioTabs .portfolio-tab.active');
                    tabToShow = activeTab ? activeTab.getAttribute('data-tab') || '' : '';
                }}
                if (tabToShow) {{
                    portfolioCurrentTab = tabToShow;
                    document.querySelectorAll('#portfolioTabs .portfolio-tab').forEach(btn => {{
                        btn.classList.toggle('active', btn.getAttribute('data-tab') === tabToShow);
                    }});
                    portfolioSetTab(tabToShow);
                    portfolioSyncUrlFromTab(tabToShow);
                }}
                tabsEl.addEventListener('click', function(e) {{
                    const tabBtn = e.target.closest('.portfolio-tab');
                    if (!tabBtn) return;
                    if (tabBtn.classList.contains('portfolio-tab-new')) {{
                        openNewGroupModal();
                        return;
                    }}
                    const tab = tabBtn.getAttribute('data-tab');
                    if (tab) {{
                        portfolioSetTab(tab);
                        portfolioSyncUrlFromTab(tab);
                    }}
                }});
            }}
            const addByInputBtn = document.getElementById('portfolioAddByInputBtn');
            if (addByInputBtn) addByInputBtn.addEventListener('click', portfolioAddByInput);
            portfolioBindFundSuggest();
            const fundTable = document.getElementById('portfolioFundTable');
            if (fundTable) fundTable.addEventListener('click', function(e) {{
                const btnRemove = e.target.closest('.btn-remove-from-group');
                if (btnRemove) {{ e.preventDefault(); portfolioRemoveFundFromGroup(btnRemove.getAttribute('data-code')); }}
            }});
            const btnNew2 = document.getElementById('portfolioBtnNewGroup');
            if (btnNew2) btnNew2.addEventListener('click', openNewGroupModal);
            window.addEventListener('popstate', function(e) {{
                const params = new URLSearchParams(location.search);
                const groupParam = params.get('group');
                let tabToShow = '';
                if (groupParam !== null && groupParam !== '') {{
                    const btn = document.querySelector('#portfolioTabs .portfolio-tab[data-tab="group-' + groupParam + '"]');
                    if (btn) tabToShow = 'group-' + groupParam;
                }}
                if (!tabToShow) {{
                    const firstTab = document.querySelector('#portfolioTabs .portfolio-tab:not(.portfolio-tab-new)');
                    tabToShow = firstTab ? firstTab.getAttribute('data-tab') || '' : '';
                }}
                if (tabToShow && tabToShow !== portfolioCurrentTab) {{
                    portfolioCurrentTab = tabToShow;
                    document.querySelectorAll('#portfolioTabs .portfolio-tab').forEach(btn => {{
                        btn.classList.toggle('active', btn.getAttribute('data-tab') === tabToShow);
                    }});
                    portfolioSetTab(tabToShow);
                }}
            }});
        }});
    </script>
</body>
</html>'''.format(css_style=css_style, username_display=username_display, fund_content=fund_content, fund_chart_data_json=fund_chart_data_json, fund_chart_info_json=fund_chart_info_json, sidebar_menu_html=sidebar_menu_html)
    return html


def get_fund_group_page_html(group_id, group, fund_map, username=None, is_admin=False):
    """分组编辑页：可修改分组名称、添加/移除基金。group: {id, name, fund_codes}"""
    css_style = get_css_style()
    sidebar_menu_html = get_sidebar_menu_items_html('portfolio', is_admin)

    username_display = ''
    if username:
        username_display += '<span class="nav-user">🍎 {username}</span>'.format(username=username)
        username_display += '<a href="/logout" class="nav-logout">退出登录</a>'

    group_name = (group or {}).get('name') or '未命名'
    fund_codes = (group or {}).get('fund_codes') or []

    # 分组内基金行 HTML（代码、名称、移除按钮），class="group-fund-row" 用于分页
    fund_rows_html = ''
    for code in fund_codes:
        name = (fund_map.get(code) or {}).get('fund_name') or code
        code_esc = code.replace('\\', '\\\\').replace("'", "\\'").replace('"', '&quot;')
        fund_rows_html += '''
            <tr class="group-fund-row">
                <td style="padding:10px;color:var(--accent);font-weight:500;">{code}</td>
                <td style="padding:10px;color:var(--text-main);">{name}</td>
                <td style="padding:10px;">
                    <button type="button" class="btn btn-secondary group-remove-fund" data-code="{code}" onclick="removeFundFromGroup(\'{code_esc}\');return false;" style="padding:4px 10px;font-size:0.85rem;">移除</button>
                </td>
            </tr>
        '''.format(code=code, name=name.replace('<', '&lt;').replace('>', '&gt;'), code_esc=code_esc)

    if not fund_rows_html:
        fund_rows_html = '<tr><td colspan="3" style="padding:20px;color:var(--text-dim);text-align:center;">暂无基金，点击「添加基金」加入</td></tr>'

    html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>编辑分组 - LanFund</title>
    <link rel="icon" href="/static/1.ico">
    {css_style}
    <link rel="stylesheet" href="/static/css/style.css">
    <style>
        body {{ background-color: var(--terminal-bg); color: var(--text-main); min-height: 100vh; display: flex; flex-direction: column; }}
        .top-navbar {{ background-color: var(--card-bg); padding: 0.8rem 2rem; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); }}
        .top-navbar-brand {{ display: flex; align-items: center; }} .top-navbar-quote {{ flex: 1; text-align: center; font-size: 1rem; }} .top-navbar-menu {{ display: flex; gap: 1rem; align-items: center; }}
        .nav-user {{ color: #3b82f6; }} .nav-logout {{ color: #f85149; text-decoration: none; }}
        .main-container {{ display: flex; flex: 1; }}
        .content-area {{ flex: 1; padding: 30px; overflow-y: auto; }}
        .group-page-header {{ margin-bottom: 24px; display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }}
        .group-name-input {{ padding: 8px 12px; border: 1px solid var(--border); border-radius: 8px; background: var(--card-bg); color: var(--text-main); font-size: 1rem; min-width: 200px; }}
        .group-funds-table {{ width: 100%; border-collapse: collapse; background: var(--card-bg); border: 1px solid var(--border); border-radius: 12px; overflow: hidden; }}
        .group-funds-table th {{ padding: 12px; text-align: left; background: rgba(59,130,246,0.1); color: var(--text-dim); font-weight: 500; }}
        .group-funds-table td {{ border-top: 1px solid var(--border); }}
    </style>
</head>
<body>
    <nav class="top-navbar">
        <div class="top-navbar-brand"><img src="/static/1.ico" alt="Logo" class="navbar-logo"></div>
        <div class="top-navbar-quote">编辑分组</div>
        <div class="top-navbar-menu">{username_display}</div>
    </nav>
    <div class="main-container">
        <div class="sidebar" style="width: 220px; border-right: 1px solid var(--border); padding: 16px 0;">
            <div class="sidebar-toggle" id="sidebarToggle">▶</div>
            {sidebar_menu_html}
        </div>
        <div class="content-area">
            <div class="group-page-header">
                <a href="/portfolio" style="color: var(--accent); text-decoration: none;">← 返回持仓基金</a>
                <h1 style="margin: 0; font-size: 1.5rem;">📁 编辑分组</h1>
            </div>
            <div style="margin-bottom: 20px; display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
                <label style="color: var(--text-dim);">分组名称</label>
                <input type="text" id="groupNameInput" class="group-name-input" value="{group_name_esc}" placeholder="输入分组名称">
                <button type="button" class="btn btn-primary" onclick="saveGroupName()">保存名称</button>
                <button type="button" class="btn btn-secondary" onclick="openAddFundModal()">+ 添加基金</button>
                <button type="button" class="btn btn-secondary" style="color: #f85149;" onclick="deleteGroup()">删除分组</button>
            </div>
            <table class="group-funds-table">
                <thead><tr><th>基金代码</th><th>基金名称</th><th>操作</th></tr></thead>
                <tbody id="groupFundsBody">
                    {fund_rows_html}
                </tbody>
            </table>
            <div id="groupPagination" style="margin-top: 16px; display: flex; align-items: center; justify-content: center; gap: 12px; flex-wrap: wrap;"></div>
        </div>
    </div>

    <div class="sector-modal" id="addFundToGroupModal">
        <div class="sector-modal-content" style="max-width: 480px;">
            <div class="sector-modal-header">添加基金到分组</div>
            <input type="text" class="sector-modal-search" id="addFundSearch" placeholder="搜索基金代码或名称...">
            <div id="addFundToList" style="max-height: 360px; overflow-y: auto;"></div>
            <div class="sector-modal-footer">
                <button class="btn btn-secondary" onclick="closeAddFundModal()">取消</button>
            </div>
        </div>
    </div>

    <script>
        const groupId = {group_id};
        const initialFundCodes = {fund_codes_json};
        const GROUP_PAGE_SIZE = 10;
        let groupCurrentPage = 1;

        function groupRenderPagination() {{
            const rows = Array.from(document.querySelectorAll('#groupFundsBody .group-fund-row'));
            const total = rows.length;
            const totalPages = Math.max(1, Math.ceil(total / GROUP_PAGE_SIZE));
            groupCurrentPage = Math.min(Math.max(1, groupCurrentPage), totalPages);
            const start = (groupCurrentPage - 1) * GROUP_PAGE_SIZE;
            const end = start + GROUP_PAGE_SIZE;
            rows.forEach((tr, i) => {{ tr.style.display = (i >= start && i < end) ? '' : 'none'; }});
            const paginationEl = document.getElementById('groupPagination');
            if (paginationEl) {{
                let html = '<span style="color:var(--text-dim);">共 ' + total + ' 条</span>';
                html += ' <button type="button" class="btn btn-secondary" onclick="groupSetPage(' + (groupCurrentPage - 1) + ')" ' + (groupCurrentPage <= 1 ? 'disabled' : '') + '>上一页</button>';
                html += ' <span style="min-width:80px;text-align:center;">第 ' + groupCurrentPage + ' / ' + totalPages + ' 页</span>';
                html += ' <button type="button" class="btn btn-secondary" onclick="groupSetPage(' + (groupCurrentPage + 1) + ')" ' + (groupCurrentPage >= totalPages ? 'disabled' : '') + '>下一页</button>';
                paginationEl.innerHTML = html;
            }}
        }}

        function groupSetPage(p) {{
            groupCurrentPage = p;
            groupRenderPagination();
        }}

        async function saveGroupName() {{
            const name = document.getElementById('groupNameInput').value.trim();
            if (!name) {{ alert('请输入分组名称'); return; }}
            try {{
                const res = await fetch('/api/fund/groups/' + groupId, {{
                    method: 'PUT',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ name: name }})
                }});
                const data = await res.json();
                if (data.success) alert('已保存');
                else alert(data.message || '保存失败');
            }} catch (e) {{ alert('保存失败: ' + e.message); }}
        }}

        async function deleteGroup() {{
            if (!confirm('确定要删除该分组吗？')) return;
            try {{
                const res = await fetch('/api/fund/groups/' + groupId, {{ method: 'DELETE' }});
                const data = await res.json();
                if (data.success) location.href = '/portfolio';
                else alert(data.message || '删除失败');
            }} catch (e) {{ alert('删除失败: ' + e.message); }}
        }}
        window.deleteGroup = deleteGroup;

        async function removeFundFromGroup(code) {{
            if (!code) return;
            if (!confirm('确定从该分组中移除该基金吗？')) return;
            try {{
                const res = await fetch('/api/fund/groups/' + groupId + '/funds/' + encodeURIComponent(code), {{ method: 'DELETE' }});
                const data = await res.json();
                if (data.success) location.reload();
                else alert(data.message || '移除失败');
            }} catch (e) {{ alert('移除失败: ' + e.message); }}
        }}
        window.removeFundFromGroup = removeFundFromGroup;

        document.getElementById('groupFundsBody').addEventListener('click', function(e) {{
            const btn = e.target.closest('.group-remove-fund');
            if (btn) removeFundFromGroup(btn.dataset.code);
        }});

        groupRenderPagination();

        let allFundsForAdd = [];
        function openAddFundModal() {{
            document.getElementById('addFundToGroupModal').classList.add('active');
            fetch('/api/fund/data').then(r => r.json()).then(fundMap => {{
                const currentCodes = Array.from(document.querySelectorAll('.group-remove-fund')).map(b => b.dataset.code);
                allFundsForAdd = Object.entries(fundMap).filter(([code]) => !currentCodes.includes(code)).map(([code, data]) => ({{ code, name: data.fund_name || code }}));
                renderAddFundList(allFundsForAdd);
            }});
        }}

        function closeAddFundModal() {{
            document.getElementById('addFundToGroupModal').classList.remove('active');
        }}

        function renderAddFundList(funds) {{
            const keyword = (document.getElementById('addFundSearch').value || '').toLowerCase();
            const filtered = keyword ? funds.filter(f => f.code.toLowerCase().includes(keyword) || (f.name || '').toLowerCase().includes(keyword)) : funds;
            const html = filtered.length ? filtered.map(f => '<div class="sector-item add-fund-item" style="padding:12px;cursor:pointer;" data-code="' + String(f.code).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;') + '">' + String(f.code).replace(/</g, '&lt;') + ' - ' + String(f.name || '').replace(/</g, '&lt;') + '</div>').join('') : '<div style="padding:16px;color:var(--text-dim);">暂无可添加基金</div>';
            document.getElementById('addFundToList').innerHTML = html;
        }}

        document.getElementById('addFundToList').addEventListener('click', function(e) {{
            const item = e.target.closest('.add-fund-item');
            if (item) addFundToGroup(item.getAttribute('data-code'));
        }});

        document.getElementById('addFundSearch').addEventListener('input', function() {{ renderAddFundList(allFundsForAdd); }});

        async function addFundToGroup(code) {{
            try {{
                const res = await fetch('/api/fund/groups/' + groupId + '/funds', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ code: code }})
                }});
                const data = await res.json();
                if (data.success) {{ closeAddFundModal(); location.reload(); }}
                else alert(data.message || '添加失败');
            }} catch (e) {{ alert('添加失败: ' + e.message); }}
        }}
    </script>
</body>
</html>'''.format(
        css_style=css_style,
        username_display=username_display,
        group_name_esc=group_name.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;'),
        fund_rows_html=fund_rows_html,
        group_id=group_id,
        fund_codes_json=__import__('json').dumps(fund_codes),
        sidebar_menu_html=sidebar_menu_html,
    )
    return html


def get_market_icon(key):
    """获取市场数据的图标"""
    icons = {
        'kx': '📰',
        'marker': '🌍',
        'real_time_gold': '🥇',
        'gold': '📈',
        'seven_A': '📊',
        'A': '📉',
        'bk': '🏢',
        'select_fund': '🔍'
    }
    return icons.get(key, '📊')


def get_position_records_page_html(username=None, is_admin=False):
    """生成持仓记录页面（加减仓记录，删除即撤销）"""
    css_style = get_css_style()
    sidebar_menu_html = get_sidebar_menu_items_html('position-records', is_admin)

    username_display = ''
    if username:
        username_display += '<span class="nav-user">🍎 {username}</span>'.format(username=username)
        username_display += '<a href="/logout" class="nav-logout">退出登录</a>'

    html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>持仓记录 - LanFund</title>
    <link rel="icon" href="/static/1.ico">
    {css_style}
    <link rel="stylesheet" href="/static/css/style.css">
    <style>
        body {{ background-color: var(--terminal-bg); color: var(--text-main); min-height: 100vh; display: flex; flex-direction: column; }}
        /* 顶部导航栏（与其他页面一致） */
        .top-navbar {{ background-color: var(--card-bg); color: var(--text-main); padding: 0.8rem 2rem; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); }}
        .top-navbar-brand {{ display: flex; align-items: center; flex: 0 0 auto; }}
        .top-navbar-quote {{ flex: 1; text-align: center; font-size: 1rem; font-weight: 500; color: var(--text-main); font-style: italic; padding: 0 2rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; letter-spacing: 0.05em; transition: opacity 0.5s ease-in-out; }}
        .navbar-logo {{ width: 32px; height: 32px; }}
        .top-navbar-menu {{ display: flex; gap: 1rem; align-items: center; }}
        .nav-user {{ color: #3b82f6; font-weight: 500; }}
        .nav-logout {{ color: #f85149; text-decoration: none; font-weight: 500; }}
        .main-container {{ display: flex; flex: 1; }}
        .content-area {{ flex: 1; padding: 30px; overflow-y: auto; }}
        .page-header {{ margin-bottom: 24px; }}
        .page-header h1 {{ font-size: 1.5rem; margin: 0 0 8px 0; color: var(--text-main); }}
        .page-header p {{ font-size: 0.9rem; color: var(--text-dim); margin: 0; }}
        .records-table {{ width: 100%; border-collapse: collapse; background: var(--card-bg); border: 1px solid var(--border); border-radius: 12px; overflow: hidden; }}
        .records-table th, .records-table td {{ padding: 12px 16px; text-align: left; border-bottom: 1px solid var(--border); }}
        .records-table th {{ background: rgba(59, 130, 246, 0.1); color: var(--text-dim); font-weight: 500; font-size: var(--font-size-base); }}
        .records-table tr:last-child td {{ border-bottom: none; }}
        .records-table tr:hover td {{ background: rgba(255,255,255,0.02); }}
        .record-op-add {{ color: #22c55e; font-weight: 500; }}
        .record-op-reduce {{ color: #f59e0b; font-weight: 500; }}
        .btn-undo {{ padding: 6px 12px; font-size: var(--font-size-sm); border-radius: 6px; border: 1px solid var(--border); background: var(--card-bg); color: var(--text-main); cursor: pointer; }}
        .btn-undo:hover {{ background: rgba(239, 68, 68, 0.15); color: #ef4444; border-color: #ef4444; }}
        .btn-undo-disabled {{ padding: 6px 12px; font-size: var(--font-size-sm); border-radius: 6px; color: var(--text-dim); cursor: not-allowed; }}
        .records-empty {{ padding: 40px; text-align: center; color: var(--text-dim); }}
        .sidebar {{ width: 200px; flex-shrink: 0; background: var(--card-bg); border-right: 1px solid var(--border); }}
        .sidebar.collapsed {{ width: 60px; }}
        .sidebar-item {{ display: flex; align-items: center; gap: 10px; padding: 12px 16px; color: var(--text-main); text-decoration: none; border-bottom: 1px solid var(--border); }}
        .sidebar-item:hover {{ background: rgba(59, 130, 246, 0.08); }}
        .sidebar-item.active {{ background: rgba(59, 130, 246, 0.15); color: #3b82f6; }}
        .hamburger-menu {{ display: none; }}
        @media (max-width: 768px) {{
            .sidebar {{ position: fixed; left: 0; top: 0; height: 100%; z-index: 1000; }}
            .hamburger-menu {{ display: block; }}
            .top-navbar {{ flex-direction: row; flex-wrap: wrap; height: auto; padding: 0.5rem 1rem; align-items: center; border-bottom: none; }}
            .top-navbar > .top-navbar-brand {{ order: 1; flex: 0 0 auto; padding-bottom: 0.5rem; border-bottom: 1px solid var(--border); }}
            .top-navbar-menu {{ order: 1; flex: 0 0 auto; margin-left: auto; padding-bottom: 0.5rem; border-bottom: 1px solid var(--border); }}
            .top-navbar-quote {{ order: 2; width: 100%; flex-basis: 100%; text-align: center; padding: 0.5rem 0; font-size: 0.8rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; border-top: 1px solid var(--border); margin-top: 0.5rem; }}
        }}
    </style>
</head>
<body>
    <nav class="top-navbar">
        <div class="top-navbar-brand">
            <a href="/portfolio" style="display:flex;align-items:center;color:inherit;text-decoration:none;">
                <img src="/static/1.ico" alt="Logo" class="navbar-logo">
            </a>
        </div>
        <div class="top-navbar-quote" id="lyricsDisplay">偶然与巧合, 舞动了蝶翼, 谁的心头风起 ————《如果我们不曾相遇》</div>
        <div class="top-navbar-menu">{username_display}</div>
    </nav>
    <div class="main-container">
        <button class="hamburger-menu" id="hamburgerMenu"><span></span><span></span><span></span></button>
        <div class="sidebar collapsed" id="sidebar">
            <div class="sidebar-toggle" id="sidebarToggle">▶</div>
            {sidebar_menu_html}
        </div>
        <main class="content-area">
            <div class="page-header">
                <h1>📋 持仓记录</h1>
                <p>每次加仓、减仓会在此记录；删除某条记录将撤销该次操作并恢复当时持仓。当日15:00前操作须在当日15:00前撤销，当日15:00后操作须在次日15:00前撤销；到账规则：当日15:00前操作次日到账(T+1)，当日15:00后操作第三天到账(T+2)。</p>
            </div>
            <div id="positionRecordsContainer">
                <p class="records-empty" id="recordsLoading">加载中…</p>
            </div>
        </main>
    </div>
    <script src="/static/js/sidebar-nav.js"></script>
    <script>
    (function() {{
        function formatDate(ymd) {{
            if (!ymd) return '—';
            var p = ymd.split('-');
            if (p.length === 3) return p[0] + '-' + p[1] + '-' + p[2];
            return ymd;
        }}
        function formatDateTime(iso) {{
            if (!iso) return '—';
            try {{
                var d = new Date(iso);
                return d.getFullYear() + '-' + String(d.getMonth()+1).padStart(2,'0') + '-' + String(d.getDate()).padStart(2,'0') + ' ' + String(d.getHours()).padStart(2,'0') + ':' + String(d.getMinutes()).padStart(2,'0');
            }} catch(e) {{ return iso; }}
        }}
        function loadRecords() {{
            var el = document.getElementById('positionRecordsContainer');
            fetch('/api/fund/position-records')
                .then(function(r) {{ return r.json(); }})
                .then(function(data) {{
                    if (!data.success || !data.records || !data.records.length) {{
                        el.innerHTML = '<p class="records-empty">暂无持仓记录</p>';
                        return;
                    }}
                    var rows = data.records.map(function(rec) {{
                        var opText = rec.op === 'add' ? '加仓' : '减仓';
                        var opClass = rec.op === 'add' ? 'record-op-add' : 'record-op-reduce';
                        var canUndo = rec.hasOwnProperty('can_undo') ? rec.can_undo : true;
                        var actionCell = canUndo
                            ? '<button type="button" class="btn-undo" data-id="' + rec.id + '">撤销</button>'
                            : '<span class="btn-undo-disabled" title="已过撤销截止时间（当日15:00前操作须在当日15:00前撤销，当日15:00后操作须在次日15:00前撤销）">已过截止</span>';
                        // 根据操作类型显示不同格式：减仓显示份额，加仓显示金额
                        var amountCell = '';
                        if (rec.op === 'reduce') {{
                            // 减仓：显示份额 = prev_holding_units - new_holding_units
                            var prevUnits = parseFloat(rec.prev_holding_units) || 0;
                            var newUnits = parseFloat(rec.new_holding_units) || 0;
                            var reduceUnits = Math.max(0, prevUnits - newUnits);
                            amountCell = reduceUnits.toFixed(2) + '份';
                        }} else {{
                            // 加仓：显示金额
                            amountCell = '¥' + (parseFloat(rec.amount) || 0).toLocaleString('zh-CN', {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }});
                        }}
                        return '<tr data-id="' + rec.id + '">' +
                            '<td>' + (rec.fund_code || '—') + '</td>' +
                            '<td>' + (rec.fund_name || '—') + '</td>' +
                            '<td>' + formatDateTime(rec.created_at) + '</td>' +
                            '<td><span class="' + opClass + '">' + opText + '</span></td>' +
                            '<td>' + amountCell + '</td>' +
                            '<td>' + actionCell + '</td>' +
                            '</tr>';
                    }}).join('');
                    el.innerHTML = '<table class="records-table"><thead><tr><th>基金编号</th><th>基金名称</th><th>操作时间</th><th>操作方式</th><th>加减仓</th><th>操作</th></tr></thead><tbody>' + rows + '</tbody></table>';
                    el.querySelectorAll('.btn-undo').forEach(function(btn) {{
                        btn.addEventListener('click', function() {{
                            var id = btn.getAttribute('data-id');
                            if (!id || !confirm('确定撤销该次操作？将恢复该次操作前的持仓。')) return;
                            fetch('/api/fund/position-records/' + id, {{ method: 'DELETE' }})
                                .then(function(r) {{ return r.json(); }})
                                .then(function(res) {{
                                    if (res.success) {{
                                        alert(res.message || '已撤销');
                                        loadRecords();
                                    }} else {{
                                        alert(res.message || '撤销失败');
                                    }}
                                }})
                                .catch(function(e) {{ alert('请求失败: ' + (e.message || e)); }});
                        }});
                    }});
                }})
                .catch(function(e) {{
                    el.innerHTML = '<p class="records-empty">加载失败: ' + (e.message || e) + '</p>';
                }});
        }}
        loadRecords();
        // 顶部导航栏歌词轮播（与其他页面一致）
        var lyrics = [
            '总要有一首我的歌, 大声唱过, 再看天地辽阔 ————《一颗苹果》',
            '苍狗又白云, 身旁有了你, 匆匆轮回又有何惧 ————《如果我们不曾相遇》',
            '活着其实很好, 再吃一颗苹果 ————《一颗苹果》',
            '偶然与巧合, 舞动了蝶翼, 谁的心头风起 ————《如果我们不曾相遇》'
        ];
        var currentLyricIndex = Math.floor(Math.random() * lyrics.length);
        var lyricsEl = document.getElementById('lyricsDisplay');
        if (lyricsEl) {{
            lyricsEl.textContent = lyrics[currentLyricIndex];
            setInterval(function() {{
                lyricsEl.style.opacity = '0';
                setTimeout(function() {{
                    currentLyricIndex = (currentLyricIndex + 1) % lyrics.length;
                    lyricsEl.textContent = lyrics[currentLyricIndex];
                    lyricsEl.style.opacity = '1';
                }}, 500);
            }}, 10000);
        }}
    }})();
    </script>
</body>
</html>'''
    return html.format(css_style=css_style, username_display=username_display, sidebar_menu_html=sidebar_menu_html)


def get_sectors_page_html(sectors_content, select_fund_content, fund_map, username=None, is_admin=False):
    """生成行业板块基金查询页面"""
    css_style = get_css_style()
    sidebar_menu_html = get_sidebar_menu_items_html('sectors', is_admin)

    username_display = ''
    if username:
        username_display += '<span class="nav-user">🍎 {username}</span>'.format(username=username)
        username_display += '<a href="/logout" class="nav-logout">退出登录</a>'

    html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>行业板块 - LanFund</title>
    <link rel="icon" href="/static/1.ico">
    {css_style}
    <link rel="stylesheet" href="/static/css/style.css">
    <style>
        body {{
            background-color: var(--terminal-bg);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }}

        /* 顶部导航栏 */
        .top-navbar {{
            background-color: var(--card-bg);
            color: var(--text-main);
            padding: 0.8rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border);
        }}

        .top-navbar-brand {{
            display: flex;
            align-items: center;
            flex: 0 0 auto;
        }}

        .top-navbar-quote {{
            flex: 1;
            text-align: center;
            font-size: 1rem;
            font-weight: 500;
            color: var(--text-main);
            font-style: italic;
            padding: 0 2rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            letter-spacing: 0.05em;
            transition: opacity 0.5s ease-in-out;
        }}

        .top-navbar-menu {{
            display: flex;
            gap: 1rem;
            align-items: center;
        }}

        .nav-user {{
            color: #3b82f6;
            font-weight: 500;
        }}

        .nav-logout {{
            color: #f85149;
            text-decoration: none;
            font-weight: 500;
        }}

        /* 主容器 */
        .main-container {{
            display: flex;
            flex: 1;
        }}

        /* 内容区域 */
        .content-area {{
            flex: 1;
            padding: 30px;
            overflow-y: auto;
        }}

        /* 隐藏滚动条但保留功能 */
        ::-webkit-scrollbar {{
            width: 6px;
            height: 6px;
        }}

        ::-webkit-scrollbar-track {{
            background: transparent;
        }}

        ::-webkit-scrollbar-thumb {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 3px;
        }}

        ::-webkit-scrollbar-thumb:hover {{
            background: rgba(255, 255, 255, 0.2);
        }}

        /* Firefox */
        * {{
            scrollbar-width: thin;
            scrollbar-color: rgba(255, 255, 255, 0.1) transparent;
        }}

        .page-header {{
            margin-bottom: 30px;
        }}

        .page-header h1 {{
            font-size: 2rem;
            font-weight: 700;
            margin: 0;
            color: var(--text-main);
            border: none;
            text-decoration: none;
        }}

        .page-header p {{
            color: var(--text-dim);
            margin-top: 10px;
            border: none;
            text-decoration: none;
        }}

        /* Tab 内容 */
        .tab-content {{
            display: none;
        }}

        .tab-content.active {{
            display: block;
        }}

        .content-card {{
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 12px;
            overflow: hidden;
        }}

        /* Tab 切换按钮 */
        .tab-button {{
            padding: 10px 20px;
            background: none;
            border: none;
            color: var(--text-dim);
            cursor: pointer;
            font-size: 1rem;
            font-weight: 500;
            transition: all 0.2s ease;
        }}

        .tab-button:hover {{
            color: var(--text-main);
        }}

        .tab-button.active {{
            color: var(--accent);
        }}

        @media (max-width: 768px) {{
            .main-container {{
                flex-direction: column;
            }}

            .sidebar {{
                width: 100%;
                border-right: none;
                border-bottom: 1px solid var(--border);
                padding: 10px 0;
            }}

            .sidebar-item {{
                padding: 10px 15px;
                font-size: 0.9rem;
            }}

            .content-area {{
                padding: 15px;
            }}

            /* 顶部导航栏两行布局 */
            .top-navbar {{
                flex-direction: row;
                flex-wrap: wrap;
                height: auto;
                padding: 0.5rem 1rem;
                align-items: center;
                border-bottom: none;
            }}

            .top-navbar > .top-navbar-brand {{
                order: 1;
                flex: 0 0 auto;
                padding-bottom: 0.5rem;
                border-bottom: 1px solid var(--border);
            }}

            .top-navbar-menu {{
                order: 1;
                flex: 0 0 auto;
                margin-left: auto;
                padding-bottom: 0.5rem;
                border-bottom: 1px solid var(--border);
            }}

            .top-navbar-quote {{
                order: 2;
                width: 100%;
                flex-basis: 100%;
                text-align: center;
                padding: 0.5rem 0;
                font-size: 0.8rem;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                border-top: 1px solid var(--border);
                margin-top: 0.5rem;
            }}
        }}
    </style>
</head>
<body>
    <!-- 顶部导航栏 -->
    <nav class="top-navbar">
        <div class="top-navbar-brand">
            <img src="/static/1.ico" alt="Logo" class="navbar-logo">
        </div>
        <div class="top-navbar-quote" id="lyricsDisplay">
            偶然与巧合, 舞动了蝶翼, 谁的心头风起 ————《如果我们不曾相遇》
        </div>
        <div class="top-navbar-menu">
            {username_display}
        </div>
    </nav>

    <!-- 主容器 -->
    <div class="main-container">
        <!-- 汉堡菜单按钮 (移动端) -->
        <button class="hamburger-menu" id="hamburgerMenu">
            <span></span>
            <span></span>
            <span></span>
        </button>

        <!-- 左侧导航栏 -->
        <div class="sidebar collapsed" id="sidebar">
            <div class="sidebar-toggle" id="sidebarToggle">▶</div>
            {sidebar_menu_html}
        </div>

        <!-- 内容区域 -->
        <div class="content-area">
            <!-- Tab 切换按钮 -->
            <div class="tab-buttons" style="display: flex; gap: 10px; margin-bottom: 20px;">
                <button class="tab-button active" onclick="switchTab('sectors')" id="tab-btn-sectors">
                    🏢 行业板块
                </button>
                <button class="tab-button" onclick="switchTab('query')" id="tab-btn-query">
                    🔍 板块基金查询
                </button>
            </div>

            <!-- 行业板块 Tab -->
            <div id="tab-sectors" class="tab-content active">
                <div class="page-header">
                    <h1 style="display: flex; align-items: center;">
                        🏢 行业板块
                        <button id="refreshBtn" onclick="refreshCurrentPage()" class="refresh-button" style="margin-left: 15px; padding: 8px 16px; background: var(--accent); color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 0.9rem; font-weight: 500; transition: all 0.2s ease; display: inline-flex; align-items: center; gap: 5px;">🔄 刷新</button>
                    </h1>
                    <p>查看各行业板块的市场表现</p>
                </div>
                <div class="content-card">
                    {sectors_content}
                </div>
            </div>

            <!-- 板块基金查询 Tab -->
            <div id="tab-query" class="tab-content">
                <div class="page-header">
                    <h1 style="display: flex; align-items: center;">
                        🔍 板块基金查询
                        <button id="refreshBtn" onclick="refreshCurrentPage()" class="refresh-button" style="margin-left: 15px; padding: 8px 16px; background: var(--accent); color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 0.9rem; font-weight: 500; transition: all 0.2s ease; display: inline-flex; align-items: center; gap: 5px;">🔄 刷新</button>
                    </h1>
                    <p>查询特定板块的基金产品</p>
                </div>
                <div class="content-card">
                    {select_fund_content}
                </div>
            </div>
        </div>
    </div>

    <script src="/static/js/main.js"></script>
    <script src="/static/js/sidebar-nav.js"></script>
    <script>
        function switchTab(tabName) {{
            // 隐藏所有 tab 内容
            document.querySelectorAll('.tab-content').forEach(tab => {{
                tab.classList.remove('active');
            }});

            // 移除所有 tab 按钮的 active 状态
            document.querySelectorAll('.tab-button').forEach(btn => {{
                btn.classList.remove('active');
            }});

            // 显示选中的 tab
            document.getElementById('tab-' + tabName).classList.add('active');

            // 设置对应 tab 按钮为 active
            document.getElementById('tab-btn-' + tabName).classList.add('active');
        }}

        // 自动颜色化函数
        function autoColorize() {{
            const cells = document.querySelectorAll('.style-table td');
            cells.forEach(cell => {{
                const text = cell.textContent.trim();
                const cleanText = text.replace(/[%,亿万手]/g, '');
                const val = parseFloat(cleanText);

                if (!isNaN(val)) {{
                    if (text.includes('%') || text.includes('涨跌')) {{
                        if (text.includes('-')) {{
                            cell.classList.add('negative');
                        }} else if (val > 0) {{
                            cell.classList.add('positive');
                        }}
                    }} else if (text.startsWith('-')) {{
                        cell.classList.add('negative');
                    }} else if (text.startsWith('+')) {{
                        cell.classList.add('positive');
                    }}
                }}
            }});
        }}

        // 默认激活第一个 tab
        document.addEventListener('DOMContentLoaded', function() {{
            const firstTabBtn = document.querySelector('.tab-button');
            if (firstTabBtn) {{
                firstTabBtn.classList.add('active');
            }}

            // 歌词轮播
            const lyrics = [
                '总要有一首我的歌, 大声唱过, 再看天地辽阔 ————《一颗苹果》',
                '苍狗又白云, 身旁有了你, 匆匆轮回又有何惧 ————《如果我们不曾相遇》',
                '活着其实很好, 再吃一颗苹果 ————《一颗苹果》',
                '偶然与巧合, 舞动了蝶翼, 谁的心头风起 ————《如果我们不曾相遇》'
            ];
            let currentLyricIndex = 0;
            const lyricsElement = document.getElementById('lyricsDisplay');

            // 随机选择初始歌词
            currentLyricIndex = Math.floor(Math.random() * lyrics.length);
            if (lyricsElement) {{
                lyricsElement.textContent = lyrics[currentLyricIndex];

                // 每10秒切换一次歌词
                setInterval(function() {{
                    // 淡出
                    lyricsElement.style.opacity = '0';

                    setTimeout(function() {{
                        // 切换歌词
                        currentLyricIndex = (currentLyricIndex + 1) % lyrics.length;
                        lyricsElement.textContent = lyrics[currentLyricIndex];

                        // 淡入
                        lyricsElement.style.opacity = '1';
                    }}, 500);
                }}, 10000);
            }}

            // 自动颜色化
            autoColorize();
        }});
    </script>
</body>
</html>'''.format(
        css_style=css_style,
        username_display=username_display,
        sectors_content=sectors_content,
        select_fund_content=select_fund_content,
        sidebar_menu_html=sidebar_menu_html
    )
    return html

