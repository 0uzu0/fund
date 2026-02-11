# -*- coding: UTF-8 -*-

import json
import sqlite3
from datetime import datetime, timedelta

import bcrypt
from loguru import logger


class Database:
    def __init__(self, db_path="cache/fund_data.db"):
        self.db_path = db_path
        self.init_database()

    def get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 返回字典格式
        return conn

    def init_database(self):
        """初始化数据库表"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # 创建用户表
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS users
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           username
                           TEXT
                           UNIQUE
                           NOT
                           NULL,
                           password_hash
                           TEXT
                           NOT
                           NULL,
                           created_at
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP
                       )
                       ''')

        # 创建用户基金表
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS user_funds
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           user_id
                           INTEGER
                           NOT
                           NULL,
                           fund_code
                           TEXT
                           NOT
                           NULL,
                           fund_key
                           TEXT
                           NOT
                           NULL,
                           fund_name
                           TEXT
                           NOT
                           NULL,
                           is_hold
                           BOOLEAN
                           DEFAULT
                           0,
                           shares
                           REAL
                           DEFAULT
                           0,
                           sectors
                           TEXT,
                           FOREIGN
                           KEY
                       (
                           user_id
                       ) REFERENCES users
                       (
                           id
                       ) ON DELETE CASCADE,
                           UNIQUE
                       (
                           user_id,
                           fund_code
                       )
                           )
                       ''')

        # 检查并添加chart_default字段
        cursor.execute("PRAGMA table_info(user_funds)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'chart_default' not in columns:
            try:
                cursor.execute('ALTER TABLE user_funds ADD COLUMN chart_default BOOLEAN DEFAULT 0')
                logger.debug("Added chart_default column to user_funds table")
            except Exception as e:
                if "duplicate column" not in str(e).lower():
                    logger.warning(f"Failed to add chart_default column: {e}")

        # 持有份额、持仓成本（持仓份额 = 持有份额 × 持仓成本）
        for col_name, col_def in [('holding_units', 'REAL DEFAULT 0'), ('cost_per_unit', 'REAL DEFAULT 1')]:
            if col_name not in columns:
                try:
                    cursor.execute(f'ALTER TABLE user_funds ADD COLUMN {col_name} {col_def}')
                    logger.debug(f"Added {col_name} column to user_funds table")
                except Exception as e:
                    if "duplicate column" not in str(e).lower():
                        logger.warning(f"Failed to add {col_name} column: {e}")

        # 迁移：旧数据将 shares 写入 holding_units，cost_per_unit 置为 1
        cursor.execute("PRAGMA table_info(user_funds)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'holding_units' in columns and 'cost_per_unit' in columns:
            cursor.execute('''
                UPDATE user_funds SET holding_units = shares, cost_per_unit = 1
                WHERE holding_units = 0 AND shares > 0
            ''')
            if cursor.rowcount:
                logger.debug("Migrated shares to holding_units/cost_per_unit")

        # 持仓记录表（加减仓记录，删除即撤销）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS position_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                fund_code TEXT NOT NULL,
                fund_name TEXT,
                op TEXT NOT NULL,
                amount REAL NOT NULL,
                trade_date TEXT NOT NULL,
                period TEXT,
                prev_holding_units REAL NOT NULL,
                prev_cost_per_unit REAL NOT NULL,
                new_holding_units REAL NOT NULL,
                new_cost_per_unit REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')

        # 用户表增加 is_admin 字段（迁移）
        cursor.execute("PRAGMA table_info(users)")
        user_cols = [c[1] for c in cursor.fetchall()]
        if 'is_admin' not in user_cols:
            try:
                cursor.execute('ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0')
                logger.debug("Added is_admin column to users table")
            except Exception as e:
                if "duplicate column" not in str(e).lower():
                    logger.warning(f"Failed to add is_admin column: {e}")
        conn.commit()
        conn.close()
        logger.debug("Database initialized successfully")
        self._ensure_admin_user()

    def _ensure_admin_user(self):
        """确保默认管理员账号 admin/admin 存在（不存在则创建）；兼容旧库 zuohao 设为管理员"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE is_admin = 1 LIMIT 1')
        has_admin = cursor.fetchone() is not None
        if has_admin:
            conn.close()
            return
        # 若存在 zuohao，将其设为管理员
        cursor.execute('SELECT id FROM users WHERE username = ?', ('zuohao',))
        zuohao = cursor.fetchone()
        if zuohao:
            cursor.execute('UPDATE users SET is_admin = 1 WHERE id = ?', (zuohao['id'],))
            conn.commit()
            conn.close()
            logger.info("Set existing user zuohao as admin")
            return
        conn.close()
        if self.get_user_by_username('admin'):
            return
        success, msg, _ = self.create_user('admin', 'admin', is_admin=True)
        if success:
            logger.info("Default admin user created: admin/admin")
        else:
            logger.warning(f"Admin user ensure skipped: {msg}")

    # ==================== User Operations ====================

    def create_user(self, username, password, is_admin=False):
        """创建新用户（新增用户默认为普通用户）

        Args:
            username: 用户名
            password: 明文密码
            is_admin: 是否管理员，默认 False

        Returns:
            (success: bool, message: str, user_id: int or None)
        """
        try:
            # 检查用户名是否已存在
            if self.get_user_by_username(username):
                return False, "用户名已存在", None

            # 生成密码哈希
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12))

            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)',
                (username, password_hash, 1 if is_admin else 0)
            )
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()

            logger.info(f"User created successfully: {username} (ID: {user_id})")
            return True, "注册成功", user_id

        except Exception as e:
            logger.error(f"Failed to create user {username}: {e}")
            return False, f"注册失败: {str(e)}", None

    def get_user_by_username(self, username):
        """根据用户名获取用户信息

        Returns:
            dict or None
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            row = cursor.fetchone()
            conn.close()

            if row:
                return dict(row)
            return None

        except Exception as e:
            logger.error(f"Failed to get user {username}: {e}")
            return None

    def get_user_by_id(self, user_id):
        """根据用户 id 获取用户信息。Returns: dict or None"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            conn.close()
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"Get user by id failed: {e}")
            return None

    def list_users(self):
        """列出所有用户（id, username, is_admin, created_at），按 id 升序"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT id, username, is_admin, created_at FROM users ORDER BY id ASC')
            rows = cursor.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"List users failed: {e}")
            return []

    def delete_user(self, user_id=None, username=None):
        """删除用户（按 id 或 username）。禁止删除管理员（is_admin=1）。"""
        if user_id is None and not username:
            return False, "请指定用户 id 或用户名"
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            if user_id is not None:
                cursor.execute('SELECT id, username, is_admin FROM users WHERE id = ?', (user_id,))
            else:
                cursor.execute('SELECT id, username, is_admin FROM users WHERE username = ?', (username,))
            row = cursor.fetchone()
            if not row:
                conn.close()
                return False, "用户不存在"
            uid, uname = row['id'], row['username']
            is_admin = row.get('is_admin', 0)
            if is_admin:
                conn.close()
                return False, "不能删除管理员账号"
            cursor.execute('DELETE FROM users WHERE id = ?', (uid,))
            conn.commit()
            conn.close()
            logger.info(f"User deleted: {uname} (ID: {uid})")
            return True, f"已删除用户 {uname}"
        except Exception as e:
            logger.error(f"Delete user failed: {e}")
            return False, str(e)

    def update_user_credentials(self, user_id, new_username=None, new_password=None):
        """修改当前用户的用户名和/或密码（仅管理员可改自己）。Returns: (success: bool, message: str)"""
        if new_username is None and new_password is None:
            return False, "请提供新用户名或新密码"
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False, "用户不存在"
            conn = self.get_connection()
            cursor = conn.cursor()
            if new_username is not None:
                new_username = new_username.strip()
                if len(new_username) < 3 or len(new_username) > 20:
                    conn.close()
                    return False, "用户名长度应为 3–20 个字符"
                cursor.execute('SELECT id FROM users WHERE username = ? AND id != ?', (new_username, user_id))
                if cursor.fetchone():
                    conn.close()
                    return False, "该用户名已被使用"
                cursor.execute('UPDATE users SET username = ? WHERE id = ?', (new_username, user_id))
            if new_password is not None:
                if len(new_password) < 6:
                    conn.close()
                    return False, "密码长度至少为 6 个字符"
                password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt(rounds=12))
                cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (password_hash, user_id))
            conn.commit()
            conn.close()
            logger.info(f"User credentials updated: id={user_id}")
            return True, "修改成功"
        except Exception as e:
            logger.error(f"Update user credentials failed: {e}")
            return False, str(e)

    def verify_password(self, username, password):
        """验证用户密码

        Returns:
            (success: bool, user_id: int or None)
        """
        try:
            user = self.get_user_by_username(username)
            if not user:
                return False, None

            password_hash = user['password_hash']
            if isinstance(password_hash, str):
                password_hash = password_hash.encode('utf-8')

            if bcrypt.checkpw(password.encode('utf-8'), password_hash):
                return True, user['id']
            else:
                return False, None

        except Exception as e:
            logger.error(f"Failed to verify password for {username}: {e}")
            return False, None

    # ==================== Fund Operations ====================

    def get_user_funds(self, user_id):
        """获取用户的所有基金数据

        Returns:
            dict: 格式与 fund_map.json 相同
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM user_funds WHERE user_id = ?', (user_id,))
            rows = cursor.fetchall()
            conn.close()

            fund_map = {}
            col_names = list(rows[0].keys()) if rows else []
            for row in rows:
                fund_code = row['fund_code']
                sectors = json.loads(row['sectors']) if row['sectors'] else []
                shares_raw = float(row['shares']) if row['shares'] else 0
                holding_units = None
                cost_per_unit = None
                if 'holding_units' in col_names and row['holding_units'] is not None:
                    holding_units = float(row['holding_units'])
                if 'cost_per_unit' in col_names and row['cost_per_unit'] is not None:
                    cost_per_unit = float(row['cost_per_unit'])
                # 持仓份额 = 持有份额 × 持仓成本；旧数据无新列时用 shares 作为持有份额、成本为 1
                if holding_units is not None and cost_per_unit is not None:
                    shares = holding_units * cost_per_unit
                else:
                    shares = shares_raw
                    holding_units = shares_raw
                    cost_per_unit = 1.0

                fund_map[fund_code] = {
                    'fund_key': row['fund_key'],
                    'fund_name': row['fund_name'],
                    'is_hold': bool(row['is_hold']),
                    'shares': shares,
                    'holding_units': holding_units,
                    'cost_per_unit': cost_per_unit,
                    'sectors': sectors,
                }

            return fund_map

        except Exception as e:
            logger.error(f"Failed to get funds for user {user_id}: {e}")
            return {}

    def save_user_funds(self, user_id, fund_map):
        """保存用户的所有基金数据（完全替换）

        Args:
            user_id: 用户ID
            fund_map: dict, 格式与 fund_map.json 相同
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # 删除用户现有的所有基金数据
            cursor.execute('DELETE FROM user_funds WHERE user_id = ?', (user_id,))

            cursor.execute("PRAGMA table_info(user_funds)")
            columns = [col[1] for col in cursor.fetchall()]
            has_holding = 'holding_units' in columns and 'cost_per_unit' in columns

            for fund_code, fund_data in fund_map.items():
                sectors_json = json.dumps(fund_data.get('sectors', []), ensure_ascii=False)
                shares_val = fund_data.get('shares', 0)
                holding_units_val = fund_data.get('holding_units', shares_val)
                cost_per_unit_val = fund_data.get('cost_per_unit', 1.0)
                if has_holding:
                    cursor.execute('''
                        INSERT INTO user_funds
                            (user_id, fund_code, fund_key, fund_name, is_hold, shares, holding_units, cost_per_unit, sectors)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        user_id, fund_code, fund_data['fund_key'], fund_data['fund_name'],
                        1 if fund_data.get('is_hold', False) else 0,
                        holding_units_val * cost_per_unit_val,
                        holding_units_val, cost_per_unit_val, sectors_json
                    ))
                else:
                    cursor.execute('''
                        INSERT INTO user_funds
                            (user_id, fund_code, fund_key, fund_name, is_hold, shares, sectors)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        user_id, fund_code, fund_data['fund_key'], fund_data['fund_name'],
                        1 if fund_data.get('is_hold', False) else 0, shares_val, sectors_json
                    ))

            conn.commit()
            conn.close()
            logger.debug(f"Saved {len(fund_map)} funds for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to save funds for user {user_id}: {e}")
            return False

    def update_fund_shares(self, user_id, fund_code, shares):
        """更新基金持仓份额（兼容旧接口：直接写份额，等价于 holding_units=shares, cost_per_unit=1）"""
        return self.update_fund_holding(user_id, fund_code, shares, 1.0)

    def update_fund_holding(self, user_id, fund_code, holding_units, cost_per_unit):
        """更新基金持有份额与持仓成本，持仓份额 = 持有份额 × 持仓成本

        Args:
            user_id: 用户ID
            fund_code: 基金代码
            holding_units: 持有份额
            cost_per_unit: 持仓成本（每份成本）
        """
        try:
            shares = holding_units * cost_per_unit
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(user_funds)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'holding_units' in columns and 'cost_per_unit' in columns:
                cursor.execute('''
                    UPDATE user_funds
                    SET shares = ?, holding_units = ?, cost_per_unit = ?
                    WHERE user_id = ? AND fund_code = ?
                ''', (shares, holding_units, cost_per_unit, user_id, fund_code))
            else:
                cursor.execute('''
                    UPDATE user_funds SET shares = ?
                    WHERE user_id = ? AND fund_code = ?
                ''', (shares, user_id, fund_code))
            conn.commit()
            affected_rows = cursor.rowcount
            conn.close()
            if affected_rows > 0:
                logger.debug(f"Updated holding for user {user_id}, fund {fund_code}: holding_units={holding_units}, cost_per_unit={cost_per_unit}, shares={shares}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to update holding: {e}")
            return False

    def insert_position_record(self, user_id, fund_code, fund_name, op, amount, trade_date, period,
                                prev_holding_units, prev_cost_per_unit, new_holding_units, new_cost_per_unit):
        """插入一条加减仓记录。op 为 'add' 或 'reduce'。"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO position_records
                (user_id, fund_code, fund_name, op, amount, trade_date, period,
                 prev_holding_units, prev_cost_per_unit, new_holding_units, new_cost_per_unit)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, fund_code, fund_name or '', op, amount, trade_date, period or '',
                  prev_holding_units, prev_cost_per_unit, new_holding_units, new_cost_per_unit))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Insert position record failed: {e}")
            return False

    def get_position_records(self, user_id):
        """获取用户的持仓记录列表，按创建时间倒序。"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, fund_code, fund_name, op, amount, trade_date, period,
                       prev_holding_units, prev_cost_per_unit, new_holding_units, new_cost_per_unit, created_at
                FROM position_records WHERE user_id = ? ORDER BY created_at DESC
            ''', (user_id,))
            rows = cursor.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Get position records failed: {e}")
            return []

    def check_position_record_undo_deadline(self, record, now=None):
        """判断该条加减仓记录是否仍可撤销。
        规则：当日3点前操作须在当日15:00前撤销；当日3点后操作须在次日15:00前撤销。
        返回 (can_undo: bool, message: str)。"""
        if now is None:
            now = datetime.now()
        trade_date = record.get('trade_date') or ''
        if not trade_date.strip():
            return True, ''
        try:
            d = datetime.strptime(trade_date.strip(), '%Y-%m-%d')
        except ValueError:
            return False, '记录日期格式错误'
        period = (record.get('period') or '').strip().lower()
        if period == 'after15':
            deadline = (d + timedelta(days=1)).replace(hour=15, minute=0, second=0, microsecond=0)
        else:
            deadline = d.replace(hour=15, minute=0, second=0, microsecond=0)
        if now >= deadline:
            return False, '已过撤销截止时间（当日15:00前操作须在当日15:00前撤销，当日15:00后操作须在次日15:00前撤销），无法撤销'
        return True, ''

    def delete_position_record_and_restore(self, user_id, record_id):
        """删除一条持仓记录并撤销该次操作：将对应基金恢复为 prev_holding_units / prev_cost_per_unit。
        超过撤销截止时间则不允许撤销。返回 (success: bool, message: str)。"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM position_records WHERE id = ? AND user_id = ?', (record_id, user_id))
            row = cursor.fetchone()
            if not row:
                conn.close()
                return False, '记录不存在或无权操作'
            rec = dict(row)
            can_undo, msg = self.check_position_record_undo_deadline(rec)
            if not can_undo:
                conn.close()
                return False, msg
            fund_code = rec['fund_code']
            prev_units = float(rec['prev_holding_units'])
            prev_cost = float(rec['prev_cost_per_unit'])
            shares = prev_units * prev_cost
            cursor.execute("PRAGMA table_info(user_funds)")
            columns = [c[1] for c in cursor.fetchall()]
            if 'holding_units' in columns and 'cost_per_unit' in columns:
                cursor.execute('''
                    UPDATE user_funds SET shares = ?, holding_units = ?, cost_per_unit = ?
                    WHERE user_id = ? AND fund_code = ?
                ''', (shares, prev_units, prev_cost, user_id, fund_code))
            else:
                cursor.execute('UPDATE user_funds SET shares = ? WHERE user_id = ? AND fund_code = ?',
                               (shares, user_id, fund_code))
            if cursor.rowcount == 0:
                conn.close()
                return False, '基金不存在，无法恢复'
            cursor.execute('DELETE FROM position_records WHERE id = ?', (record_id,))
            conn.commit()
            conn.close()
            return True, '已撤销并恢复持仓'
        except Exception as e:
            logger.error(f"Delete position record and restore failed: {e}")
            return False, str(e)

    def add_fund(self, user_id, fund_code, fund_key, fund_name):
        """添加基金到用户列表

        Returns:
            bool: 是否成功
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR REPLACE INTO user_funds
                (user_id, fund_code, fund_key, fund_name, is_hold, shares, sectors)
                VALUES (?, ?, ?, ?, 0, 0, '[]')
            ''', (user_id, fund_code, fund_key, fund_name))

            conn.commit()
            conn.close()
            logger.debug(f"Added fund {fund_code} for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to add fund: {e}")
            return False

    def delete_fund(self, user_id, fund_code):
        """删除用户的基金

        Returns:
            bool: 是否成功
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                           DELETE
                           FROM user_funds
                           WHERE user_id = ?
                             AND fund_code = ?
                           ''', (user_id, fund_code))

            conn.commit()
            affected_rows = cursor.rowcount
            conn.close()

            if affected_rows > 0:
                logger.debug(f"Deleted fund {fund_code} for user {user_id}")
                return True
            else:
                logger.warning(f"No fund found to delete: user {user_id}, fund {fund_code}")
                return False

        except Exception as e:
            logger.error(f"Failed to delete fund: {e}")
            return False

    def update_chart_default(self, user_id, fund_code):
        """设置估值趋势图默认基金

        Args:
            user_id: 用户ID
            fund_code: 基金代码

        Returns:
            bool: 是否成功
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # 先清除该用户的所有chart_default标记
            cursor.execute('UPDATE user_funds SET chart_default = 0 WHERE user_id = ?', (user_id,))

            # 设置新的默认基金
            cursor.execute('''
                           UPDATE user_funds
                           SET chart_default = 1
                           WHERE user_id = ?
                             AND fund_code = ?
                           ''', (user_id, fund_code))

            conn.commit()
            affected_rows = cursor.rowcount
            conn.close()

            if affected_rows > 0:
                logger.debug(f"Set chart default fund for user {user_id}: {fund_code}")
                return True
            else:
                logger.warning(f"No fund found to set as default: user {user_id}, fund {fund_code}")
                return False

        except Exception as e:
            logger.error(f"Failed to update chart default: {e}")
            return False

    def get_chart_default_fund(self, user_id):
        """获取估值趋势图默认基金

        Args:
            user_id: 用户ID

        Returns:
            dict or None: {'fund_code': str, 'fund_key': str, 'fund_name': str}
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                           SELECT fund_code, fund_key, fund_name
                           FROM user_funds
                           WHERE user_id = ? AND chart_default = 1
                           ''', (user_id,))
            row = cursor.fetchone()
            conn.close()

            if row:
                return {
                    'fund_code': row['fund_code'],
                    'fund_key': row['fund_key'],
                    'fund_name': row['fund_name']
                }
            return None

        except Exception as e:
            logger.error(f"Failed to get chart default fund for user {user_id}: {e}")
            return None
