# -*- coding: UTF-8 -*-
"""Fund tab, table, full page HTML and sidebar sections."""
import re

from src.html.assets import get_css_style, get_javascript_code



def enhance_fund_tab_content(content, shares_map=None, groups=None, use_empty_table=False):
    """
    Enhance the fund tab content with operations panel, file operations, and shares input.
    Args:
        content: HTML content to enhance
        shares_map: Dict mapping fund_code -> shares value (optional)
        groups: List of {id, name, fund_codes} for portfolio tab bar and row data-groups (optional)
        use_empty_table: 若 True 且 groups 不为 None，表格仅渲染表头+空 tbody，由前端按分组请求数据
    """
    code_to_group_ids = {}
    if groups:
        for g in groups:
            gid = g.get('id')
            codes = g.get('fund_codes') or []
            if gid is not None:
                for code in codes:
                    code_to_group_ids.setdefault(str(code), []).append(gid)
    # 添加文件操作和持仓统计区域（样式与 fund-operations 一致，由 style.css 统一）
    file_operations = """
        <div class="file-operations">
            <button type="button" class="btn btn-secondary" onclick="downloadFundMap()">📥 导出基金列表</button>
            <input type="file" id="uploadFile" accept=".json" style="display:none" onchange="uploadFundMap(this.files[0])">
            <button type="button" class="btn btn-secondary" onclick="document.getElementById('uploadFile').click()">📤 导入基金列表</button>
            <span class="file-operations-tip"><span aria-hidden="true">⚠️</span> 导入/导出为覆盖性操作，直接应用最新配置（非累加）</span>
        </div>
    """

    # 添加持仓统计区域（将通过JavaScript动态填充）
    position_summary = """
        <div id="positionSummary" class="position-summary" style="display: none; background: var(--card-bg); border: 1px solid var(--border); border-radius: 12px; padding: 20px; margin-bottom: 20px;">
            <h3 style="margin: 0 0 15px 0; font-size: var(--font-size-xl); font-weight: 600; color: var(--text-main); display: flex; justify-content: space-between; align-items: center;">
                💰 持仓统计
                <div style="display: flex; gap: 10px; align-items: center;">
                    <button id="showoffBtn" onclick="openShowoffCard()"
                            style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                   border: none; border-radius: 20px; padding: 6px 16px;
                                   color: white; font-size: var(--font-size-md); font-weight: 600;
                                   cursor: pointer; display: flex; align-items: center; gap: 6px;
                                   box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
                                   transition: all 0.3s ease; white-space: nowrap;">
                        ✨ 一键炫耀
                    </button>
                    <span id="toggleSensitiveValues" style="cursor: pointer; font-size: var(--font-size-xl); user-select: none;" title="显示 / 隐藏 收益明细">😀</span>
                </div>
            </h3>
            <div class="stats-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                <div class="stat-item" style="text-align: center;">
                    <div style="font-size: var(--font-size-sm); color: var(--text-dim); margin-bottom: 5px;">总持仓金额</div>
                    <div id="totalValue" class="sensitive-value" style="font-size: var(--font-size-3xl); font-weight: bold; color: var(--text-main); text-align: center;">
                        <span class="real-value">¥0.00</span><span class="hidden-value">****</span>
                    </div>
                </div>
                <div class="stat-item" style="text-align: center;">
                    <div style="font-size: var(--font-size-sm); color: var(--text-dim); margin-bottom: 5px;">今日预估涨跌</div>
                    <div id="estimatedGain" style="font-size: var(--font-size-3xl); font-weight: bold; white-space: nowrap; color: var(--text-main); text-align: center;">
                        <span class="sensitive-value"><span class="real-value">¥0.00</span><span class="hidden-value">****</span></span><span id="estimatedGainPct"> (+0.00%)</span>
                    </div>
                </div>
                <div class="stat-item" style="text-align: center;">
                    <div style="font-size: var(--font-size-sm); color: var(--text-dim); margin-bottom: 5px;">今日实际涨跌(已结算部分)</div>
                    <div id="actualGain" style="font-size: var(--font-size-3xl); font-weight: bold; white-space: nowrap; color: var(--text-main); text-align: center;">
                        <span class="sensitive-value"><span class="real-value">¥0.00</span><span class="hidden-value">****</span></span><span id="actualGainPct"> (+0.00%)</span>
                    </div>
                </div>
                <div class="stat-item" style="text-align: center;">
                    <div style="font-size: var(--font-size-sm); color: var(--text-dim); margin-bottom: 5px;">累计收益</div>
                    <div style="display: inline-flex; align-items: center; gap: 8px; flex-wrap: wrap; justify-content: center;">
                        <div id="cumulativeGain" style="font-size: var(--font-size-3xl); font-weight: bold; white-space: nowrap; color: var(--text-main);">
                            <span class="sensitive-value"><span class="real-value">¥0.00</span><span class="hidden-value">****</span></span>
                        </div>
                        <button type="button" id="cumulativeCorrectionBtn" onclick="openCumulativeCorrectionModal()" title="修正累计收益显示"
                                style="font-size: var(--font-size-sm); padding: 2px 8px; color: var(--accent); background: transparent; border: 1px solid var(--accent); border-radius: 6px; cursor: pointer;">修正</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- 累计收益修正弹窗（与其它弹窗统一样式） -->
        <div id="cumulativeCorrectionModal" class="cumulative-correction-modal" onclick="closeCumulativeCorrectionModal()">
            <div class="cumulative-correction-dialog" onclick="event.stopPropagation()">
                <h3 class="sector-modal-header" style="margin: 0 0 16px 0;">修正累计收益</h3>
                <p style="font-size: var(--font-size-base); color: var(--text-dim); margin: 0 0 12px 0;">显示累计收益 = 现有累计收益 − 修正金额</p>
                <div style="margin-bottom: 16px;">
                    <label style="display: block; font-size: var(--font-size-base); color: var(--text-dim); margin-bottom: 6px;">修正金额（元）</label>
                    <input type="number" id="cumulativeCorrectionInput" step="0.01" placeholder="0" class="sector-modal-search" style="margin-bottom: 0;">
                </div>
                <div class="sector-modal-footer" style="margin-top: 16px;">
                    <button type="button" class="btn btn-secondary" onclick="closeCumulativeCorrectionModal()">取消</button>
                    <button type="button" class="btn btn-primary" onclick="applyCumulativeCorrection()">确定</button>
                </div>
            </div>
        </div>

        <div id="fundDetailsSummary" class="fund-details-summary" style="display: none; background: var(--card-bg); border: 1px solid var(--border); border-radius: 12px; padding: 20px; margin-bottom: 20px;">
            <h3 style="margin: 0 0 15px 0; font-size: var(--font-size-lg); font-weight: 600; color: var(--text-main);">📊 持有基金</h3>
            <div style="overflow-x: auto;">
                <table id="fundDetailsTable" style="width: 100%; min-width: 700px; border-collapse: collapse; table-layout: auto; white-space: nowrap;">
                    <thead>
                        <tr style="background: rgba(59, 130, 246, 0.1);">
                            <th style="padding: 10px; text-align: center; white-space: nowrap; vertical-align: middle; color: var(--text-dim); font-weight: 500;">基金代码</th>
                            <th style="padding: 10px; text-align: center; white-space: nowrap; vertical-align: middle; color: var(--text-dim); font-weight: 500;">基金名称</th>
                            <th class="sortable" onclick="sortTable(this.closest('table'), 2)" style="padding: 10px; text-align: center; white-space: nowrap; vertical-align: middle; color: var(--text-dim); font-weight: 500; cursor: pointer; user-select: none;">持仓金额</th>
                            <th class="sortable" onclick="sortTable(this.closest('table'), 3)" style="padding: 10px; text-align: center; white-space: nowrap; vertical-align: middle; color: var(--text-dim); font-weight: 500; cursor: pointer; user-select: none;">预估收益</th>
                            <th class="sortable" onclick="sortTable(this.closest('table'), 4)" style="padding: 10px; text-align: center; white-space: nowrap; vertical-align: middle; color: var(--text-dim); font-weight: 500; cursor: pointer; user-select: none;">预估涨跌</th>
                            <th class="sortable" onclick="sortTable(this.closest('table'), 5)" style="padding: 10px; text-align: center; white-space: nowrap; vertical-align: middle; color: var(--text-dim); font-weight: 500; cursor: pointer; user-select: none;">实际收益</th>
                            <th class="sortable" onclick="sortTable(this.closest('table'), 6)" style="padding: 10px; text-align: center; white-space: nowrap; vertical-align: middle; color: var(--text-dim); font-weight: 500; cursor: pointer; user-select: none;">实际涨跌</th>
                            <th class="sortable" onclick="sortTable(this.closest('table'), 7)" style="padding: 10px; text-align: center; white-space: nowrap; vertical-align: middle; color: var(--text-dim); font-weight: 500; cursor: pointer; user-select: none;">累计收益</th>
                            <th style="padding: 10px; text-align: center; white-space: nowrap; vertical-align: middle; color: var(--text-dim); font-weight: 500;">修改持仓</th>
                        </tr>
                    </thead>
                    <tbody id="fundDetailsTableBody">
                    </tbody>
                </table>
            </div>
        </div>

        <!-- 基金详情弹窗（点击自选基金名称打开） -->
        <style>.style-table tbody td:nth-child(2){ cursor: pointer; } .style-table tbody td:nth-child(2):hover{ color: var(--accent); }</style>
        <div id="fundDetailModal" class="fund-detail-modal" style="display: none; position: fixed; inset: 0; z-index: 10003; align-items: center; justify-content: center; background: rgba(0,0,0,0.5);" onclick="if(event.target===this) window.closeFundDetailModal && window.closeFundDetailModal()">
            <div class="fund-detail-dialog" onclick="event.stopPropagation()" style="background: var(--card-bg); border: 1px solid var(--border); border-radius: 12px; max-width: 480px; width: 95%; max-height: 90vh; overflow-y: auto; padding: 20px; color: var(--text-main);">
                <div class="fund-detail-header" style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; flex-wrap: wrap; gap: 8px;">
                    <div>
                        <div class="fund-detail-name" style="font-size: var(--font-size-xl); font-weight: 700; color: var(--text-main); line-height: 1.3;" id="fundDetailName">—</div>
                        <div class="fund-detail-code" style="font-size: var(--font-size-base); color: var(--text-dim); margin-top: 4px;" id="fundDetailCode">—</div>
                    </div>
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="font-size: var(--font-size-sm); color: var(--text-dim);">估值时间</span>
                        <span id="fundDetailEstTime" style="font-size: var(--font-size-base);">—</span>
                        <button type="button" id="fundDetailCloseBtn" title="关闭" style="background: none; border: none; color: var(--text-dim); cursor: pointer; padding: 4px; font-size: var(--font-size-lg);">✕</button>
                    </div>
                </div>
                <div class="fund-detail-metrics" style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px 24px; margin-bottom: 20px; font-size: var(--font-size-base);">
                    <div><span style="color: var(--text-dim);">单位净值</span><div id="fundDetailNetValue" style="font-weight: 600; margin-top: 2px;">—</div></div>
                    <div><span style="color: var(--text-dim);">估值净值</span><div id="fundDetailEstNetValue" style="font-weight: 600; margin-top: 2px;">—</div></div>
                    <div><span style="color: var(--text-dim);">持仓金额</span><div id="fundDetailPosition" class="sensitive-value" style="font-weight: 600; margin-top: 2px;"><span class="real-value">—</span><span class="hidden-value">****</span></div></div>
                    <div><span style="color: var(--text-dim);">估值涨跌幅</span><div id="fundDetailEstPct" style="font-weight: 600; margin-top: 2px;">—</div></div>
                    <div><span style="color: var(--text-dim);">当日盈亏</span><div id="fundDetailDailyPnl" style="font-weight: 600; margin-top: 2px;">—</div></div>
                    <div><span style="color: var(--text-dim);">持有收益</span><div id="fundDetailCumulative" style="font-weight: 600; margin-top: 2px;">—</div></div>
                </div>
                <div class="fund-detail-holdings" style="border-top: 1px solid var(--border); padding-top: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <span style="font-size: var(--font-size-md); font-weight: 600;">前10重仓股票</span>
                        <span style="font-size: var(--font-size-sm); color: var(--text-dim);">涨跌幅 / 占比</span>
                    </div>
                    <div id="fundDetailHoldingsList" style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px 16px; font-size: var(--font-size-base);">
                        <div style="grid-column: 1 / -1; color: var(--text-dim);" id="fundDetailHoldingsPlaceholder">暂无数据</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 炫耀卡片模态框 -->
        <div id="showoffModal" class="showoff-modal" onclick="closeShowoffCard(event)">
            <div class="showoff-card" onclick="event.stopPropagation()">
                <!-- 关闭按钮 -->
                <button class="showoff-close" onclick="closeShowoffCard()">✕</button>

                <!-- 左上角品牌标识 -->
                <div class="showoff-brand-corner">
                    <img src="/static/1.ico" alt="Lan Fund" class="brand-logo" onerror="this.style.display='none'">
                    <span class="brand-name">Lan Fund</span>
                </div>

                <!-- 卡片背景装饰 -->
                <div class="showoff-bg-decoration">
                    <div class="bg-circle circle-1"></div>
                    <div class="bg-circle circle-2"></div>
                    <div class="bg-circle circle-3"></div>
                    <div class="bg-stars"></div>
                </div>

                <!-- 卡片头部 -->
                <div class="showoff-header">
                    <div class="showoff-icon">💰</div>
                    <h2 class="showoff-title">今日收益</h2>
                    <p class="showoff-date" id="showoffDate">2026-02-03</p>
                </div>

                <!-- 持仓统计摘要 -->
                <div class="showoff-summary">
                    <div class="summary-row summary-row-total">
                        <div class="summary-item">
                            <div class="summary-label">总持仓</div>
                            <div class="summary-value" id="showoffTotalValue">¥0.00</div>
                        </div>
                    </div>
                    <div class="summary-row">
                        <div class="summary-item">
                            <div class="summary-label">今日预估</div>
                            <div class="summary-value" id="showoffEstimatedGain">+¥0.00</div>
                        </div>
                        <div class="summary-item">
                            <div class="summary-label">今日实际</div>
                            <div class="summary-value" id="showoffActualGain">+¥0.00</div>
                        </div>
                    </div>
                </div>

                <!-- Top3基金明细 -->
                <div class="showoff-funds">
                    <div class="funds-header">
                        <span class="funds-title">🏆 收益Top3</span>
                    </div>
                    <div class="funds-list" id="showoffFundsList">
                        <!-- 动态生成 -->
                    </div>
                </div>
            </div>
        </div>
    """

    # 添加操作按钮面板
    operations_panel = """
        <div class="fund-operations">
            <div class="operation-group">
                <button class="btn btn-info" onclick="openFundSelectionModal('sector')">🏷️ 标注板块</button>
                <button class="btn btn-warning" onclick="openFundSelectionModal('unsector')">🏷️ 删除板块</button>
                <button class="btn btn-danger" onclick="openFundSelectionModal('delete')">🗑️ 删除基金</button>
            </div>
        </div>
    """

    # 简化的添加基金输入框
    add_fund_area = """
        <div class="add-fund-input">
            <input type="text" id="fundCodesInput" placeholder="输入基金代码（逗号分隔，如：016858,007872）">
            <button class="btn btn-primary" onclick="addFunds()">添加</button>
        </div>
    """

    # 在"近30天"列后添加"持仓金额"列（默认 tab 显示，分组 tab 隐藏）
    content = re.sub(r'(<th[^>]*>近30天</th>)',
                   r'\1\n                    <th class="portfolio-position-col">持仓金额</th>',
                   content, count=1)

    # 在每个数据行添加份额输入框
    # 先找到所有表格行，然后在包含基金代码的行末尾添加份额输入框
    def add_shares_to_row(match):
        row_content = match.group(0)
        # 从行内容中提取第一个6位数字（基金代码）- 假设第一列是基金代码
        code_match = re.search(r'<td[^>]*>(\d{6})</td>', row_content)
        if code_match:
            fund_code = code_match.group(1)

            # 根据份额数据确定按钮状态
            shares = 0
            if shares_map and fund_code in shares_map:
                try:
                    shares = float(shares_map[fund_code])
                except (ValueError, TypeError):
                    shares = 0

            # 根据份额值设置按钮文本和颜色
            if shares > 0:
                button_text = '修改'
                button_color = '#10b981'  # 绿色
            else:
                button_text = '设置'
                button_color = '#3b82f6'  # 蓝色

            # 在行末添加份额设置按钮（在</tr>之前）- 去掉最后的</tr>，添加按钮后再加回；用 data-fund-code 便于事件委托；持仓金额列在分组 tab 隐藏
            row_with_shares = row_content[:-5] + f'''<td class="portfolio-position-col">
                <button type="button" class="shares-button" id="sharesBtn_{fund_code}" data-fund-code="{fund_code}"
                        style="padding: 6px 12px; background: {button_color}; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: var(--font-size-base); transition: all 0.2s;">
                    {button_text}
                </button>
            </td></tr>'''
            # 为 tab 切换与分页添加 data 属性（持有/自选/分组）
            group_ids = code_to_group_ids.get(fund_code, [])
            data_attrs = ' data-code="%s" data-holding="%s" data-watchlist="%s" data-groups="%s"' % (
                fund_code,
                '1' if shares > 0 else '',
                '1' if shares <= 0 else '',
                ','.join(str(x) for x in group_ids),
            )
            row_with_shares = re.sub(r'<tr\b', '<tr' + data_attrs, row_with_shares, count=1)
            # 分组下增加「移除」列，仅保留移除按钮，样式与总体一致
            if groups is not None:
                code_esc = fund_code.replace('\\', '\\\\').replace("'", "\\'").replace('"', '&quot;')
                row_with_shares = row_with_shares.replace(
                    '</tr>',
                    '<td class="portfolio-op-cell portfolio-op-col"><button type="button" class="btn btn-secondary btn-remove-from-group" data-code="' + fund_code + '" onclick="(typeof portfolioRemoveFundFromGroup===\'function\'&&portfolioRemoveFundFromGroup(\'' + code_esc + '\'));return false;" style="padding:4px 10px;font-size:0.85rem;">移除</button></td></tr>'
                )
            return row_with_shares
        return row_content

    # 匹配完整的表格行（非贪婪匹配行内容）
    content = re.sub(r'<tr>.*?</tr>', add_shares_to_row, content, flags=re.DOTALL)

    if groups is None:
        # 非持仓页（未传 groups）：仅「自选基金」标题，无 tab
        fund_list_section = '''
        <div class="fund-list-section" style="background: var(--card-bg); border: 1px solid var(--border); border-radius: 12px; padding: 20px; margin-bottom: 20px;">
            <h3 style="margin: 0 0 15px 0; font-size: var(--font-size-lg); font-weight: 600; color: var(--text-main);">📊 自选基金</h3>
            <div style="overflow-x: auto;">
''' + content + '''
            </div>
        </div>
'''
        return file_operations + position_summary + operations_panel + add_fund_area + fund_list_section

    # 持仓页：默认与新建分组在同一主页面切换，不跳转；tab 切换仅过滤表格数据
    tabs_html = ''
    for i, g in enumerate(groups):
        gid = g.get('id')
        name = (g.get('name') or '未命名').replace('<', '&lt;').replace('>', '&gt;')
        if gid is None:
            continue
        active = ' active' if i == 0 else ''
        cls = 'portfolio-tab portfolio-tab-group' if i > 0 else 'portfolio-tab'
        default_attr = ' data-default="1"' if i == 0 else ''
        tabs_html += f'<button type="button" class="{cls}{active}" data-tab="group-{gid}"{default_attr}>{name}</button>\n'
    tabs_html += '<button type="button" class="portfolio-tab portfolio-tab-new" id="portfolioBtnNewGroup">+ 新建分组</button>'

    # 输入基金代码新增：放在 tab 下；联想数据来自默认页所有基金；分组 tab 时在添加按钮后显示「删除分组」
    add_fund_in_tab = '''
            <div class="portfolio-add-fund-row add-fund-input" style="display: flex; align-items: stretch; gap: 12px; flex-wrap: wrap; margin-bottom: 16px;">
                <div class="portfolio-add-fund-suggest-wrap" style="position: relative; flex: 1; min-width: 200px;">
                    <input type="text" id="fundCodesInput" placeholder="输入基金代码或名称（支持联想）" class="sector-modal-search" autocomplete="off" style="width: 100%; height: 36px; box-sizing: border-box;">
                    <div id="portfolioFundSuggestList" class="portfolio-fund-suggest-list" style="display: none; position: absolute; left: 0; right: 0; top: 100%; z-index: 100; max-height: 240px; overflow-y: auto; background: var(--card-bg); border: 1px solid var(--border); border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin-top: 4px;"></div>
                </div>
                <button type="button" class="btn btn-primary" id="portfolioAddByInputBtn" style="height: 36px; box-sizing: border-box;">添加</button>
                <span id="portfolioGroupActionsWrap" style="display: none;"><button type="button" class="btn btn-secondary" id="portfolioDeleteGroupBtn" style="height: 36px; box-sizing: border-box; color: #f85149;">删除分组</button></span>
            </div>
'''

    # content 为 get_table_html 输出：<div class="table-container"><table>...</table></div>，抽出 thead+tbody+</table>
    if use_empty_table and groups is not None:
        # 持仓页按分组请求数据：首屏只渲染表头+空 tbody，避免所有分组共享同一份初始数据
        empty_content = get_table_html(
            ["基金代码", "基金名称", "当前时间", "净值", "今日涨幅", "昨日涨幅", "连涨/跌", "近30天"],
            [],
            sortable_columns=[4, 5, 6, 7]
        )
        empty_content = re.sub(r'(<th[^>]*>近30天</th>)', r'\1\n                    <th class="portfolio-position-col">持仓金额</th>', empty_content, count=1)
        table_inner = re.sub(r'^<div class="table-container">\s*<table class="style-table">\s*', '', empty_content, flags=re.DOTALL)
        table_inner = re.sub(r'\s*</table>\s*</div>\s*$', '\n    </table>', table_inner, flags=re.DOTALL)
        table_inner = re.sub(r'(</tr>\s*</thead>)', r'<th class="portfolio-op-cell portfolio-op-col">操作</th>\1', table_inner, count=1)
    else:
        table_inner = re.sub(r'^<div class="table-container">\s*<table class="style-table">\s*', '', content, flags=re.DOTALL)
        table_inner = re.sub(r'\s*</table>\s*</div>\s*$', '\n    </table>', table_inner, flags=re.DOTALL)
        # 分组「移除」列：表头增加「操作」（默认 tab 隐藏，分组 tab 显示）
        table_inner = re.sub(r'(</tr>\s*</thead>)', r'<th class="portfolio-op-cell portfolio-op-col">操作</th>\1', table_inner, count=1)

    fund_list_section = '''
        <div class="fund-list-section portfolio-with-tabs" style="background: var(--card-bg); border: 1px solid var(--border); border-radius: 12px; padding: 20px; margin-bottom: 20px;">
            <div class="portfolio-section-header" style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; margin-bottom: 16px;">
                <h3 style="margin: 0; font-size: var(--font-size-lg); font-weight: 600; color: var(--text-main);">💎 自选基金</h3>
            </div>
            <div class="portfolio-tabs" id="portfolioTabs" style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px;">
''' + tabs_html + '''
            </div>
''' + add_fund_in_tab + '''
            <div class="portfolio-table-wrap" id="portfolioTableWrap" style="overflow-x: auto;">
                <div class="table-container">
                <table class="style-table" id="portfolioFundTable">
''' + table_inner + '''
                </div>
            </div>
            <div class="portfolio-pagination" id="portfolioPagination" style="margin-top: 16px; display: flex; align-items: center; justify-content: center; gap: 12px; flex-wrap: wrap;"></div>
        </div>
'''
    return file_operations + position_summary + operations_panel + fund_list_section



def build_portfolio_table_rows(result_rows, code_to_group_ids, shares_map, with_op_col=False, with_position_col=True):
    """
    根据基金表格数据生成自选分组表格的 tbody 行 HTML（供按分组请求数据使用）。
    :param result_rows: list of lists，每行 8 列：基金代码、基金名称、当前时间、净值、今日涨幅、昨日涨幅、连涨/跌、近30天
    :param code_to_group_ids: dict, fund_code -> [group_id, ...]
    :param shares_map: dict, fund_code -> shares 数值
    :param with_op_col: 是否添加「操作」列（移除按钮），默认分组不含
    :param with_position_col: 是否添加「持仓金额」列（设置/修改按钮），新建分组不含
    :return: str, <tr>...</tr> 拼接的 HTML
    """
    def esc(s):
        if s is None:
            return ''
        s = str(s)
        return s.replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')

    rows_html = []
    for row in result_rows:
        if len(row) < 8:
            continue
        fund_code = str(row[0])
        group_ids = code_to_group_ids.get(fund_code, [])
        try:
            shares = float(shares_map.get(fund_code, 0) or 0)
        except (ValueError, TypeError):
            shares = 0
        button_text = '修改' if shares > 0 else '设置'
        button_color = '#10b981' if shares > 0 else '#3b82f6'
        data_attrs = ' data-code="%s" data-holding="%s" data-watchlist="%s" data-groups="%s"' % (
            esc(fund_code),
            '1' if shares > 0 else '',
            '1' if shares <= 0 else '',
            ','.join(str(x) for x in group_ids),
        )
        tds = ''.join('<td>' + esc(cell) + '</td>' for cell in row)
        op_td = ''
        if with_op_col:
            code_esc = fund_code.replace('\\', '\\\\').replace("'", "\\'").replace('"', '&quot;')
            op_td = '<td class="portfolio-op-cell portfolio-op-col"><button type="button" class="btn btn-secondary btn-remove-from-group" data-code="' + esc(fund_code) + '" onclick="(typeof portfolioRemoveFundFromGroup===\'function\'&&portfolioRemoveFundFromGroup(\'' + code_esc + '\'));return false;" style="padding:4px 10px;font-size:0.85rem;">移除</button></td>'
        position_td = ''
        if with_position_col:
            position_td = '<td class="portfolio-position-col"><button type="button" class="shares-button" id="sharesBtn_' + esc(fund_code) + '" data-fund-code="' + esc(fund_code) + '" style="padding: 6px 12px; background: ' + button_color + '; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: var(--font-size-base); transition: all 0.2s;">' + button_text + '</button></td>'
        row_html = '<tr' + data_attrs + '>' + tds + position_td + op_td + '</tr>'
        rows_html.append(row_html)
    return ''.join(rows_html)


def get_table_html(title, data, sortable_columns=None):
    """
    生成单个表格的HTML代码。
    :param title: list, 表头标题列表。
    :param data: list of lists, 表格数据。
    :param sortable_columns: list, 可排序的列的索引 (从0开始)。例如 [1, 2, 3]
    """
    if sortable_columns is None:
        sortable_columns = []

    ths = []
    for i, col_name in enumerate(title):
        if i in sortable_columns:
            ths.append(f'<th class="sortable" onclick="sortTable(this.closest(\'table\'), {i})">{col_name}</th>')
        else:
            ths.append(f"<th>{col_name}</th>")

    thead_html = f"""
    <thead>
        <tr>
            {''.join(ths)}
        </tr>
    </thead>
    """

    tbody_rows = []
    for row_data in data:
        tds = [f"<td>{x}</td>" for x in row_data]
        tbody_rows.append(f"<tr>{''.join(tds)}</tr>")

    tbody_html = f"""
    <tbody>
        {''.join(tbody_rows)}
    </tbody>
    """

    return f"""
    <div class="table-container">
        <table class="style-table">
            {thead_html}
            {tbody_html}
        </table>
    </div>
    """


def generate_holdings_cards_html(fund_data_map):
    """
    Generate holdings cards HTML for funds with shares > 0.
    :param fund_data_map: dict, mapping of fund code to fund data
    :return: str, HTML for holdings cards section
    """
    # Filter funds with position (shares > 0)
    held_funds = []
    for code, data in fund_data_map.items():
        if (data.get('shares') or 0) > 0:
            held_funds.append((code, data))

    if not held_funds:
        return ""

    cards_html = []
    for code, data in held_funds:
        fund_name = data.get('fund_name', 'Unknown')
        sectors = data.get('sectors', [])

        # Generate sector tags with icon and gray text (like delete sector popup)
        sector_tags = f'<span style="color: #8b949e; font-size: var(--font-size-sm);"> 🏷️ {", ".join(sectors)}</span>' if sectors else ''

        # Card HTML
        card_html = f"""
        <div class="holding-card" data-code="{code}">
            <div class="holding-card-header">
                <div class="holding-card-title">
                    <div class="holding-card-code">{code}</div>
                    <div class="holding-card-name">{fund_name}</div>
                    {f'<div class="holding-card-sectors">{sector_tags}</div>' if sectors else ''}
                </div>
                <div class="holding-card-badge">持仓</div>
            </div>
            <div class="holding-card-metrics">
                <div class="holding-metric">
                    <div class="holding-metric-label">净值</div>
                    <div class="holding-metric-value" id="card-netvalue-{code}">--</div>
                </div>
                <div class="holding-metric">
                    <div class="holding-metric-label">估值增长</div>
                    <div class="holding-metric-value" id="card-estimated-{code}">--</div>
                </div>
                <div class="holding-metric">
                    <div class="holding-metric-label">日涨幅</div>
                    <div class="holding-metric-value" id="card-daygrowth-{code}">--</div>
                </div>
                <div class="holding-metric">
                    <div class="holding-metric-label">持仓金额</div>
                    <div class="holding-metric-value" id="card-position-{code}">¥0.00</div>
                </div>
            </div>
            <div class="holding-card-footer">
                <div class="holding-footer-item">
                    <div class="holding-footer-label">连涨/跌</div>
                    <div class="holding-footer-value" id="card-consecutive-{code}">--</div>
                </div>
                <div class="holding-footer-item">
                    <div class="holding-footer-label">近30天</div>
                    <div class="holding-footer-value" id="card-monthly-{code}">--</div>
                </div>
                <div class="holding-footer-item">
                    <div class="holding-footer-label">份额</div>
                    <div class="holding-footer-value">
                        <input type="number" step="0.01" min="0"
                               id="card-shares-{code}"
                               class="shares-input"
                               data-code="{code}"
                               placeholder="0"
                               value=""
                               style="width: 60px; padding: 2px 4px; border: 1px solid var(--border); border-radius: 4px; font-size: var(--font-size-xs); background: var(--card-bg); color: var(--text-main);"
                               onchange="updateShares('{code}', this.value)">
                    </div>
                </div>
            </div>
        </div>
        """
        cards_html.append(card_html)

    return f"""
    <div class="holdings-section">
        <div class="holdings-header">
            <div class="holdings-title">💎 Core Holdings</div>
            <div class="holdings-count">{len(held_funds)} Positions</div>
        </div>
        <div class="holdings-grid">
            {''.join(cards_html)}
        </div>
    </div>
    """


def generate_terminal_dashboard_html():
    """
    Generate the Terminal Dashboard HTML (will be populated by JavaScript).
    """
    return """
    <div class="terminal-dashboard" id="terminalDashboard" style="display: none;">
        <div class="stat-group">
            <label>今日预估收益 (EST. TODAY)</label>
            <div class="big-num" id="dashEstGain">¥0.00</div>
            <div class="stat-change" id="dashEstGainPct">0.00% ↑</div>
        </div>
        <div class="stat-group">
            <label>持仓金额 (POSITION VALUE)</label>
            <div class="big-num" id="dashTotalValue">¥0.00</div>
            <div class="stat-change" id="dashHoldingCount">0 只持有中</div>
        </div>
        <div class="stat-group">
            <label>昨日结算 (SETTLED)</label>
            <div class="big-num" id="dashActualGain">¥0.00</div>
            <div class="stat-change" id="dashActualGainPct">0.00% ↓</div>
        </div>
    </div>
    """


def get_full_page_html_sidebar(tabs_data, username=None):
    """Generate full page HTML with sidebar navigation"""
    js_script = get_javascript_code()
    css_style = get_css_style()

    # Get fund data for holdings/watchlist sections
    fund_map = {}
    for tab in tabs_data:
        if tab['id'] == 'fund':
            # Extract fund_map from fund tab - will be passed from fund_server.py
            fund_map = tab.get('fund_map', {})
            break

    # Generate sections for other tabs (hidden by default)
    other_sections_html = ''
    for tab in tabs_data:
        if tab['id'] != 'fund':
            tab_id = tab['id']
            tab_title = tab['title']
            other_sections_html += f'''
                <section class="content-section hidden" id="{tab_id}Section">
                    <div class="section-header">
                        <h2 class="section-heading">{tab_title}</h2>
                    </div>
                    <div class="section-content" id="{tab_id}Content"></div>
                </section>
            '''

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LanFund Terminal</title>
    {css_style}
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <!-- Navbar with logo and quote -->
    <nav class="navbar">
        <div class="navbar-brand">
            <img src="/static/1.ico" alt="Logo" class="navbar-logo">
        </div>
        <div class="navbar-quote">
            偶然与巧合, 舞动了蝶翼, 谁的心头风起 ————《如果我们不曾相遇》
        </div>
        <div class="navbar-menu">
            <span class="navbar-item">实时行情</span>
            {f'<span class="navbar-item" style="color: #3b82f6;">🍎 {username}</span>' if username else ''}
            {f'<a href="/logout" class="navbar-item" style="color: #f85149; text-decoration: none;">退出登录</a>' if username else ''}
        </div>
    </nav>

    <!-- App Container with Sidebar -->
    <div class="app-container-sidebar">
        {get_sidebar_navigation_html()}

        <main class="main-content-area">
            {get_header_bar_html()}
            {get_summary_bar_html()}

            <div class="content-body" id="contentBody">
                <!-- Holdings & Watchlist Sections -->
                {generate_holdings_section_html(fund_map)}
                {generate_watchlist_section_html(fund_map)}

                <!-- Other tab sections (hidden by default) -->
                {other_sections_html}
            </div>
        </main>
    </div>

    <!-- Modals (preserved) -->
    <!-- 板块选择对话框 -->
    <div class="sector-modal" id="sectorModal">
        <div class="sector-modal-content">
            <div class="sector-modal-header">选择板块</div>
            <input type="text" class="sector-modal-search" id="sectorSearch" placeholder="搜索板块名称...">
            <div id="sectorCategories">
                <!-- 板块分类将通过JS动态生成 -->
            </div>
            <div class="sector-modal-footer">
                <button class="btn btn-secondary" onclick="closeSectorModal()">取消</button>
                <button class="btn btn-primary" onclick="confirmSector()">确定</button>
            </div>
        </div>
    </div>

    <!-- 基金选择对话框 -->
    <div class="sector-modal" id="fundSelectionModal">
        <div class="sector-modal-content">
            <div class="sector-modal-header" id="fundSelectionTitle">选择基金</div>
            <input type="text" class="sector-modal-search" id="fundSelectionSearch" placeholder="搜索基金代码或名称...">
            <div id="fundSelectionList" style="max-height: 400px; overflow-y: auto;">
                <!-- 基金列表将通过JS动态生成 -->
            </div>
            <div class="sector-modal-footer">
                <button class="btn btn-secondary" onclick="closeFundSelectionModal()">取消</button>
                <button class="btn btn-primary" id="fundSelectionConfirmBtn" onclick="confirmFundSelection()">确定</button>
            </div>
        </div>
    </div>

    <!-- 确认对话框 -->
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

    <!-- 加仓时间选择器（约占加仓弹窗 90%） -->
    <div id="addPositionTimePicker" style="display: none; position: fixed; inset: 0; z-index: 10002; align-items: center; justify-content: center; pointer-events: none;">
        <div class="sector-modal-content" style="max-width: 378px; width: 90%; pointer-events: auto; box-shadow: 0 4px 20px rgba(0,0,0,0.2); padding: 0 18px 14px;">
            <div style="display: flex; align-items: center; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid var(--border); margin-bottom: 10px;">
                <button type="button" onclick="closeAddPositionTimePicker()" style="background: none; border: none; color: var(--accent); font-size: var(--font-size-lg); cursor: pointer;">取消</button>
                <span style="font-weight: 600; color: var(--text-main); font-size: var(--font-size-lg);">加仓时间</span>
                <button type="button" onclick="confirmAddPositionTime()" style="background: none; border: none; color: var(--accent); font-size: var(--font-size-lg); cursor: pointer;">确认</button>
            </div>
            <div id="addPositionTimeOptions" style="overflow-y: auto; max-height: 320px; padding: 4px 0;">
                <!-- 选项由 JS 动态生成 -->
            </div>
        </div>
    </div>
    <div id="addPositionTimePickerOverlay" onclick="closeAddPositionTimePicker()" style="display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.4); z-index: 10001;"></div>

    <!-- 减仓弹窗 -->
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
                    <span style="font-size: var(--font-size-sm); color: var(--text-dim); margin-left: 8px;">持有份额</span><span id="reducePositionUnits" style="font-weight: 500; margin-left: 4px;"></span>
                </div>
                <div style="margin-bottom: 12px;">
                    <label style="display: block; font-size: var(--font-size-base); font-weight: 500; color: var(--text-main); margin-bottom: 6px;">减仓金额（元）</label>
                    <div style="display: flex; align-items: center; border: 1px solid var(--border); border-radius: 8px; background: var(--card-bg);">
                        <span style="padding: 10px 12px; color: var(--text-dim);">¥</span>
                        <input type="number" id="reducePositionAmount" step="0.01" min="0" placeholder="请输入减仓金额" style="flex: 1; padding: 10px 0; border: none; background: none; font-size: var(--font-size-md); color: var(--text-main);" oninput="if(window.updateReducePositionFee) window.updateReducePositionFee()">
                    </div>
                </div>
                <div style="margin-bottom: 12px;">
                    <label style="display: block; font-size: var(--font-size-base); font-weight: 500; color: var(--text-main); margin-bottom: 6px;">卖出费率</label>
                    <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                        <label style="display: inline-flex; align-items: center; cursor: pointer; font-size: var(--font-size-base); color: var(--text-main);"><input type="radio" name="reducePositionFeeRate" value="0" checked style="margin-right: 4px;">0%</label>
                        <label style="display: inline-flex; align-items: center; cursor: pointer; font-size: var(--font-size-base); color: var(--text-main);"><input type="radio" name="reducePositionFeeRate" value="0.5" style="margin-right: 4px;">0.5%</label>
                        <label style="display: inline-flex; align-items: center; cursor: pointer; font-size: var(--font-size-base); color: var(--text-main);"><input type="radio" name="reducePositionFeeRate" value="1" style="margin-right: 4px;">1%</label>
                        <label style="display: inline-flex; align-items: center; cursor: pointer; font-size: var(--font-size-base); color: var(--text-main);"><input type="radio" name="reducePositionFeeRate" value="1.5" style="margin-right: 4px;">1.5%</label>
                    </div>
                </div>
                <div style="margin-bottom: 12px; font-size: var(--font-size-sm); color: var(--text-dim);">
                    估算手续费 <span id="reducePositionFee">0.00</span> 元
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

    {js_script}
    <script src="/static/js/main.js"></script>
    <script src="/static/js/sidebar-nav.js"></script>
</body>
</html>'''

    return html


def get_full_page_html(tabs_data, username=None, use_sidebar=False):
    # Use new sidebar layout if requested
    if use_sidebar:
        return get_full_page_html_sidebar(tabs_data, username)

    js_script = get_javascript_code()
    css_style = get_css_style()

    # Generate Tab Headers
    tab_headers = []
    tab_contents = []

    # Check if tabs_data is a list of dicts (new format) or list of strings (old format fallback)
    if isinstance(tabs_data, list) and len(tabs_data) > 0 and isinstance(tabs_data[0], str):
        # Fallback for old format
        return f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>LanFund Dashboard</title>
            {css_style}
        </head>
        <body>
            <div class="app-container">
                <div class="main-content">
                    <div class="dashboard-grid">
                        {''.join(tabs_data)}
                    </div>
                </div>
            </div>
            {js_script}
        </body>
        </html>
        """

    for index, tab in enumerate(tabs_data):
        is_active = 'active' if index == 0 else ''
        tab_id = tab['id']
        tab_title = tab['title']
        content = tab['content']

        tab_headers.append(f"""
            <button class="tab-button {is_active}" onclick="openTab(event, '{tab_id}')">
                {tab_title}
            </button>
        """)

        # 为"自选基金"标签页添加操作区域
        if tab_id == "fund":
            # 使用 enhance_fund_tab_content 函数来添加操作区域（避免重复代码）
            enhanced_content = enhance_fund_tab_content(content)
        else:
            enhanced_content = content

        tab_contents.append(f"""
            <div id="{tab_id}" class="tab-content {is_active}">
                {enhanced_content}
            </div>
        """)

    # Check if we have actual data or if this is initial SSE setup
    has_data = tabs_data and len(tabs_data) > 0 and tabs_data[0].get('content', '').strip()

    if not has_data:
        # Return SSE-enabled loading page
        return get_sse_loading_page(css_style, js_script)

    return f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
        <meta http-equiv="Pragma" content="no-cache">
        <meta http-equiv="Expires" content="0">
        <title>LanFund Dashboard</title>
        {css_style}
    </head>
    <body>
        <nav class="navbar">
            <div class="navbar-brand">BuBu Fund LanFund助手</div>
            <div class="navbar-menu">
                <span class="navbar-item">实时行情</span>
                {f'<span class="navbar-item" style="color: #3b82f6;">🍎 {username}</span>' if username else ''}
                {f'<a href="/logout" class="navbar-item" style="color: #f85149; text-decoration: none;">退出登录</a>' if username else ''}
            </div>
        </nav>
        
        <div class="app-container">
            <div class="main-content">
                <div class="tabs-header">
                    {''.join(tab_headers)}
                </div>
                <div class="dashboard-grid">
                    {''.join(tab_contents)}
                </div>
            </div>
        </div>

        <!-- 板块选择对话框 -->
        <div class="sector-modal" id="sectorModal">
            <div class="sector-modal-content">
                <div class="sector-modal-header">选择板块</div>
                <input type="text" class="sector-modal-search" id="sectorSearch" placeholder="搜索板块名称...">
                <div id="sectorCategories">
                    <!-- 板块分类将通过JS动态生成 -->
                </div>
                <div class="sector-modal-footer">
                    <button class="btn btn-secondary" onclick="closeSectorModal()">取消</button>
                    <button class="btn btn-primary" onclick="confirmSector()">确定</button>
                </div>
            </div>
        </div>

        <!-- 基金选择对话框 -->
        <div class="sector-modal" id="fundSelectionModal">
            <div class="sector-modal-content">
                <div class="sector-modal-header" id="fundSelectionTitle">选择基金</div>
                <input type="text" class="sector-modal-search" id="fundSelectionSearch" placeholder="搜索基金代码或名称...">
                <div id="fundSelectionList" style="max-height: 400px; overflow-y: auto;">
                    <!-- 基金列表将通过JS动态生成 -->
                </div>
                <div class="sector-modal-footer">
                    <button class="btn btn-secondary" onclick="closeFundSelectionModal()">取消</button>
                    <button class="btn btn-primary" id="fundSelectionConfirmBtn" onclick="confirmFundSelection()">确定</button>
                </div>
            </div>
        </div>

        <!-- 确认对话框 -->
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

        {js_script}
    </body>
    </html>
    """


def get_sse_loading_page(css_style, js_script):
    """Return a loading page that will be updated via SSE"""
    return f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>LanFund Dashboard - Loading</title>
        {css_style}
        <style>
            .loading-container {{
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100%;
                padding: 2rem;
            }}
            .navbar-brand {{
                display: flex;
                align-items: center;
            }}
            .navbar-logo {{
                width: 32px;
                height: 32px;
                margin-right: 12px;
            }}
            .loading-spinner {{
                border: 4px solid #f3f3f3;
                border-top: 4px solid var(--bloomberg-blue);
                border-radius: 50%;
                width: 50px;
                height: 50px;
                animation: spin 1s linear infinite;
            }}
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
            .loading-status {{
                margin-top: 1rem;
                font-size: 0.9rem;
                color: #666;
            }}
            .task-list {{
                margin-top: 1rem;
                max-width: 400px;
            }}
            .task-item {{
                padding: 0.5rem;
                margin: 0.3rem 0;
                border-radius: 4px;
                background: #f5f5f5;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            .task-item.completed {{
                background: #d4edda;
                color: #155724;
            }}
            .task-item.error {{
                background: #f8d7da;
                color: #721c24;
            }}
        </style>
    </head>
    <body>
        <nav class="navbar">
            <div class="navbar-brand">
                <img src="/static/1.ico" alt="Logo" class="navbar-logo">
                <span>BuBu Fund LanFund助手</span>
            </div>
            <div class="navbar-menu">
                <span class="navbar-item">加载中...</span>
            </div>
        </nav>
        
        <div class="app-container">
            <div class="main-content">
                <div class="loading-container">
                    <div class="loading-spinner"></div>
                    <div class="loading-status" id="status">正在连接数据源...</div>
                    <div class="task-list" id="task-list"></div>
                </div>
            </div>
        </div>

        <script>
        const eventSource = new EventSource('/fund' + window.location.search);
        const taskList = document.getElementById('task-list');
        const statusEl = document.getElementById('status');
        const taskElements = {{}};

        eventSource.addEventListener('message', function(e) {{
            try {{
                const data = JSON.parse(e.data);
                
                if (data.type === 'init') {{
                    statusEl.textContent = '正在加载数据模块...';
                    data.tasks.forEach(taskName => {{
                        const taskEl = document.createElement('div');
                        taskEl.className = 'task-item';
                        taskEl.innerHTML = `<span>${{getTaskTitle(taskName)}}</span><span>⏳</span>`;
                        taskList.appendChild(taskEl);
                        taskElements[taskName] = taskEl;
                    }});
                }}
                else if (data.type === 'task_complete') {{
                    if (taskElements[data.name]) {{
                        taskElements[data.name].className = 'task-item completed';
                        taskElements[data.name].querySelector('span:last-child').textContent = '✓';
                    }}
                }}
                else if (data.type === 'error') {{
                    if (taskElements[data.name]) {{
                        taskElements[data.name].className = 'task-item error';
                        taskElements[data.name].querySelector('span:last-child').textContent = '✗';
                    }}
                }}
                else if (data.type === 'complete') {{
                    statusEl.textContent = '加载完成！正在渲染页面...';
                    eventSource.close();
                    // Replace entire page with the complete HTML
                    document.open();
                    document.write(data.html);
                    document.close();
                }}
            }} catch (err) {{
                console.error('SSE parse error:', err);
            }}
        }});

        eventSource.addEventListener('error', function(e) {{
            statusEl.textContent = '连接错误，正在重试...';
            console.error('SSE error:', e);
        }});

        function getTaskTitle(taskName) {{
            const titles = {{
                'kx': '7*24快讯',
                'marker': '全球指数',
                'real_time_gold': '实时贵金属',
                'gold': '历史金价',
                'seven_A': '成交量趋势',
                'A': '上证分时',
                'fund': '自选基金',
                'bk': '行业板块'
            }};
            return titles[taskName] || taskName;
        }}
        </script>
    </body>
    </html>
    """


def get_sidebar_navigation_html():
    """Generate 70px sidebar with 9 section icons"""
    sections = [
        {'id': 'news', 'icon': '📰', 'label': '快讯', 'tab_id': 'kx'},
        {'id': 'indices', 'icon': '📊', 'label': '指数', 'tab_id': 'marker'},
        {'id': 'gold-realtime', 'icon': '🥇', 'label': '贵金属', 'tab_id': 'real_time_gold'},
        {'id': 'gold-history', 'icon': '📈', 'label': '金价', 'tab_id': 'gold'},
        {'id': 'volume', 'icon': '📉', 'label': '成交量', 'tab_id': 'seven_A'},
        {'id': 'timing', 'icon': '🔴', 'label': '分时', 'tab_id': 'A'},
        {'id': 'funds', 'icon': '💼', 'label': '基金', 'tab_id': 'fund'},
        {'id': 'sectors', 'icon': '🏢', 'label': '板块', 'tab_id': 'bk'},
        {'id': 'query', 'icon': '🔍', 'label': '查询', 'tab_id': 'select_fund'},
    ]

    html = '<aside class="sidebar-nav" id="sidebarNav">\n'
    html += '  <div class="sidebar-icons">\n'

    for i, section in enumerate(sections):
        active = ' active' if i == 6 else ''  # funds section active by default
        html += f'''    <button class="sidebar-icon{active}" data-section="{section['id']}" data-tab-id="{section['tab_id']}">
      <i class="icon">{section['icon']}</i>
      <span class="icon-label">{section['label']}</span>
    </button>\n'''

    html += '''    <button class="sidebar-toggle" id="sidebarToggle">
      <span>▶</span>
      <span class="toggle-text">展开</span>
    </button>
'''
    html += '  </div>\n'
    html += '</aside>\n'

    return html


def get_header_bar_html(section_title='自选基金'):
    """Generate header bar with section title and market status"""
    return f'''<header class="content-header">
  <div class="header-left">
    <h1 class="section-title" id="sectionTitle">{section_title}</h1>
    <span class="market-status">
      <span class="status-dot"></span>
      <span id="marketStatusText">市场开盘中</span>
    </span>
  </div>
  <div class="header-right">
    <span class="last-update" id="lastUpdate">更新于 --:--:--</span>
  </div>
</header>'''


def get_summary_bar_html():
    """Generate 4-column summary bar (populated by JavaScript)"""
    return '''<section class="summary-bar" id="summaryBar">
  <div class="summary-card">
    <div class="summary-label">总持仓</div>
    <div class="summary-value" id="summaryTotalValue">¥0.00</div>
    <div class="summary-change neutral" id="summaryTotalChange">--</div>
  </div>
  <div class="summary-card">
    <div class="summary-label">今日预估</div>
    <div class="summary-value" id="summaryEstGain">¥0.00</div>
    <div class="summary-change neutral" id="summaryEstChange">+0.00%</div>
  </div>
  <div class="summary-card">
    <div class="summary-label">已结算</div>
    <div class="summary-value" id="summaryActualGain">¥0.00</div>
    <div class="summary-change neutral" id="summaryActualChange">+0.00%</div>
  </div>
  <div class="summary-card">
    <div class="summary-label">累计收益</div>
    <div class="summary-value" id="summaryCumulativeGain">¥0.00</div>
    <div class="summary-change neutral">明细合计</div>
  </div>
  <div class="summary-card">
    <div class="summary-label">持仓数量</div>
    <div class="summary-value" id="summaryHoldCount">0 只</div>
    <div class="summary-change neutral">已标记</div>
  </div>
</section>'''


def generate_fund_row_html(fund_code, fund_data, is_held=True):
    """Generate a single fund row (replaces holdings cards)"""
    import html

    # Extract fund data
    name = fund_data.get('fund_name', '')
    sectors = fund_data.get('sectors', [])
    shares = fund_data.get('shares', 0)

    # Escape fund_code and name for safe HTML/JavaScript usage
    safe_code = html.escape(str(fund_code))
    safe_name = html.escape(str(name))

    # Build sector tags
    sector_tags = ''
    if sectors:
        # Display sectors with icon and gray text (like delete sector popup style)
        safe_sectors = html.escape(', '.join(str(s) for s in sectors))
        sector_tags += f'<span style="color: #8b949e; font-size: var(--font-size-sm);"> 🏷️ {safe_sectors}</span>'

    # Shares input (only for held funds) + 修改按钮打开份额弹窗
    shares_html = ''
    if is_held:
        shares_html = f'''<div class="metric metric-shares">
        <span class="metric-label">持仓金额</span>
        <input type="number" class="shares-input" id="shares_{safe_code}"
               value="{shares}" step="0.01" min="0"
               onchange="if(window.updateShares) window.updateShares('{safe_code}', this.value)">
        <button type="button" class="shares-button" data-fund-code="{safe_code}" title="修改持仓份额与成本"
                style="margin-left:6px;padding:4px 8px;font-size: var(--font-size-sm);border-radius:4px;cursor:pointer;background:var(--accent);color:#fff;border:none;">修改</button>
      </div>'''

    return f'''<div class="fund-row" data-code="{safe_code}">
  <div class="fund-row-main">
    <div class="fund-info">
      <div class="fund-code-name">
        <span class="fund-code">{safe_code}</span>
        <span class="fund-name">{safe_name}</span>
      </div>
      <div class="fund-tags">{sector_tags}</div>
    </div>
    <div class="fund-metrics" id="metrics_{safe_code}">
      <!-- Metrics populated by JavaScript -->
      <div class="metric"><span class="metric-label">净值</span><span class="metric-value">--</span></div>
      <div class="metric"><span class="metric-label">估值增长</span><span class="metric-value">--</span></div>
      <div class="metric"><span class="metric-label">日涨幅</span><span class="metric-value">--</span></div>
      <div class="metric"><span class="metric-label">连涨/跌</span><span class="metric-value">--</span></div>
      <div class="metric"><span class="metric-label">近30天</span><span class="metric-value">--</span></div>
      {shares_html}
    </div>
  </div>
  <div class="fund-row-actions">
    <button class="btn-icon" onclick="toggleFundExpand('{safe_code}')" title="展开/收起">
      <span>▼</span>
    </button>
  </div>
</div>'''


def generate_holdings_section_html(fund_map):
    """Generate Core Holdings section: funds with shares > 0"""
    held_funds = {code: data for code, data in fund_map.items() if (data.get('shares') or 0) > 0}

    html = '''<section class="content-section" id="holdingsSection">
  <div class="section-header">
    <h2 class="section-heading">
      <span class="heading-icon">💎</span>
      核心持仓
    </h2>
    <div class="section-meta">
      <span class="fund-count" id="holdingsCount">''' + str(len(held_funds)) + ''' 只基金</span>
    </div>
  </div>
  <div class="section-content" id="holdingsContent">'''

    for code, data in held_funds.items():
        html += generate_fund_row_html(code, data, is_held=True)

    if not held_funds:
        html += '<div class="empty-state">暂无持仓基金</div>'

    html += '  </div>\n</section>'
    return html


def generate_watchlist_section_html(fund_map):
    """Generate Market Watchlist section: funds with no shares"""
    watchlist_funds = {code: data for code, data in fund_map.items() if (data.get('shares') or 0) <= 0}

    html = '''<section class="content-section" id="watchlistSection">
  <div class="section-header">
    <h2 class="section-heading">
      <span class="heading-icon">📋</span>
      市场观察
    </h2>
    <div class="section-meta">
      <span class="fund-count" id="watchlistCount">''' + str(len(watchlist_funds)) + ''' 只基金</span>
    </div>
  </div>
  <div class="section-content" id="watchlistContent">'''

    for code, data in watchlist_funds.items():
        html += generate_fund_row_html(code, data, is_held=False)

    if not watchlist_funds:
        html += '<div class="empty-state">暂无观察基金</div>'

    html += '  </div>\n</section>'
    return html

