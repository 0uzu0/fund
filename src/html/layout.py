# -*- coding: UTF-8 -*-
"""布局相关：顶部导航、侧边栏菜单、歌词脚本等"""


def get_top_navbar_html(username=None):
    """
    生成顶部导航栏HTML（包含歌词）。
    支持桌面端单行布局和移动端两行布局。
    :param username: str, 用户名（可选）
    :return: tuple, (navbar_html, username_display)
    """
    username_display = ''
    if username:
        username_display += '<span class="nav-user">🍎 {username}</span>'.format(username=username)
        username_display += '<a href="/logout" class="nav-logout">退出登录</a>'

    navbar_html = '''
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
    '''.format(username_display=username_display)

    return navbar_html, username_display


def get_sidebar_menu_items_html(active_page, is_admin=False):
    """侧边栏菜单项 HTML（含可选的用户管理），供各页面复用"""
    menu_items = [
        ('market', '📈', '市场行情'),
        ('market-indices', '📊', '市场指数'),
        ('precious-metals', '🥇', '贵金属行情'),
        ('portfolio', '💰', '持仓基金'),
        ('position-records', '📋', '持仓记录'),
        ('sectors', '🏢', '行业板块'),
    ]
    menu_html = ''
    for page_id, icon, label in menu_items:
        active_class = 'active' if page_id == active_page else ''
        href = f'/{page_id}'
        menu_html += f'''
            <a href="{href}" class="sidebar-item {active_class}">
                <span class="sidebar-icon">{icon}</span>
                <span>{label}</span>
            </a>
        '''
    if is_admin:
        admin_active = 'active' if active_page == 'admin-users' else ''
        menu_html += f'''
            <a href="/admin/users" class="sidebar-item {admin_active}">
                <span class="sidebar-icon">⚙</span>
                <span>用户管理</span>
            </a>
        '''
    return menu_html


def get_legacy_sidebar_html(active_page, is_admin=False):
    """
    生成传统侧边栏HTML（用于非portfolio页面）。
    :param active_page: str, 当前激活的页面
    :param is_admin: bool, 是否显示用户管理入口
    :return: str, 侧边栏HTML
    """
    menu_html = get_sidebar_menu_items_html(active_page, is_admin)
    return '''
        <!-- 汉堡菜单按钮 (移动端) -->
        <button class="hamburger-menu" id="hamburgerMenu">
            <span></span>
            <span></span>
            <span></span>
        </button>

        <!-- 左侧导航栏 -->
        <div class="sidebar collapsed" id="sidebar">
            <div class="sidebar-toggle" id="sidebarToggle">▶</div>
            {menu_items}
        </div>
    '''.format(menu_items=menu_html)


def get_lyrics_script():
    """
    生成歌词轮播的JavaScript代码。
    :return: str, JavaScript代码
    """
    return '''
    <script>
        // 歌词轮播
        (function() {
            const lyrics = [
                "偶然与巧合, 舞动了蝶翼, 谁的心头风起 ————《如果我们不曾相遇》",
                "如海上的浪花, 如深海的鱼, 浪与鱼相依 ————《鱼仔》",
                "阳光下的泡沫, 是彩色的, 一触就破 ————《泡沫》",
                "如果我变成回忆, 退出了这场生命 ————《如果我变成回忆》"
            ];
            let currentIndex = 0;
            const lyricsElement = document.getElementById('lyricsDisplay');

            function rotateLyrics() {
                if (!lyricsElement) return;
                lyricsElement.style.opacity = '0';
                setTimeout(() => {
                    currentIndex = (currentIndex + 1) % lyrics.length;
                    lyricsElement.textContent = lyrics[currentIndex];
                    lyricsElement.style.opacity = '1';
                }, 500);
            }

            setInterval(rotateLyrics, 10000);
        })();
    </script>
    '''
