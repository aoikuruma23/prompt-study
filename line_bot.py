import os
from database import LearningDatabase
from learning_content import LearningContentManager
from quiz_manager import QuizManager

# LINE Bot SDKのインポートを試行
try:
    from linebot import LineBotApi, WebhookHandler
    from linebot.exceptions import InvalidSignatureError
    from linebot.models import MessageEvent, TextMessage, TextSendMessage
    LINE_BOT_AVAILABLE = True
except ImportError:
    print("⚠️ LINE Bot SDKが利用できません。テストモードで動作します。")
    LINE_BOT_AVAILABLE = False

class LineBotHandler:
    def __init__(self):
        if not LINE_BOT_AVAILABLE:
            print("⚠️ LINE Bot SDKが利用できないため、テストモードで動作します")
            self.line_bot_api = None
            self.handler = None
            self.channel_access_token = "dummy_token"
            self.channel_secret = "dummy_secret"
        else:
            self.channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
            self.channel_secret = os.getenv('LINE_CHANNEL_SECRET')
            
            if not self.channel_access_token or not self.channel_secret:
                # テスト用のダミー値を設定
                self.channel_access_token = "dummy_token"
                self.channel_secret = "dummy_secret"
                print("⚠️ 環境変数が設定されていないため、テストモードで動作します")
            
            try:
                self.line_bot_api = LineBotApi(self.channel_access_token)
                self.handler = WebhookHandler(self.channel_secret)
            except Exception as e:
                print(f"⚠️ LINE Bot API初期化エラー: {e}")
                self.line_bot_api = None
                self.handler = None
        
        # 各マネージャーを初期化
        self.db = LearningDatabase()
        self.learning_manager = LearningContentManager()
        self.quiz_manager = QuizManager()
        
        # イベントハンドラーを設定
        self.setup_handlers()
    
    def setup_handlers(self):
        """イベントハンドラーを設定"""
        if self.handler is not None:
            @self.handler.add(MessageEvent, message=TextMessage)
            def handle_message(event):
                self.handle_text_message(event)
    
    def handle_text_message(self, event):
        """テキストメッセージを処理"""
        if self.line_bot_api is None:
            print("📱 [テストモード] メッセージ受信: LINE Bot機能は無効化されています")
            return
            
        user_id = event.source.user_id
        message_text = event.message.text
        
        # ユーザーが存在しない場合は追加
        if not self.db.get_user_level(user_id):
            self.db.add_user(user_id)
        
        # コマンド処理
        response = self.process_command(user_id, message_text)
        
        # レスポンスを送信
        if response:
            self.line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=response)
            )
    
    def process_command(self, user_id, message_text):
        """コマンドを処理"""
        message_text = message_text.strip().lower()
        
        # クイズ回答処理（1-4の数字）
        if message_text in ['1', '2', '3', '4']:
            return self.quiz_manager.process_quiz_answer(user_id, message_text)
        
        # コマンド処理
        if message_text == 'help' or message_text == 'ヘルプ':
            return self.get_help_message()
        
        elif message_text == 'progress' or message_text == '進捗':
            return self.learning_manager.get_weekly_summary(user_id)
        
        elif message_text == 'stats' or message_text == '統計':
            return self.quiz_manager.get_quiz_statistics_message(user_id)
        
        elif message_text == 'weak' or message_text == '苦手':
            return self.quiz_manager.get_weak_areas_message(user_id)
        
        elif message_text == 'level' or message_text == 'レベル':
            return self.get_level_message(user_id)
        
        elif message_text == 'lesson' or message_text == 'レッスン':
            return self.request_lesson(user_id)
        
        elif message_text == 'quiz' or message_text == 'クイズ':
            return self.request_quiz(user_id)
        
        elif message_text == 'review' or message_text == '復習':
            return self.request_review(user_id)
        
        elif message_text == 'motivation' or message_text == 'モチベーション':
            return self.learning_manager.get_motivational_message()
        
        else:
            return self.get_help_message()
    
    def get_help_message(self):
        """ヘルプメッセージを取得"""
        message = "🤖 プロンプトエンジニアリング学習Bot\n\n"
        message += "📝 利用可能なコマンド：\n\n"
        message += "📚 レッスン - 学習コンテンツを表示\n"
        message += "🧪 クイズ - 理解度テストを開始\n"
        message += "🔄 復習 - 復習コンテンツを表示\n"
        message += "📊 進捗 - 学習進捗を確認\n"
        message += "📈 統計 - テスト結果を確認\n"
        message += "📚 苦手 - 苦手分野を確認\n"
        message += "🎯 レベル - 現在のレベルを確認\n"
        message += "💪 モチベーション - 励ましメッセージ\n"
        message += "❓ ヘルプ - このメッセージを表示\n\n"
        message += "💡 クイズの回答は「1」「2」「3」「4」で送信してください。"
        
        return message
    
    def get_level_message(self, user_id):
        """レベル情報メッセージを取得"""
        user_level = self.db.get_user_level(user_id)
        progress = self.learning_manager.get_level_progress(user_id)
        
        level_names = {
            "beginner": "初級",
            "intermediate": "中級", 
            "advanced": "上級"
        }
        
        message = f"🎯 現在のレベル: {level_names.get(user_level, user_level)}\n\n"
        message += f"📚 最近30日の学習回数: {progress['total_recent']}回\n"
        
        # レベルアップ条件を表示
        if user_level == "beginner":
            message += "\n📈 中級への条件: テスト正答率80%以上"
        elif user_level == "intermediate":
            message += "\n📈 上級への条件: テスト正答率85%以上"
        else:
            message += "\n🏆 最高レベルです！"
        
        return message
    
    def request_lesson(self, user_id):
        """レッスンを要求"""
        lesson = self.learning_manager.get_next_lesson(user_id)
        if lesson:
            return self.learning_manager.format_lesson_message(lesson)
        else:
            return "📚 現在利用可能なレッスンがありません。"
    
    def request_quiz(self, user_id):
        """クイズを要求"""
        quiz = self.quiz_manager.get_weekly_quiz(user_id)
        if quiz:
            return self.quiz_manager.format_quiz_message(quiz)
        else:
            return "🧪 現在利用可能なクイズがありません。"
    
    def request_review(self, user_id):
        """復習コンテンツを要求"""
        review_lesson = self.learning_manager.get_review_lesson(user_id)
        if review_lesson:
            message = "🔄 復習コンテンツ\n\n"
            message += self.learning_manager.format_lesson_message(review_lesson)
            return message
        else:
            return "🔄 現在復習が必要なコンテンツはありません。"
    
    def push_message(self, user_id, message):
        """プッシュメッセージを送信"""
        if self.line_bot_api is None:
            print(f"📱 [テストモード] ユーザー {user_id} にメッセージを送信: {message[:50]}...")
            return True
        try:
            self.line_bot_api.push_message(user_id, TextSendMessage(text=message))
            return True
        except Exception as e:
            print(f"プッシュメッセージ送信エラー: {e}")
            return False
    
    def broadcast_message(self, message):
        """ブロードキャストメッセージを送信"""
        if self.line_bot_api is None:
            print(f"📱 [テストモード] ブロードキャストメッセージ: {message[:50]}...")
            return True
        try:
            self.line_bot_api.broadcast(TextSendMessage(text=message))
            return True
        except Exception as e:
            print(f"ブロードキャストメッセージ送信エラー: {e}")
            return False
    
    def get_user_profile(self, user_id):
        """ユーザープロフィールを取得"""
        try:
            profile = self.line_bot_api.get_profile(user_id)
            return {
                'user_id': profile.user_id,
                'display_name': profile.display_name,
                'picture_url': profile.picture_url,
                'status_message': profile.status_message
            }
        except Exception as e:
            print(f"プロフィール取得エラー: {e}")
            return None
    
    def handle_webhook(self, body, signature):
        """Webhookを処理"""
        if self.handler is None:
            print("📱 [テストモード] Webhook処理: LINE Bot機能は無効化されています")
            return True
        try:
            self.handler.handle(body, signature)
        except InvalidSignatureError:
            print("Invalid signature")
            return False
        except Exception as e:
            print(f"Webhook処理エラー: {e}")
            return False
        
        return True 