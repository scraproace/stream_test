from datetime import datetime, time, timedelta
import sqlite3


class DBController:
    """データベースコントローラクラス"""
    def __init__(self):
        """DBControllerの初期化を行い、データベース接続を確立し、必要なテーブルを作成します。"""
        self.conn = sqlite3.connect('shift.db', check_same_thread=False)
        self.conn.execute('PRAGMA foreign_keys = ON')
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()
        self.create_users_table()
        self.create_places_table()
        self.create_shifts_table()

    def create_users_table(self):
        """ユーザーテーブルを作成します。"""
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                closing_day INTEGER,
                goal_amount INTEGER,
                is_valid INTEGER DEFAULT 1
            )
        ''')
        self.conn.commit()

    def create_places_table(self):
        """勤務先テーブルを作成します。"""
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS places (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                is_valid INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        self.conn.commit()

    def create_shifts_table(self):
        """シフトテーブルを作成します。"""
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS shifts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                place TEXT NOT NULL,
                title TEXT NOT NULL,
                start_datetime TEXT NOT NULL,
                end_datetime TEXT NOT NULL,
                break_time TEXT NOT NULL,
                hourly_wage INTEGER NOT NULL,
                amount INTEGER NOT NULL,
                is_valid INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        self.conn.commit()

    def login(self, username: str, password: str) -> int | None:
        """ユーザーのログインを行います。"""
        self.cur.execute('''
            SELECT id, username, password FROM users
            WHERE username = :username
            AND password = :password
            AND is_valid = 1
            LIMIT 1
        ''',
        {'username': username, 'password': password})

        result = self.cur.fetchone()
        return result['id'] if result is not None else None

    def get_user(self, user_id: int) -> list[str]:
        """指定されたユーザーの情報を取得します。"""
        self.cur.execute('''
            SELECT username, password, closing_day, goal_amount FROM users
            WHERE id = :user_id
        ''',
        {'user_id': user_id})

        user = self.cur.fetchone()
        return user

    def add_user(
        self,
        username: str,
        password: str,
        closing_day: int,
        goal_amount: int
    ) -> bool:
        """新しいユーザーを追加します。"""
        if self.is_exist_user(username):
            return False

        self.cur.execute('''
            INSERT INTO users(username, password, closing_day, goal_amount)
            VALUES (:username, :password, :closing_day, :goal_amount)
        ''',
        {'username': username, 'password': password, 'closing_day': closing_day, 'goal_amount': goal_amount})

        self.conn.commit()
        return True

    def update_user(
        self,
        user_id: int,
        username: str,
        password: str,
        closing_day: int,
        goal_amount: int
    ) -> bool:
        """ユーザー情報を更新します。"""
        if self.is_exist_user(username, user_id):
            return False

        self.cur.execute('''
            UPDATE users
            SET username = :username,
                password = :password,
                closing_day = :closing_day,
                goal_amount = :goal_amount
            WHERE id = :user_id
        ''',
        {'user_id': user_id, 'username': username, 'password': password, 'closing_day': closing_day, 'goal_amount': goal_amount})

        self.conn.commit()
        return True

    def is_exist_user(self, username: str, exclude_user_id: int | None = None) -> bool:
        """ユーザー名の重複を確認します。"""
        self.cur.execute('''
            SELECT * FROM users
            WHERE id != :exclude_user_id
            AND username = :username
            AND is_valid = 1
            LIMIT 1
        ''',
        {'username': username, 'exclude_user_id': exclude_user_id})

        if self.cur.fetchone() is not None:
            return True
        return False

    def add_place(self, user_id: int, name: str) -> bool:
        """新しい勤務先を追加します。"""
        self.cur.execute('''
            SELECT * FROM places
            WHERE user_id = :user_id
            AND name = :name
            AND is_valid = 1
            LIMIT 1
        ''',
        {'user_id': user_id, 'name': name})

        if self.cur.fetchone() is not None:
            return False

        self.cur.execute('''
            INSERT INTO places(user_id, name)
            VALUES (:user_id, :name)
        ''',
        {'user_id': user_id, 'name': name})

        self.conn.commit()
        return True

    def get_places(self, user_id: int) -> list[str]:
        """指定されたユーザーに登録されている勤務先のリストを取得します。"""
        self.cur.execute('''
            SELECT name FROM places
            WHERE user_id = :user_id
            AND is_valid = 1
            ORDER BY id
        ''',
        {'user_id': user_id})

        places = [row['name'] for row in self.cur.fetchall()]
        return places

    def add_shift(
        self,
        user_id: int,
        place: str,
        title: str,
        start_datetime: datetime,
        end_datetime: datetime,
        break_time: time,
        hourly_wage: int,
        *,
        is_upadate: bool = False,
    ) -> bool:
        """新しいシフトを追加します。"""
        start_datetime_str = datetime.strftime(start_datetime, '%Y-%m-%d %H:%M:%S')
        end_datetime_str = datetime.strftime(end_datetime, '%Y-%m-%d %H:%M:%S')

        self.cur.execute('''
            SELECT id FROM shifts
            WHERE user_id = :user_id
            AND (
                (start_datetime < :end_datetime_str AND end_datetime > :start_datetime_str) OR
                (start_datetime >= :start_datetime_str AND start_datetime < :end_datetime_str) OR
                (end_datetime > :start_datetime_str AND end_datetime <= :end_datetime_str)
            )
            AND is_valid = 1
            LIMIT 1
        ''',
        {'user_id': user_id, 'start_datetime_str': start_datetime_str, 'end_datetime_str': end_datetime_str})

        result = self.cur.fetchone()

        if result is not None:
            if is_upadate:
                shift_id = result['id']
                self.cur.execute('''
                    UPDATE shifts
                    SET is_valid = 0
                    WHERE id = :shift_id
                ''',
                {'shift_id': shift_id})
            else:
                return False

        break_time_str = time.strftime(break_time, '%M:%S')

        total_duration = end_datetime - start_datetime - timedelta(hours=break_time.hour, minutes=break_time.minute, seconds=break_time.second)
        amount = round(total_duration.total_seconds() / 3600 * hourly_wage)

        self.cur.execute('''
            INSERT INTO shifts (
                user_id,
                place,
                title,
                start_datetime,
                end_datetime,
                break_time,
                hourly_wage,
                amount
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (user_id, place, title, start_datetime_str, end_datetime_str, break_time_str, hourly_wage, amount))
        self.conn.commit()

        return True

    def delete_shift(
        self,
        id: int,
    ) -> None:
        """シフトを削除します。"""
        self.cur.execute('''
            UPDATE shifts
            SET is_valid = 0
            WHERE id = :id
        ''',
        {'id': id})
        self.conn.commit()

    def get_shifts(
        self,
        user_id: int,
    ) -> list[dict]:
        """指定されたユーザーに登録されているシフトのリストを取得します。"""
        self.cur.execute('''
            SELECT id, place, title, start_datetime, end_datetime, break_time, hourly_wage FROM shifts
            WHERE user_id = :user_id
            AND is_valid = 1
        ''',
        {'user_id': user_id})

        shifts = [dict(row) for row in self.cur.fetchall()]
        for shift in shifts:
            shift['start_datetime'] = datetime.strptime(shift['start_datetime'], '%Y-%m-%d %H:%M:%S')
            shift['end_datetime'] = datetime.strptime(shift['end_datetime'], '%Y-%m-%d %H:%M:%S')
            shift['break_time'] = datetime.strptime(shift['break_time'], '%M:%S').time()

        return shifts

    def get_amount(
        self,
        user_id: int,
        start_datetime: datetime,
        end_datetime: datetime,
    ) -> int:
        """指定されたユーザーの指定期間内の合計金額を取得します。"""
        start_datetime_str = datetime.strftime(start_datetime, '%Y-%m-%d %H:%M:%S')
        end_datetime_str = datetime.strftime(end_datetime, '%Y-%m-%d %H:%M:%S')

        self.cur.execute('''
            SELECT SUM(amount) AS amount FROM shifts
            WHERE user_id = :user_id
            AND end_datetime >= :start_datetime_str
            AND end_datetime <= :end_datetime_str
            AND is_valid = 1
            LIMIT 1
        ''',
        {'user_id': user_id, 'start_datetime_str': start_datetime_str, 'end_datetime_str': end_datetime_str})

        result = self.cur.fetchone()
        return result['amount'] if result['amount'] is not None else 0

    def get_next_shift(
        self,
        user_id: int,
        start_datetime: datetime,
    ) -> datetime | None:
        """指定されたユーザーの次のシフトを取得します。"""
        start_datetime_str = datetime.strftime(start_datetime, '%Y-%m-%d %H:%M:%S')

        self.cur.execute('''
            SELECT start_datetime FROM shifts
            WHERE user_id = :user_id
            AND start_datetime >= :start_datetime_str
            AND is_valid = 1
            ORDER BY start_datetime
            LIMIT 1
        ''',
        {'user_id': user_id, 'start_datetime_str': start_datetime_str})

        result = self.cur.fetchone()
        if result is None:
            return None

        next_shift = datetime.strptime(result['start_datetime'], '%Y-%m-%d %H:%M:%S')
        return next_shift
