import sqlite3
import json
from datetime import datetime, timedelta
import os

class LearningDatabase:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.getenv("DATABASE_PATH") or os.path.abspath("database/learning.db")
        print("LearningDatabaseインスタンス化直前", flush=True)
        self.db_path = db_path
        print(f"DBパス: {self.db_path}", flush=True)
        print("LearningDatabaseインスタンス化直後", flush=True)
        self.init_database()
    
    def init_database(self):
        """データベースとテーブルを初期化"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # ユーザーテーブル
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    level TEXT DEFAULT 'beginner',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 学習履歴テーブル
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS learning_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    lesson_id TEXT,
                    level TEXT,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # テスト結果テーブル
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS quiz_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    quiz_id TEXT,
                    user_answer INTEGER,
                    correct_answer INTEGER,
                    is_correct BOOLEAN,
                    answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # 復習キュー テーブル
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS review_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    lesson_id TEXT,
                    level TEXT,
                    reason TEXT,
                    priority INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # 質問履歴テーブル
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS question_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    question TEXT,
                    asked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # プレミアムサブスクリプションテーブル
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS premium_subscriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    stripe_subscription_id TEXT UNIQUE,
                    stripe_customer_id TEXT,
                    plan_type TEXT DEFAULT 'free',
                    status TEXT DEFAULT 'inactive',
                    started_at TIMESTAMP,
                    expires_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            conn.commit()
    
    def add_user(self, user_id, level="beginner"):
        """新しいユーザーを追加"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO users (user_id, level, last_activity)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, level))
            conn.commit()
    
    def get_user_level(self, user_id):
        """ユーザーの現在のレベルを取得"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT level FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            return result[0] if result else None
    
    def get_all_users(self):
        """全ユーザーIDを取得"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT user_id FROM users')
            results = cursor.fetchall()
            print(f"get_all_users: {results}")
            return [row[0] for row in results]
    
    def update_user_level(self, user_id, new_level):
        """ユーザーのレベルを更新"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users 
                SET level = ?, last_activity = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (new_level, user_id))
            conn.commit()
    
    def record_lesson_sent(self, user_id, lesson_id, level):
        """学習メッセージの送信を記録"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO learning_history (user_id, lesson_id, level)
                VALUES (?, ?, ?)
            ''', (user_id, lesson_id, level))
            conn.commit()
    
    def get_recent_lessons(self, user_id, days=7):
        """最近送信されたレッスンを取得"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT lesson_id, level, sent_at 
                FROM learning_history 
                WHERE user_id = ? 
                AND sent_at >= datetime('now', '-{} days')
                ORDER BY sent_at DESC
            '''.format(days), (user_id,))
            return cursor.fetchall()
    
    def record_quiz_result(self, user_id, quiz_id, user_answer, correct_answer):
        """テスト結果を記録"""
        is_correct = user_answer == correct_answer
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO quiz_results (user_id, quiz_id, user_answer, correct_answer, is_correct)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, quiz_id, user_answer, correct_answer, is_correct))
            conn.commit()
    
    def get_quiz_statistics(self, user_id, days=30):
        """テスト統計を取得"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT
                    COUNT(*) as total_quizzes,
                    SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) as correct_answers,
                    AVG(CASE WHEN is_correct THEN 1.0 ELSE 0.0 END) * 100 as accuracy
                FROM quiz_results
                WHERE user_id = ?
                AND answered_at >= datetime('now', '-{} days')
            '''.format(days), (user_id,))
            return cursor.fetchone()

    def get_quiz_statistics_by_level(self, user_id, level_prefix, days=365):
        """特定レベルのテスト統計を取得

        Args:
            user_id: ユーザーID
            level_prefix: クイズIDのプレフィックス（'bq'=初級, 'iq'=中級, 'aq'=上級）
            days: 集計期間（日数）

        Returns:
            (total_quizzes, correct_answers, accuracy) のタプル
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT
                    COUNT(*) as total_quizzes,
                    SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) as correct_answers,
                    AVG(CASE WHEN is_correct THEN 1.0 ELSE 0.0 END) * 100 as accuracy
                FROM quiz_results
                WHERE user_id = ?
                AND quiz_id LIKE ?
                AND answered_at >= datetime('now', '-{} days')
            '''.format(days), (user_id, level_prefix + '%'))
            return cursor.fetchone()
    
    def add_to_review_queue(self, user_id, lesson_id, level, reason, priority=1):
        """復習キューに追加"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO review_queue (user_id, lesson_id, level, reason, priority)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, lesson_id, level, reason, priority))
            conn.commit()
    
    def get_review_items(self, user_id, limit=5):
        """復習アイテムを取得"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT lesson_id, level, reason, priority
                FROM review_queue 
                WHERE user_id = ?
                ORDER BY priority DESC, created_at ASC
                LIMIT ?
            ''', (user_id, limit))
            return cursor.fetchall()
    
    def remove_from_review_queue(self, user_id, lesson_id):
        """復習キューから削除"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM review_queue 
                WHERE user_id = ? AND lesson_id = ?
            ''', (user_id, lesson_id))
            conn.commit()
    
    def get_weak_areas(self, user_id, days=30):
        """苦手分野を特定"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    q.quiz_id,
                    COUNT(*) as total_attempts,
                    SUM(CASE WHEN q.is_correct THEN 1 ELSE 0 END) as correct_attempts
                FROM quiz_results q
                WHERE q.user_id = ? 
                AND q.answered_at >= datetime('now', '-{} days')
                GROUP BY q.quiz_id
                HAVING correct_attempts < total_attempts
                ORDER BY (correct_attempts * 1.0 / total_attempts) ASC
            '''.format(days), (user_id,))
            return cursor.fetchall()
    
    def get_learning_progress(self, user_id):
        """学習進捗を取得"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 総学習回数
            cursor.execute('''
                SELECT COUNT(*) FROM learning_history WHERE user_id = ?
            ''', (user_id,))
            total_lessons = cursor.fetchone()[0]
            
            # 今週の学習回数
            cursor.execute('''
                SELECT COUNT(*) FROM learning_history 
                WHERE user_id = ? 
                AND sent_at >= datetime('now', '-7 days')
            ''', (user_id,))
            weekly_lessons = cursor.fetchone()[0]
            
            # テスト正答率
            cursor.execute('''
                SELECT AVG(CASE WHEN is_correct THEN 1.0 ELSE 0.0 END) * 100
                FROM quiz_results WHERE user_id = ?
            ''', (user_id,))
            quiz_accuracy = cursor.fetchone()[0] or 0
            
            return {
                'total_lessons': total_lessons,
                'weekly_lessons': weekly_lessons,
                'quiz_accuracy': quiz_accuracy
            } 

    def set_last_quiz_id(self, user_id, quiz_id):
        """ユーザーごとに直近出題したクイズIDを保存"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_state (
                    user_id TEXT PRIMARY KEY,
                    last_quiz_id TEXT
                )
            ''')
            cursor.execute('''
                INSERT OR REPLACE INTO user_state (user_id, last_quiz_id)
                VALUES (?, ?)
            ''', (user_id, quiz_id))
            conn.commit()

    def get_last_quiz_id(self, user_id):
        """ユーザーごとに直近出題したクイズIDを取得"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_state (
                    user_id TEXT PRIMARY KEY,
                    last_quiz_id TEXT
                )
            ''')
            cursor.execute('SELECT last_quiz_id FROM user_state WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            return result[0] if result else None
    
    def record_question_asked(self, user_id, question=""):
        """質問を記録"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # 日本時間で現在時刻を取得
                jst_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute('''
                    INSERT INTO question_history (user_id, question, asked_at)
                    VALUES (?, ?, ?)
                ''', (user_id, question, jst_now))
                conn.commit()
                print(f"🔍 デバッグ: 質問記録成功 - user_id={user_id}, question={question[:20]}..., time={jst_now}")
                
                # 記録直後に確認
                cursor.execute('''
                    SELECT COUNT(*) FROM question_history WHERE user_id = ?
                ''', (user_id,))
                total_count = cursor.fetchone()[0]
                print(f"🔍 デバッグ: このユーザーの総質問数 = {total_count}")
                
        except Exception as e:
            print(f"❌ 質問記録エラー: {e}")
            raise
    
    def get_daily_question_count(self, user_id, date):
        """指定日の質問回数を取得"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # 日付を文字列形式に変換
                date_str = date.strftime('%Y-%m-%d')
                
                # まず、実際のasked_atの値を確認
                cursor.execute('''
                    SELECT asked_at FROM question_history 
                    WHERE user_id = ? 
                    ORDER BY asked_at DESC 
                    LIMIT 3
                ''', (user_id,))
                recent_records = cursor.fetchall()
                print(f"🔍 デバッグ: 最近のasked_at値 = {recent_records}")
                
                # 日付比較（文字列の左側9文字で日付部分を比較）
                cursor.execute('''
                    SELECT COUNT(*) FROM question_history 
                    WHERE user_id = ? AND substr(asked_at, 1, 10) = ?
                ''', (user_id, date_str))
                result = cursor.fetchone()
                count = result[0] if result else 0
                print(f"🔍 デバッグ: 質問回数取得 - user_id={user_id}, date={date_str}, count={count}")
                
                return count
        except Exception as e:
            print(f"❌ 質問回数取得エラー: {e}")
            return 0

    def get_inactive_users(self, days=7):
        """指定日数以上アクティブでないユーザーを取得"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 指定日数前の日付を計算
                cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
                
                # 最後のアクティビティが指定日数前より古いユーザーを取得
                cursor.execute('''
                    SELECT user_id FROM users 
                    WHERE last_activity < ? OR last_activity IS NULL
                ''', (cutoff_date,))
                
                inactive_users = [row[0] for row in cursor.fetchall()]
                print(f"📊 非アクティブユーザー取得 - {days}日以上: {len(inactive_users)}人")
                
                return inactive_users
                
        except Exception as e:
            print(f"❌ 非アクティブユーザー取得エラー: {e}")
            return []
    
    def create_premium_subscription(self, user_id, stripe_subscription_id, stripe_customer_id):
        """プレミアムサブスクリプションを作成"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                started_at = datetime.now()
                expires_at = started_at + timedelta(days=30)
                
                cursor.execute('''
                    INSERT OR REPLACE INTO premium_subscriptions 
                    (user_id, stripe_subscription_id, stripe_customer_id, plan_type, status, started_at, expires_at, updated_at)
                    VALUES (?, ?, ?, 'premium', 'active', ?, ?, CURRENT_TIMESTAMP)
                ''', (user_id, stripe_subscription_id, stripe_customer_id, started_at, expires_at))
                conn.commit()
                print(f"✅ プレミアムサブスクリプション作成: {user_id}")
                return True
        except Exception as e:
            print(f"❌ プレミアムサブスクリプション作成エラー: {e}")
            return False
    
    def get_user_subscription(self, user_id):
        """ユーザーのサブスクリプション状態を取得"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT plan_type, status, expires_at, stripe_subscription_id
                    FROM premium_subscriptions 
                    WHERE user_id = ? AND status = 'active' AND expires_at > CURRENT_TIMESTAMP
                    ORDER BY created_at DESC LIMIT 1
                ''', (user_id,))
                result = cursor.fetchone()
                
                if result:
                    return {
                        'plan_type': result[0],
                        'status': result[1],
                        'expires_at': result[2],
                        'stripe_subscription_id': result[3]
                    }
                else:
                    return {
                        'plan_type': 'free',
                        'status': 'inactive',
                        'expires_at': None,
                        'stripe_subscription_id': None
                    }
        except Exception as e:
            print(f"❌ サブスクリプション取得エラー: {e}")
            return {'plan_type': 'free', 'status': 'inactive', 'expires_at': None, 'stripe_subscription_id': None}
    
    def cancel_premium_subscription(self, user_id, stripe_subscription_id):
        """プレミアムサブスクリプションをキャンセル"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE premium_subscriptions 
                    SET status = 'cancelled', updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ? AND stripe_subscription_id = ?
                ''', (user_id, stripe_subscription_id))
                conn.commit()
                print(f"✅ プレミアムサブスクリプションキャンセル: {user_id}")
                return True
        except Exception as e:
            print(f"❌ プレミアムサブスクリプションキャンセルエラー: {e}")
            return False
    
    def get_question_limit_for_user(self, user_id):
        """ユーザーの1日の質問制限数を取得"""
        subscription = self.get_user_subscription(user_id)
        return 10 if subscription['plan_type'] == 'premium' and subscription['status'] == 'active' else 3 