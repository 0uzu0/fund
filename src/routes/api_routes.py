# -*- coding: UTF-8 -*-
"""API 与 /fund/sector 路由。"""
import json
import tempfile
from datetime import datetime, timedelta, timezone

try:
    from zoneinfo import ZoneInfo
except ImportError:
    ZoneInfo = None

from flask import Blueprint, request, jsonify, send_file

from loguru import logger

from src.auth import login_required, get_current_user_id
from src.routes import get_db, get_get_lan_fund
from src.module_html import enhance_fund_tab_content
from src.html.fund import build_portfolio_table_rows

api_bp = Blueprint('api', __name__)


def _beijing_now():
    if ZoneInfo is not None:
        try:
            return datetime.now(ZoneInfo('Asia/Shanghai'))
        except Exception:
            pass
    return datetime.now(timezone.utc) + timedelta(hours=8)


# ---------- /fund/sector (GET) ----------
@api_bp.route('/fund/sector', methods=['GET'])
@login_required
def get_sector_funds():
    bk_id = request.args.get("bk_id")
    my_fund = get_get_lan_fund()()
    return my_fund.select_fund_html(bk_id=bk_id)


# ---------- Fund API ----------
@api_bp.route('/api/fund/add', methods=['POST'])
@login_required
def api_fund_add():
    try:
        data = request.json
        codes = data.get('codes', '')
        if not codes:
            return jsonify({'success': False, 'message': '请提供基金代码'})
        user_id = get_current_user_id()
        my_fund = get_get_lan_fund()(user_id)
        my_fund.add_code(codes)
        return jsonify({'success': True, 'message': f'已添加基金: {codes}'})
    except Exception as e:
        logger.error(f"添加基金失败: {e}")
        return jsonify({'success': False, 'message': f'添加失败: {str(e)}'})


@api_bp.route('/api/fund/delete', methods=['POST'])
@login_required
def api_fund_delete():
    try:
        data = request.json
        codes = data.get('codes', '')
        if not codes:
            return jsonify({'success': False, 'message': '请提供基金代码'})
        user_id = get_current_user_id()
        my_fund = get_get_lan_fund()(user_id)
        my_fund.delete_code(codes)
        return jsonify({'success': True, 'message': f'已删除基金: {codes}'})
    except Exception as e:
        logger.error(f"删除基金失败: {e}")
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'})


@api_bp.route('/api/fund/sector', methods=['POST'])
@login_required
def api_fund_sector():
    try:
        data = request.json
        codes = data.get('codes', '')
        sectors = data.get('sectors', [])
        if not codes:
            return jsonify({'success': False, 'message': '请提供基金代码'})
        if not sectors:
            return jsonify({'success': False, 'message': '请选择板块'})
        user_id = get_current_user_id()
        my_fund = get_get_lan_fund()(user_id)
        code_list = [c.strip() for c in codes.split(',')]
        my_fund.mark_fund_sector_web(code_list, sectors)
        return jsonify({'success': True, 'message': f'已标注板块: {codes} -> {", ".join(sectors)}'})
    except Exception as e:
        logger.error(f"标注板块失败: {e}")
        return jsonify({'success': False, 'message': f'操作失败: {str(e)}'})


@api_bp.route('/api/fund/sector/remove', methods=['POST'])
@login_required
def api_fund_sector_remove():
    try:
        data = request.json
        codes = data.get('codes', '')
        if not codes:
            return jsonify({'success': False, 'message': '请提供基金代码'})
        user_id = get_current_user_id()
        my_fund = get_get_lan_fund()(user_id)
        code_list = [c.strip() for c in codes.split(',')]
        my_fund.unmark_fund_sector_web(code_list)
        return jsonify({'success': True, 'message': f'已删除板块标记: {codes}'})
    except Exception as e:
        logger.error(f"删除板块标记失败: {e}")
        return jsonify({'success': False, 'message': f'操作失败: {str(e)}'})


@api_bp.route('/api/fund/upload', methods=['POST'])
@login_required
def api_fund_upload():
    db = get_db()
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': '未找到上传文件'})

        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': '未选择文件'})

        if not file.filename.endswith('.json'):
            return jsonify({'success': False, 'message': '只支持JSON文件'})

        content = file.read().decode('gbk')
        fund_map = json.loads(content)

        if not isinstance(fund_map, dict):
            return jsonify({'success': False, 'message': '文件格式错误：应为JSON对象'})

        for code, fund_data in fund_map.items():
            if not isinstance(fund_data, dict):
                return jsonify({'success': False, 'message': f'基金{code}数据格式错误'})
            if 'fund_key' not in fund_data or 'fund_name' not in fund_data:
                return jsonify({'success': False, 'message': f'基金{code}缺少必要字段'})
            if 'holding_units' not in fund_data:
                fund_data['holding_units'] = fund_data.get('shares', 0)
            if 'cost_per_unit' not in fund_data:
                fund_data['cost_per_unit'] = 1.0

        user_id = get_current_user_id()
        success = db.save_user_funds(user_id, fund_map)

        if success:
            return jsonify({'success': True, 'message': f'成功导入{len(fund_map)}个基金'})
        return jsonify({'success': False, 'message': '保存失败'})

    except json.JSONDecodeError:
        return jsonify({'success': False, 'message': 'JSON格式错误'})
    except Exception as e:
        logger.error(f"上传文件失败: {e}")
        return jsonify({'success': False, 'message': f'上传失败: {str(e)}'})


@api_bp.route('/api/fund/download', methods=['GET'])
@login_required
def api_fund_download():
    db = get_db()
    try:
        user_id = get_current_user_id()
        fund_map = db.get_user_funds(user_id)

        for code, data in fund_map.items():
            if not isinstance(data, dict):
                continue
            if 'holding_units' not in data:
                data['holding_units'] = data.get('shares', 0)
            if 'cost_per_unit' not in data:
                data['cost_per_unit'] = 1.0

        with tempfile.NamedTemporaryFile(mode='w', encoding='gbk', suffix='.json', delete=False) as f:
            json.dump(fund_map, f, ensure_ascii=False, indent=4)
            temp_path = f.name

        return send_file(
            temp_path,
            as_attachment=True,
            download_name='fund_map.json',
            mimetype='application/json'
        )

    except Exception as e:
        logger.error(f"下载文件失败: {e}")
        return jsonify({'success': False, 'message': f'下载失败: {str(e)}'})


@api_bp.route('/api/fund/shares', methods=['POST'])
@login_required
def api_fund_shares():
    db = get_db()
    try:
        data = request.json
        code = data.get('code', '').strip()
        holding_units = data.get('holding_units')
        cost_per_unit = data.get('cost_per_unit')
        shares = data.get('shares')
        record_op = data.get('record_op')
        amount = data.get('amount')
        trade_date = data.get('trade_date', '')
        period = data.get('period', '')
        fund_name = data.get('fund_name', '')

        if not code:
            return jsonify({'success': False, 'message': '请提供基金代码'})

        if holding_units is not None and cost_per_unit is not None:
            try:
                holding_units = float(holding_units)
                cost_per_unit = float(cost_per_unit)
                if holding_units < 0 or cost_per_unit < 0:
                    return jsonify({'success': False, 'message': '持有份额与持仓成本不能为负数'})
            except (ValueError, TypeError):
                return jsonify({'success': False, 'message': '持有份额或持仓成本格式错误'})
            shares = holding_units * cost_per_unit
        else:
            try:
                shares = float(shares) if shares is not None else 0
                if shares < 0:
                    return jsonify({'success': False, 'message': '份额不能为负数'})
            except (ValueError, TypeError):
                return jsonify({'success': False, 'message': '份额格式错误'})
            holding_units = shares
            cost_per_unit = 1.0

        user_id = get_current_user_id()
        fund_map = db.get_user_funds(user_id)
        if code not in fund_map:
            return jsonify({'success': False, 'message': '更新失败，基金不存在'})

        prev_holding_units = float(fund_map[code].get('holding_units', 0) or 0)
        prev_cost_per_unit = float(fund_map[code].get('cost_per_unit', 1) or 1)
        prev_fund_name = fund_map[code].get('fund_name', fund_name)

        success = db.update_fund_holding(user_id, code, holding_units, cost_per_unit)

        if success:
            if shares > 0:
                fund_map[code]['shares'] = shares
                fund_map[code]['holding_units'] = holding_units
                fund_map[code]['cost_per_unit'] = cost_per_unit
                db.save_user_funds(user_id, fund_map)
            if record_op in ('add', 'reduce') and amount is not None and trade_date:
                try:
                    amt = float(amount)
                    db.insert_position_record(
                        user_id, code, prev_fund_name or fund_map[code].get('fund_name', ''),
                        record_op, amt, trade_date.strip(), (period or '').strip(),
                        prev_holding_units, prev_cost_per_unit, holding_units, cost_per_unit
                    )
                except Exception as e:
                    logger.warning(f"Insert position record failed: {e}")
            return jsonify({'success': True, 'message': '已更新持仓金额', 'shares': shares, 'holding_units': holding_units, 'cost_per_unit': cost_per_unit})
        return jsonify({'success': False, 'message': '更新失败，基金不存在'})

    except Exception as e:
        logger.error(f"更新份额失败: {e}")
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'})


@api_bp.route('/api/time/beijing', methods=['GET'])
def api_time_beijing():
    now_dt = _beijing_now()
    return jsonify({
        'datetime': now_dt.isoformat(),
        'date': now_dt.strftime('%Y-%m-%d'),
        'time': now_dt.strftime('%H:%M:%S'),
        'hour': now_dt.hour,
        'minute': now_dt.minute,
        'is_before_930': now_dt.hour < 9 or (now_dt.hour == 9 and now_dt.minute < 30),
    })


@api_bp.route('/api/fund/data', methods=['GET'])
@login_required
def api_fund_data():
    db = get_db()
    try:
        user_id = get_current_user_id()
        fund_map = db.get_user_funds(user_id)
        return jsonify(fund_map)
    except Exception as e:
        logger.error(f"获取基金数据失败: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/api/fund/position-records', methods=['GET'])
@login_required
def api_fund_position_records():
    db = get_db()
    try:
        user_id = get_current_user_id()
        records = db.get_position_records(user_id)
        for rec in records:
            can_undo, _ = db.check_position_record_undo_deadline(rec)
            rec['can_undo'] = can_undo
        return jsonify({'success': True, 'records': records})
    except Exception as e:
        logger.error(f"获取持仓记录失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/api/fund/position-records/<int:record_id>', methods=['DELETE'])
@login_required
def api_fund_position_record_delete(record_id):
    db = get_db()
    try:
        user_id = get_current_user_id()
        success, message = db.delete_position_record_and_restore(user_id, record_id)
        if success:
            return jsonify({'success': True, 'message': message})
        return jsonify({'success': False, 'message': message}), 400
    except Exception as e:
        logger.error(f"撤销持仓记录失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ---------- 自选分组表格数据（按分组请求）----------
@api_bp.route('/api/portfolio/table', methods=['GET'])
@login_required
def api_portfolio_table():
    """按分组返回自选基金表格 tbody 行 HTML。query: group=<分组id>，不传或传默认分组 id 时返回默认（所有分组并集）数据。"""
    db = get_db()
    try:
        user_id = get_current_user_id()
        groups = db.get_fund_groups(user_id)
        default_group = db.get_or_create_default_group(user_id)
        if default_group:
            groups = [default_group] + [g for g in groups if g.get('id') != default_group['id']]
        default_gid = default_group['id'] if default_group else None

        group_param = request.args.get('group')
        if group_param is None or group_param == '':
            group_param = str(default_gid) if default_gid is not None else None
        else:
            try:
                group_param = str(int(group_param))
            except (ValueError, TypeError):
                group_param = str(default_gid) if default_gid is not None else None

        code_to_group_ids = {}
        for g in groups:
            gid = g.get('id')
            codes = g.get('fund_codes') or []
            if gid is not None:
                for code in codes:
                    code_to_group_ids.setdefault(str(code), []).append(gid)

        if group_param is None:
            codes = set()
        elif group_param == str(default_gid):
            codes = set()
            for g in groups:
                for code in (g.get('fund_codes') or []):
                    codes.add(str(code))
        else:
            codes = set()
            for g in groups:
                if str(g.get('id')) == group_param:
                    codes = set(str(c) for c in (g.get('fund_codes') or []))
                    break

        fund_map = db.get_user_funds(user_id)
        shares_map = {code: data.get('shares', 0) for code, data in fund_map.items()}

        my_fund = get_get_lan_fund()(user_id)
        full_result = my_fund.search_code(True)
        if not full_result:
            full_result = []
        result_rows = [r for r in full_result if len(r) > 0 and str(r[0]) in codes]

        is_default_group = group_param is not None and group_param == str(default_gid)
        with_op_col = not is_default_group
        with_position_col = is_default_group
        html = build_portfolio_table_rows(result_rows, code_to_group_ids, shares_map, with_op_col=with_op_col, with_position_col=with_position_col)
        resp = jsonify({'success': True, 'html': html, 'total': len(result_rows)})
        resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
        return resp
    except Exception as e:
        logger.error(f"获取分组表格数据失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ---------- 默认页基金列表（供新建分组添加联想）----------
@api_bp.route('/api/portfolio/fund-list', methods=['GET'])
@login_required
def api_portfolio_fund_list():
    """返回默认页所有基金列表（各分组并集），用于添加时的联想。返回 [{ code, name }, ...]。"""
    db = get_db()
    try:
        user_id = get_current_user_id()
        groups = db.get_fund_groups(user_id)
        default_group = db.get_or_create_default_group(user_id)
        if default_group:
            groups = [default_group] + [g for g in groups if g.get('id') != default_group['id']]
        default_gid = default_group['id'] if default_group else None
        codes = set()
        for g in groups:
            for code in (g.get('fund_codes') or []):
                codes.add(str(code))
        fund_map = db.get_user_funds(user_id)
        funds = []
        for code in sorted(codes):
            name = (fund_map.get(code) or {}).get('fund_name') or ('基金' + code)
            funds.append({'code': code, 'name': name})
        return jsonify({'success': True, 'funds': funds})
    except Exception as e:
        logger.error(f"获取默认页基金列表失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ---------- Fund Groups（自定义分组）API ----------
@api_bp.route('/api/fund/groups', methods=['GET'])
@login_required
def api_fund_groups_list():
    db = get_db()
    try:
        user_id = get_current_user_id()
        groups = db.get_fund_groups(user_id)
        return jsonify({'success': True, 'groups': groups})
    except Exception as e:
        logger.error(f"获取分组列表失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/api/fund/groups', methods=['POST'])
@login_required
def api_fund_groups_create():
    """新建分组：仅接受 name，fund_codes 固定为空，页面默认为空数据。"""
    db = get_db()
    try:
        user_id = get_current_user_id()
        data = request.json or {}
        name = (data.get('name') or '').strip()
        success, message, group_id = db.create_fund_group(user_id, name)
        if success:
            return jsonify({'success': True, 'message': message, 'group_id': group_id})
        return jsonify({'success': False, 'message': message}), 400
    except Exception as e:
        logger.error(f"创建分组失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/api/fund/groups/<int:group_id>', methods=['GET'])
@login_required
def api_fund_group_get(group_id):
    db = get_db()
    try:
        user_id = get_current_user_id()
        group = db.get_fund_group(user_id, group_id)
        if not group:
            return jsonify({'success': False, 'message': '分组不存在'}), 404
        return jsonify({'success': True, 'group': group})
    except Exception as e:
        logger.error(f"获取分组失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/api/fund/groups/<int:group_id>', methods=['PUT'])
@login_required
def api_fund_group_update(group_id):
    db = get_db()
    try:
        user_id = get_current_user_id()
        data = request.json or {}
        name = data.get('name')
        fund_codes = data.get('fund_codes')
        if name is None and fund_codes is None:
            return jsonify({'success': False, 'message': '请提供 name 或 fund_codes'}), 400
        success, message = db.update_fund_group(user_id, group_id, name=name, fund_codes=fund_codes)
        if success:
            return jsonify({'success': True, 'message': message})
        return jsonify({'success': False, 'message': message}), 400
    except Exception as e:
        logger.error(f"更新分组失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/api/fund/groups/<int:group_id>', methods=['DELETE'])
@login_required
def api_fund_group_delete(group_id):
    db = get_db()
    try:
        user_id = get_current_user_id()
        success, message = db.delete_fund_group(user_id, group_id)
        if success:
            return jsonify({'success': True, 'message': message})
        return jsonify({'success': False, 'message': message}), 400
    except Exception as e:
        logger.error(f"删除分组失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/api/fund/groups/<int:group_id>/funds', methods=['POST'])
@login_required
def api_fund_group_add_fund(group_id):
    db = get_db()
    try:
        user_id = get_current_user_id()
        data = request.json or {}
        code = (data.get('code') or data.get('fund_code') or '').strip()
        if not code:
            return jsonify({'success': False, 'message': '请提供基金代码'}), 400
        fund_map = db.get_user_funds(user_id)
        if code not in fund_map:
            my_fund = get_get_lan_fund()(user_id)
            my_fund.add_code(code)
        success, message = db.add_fund_to_group(user_id, group_id, code)
        if not success:
            return jsonify({'success': False, 'message': message}), 400
        default_gid = db.get_default_group_id(user_id)
        if default_gid is not None and default_gid != group_id:
            db.add_fund_to_group(user_id, default_gid, code)
        return jsonify({'success': True, 'message': message})
    except Exception as e:
        logger.error(f"分组添加基金失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/api/fund/groups/<int:group_id>/funds/<code>', methods=['DELETE'])
@login_required
def api_fund_group_remove_fund(group_id, code):
    db = get_db()
    try:
        user_id = get_current_user_id()
        success, message = db.remove_fund_from_group(user_id, group_id, code)
        if not success:
            return jsonify({'success': False, 'message': message}), 400
        default_gid = db.get_default_group_id(user_id)
        if default_gid is not None and default_gid != group_id:
            db.remove_fund_from_group(user_id, default_gid, code)
        return jsonify({'success': True, 'message': message})
    except Exception as e:
        logger.error(f"分组移除基金失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/api/client/fund/config', methods=['POST'])
def api_client_fund_config():
    db = get_db()
    try:
        data = request.json
        username = data.get('username', '').strip()
        password = data.get('password', '')
        action = data.get('action', 'get')

        if not username or not password:
            return jsonify({'success': False, 'message': '请提供用户名和密码'}), 400

        success, user_id = db.verify_password(username, password)
        if not success:
            return jsonify({'success': False, 'message': '用户名或密码错误'}), 401

        if action == 'get':
            fund_map = db.get_user_funds(user_id)
            return jsonify({'success': True, 'fund_map': fund_map})

        elif action == 'push':
            fund_map = data.get('fund_map')
            if not isinstance(fund_map, dict):
                return jsonify({'success': False, 'message': '配置格式错误'}), 400

            if db.save_user_funds(user_id, fund_map):
                return jsonify({'success': True, 'message': '配置已同步'})
            return jsonify({'success': False, 'message': '保存失败'}), 500

        return jsonify({'success': False, 'message': '无效的操作类型'}), 400

    except Exception as e:
        logger.error(f"客户端配置同步失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/api/tab/<tab_id>', methods=['GET'])
@login_required
def api_get_tab_data(tab_id):
    db = get_db()
    try:
        user_id = get_current_user_id()
        my_fund = get_get_lan_fund()(user_id)

        tab_functions = {
            'kx': my_fund.kx_html,
            'marker': my_fund.marker_html,
            'real_time_gold': my_fund.real_time_gold_html,
            'gold': my_fund.gold_html,
            'seven_A': my_fund.seven_A_html,
            'A': my_fund.A_html,
            'fund': my_fund.fund_html,
            'bk': my_fund.bk_html,
            'select_fund': my_fund.select_fund_html,
        }

        if tab_id not in tab_functions:
            return jsonify({'success': False, 'message': f'未知的tab ID: {tab_id}'}), 404

        content = tab_functions[tab_id]()

        if tab_id == 'fund':
            fund_map = db.get_user_funds(user_id)
            shares_map = {code: data.get('shares', 0) for code, data in fund_map.items()}
            content = enhance_fund_tab_content(content, shares_map)

        return jsonify({'success': True, 'content': content})
    except Exception as e:
        logger.error(f"加载tab {tab_id} 数据失败: {e}")
        return jsonify({'success': False, 'message': f'数据加载失败: {str(e)}'}), 500


@api_bp.route('/api/timing', methods=['GET'])
@login_required
def api_timing_data():
    try:
        user_id = get_current_user_id()
        my_fund = get_get_lan_fund()(user_id)
        data = my_fund.get_timing_chart_data()
        if data['prices']:
            data['current_price'] = data['prices'][-1]
            data['change'] = data['change_amounts'][-1] if data.get('change_amounts') else 0
            data['change_pct'] = data['change_pcts'][-1] if data.get('change_pcts') else 0
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        logger.error(f"获取上证分时数据失败: {e}")
        return jsonify({'success': False, 'message': f'数据加载失败: {str(e)}'}), 500


@api_bp.route('/api/news/7x24', methods=['GET'])
@login_required
def api_news_7x24():
    try:
        my_fund = get_get_lan_fund()(get_current_user_id())
        result = my_fund.kx(True)
        news_items = []
        if result:
            import datetime as dt
            for item in result:
                try:
                    title = item.get('title', '')
                    if not title and 'content' in item and 'items' in item['content']:
                        content_items = item['content'].get('items', [])
                        if content_items:
                            title = content_items[0].get('data', '')
                    publish_time = item.get('publish_time', '')
                    if publish_time:
                        try:
                            publish_time = dt.datetime.fromtimestamp(int(publish_time)).strftime("%H:%M:%S")
                        except Exception:
                            publish_time = ''
                    evaluate = item.get('evaluate', '')
                    news_items.append({
                        'time': publish_time,
                        'content': title,
                        'source': evaluate if evaluate else ''
                    })
                except Exception as e:
                    logger.debug(f"Error processing news item: {e}")
                    continue
        return jsonify({'success': True, 'data': news_items})
    except Exception as e:
        logger.error(f"获取7*24快讯失败: {e}")
        return jsonify({'success': False, 'message': f'数据加载失败: {str(e)}'}), 500


@api_bp.route('/api/indices/global', methods=['GET'])
@login_required
def api_indices_global():
    try:
        my_fund = get_get_lan_fund()(get_current_user_id())
        result = my_fund.get_market_info(True)
        indices = []
        if result:
            for item in result:
                if len(item) >= 3:
                    change_str = (item[2] or "0").replace('%', '').replace('\033[1;31m', '').replace('\033[1;32m', '')
                    change = float(change_str) if change_str else 0
                    indices.append({
                        'name': item[0],
                        'value': item[1],
                        'change': change_str + '%',
                        'change_pct': change
                    })
        return jsonify({'success': True, 'data': indices})
    except Exception as e:
        logger.error(f"获取全球指数失败: {e}")
        return jsonify({'success': False, 'message': f'数据加载失败: {str(e)}'}), 500


@api_bp.route('/api/indices/volume', methods=['GET'])
@login_required
def api_indices_volume():
    try:
        my_fund = get_get_lan_fund()(get_current_user_id())
        data = my_fund.get_volume_chart_data()
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        logger.error(f"获取成交量趋势失败: {e}")
        return jsonify({'success': False, 'message': f'数据加载失败: {str(e)}'}), 500


@api_bp.route('/api/gold/real-time', methods=['GET'])
@login_required
def api_gold_realtime():
    try:
        my_fund = get_get_lan_fund()(get_current_user_id())
        result = my_fund.real_time_gold(True)
        gold_data = []
        gold_names = ['中国黄金', '周大福', '周生生']
        if result and len(result) >= 3:
            for i, gold_type_data in enumerate(result):
                if len(gold_type_data) >= 4:
                    gold_data.append({
                        'name': gold_type_data[0] if gold_type_data else gold_names[i],
                        'price': gold_type_data[1] if len(gold_type_data) > 1 else '',
                        'change_amount': gold_type_data[2] if len(gold_type_data) > 2 else '',
                        'change_pct': gold_type_data[3] if len(gold_type_data) > 3 else '',
                        'open_price': gold_type_data[4] if len(gold_type_data) > 4 else '',
                        'high_price': gold_type_data[5] if len(gold_type_data) > 5 else '',
                        'low_price': gold_type_data[6] if len(gold_type_data) > 6 else '',
                        'prev_close': gold_type_data[7] if len(gold_type_data) > 7 else '',
                        'update_time': gold_type_data[8] if len(gold_type_data) > 8 else '',
                        'unit': gold_type_data[9] if len(gold_type_data) > 9 else ''
                    })
        return jsonify({'success': True, 'data': gold_data})
    except Exception as e:
        logger.error(f"获取实时金价失败: {e}")
        return jsonify({'success': False, 'message': f'数据加载失败: {str(e)}'}), 500


@api_bp.route('/api/gold/history', methods=['GET'])
@login_required
def api_gold_history():
    try:
        my_fund = get_get_lan_fund()(get_current_user_id())
        result = my_fund.gold(True)
        gold_history = []
        if result:
            for item in result:
                if len(item) >= 3:
                    gold_history.append({
                        'date': item[0],
                        'china_gold_price': item[1],
                        'chow_tai_fook_price': item[2],
                        'china_gold_change': item[3] if len(item) > 3 else '',
                        'chow_tai_fook_change': item[4] if len(item) > 4 else ''
                    })
        return jsonify({'success': True, 'data': gold_history})
    except Exception as e:
        logger.error(f"获取历史金价失败: {e}")
        return jsonify({'success': False, 'message': f'数据加载失败: {str(e)}'}), 500


@api_bp.route('/api/sectors', methods=['GET'])
@login_required
def api_sectors():
    try:
        import requests
        url = "https://push2.eastmoney.com/api/qt/clist/get"
        params = {
            "cb": "", "fid": "f62", "po": "1", "pz": "100", "pn": "1", "np": "1",
            "fltt": "2", "invt": "2", "ut": "8dec03ba335b81bf4ebdf7b29ec27d15",
            "fs": "m:90 t:2",
            "fields": "f12,f14,f2,f3,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,f204,f205,f124,f1,f13"
        }
        response = requests.get(url, params=params, timeout=10, verify=False)
        if str(response.json().get("data")):
            data = response.json()["data"]
            sectors = []
            for bk in data["diff"]:
                sectors.append({
                    'code': bk["f12"],
                    'name': bk["f14"],
                    'change': str(bk["f3"]) + "%",
                    'main_inflow': str(round(bk["f62"] / 100000000, 2)) + "亿",
                    'main_inflow_pct': str(round(bk["f184"], 2)) + "%",
                    'small_inflow': str(round(bk["f84"] / 100000000, 2)) + "亿",
                    'small_inflow_pct': str(round(bk["f87"], 2)) + "%"
                })
            sectors = sorted(
                sectors,
                key=lambda x: float(x['change'].replace("%", "")) if x.get('main_inflow_pct') != "N/A" else -99,
                reverse=True
            )
        else:
            sectors = []
        return jsonify({'success': True, 'data': sectors})
    except Exception as e:
        logger.error(f"获取行业板块失败: {e}")
        return jsonify({'success': False, 'message': f'数据加载失败: {str(e)}'}), 500


@api_bp.route('/api/fund/list', methods=['GET'])
@login_required
def api_fund_list():
    db = get_db()
    try:
        user_id = get_current_user_id()
        my_fund = get_get_lan_fund()(user_id)
        fund_map = db.get_user_funds(user_id)
        funds = []
        for code, data in fund_map.items():
            fund_info = my_fund.CACHE_MAP.get(code, {})
            funds.append({
                'code': code,
                'name': data.get('fund_name', fund_info.get('name', '')),
                'shares': data.get('shares', 0),
                'is_hold': data.get('is_hold', False),
                'sectors': data.get('sectors', []),
                'net_value': fund_info.get('net_value', 0),
                'day_growth': fund_info.get('day_growth', 0),
                'estimated_growth': fund_info.get('estimated_growth', 0)
            })
        return jsonify({'success': True, 'data': funds})
    except Exception as e:
        logger.error(f"获取基金列表失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/api/sector/<sector_id>', methods=['GET'])
@login_required
def api_sector_funds(sector_id):
    try:
        my_fund = get_get_lan_fund()(get_current_user_id())
        result = my_fund.select_fund(bk_id=sector_id, is_return=True)
        funds = []
        if result:
            for item in result:
                if len(item) >= 5:
                    funds.append({
                        'code': item[0],
                        'name': item[1],
                        'net_value': item[2],
                        'day_growth': item[3],
                        'estimated_growth': item[4] if len(item) > 4 else ''
                    })
        return jsonify({'success': True, 'data': funds})
    except Exception as e:
        logger.error(f"获取板块基金失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/api/fund/chart-data')
@login_required
def api_fund_chart_data():
    db = get_db()
    fund_code = request.args.get('code')
    if not fund_code:
        return jsonify({'error': 'Missing fund code'}), 400
    user_id = get_current_user_id()
    user_funds = db.get_user_funds(user_id)
    if fund_code not in user_funds:
        return jsonify({'error': 'Fund not in user list'}), 400
    fund_data = {
        'fund_key': user_funds[fund_code]['fund_key'],
        'fund_name': user_funds[fund_code]['fund_name']
    }
    my_fund = get_get_lan_fund()(user_id)
    chart_data = my_fund.get_fund_chart_data(fund_code, fund_data)
    return jsonify({
        'chart_data': chart_data,
        'fund_info': {'code': fund_code, 'name': fund_data['fund_name']}
    })


@api_bp.route('/api/fund/chart-default', methods=['POST'])
@login_required
def api_fund_chart_default():
    db = get_db()
    data = request.json
    fund_code = data.get('fund_code')
    if not fund_code:
        return jsonify({'error': 'Missing fund code'}), 400
    user_id = get_current_user_id()
    user_funds = db.get_user_funds(user_id)
    if fund_code not in user_funds:
        return jsonify({'error': 'Fund not in user list'}), 400
    db.update_chart_default(user_id, fund_code)
    return jsonify({'success': True})
