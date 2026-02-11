# -*- coding: UTF-8 -*-
"""页面路由（HTML 整页）。"""
from flask import Blueprint, request, redirect

from loguru import logger

from src.auth import login_required, get_current_user_id, get_current_username, is_admin
from src.routes import get_db, get_get_lan_fund
from src.module_html import enhance_fund_tab_content

pages_bp = Blueprint('pages', __name__)


@pages_bp.route('/')
@login_required
def get_index():
    return redirect('/portfolio')


@pages_bp.route('/fund')
@login_required
def get_fund():
    return redirect('/portfolio')


@pages_bp.route('/market')
@login_required
def get_market():
    db = get_db()
    user_id = get_current_user_id()
    my_fund = get_get_lan_fund()(user_id)
    try:
        news_content = my_fund.kx_html()
        logger.debug("✓ 7*24快讯")
    except Exception as e:
        news_content = f"<p style='color:#f44336;'>加载失败: {str(e)}</p>"

    from src.module_html import get_news_page_html
    html = get_news_page_html(news_content, username=get_current_username(), is_admin=is_admin())
    return html


@pages_bp.route('/precious-metals')
@login_required
def get_precious_metals():
    user_id = get_current_user_id()
    my_fund = get_get_lan_fund()(user_id)
    precious_metals_data = {}
    try:
        precious_metals_data['real_time'] = my_fund.real_time_gold_html()
        logger.debug("✓ 实时贵金属")
    except Exception as e:
        precious_metals_data['real_time'] = f"<p style='color:#f44336;'>加载失败: {str(e)}</p>"
    try:
        precious_metals_data['one_day'] = my_fund.one_day_gold_html()
        logger.debug("✓ 分时黄金价格")
    except Exception as e:
        precious_metals_data['one_day'] = f"<p style='color:#f44336;'>加载失败: {str(e)}</p>"
    try:
        precious_metals_data['history'] = my_fund.gold_html()
        logger.debug("✓ 历史金价")
    except Exception as e:
        precious_metals_data['history'] = f"<p style='color:#f44336;'>加载失败: {str(e)}</p>"

    from src.module_html import get_precious_metals_page_html
    html = get_precious_metals_page_html(precious_metals_data, username=get_current_username(), is_admin=is_admin())
    return html


@pages_bp.route('/market-indices')
@login_required
def get_market_indices():
    user_id = get_current_user_id()
    my_fund = get_get_lan_fund()(user_id)
    market_charts = {}
    chart_data = {}
    try:
        market_charts['indices'] = my_fund.marker_html()
        chart_data['indices'] = my_fund.get_market_chart_data()
        logger.debug("✓ 全球指数")
    except Exception as e:
        market_charts['indices'] = f"<p style='color:#f44336;'>加载失败: {str(e)}</p>"
        chart_data['indices'] = {'labels': [], 'prices': [], 'changes': []}
    try:
        market_charts['volume'] = my_fund.seven_A_html()
        chart_data['volume'] = my_fund.get_volume_chart_data()
        logger.debug("✓ 成交量趋势")
    except Exception as e:
        market_charts['volume'] = f"<p style='color:#f44336;'>加载失败: {str(e)}</p>"
        chart_data['volume'] = {'labels': [], 'total': [], 'sh': [], 'sz': [], 'bj': []}
    try:
        market_charts['timing'] = my_fund.A_html()
        chart_data['timing'] = my_fund.get_timing_chart_data()
        logger.debug("✓ 上证分时")
    except Exception as e:
        market_charts['timing'] = f"<p style='color:#f44336;'>加载失败: {str(e)}</p>"
        chart_data['timing'] = {'labels': [], 'prices': [], 'change_pcts': [], 'change_amounts': [], 'volumes': [], 'amounts': []}

    from src.module_html import get_market_indices_page_html
    html = get_market_indices_page_html(
        market_charts=market_charts,
        chart_data=chart_data,
        timing_data=chart_data.get('timing'),
        username=get_current_username(),
        is_admin=is_admin()
    )
    return html


@pages_bp.route('/portfolio')
@login_required
def get_portfolio():
    db = get_db()
    add = request.args.get("add")
    delete = request.args.get("delete")
    user_id = get_current_user_id()
    my_fund = get_get_lan_fund()(user_id)
    if add:
        my_fund.add_code(add)
    if delete:
        my_fund.delete_code(delete)

    try:
        fund_content = my_fund.fund_html()
        fund_map = db.get_user_funds(user_id)
        shares_map = {code: data.get('shares', 0) for code, data in fund_map.items()}
        groups = db.get_fund_groups(user_id)
        default_group = db.get_or_create_default_group(user_id)
        if default_group:
            groups = [default_group] + [g for g in groups if g.get('id') != default_group['id']]
        fund_content = enhance_fund_tab_content(fund_content, shares_map, groups=groups, use_empty_table=True)
    except Exception as e:
        fund_content = f"<p style='color:#f44336;'>数据加载失败: {str(e)}</p>"

    user_funds = db.get_user_funds(user_id)
    default_fund = None
    fund_chart_data = None
    fund_chart_info = {}

    if user_funds:
        saved_default = db.get_chart_default_fund(user_id)
        if saved_default and saved_default['fund_code'] in user_funds:
            default_fund = saved_default
        else:
            held_funds = {code: data for code, data in user_funds.items() if data.get('shares', 0) > 0}
            if held_funds:
                first_code = list(held_funds.keys())[0]
                default_fund = {
                    'fund_code': first_code,
                    'fund_key': held_funds[first_code]['fund_key'],
                    'fund_name': held_funds[first_code]['fund_name']
                }
            else:
                first_code = list(user_funds.keys())[0]
                default_fund = {
                    'fund_code': first_code,
                    'fund_key': user_funds[first_code]['fund_key'],
                    'fund_name': user_funds[first_code]['fund_name']
                }

        if default_fund:
            fund_chart_data = my_fund.get_fund_chart_data(default_fund['fund_code'], default_fund)

        for code, data in user_funds.items():
            fund_chart_info[code] = {
                'name': data['fund_name'],
                'is_default': (default_fund and code == default_fund['fund_code'])
            }

    from src.module_html import get_portfolio_page_html
    html = get_portfolio_page_html(
        fund_content=fund_content,
        fund_map=my_fund.CACHE_MAP,
        fund_chart_data=fund_chart_data,
        fund_chart_info=fund_chart_info,
        username=get_current_username(),
        is_admin=is_admin()
    )
    return html


@pages_bp.route('/portfolio/group/<int:group_id>')
@login_required
def get_fund_group(group_id):
    db = get_db()
    user_id = get_current_user_id()
    group = db.get_fund_group(user_id, group_id)
    if not group:
        return redirect('/portfolio')
    fund_map = db.get_user_funds(user_id)
    from src.module_html import get_fund_group_page_html
    html = get_fund_group_page_html(
        group_id=group_id,
        group=group,
        fund_map=fund_map,
        username=get_current_username(),
        is_admin=is_admin()
    )
    return html


@pages_bp.route('/position-records')
@login_required
def get_position_records():
    from src.module_html import get_position_records_page_html
    html = get_position_records_page_html(username=get_current_username(), is_admin=is_admin())
    return html


@pages_bp.route('/sectors')
@login_required
def get_sectors():
    user_id = get_current_user_id()
    my_fund = get_get_lan_fund()(user_id)
    try:
        sectors_content = my_fund.bk_html()
        logger.debug("✓ 行业板块")
    except Exception as e:
        sectors_content = f"<p style='color:#f44336;'>数据加载失败: {str(e)}</p>"
    try:
        select_fund_content = my_fund.select_fund_html()
        logger.debug("✓ 板块基金查询")
    except Exception as e:
        select_fund_content = f"<p style='color:#f44336;'>数据加载失败: {str(e)}</p>"

    from src.module_html import get_sectors_page_html
    html = get_sectors_page_html(
        sectors_content=sectors_content,
        select_fund_content=select_fund_content,
        fund_map=my_fund.CACHE_MAP,
        username=get_current_username(),
        is_admin=is_admin()
    )
    return html
