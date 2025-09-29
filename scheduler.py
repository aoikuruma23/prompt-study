import schedule
import time
import threading
from datetime import datetime, timedelta
from line_bot import LineBotHandler
from database import LearningDatabase
from learning_content import LearningContentManager
from quiz_manager import QuizManager
import sqlite3

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
        
        # 有料プランにアップグレードしたため、配信を再開
        print("✅ 有料プランにアップグレード完了！配信を再開します")
        
        # スケジューラーを実行可能に設定
        self.running = True
        
        # スケジュールジョブの設定
        self.setup_scheduled_jobs()
        
        # スケジュール設定の確認
        print(f"📅 スケジュール設定完了:")
        print(f"   - 非アクティブユーザー再開促し: 毎週月曜 09:00")
        print(f"   - 朝の学習メッセージ: 毎日 10:00")
        print(f"   - 午後の学習メッセージ: 毎日 15:00")
        print(f"   - 夜の学習メッセージ: 毎日 20:00")
        print(f"   - 週間クイズ: 日曜 20:00")
        print(f"   - 週間サマリー: 土曜 21:00")
        print(f"   - 復習リマインダー: 水曜 19:00")
        
        # 現在のスケジュールを確認
        print(f"📋 現在のスケジュール:")
        for job in schedule.jobs:
            print(f"   - {job.job_func.__name__}: {job.next_run}")
    
    def run_scheduler(self):
        """スケジューラーを実行"""
        print("🔄 スケジューラーループを開始しました")
        loop_count = 0
        last_heartbeat = datetime.now()
        
        while self.running:
            try:
                loop_count += 1
                current_time = datetime.now()
                
                # 10分ごとにハートビートログ
                if (current_time - last_heartbeat).seconds >= 600:
                    print(f"💓 スケジューラーハートビート: {current_time} (ループ {loop_count})")
                    last_heartbeat = current_time
                
                # 60分ごとに詳細ログ
                if loop_count % 60 == 0:
                    print(f"🔄 スケジューラーループ実行中... (ループ {loop_count})")
                
                schedule.run_pending()
                
                # デバッグ用：現在時刻と次のジョブをログ出力
                if schedule.jobs:
                    next_job = min(schedule.jobs, key=lambda x: x.next_run)
                    print(f"⏰ 現在時刻: {current_time}, 次のジョブ: {next_job.job_func.__name__} at {next_job.next_run}")
                else:
                    print(f"⚠️ スケジュールされたジョブがありません")
                
                time.sleep(60)  # 1分ごとにチェック
                
            except Exception as e:
                print(f"❌ スケジューラーエラー: {e}")
                print(f"📝 エラー詳細: {type(e).__name__}: {str(e)}")
                # エラーが発生してもスケジューラーを停止させない
                time.sleep(60)
                continue
    
    def stop(self):
        """スケジューラーを停止"""
        self.running = False
        print("⏹️ 学習スケジューラーを停止しました")
    
    def send_morning_lesson(self):
        """朝の学習メッセージを送信"""
        print(f"🌅 朝の学習メッセージを送信中... ({datetime.now()})")
        print(f"🌅 アクティブユーザー数: {len(self.get_active_users())}")
        self.send_daily_lesson_to_all_users("🌅 おはようございます！今日もプロンプトエンジニアリングを学びましょう！")
    
    def send_afternoon_lesson(self):
        """午後の学習メッセージを送信"""
        print(f"☀️ 午後の学習メッセージを送信中... ({datetime.now()})")
        print(f"☀️ アクティブユーザー数: {len(self.get_active_users())}")
        self.send_daily_lesson_to_all_users("☀️ 午後の学習時間です！集中してスキルアップしましょう！")
    
    def send_evening_lesson(self):
        """夜の学習メッセージを送信"""
        print(f"🌙 夜の学習メッセージを送信中... ({datetime.now()})")
        print(f"🌙 アクティブユーザー数: {len(self.get_active_users())}")
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
    
    def send_inactive_user_reengagement(self):
        """一週間非アクティブユーザーに再開を促すメッセージを送信"""
        try:
            # 一週間以上アクティブでないユーザーを取得
            inactive_users = self.db.get_inactive_users(days=7)
            print(f"📢 非アクティブユーザー再開促し送信開始 - 対象ユーザー数: {len(inactive_users)}")
            
            for user_id in inactive_users:
                message = """
🤖 プロンプトエンジニアリング学習bot

お久しぶりです！学習はお休みですか？

💡 一週間ぶりですが、今日から再び一緒に学びませんか？

🚀 AI時代の準備は継続が大切です。
   1日1分×3回のレッスンで、着実にスキルアップできます。

📅 今日の予定：
   • 10:00 - 朝の学習メッセージ
   • 15:00 - 午後の学習メッセージ  
   • 20:00 - 夜の学習メッセージ

💬 何か質問があれば、いつでもお気軽にどうぞ！
   学習を再開する準備ができたら、何かメッセージを送ってください。

一緒にAI時代の勝者になりましょう！
                """
                
                self.line_bot.send_message(user_id, message)
                print(f"✅ 非アクティブユーザー再開促し送信完了 - user_id: {user_id}")
                
        except Exception as e:
            print(f"❌ 非アクティブユーザー再開促し送信エラー: {e}")

    def setup_scheduled_jobs(self):
        """スケジュールされたジョブを設定"""
        try:
            # 非アクティブユーザー再開促し（毎週月曜日AM9:00）
            schedule.every().monday.at("09:00").do(self.send_inactive_user_reengagement)
            
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
            
            print("✅ スケジュールジョブ設定完了")
            
        except Exception as e:
            print(f"❌ スケジュールジョブ設定エラー: {e}")
            import traceback
            print(f"📝 エラー詳細: {traceback.format_exc()}")
    
    def send_daily_lesson_to_all_users(self, intro_message=""):
        """全ユーザーに毎日の学習メッセージを送信"""
        users = self.get_active_users()
        print(f"📤 配信開始：{len(users)}人のユーザーに送信中...")

        sent_count = 0
        failed_count = 0

        for i, user_id in enumerate(users, 1):
            try:
                print(f"📨 ユーザー {i}/{len(users)}: {user_id} に送信中...")

                # イントロメッセージを送信
                if intro_message:
                    intro_success = self.line_bot.push_message(user_id, intro_message)
                    if intro_success:
                        print(f"✅ イントロメッセージ送信成功: {user_id}")
                    else:
                        print(f"❌ イントロメッセージ送信失敗: {user_id}")
                    time.sleep(1)  # 少し待機

                # 学習コンテンツを送信
                print(f"📚 学習コンテンツを送信中: {user_id}")
                success = self.learning_manager.send_daily_lesson(user_id, self.line_bot)

                if success:
                    print(f"✅ ユーザー {user_id} に学習メッセージを送信しました")
                    sent_count += 1
                else:
                    print(f"❌ ユーザー {user_id} への学習メッセージ送信に失敗しました")
                    failed_count += 1

                time.sleep(0.5)  # レート制限を避けるため少し待機

            except Exception as e:
                print(f"❌ ユーザー {user_id} への送信で予期しないエラー: {e}")
                print(f"📝 エラータイプ: {type(e).__name__}")
                import traceback
                print(f"🔍 エラー詳細: {traceback.format_exc()}")
                failed_count += 1
                continue

        print(f"📊 配信完了 - 成功: {sent_count}人, 失敗: {failed_count}人")
    
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
        try:
            # データベースから実際のユーザーIDを取得
            users = self.db.get_all_users()
            if users:
                print(f"📋 データベースから取得したユーザー: {users}", flush=True)
                return users
            else:
                print("⚠️ データベースにユーザーが登録されていません", flush=True)
                return []
        except Exception as e:
            print(f"⚠️ ユーザー取得エラー: {e}", flush=True)
            return []
    
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