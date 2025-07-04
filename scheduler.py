import schedule
import time
import threading
from datetime import datetime, timedelta
from line_bot import LineBotHandler
from database import LearningDatabase
from learning_content import LearningContentManager
from quiz_manager import QuizManager

class LearningScheduler:
    def __init__(self):
        self.line_bot = LineBotHandler()
        self.db = LearningDatabase()
        self.learning_manager = LearningContentManager()
        self.quiz_manager = QuizManager()
        self.running = False
        
    def start(self):
        """スケジューラーを開始"""
        print("🚀 学習スケジューラーを開始しました")
        
        # 毎日の学習メッセージ（10時、15時、20時）
        schedule.every().day.at("10:00").do(self.send_morning_lesson)
        schedule.every().day.at("15:00").do(self.send_afternoon_lesson)
        schedule.every().day.at("20:00").do(self.send_evening_lesson)
        
        # 週間クイズ（日曜20時）
        schedule.every().sunday.at("20:00").do(self.send_weekly_quiz)
        
        # 週間サマリー（土曜21時）
        schedule.every().saturday.at("21:00").do(self.send_weekly_summary)
        
        # 復習メッセージ（水曜19時）
        schedule.every().wednesday.at("19:00").do(self.send_review_reminder)
        
        self.running = True
        
        # スケジューラーをバックグラウンドで実行
        scheduler_thread = threading.Thread(target=self.run_scheduler)
        scheduler_thread.daemon = True
        scheduler_thread.start()
        
        print("📅 スケジュール設定完了:")
        print("   - 毎日 10:00, 15:00, 20:00: 学習メッセージ")
        print("   - 日曜 20:00: 週間クイズ")
        print("   - 土曜 21:00: 週間サマリー")
        print("   - 水曜 19:00: 復習リマインダー")
    
    def run_scheduler(self):
        """スケジューラーを実行"""
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # 1分ごとにチェック
    
    def stop(self):
        """スケジューラーを停止"""
        self.running = False
        print("⏹️ 学習スケジューラーを停止しました")
    
    def send_morning_lesson(self):
        """朝の学習メッセージを送信"""
        print(f"🌅 朝の学習メッセージを送信中... ({datetime.now()})")
        self.send_daily_lesson_to_all_users("🌅 おはようございます！今日もプロンプトエンジニアリングを学びましょう！")
    
    def send_afternoon_lesson(self):
        """午後の学習メッセージを送信"""
        print(f"☀️ 午後の学習メッセージを送信中... ({datetime.now()})")
        self.send_daily_lesson_to_all_users("☀️ 午後の学習時間です！集中してスキルアップしましょう！")
    
    def send_evening_lesson(self):
        """夜の学習メッセージを送信"""
        print(f"🌙 夜の学習メッセージを送信中... ({datetime.now()})")
        self.send_daily_lesson_to_all_users("🌙 夜の学習時間です！今日の復習をしましょう！")
    
    def send_weekly_quiz(self):
        """週間クイズを送信"""
        print(f"🧪 週間クイズを送信中... ({datetime.now()})")
        self.send_quiz_to_all_users()
    
    def send_weekly_summary(self):
        """週間サマリーを送信"""
        print(f"📊 週間サマリーを送信中... ({datetime.now()})")
        self.send_summary_to_all_users()
    
    def send_review_reminder(self):
        """復習リマインダーを送信"""
        print(f"🔄 復習リマインダーを送信中... ({datetime.now()})")
        self.send_review_reminder_to_all_users()
    
    def send_daily_lesson_to_all_users(self, intro_message=""):
        """全ユーザーに毎日の学習メッセージを送信"""
        users = self.get_active_users()
        
        for user_id in users:
            try:
                # イントロメッセージを送信
                if intro_message:
                    self.line_bot.push_message(user_id, intro_message)
                    time.sleep(1)  # 少し待機
                
                # 学習コンテンツを送信
                success = self.learning_manager.send_daily_lesson(user_id, self.line_bot)
                
                if success:
                    print(f"✅ ユーザー {user_id} に学習メッセージを送信しました")
                else:
                    print(f"❌ ユーザー {user_id} への学習メッセージ送信に失敗しました")
                
                time.sleep(0.5)  # レート制限を避けるため少し待機
                
            except Exception as e:
                print(f"❌ ユーザー {user_id} への送信エラー: {e}")
    
    def send_quiz_to_all_users(self):
        """全ユーザーに週間クイズを送信"""
        users = self.get_active_users()
        
        for user_id in users:
            try:
                success = self.quiz_manager.send_weekly_quiz(user_id, self.line_bot)
                
                if success:
                    print(f"✅ ユーザー {user_id} に週間クイズを送信しました")
                else:
                    print(f"❌ ユーザー {user_id} への週間クイズ送信に失敗しました")
                
                time.sleep(0.5)
                
            except Exception as e:
                print(f"❌ ユーザー {user_id} へのクイズ送信エラー: {e}")
    
    def send_summary_to_all_users(self):
        """全ユーザーに週間サマリーを送信"""
        users = self.get_active_users()
        
        for user_id in users:
            try:
                summary = self.learning_manager.get_weekly_summary(user_id)
                success = self.line_bot.push_message(user_id, summary)
                
                if success:
                    print(f"✅ ユーザー {user_id} に週間サマリーを送信しました")
                else:
                    print(f"❌ ユーザー {user_id} への週間サマリー送信に失敗しました")
                
                time.sleep(0.5)
                
            except Exception as e:
                print(f"❌ ユーザー {user_id} へのサマリー送信エラー: {e}")
    
    def send_review_reminder_to_all_users(self):
        """全ユーザーに復習リマインダーを送信"""
        users = self.get_active_users()
        
        for user_id in users:
            try:
                # 復習が必要かチェック
                if self.quiz_manager.should_send_review_quiz(user_id):
                    review_quiz = self.quiz_manager.get_review_quiz(user_id)
                    if review_quiz:
                        message = "🔄 復習の時間です！\n\n"
                        message += self.quiz_manager.format_review_quiz_message(review_quiz)
                        success = self.line_bot.push_message(user_id, message)
                        
                        if success:
                            print(f"✅ ユーザー {user_id} に復習クイズを送信しました")
                        else:
                            print(f"❌ ユーザー {user_id} への復習クイズ送信に失敗しました")
                
                time.sleep(0.5)
                
            except Exception as e:
                print(f"❌ ユーザー {user_id} への復習リマインダー送信エラー: {e}")
    
    def get_active_users(self):
        """アクティブユーザーのリストを取得"""
        # 実際の実装では、データベースからアクティブユーザーを取得
        # ここでは簡略化のため、テスト用のユーザーIDを返す
        try:
            with self.db.db_path.replace('.db', '_users.txt') as f:
                return [line.strip() for line in f if line.strip()]
        except:
            # テスト用のダミーユーザーID
            return ["test_user_1", "test_user_2"]
    
    def manual_send_lesson(self, user_id):
        """手動でレッスンを送信（テスト用）"""
        try:
            success = self.learning_manager.send_daily_lesson(user_id, self.line_bot)
            if success:
                print(f"✅ ユーザー {user_id} に手動でレッスンを送信しました")
            else:
                print(f"❌ ユーザー {user_id} への手動レッスン送信に失敗しました")
            return success
        except Exception as e:
            print(f"❌ 手動レッスン送信エラー: {e}")
            return False
    
    def manual_send_quiz(self, user_id):
        """手動でクイズを送信（テスト用）"""
        try:
            success = self.quiz_manager.send_weekly_quiz(user_id, self.line_bot)
            if success:
                print(f"✅ ユーザー {user_id} に手動でクイズを送信しました")
            else:
                print(f"❌ ユーザー {user_id} への手動クイズ送信に失敗しました")
            return success
        except Exception as e:
            print(f"❌ 手動クイズ送信エラー: {e}")
            return False
    
    def get_next_scheduled_tasks(self):
        """次のスケジュールタスクを取得"""
        next_tasks = []
        for job in schedule.jobs:
            next_tasks.append({
                'function': job.job_func.__name__,
                'next_run': job.next_run,
                'interval': str(job.interval)
            })
        return next_tasks 