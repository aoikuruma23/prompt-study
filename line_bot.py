import os
import requests
from database import LearningDatabase
from learning_content import LearningContentManager
from quiz_manager import QuizManager
import openai
from datetime import datetime, timedelta

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
            print("⚠️ LINE Bot SDKが利用できないため、テストモードで動作します", flush=True)
            self.line_bot_api = None
            self.handler = None
            self.channel_access_token = "dummy_token"
            self.channel_secret = "dummy_secret"
        else:
            self.channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
            self.channel_secret = os.getenv('LINE_CHANNEL_SECRET')
            if not self.channel_access_token or not self.channel_secret:
                self.channel_access_token = "dummy_token"
                self.channel_secret = "dummy_secret"
                print("⚠️ 環境変数が設定されていないため、テストモードで動作します", flush=True)
            try:
                self.line_bot_api = LineBotApi(self.channel_access_token)
                self.handler = WebhookHandler(self.channel_secret)
            except Exception as e:
                print(f"⚠️ LINE Bot API初期化エラー: {e}", flush=True)
                self.line_bot_api = None
                self.handler = None
        
        # 各マネージャーを初期化
        self.db = LearningDatabase()
        print(f"DBパス: {self.db.db_path}", flush=True)
        self.learning_manager = LearningContentManager()
        self.quiz_manager = QuizManager()
        
        # OpenAI API設定
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if self.openai_api_key:
            # APIキーから余分なスペースや改行を削除
            self.openai_api_key = self.openai_api_key.strip()
            openai.api_key = self.openai_api_key
            print(f"✅ OpenAI API設定完了: {self.openai_api_key[:10]}...")
        else:
            print("⚠️ OpenAI APIキーが設定されていません")
        
        # イベントハンドラーを設定
        self.setup_handlers()
        
        print(f"LINE_CHANNEL_ACCESS_TOKEN: {self.channel_access_token}", flush=True)
        print(f"LINE_CHANNEL_SECRET: {self.channel_secret}", flush=True)
        
        # アプリ起動時のダミーpushメッセージ送信
        self.send_startup_activation_message()
    
    def send_startup_activation_message(self):
        """アプリ起動時にダミーのpushメッセージを送信してLINE Botをアクティブ化"""
        try:
            # 環境変数からアクセストークンとユーザーIDを取得
            channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
            activation_user_id = os.getenv('LINE_ACTIVATION_USER_ID')
            
            if not channel_access_token:
                print("⚠️ LINE_CHANNEL_ACCESS_TOKENが設定されていないため、アクティベーション送信をスキップします", flush=True)
                return False
            
            if not activation_user_id:
                print("⚠️ LINE_ACTIVATION_USER_IDが設定されていないため、アクティベーション送信をスキップします", flush=True)
                return False
            
            # LINE Messaging APIのpushエンドポイントにPOSTリクエスト
            url = "https://api.line.me/v2/bot/message/push"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {channel_access_token}"
            }
            
            # アクティベーションメッセージを送信
            activation_data = {
                "to": activation_user_id,
                "messages": [
                    {
                        "type": "text",
                        "text": "🤖 プロンプトエンジニアリング学習Botが起動しました！\n\n毎日3回の学習メッセージと週1回のテストを自動配信します。\n\n何かメッセージを送信すると、学習が始まります！"
                    }
                ]
            }
            
            print(f"🚀 アプリ起動時のアクティベーションメッセージを送信中...", flush=True)
            print(f"📤 送信先ユーザーID: {activation_user_id}", flush=True)
            
            response = requests.post(url, headers=headers, json=activation_data)
            
            if response.status_code == 200:
                print("✅ アクティベーションメッセージの送信に成功しました", flush=True)
                print(f"📊 レスポンス: {response.status_code} - {response.text}", flush=True)
                
                # 既存ユーザー全員にも起動通知を送信
                self.send_startup_notification_to_all_users(channel_access_token, headers)
                
                return True
            else:
                print(f"❌ アクティベーションメッセージの送信に失敗しました", flush=True)
                print(f"📊 ステータスコード: {response.status_code}", flush=True)
                print(f"📊 レスポンス: {response.text}", flush=True)
                return False
                
        except Exception as e:
            print(f"❌ アクティベーションメッセージ送信エラー: {e}", flush=True)
            return False
    
    def send_startup_notification_to_all_users(self, channel_access_token, headers):
        """既存ユーザー全員に起動通知を送信"""
        try:
            # データベースから全ユーザーを取得
            all_users = self.db.get_all_users()
            
            if not all_users:
                print("📝 既存ユーザーが登録されていません", flush=True)
                return
            
            print(f"📤 既存ユーザー {len(all_users)}人に起動通知を送信中...", flush=True)
            
            # 各ユーザーに起動通知を送信
            for user_id in all_users:
                try:
                    notification_data = {
                        "to": user_id,
                        "messages": [
                            {
                                "type": "text",
                                "text": "🔄 プロンプトエンジニアリング学習Botが再起動しました！\n\n学習スケジュールは継続されます。\n\n今夜20時の学習メッセージをお楽しみに！"
                            }
                        ]
                    }
                    
                    response = requests.post("https://api.line.me/v2/bot/message/push", 
                                          headers=headers, json=notification_data)
                    
                    if response.status_code == 200:
                        print(f"✅ ユーザー {user_id} に起動通知を送信しました", flush=True)
                    else:
                        print(f"⚠️ ユーザー {user_id} への起動通知送信に失敗: {response.status_code}", flush=True)
                        
                except Exception as e:
                    print(f"❌ ユーザー {user_id} への起動通知送信エラー: {e}", flush=True)
                    continue
            
            print(f"✅ 起動通知の送信が完了しました（対象: {len(all_users)}人）", flush=True)
            
        except Exception as e:
            print(f"❌ 起動通知送信エラー: {e}", flush=True)
    
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
        
        # ユーザーIDをログ出力（デバッグ用）
        print(f"📱 メッセージ受信 - ユーザーID: {user_id}, メッセージ: {message_text}")
        
        # ユーザーが存在しない場合は追加
        if not self.db.get_user_level(user_id):
            print(f"新規ユーザー検出: {user_id}")
            self.db.add_user(user_id)
        else:
            print(f"既存ユーザー: {user_id}")
        
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
        original_text = message_text.strip()
        message_text = message_text.strip().lower()
        
        # クイズ回答処理（1-4の数字）
        if message_text in ['1', '2', '3', '4']:
            return self.quiz_manager.process_quiz_answer(user_id, message_text)
        
        # コマンド処理（日本語は元のテキストでも比較）
        if message_text == 'help' or original_text == 'ヘルプ':
            return self.get_help_message()
        
        elif message_text == 'progress' or original_text == '進捗':
            return self.learning_manager.get_weekly_summary(user_id)
        
        elif message_text == 'stats' or original_text == '統計':
            return self.quiz_manager.get_quiz_statistics_message(user_id)
        
        elif message_text == 'weak' or original_text == '苦手':
            return self.quiz_manager.get_weak_areas_message(user_id)
        
        elif message_text == 'level' or original_text == 'レベル':
            return self.get_level_message(user_id)
        
        elif message_text == 'lesson' or original_text == 'レッスン':
            return self.request_lesson(user_id)
        
        elif message_text == 'quiz' or original_text == 'クイズ':
            return self.request_quiz(user_id)
        
        elif message_text == 'review' or original_text == '復習':
            return self.request_review(user_id)
        
        elif message_text == 'motivation' or original_text == 'モチベーション':
            return self.learning_manager.get_motivational_message()
        
        elif message_text == 'premium' or original_text == 'プレミアム':
            return self.handle_premium_upgrade(user_id)
        
        elif message_text == 'plan' or original_text == 'プラン':
            return self.get_plan_info(user_id)
        
        else:
            # AI質問回答機能
            return self.handle_ai_question(user_id, original_text)
    
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
        message += "🤖 AI質問機能：\n"
        message += "プロンプトエンジニアリングに関する質問を自由にしてください！\n"
        message += "（無料プラン：1日3回、プレミアム：1日10回）\n\n"
        message += "💎 プレミアム - プレミアムプランの詳細\n"
        message += "📋 プラン - 現在のプラン状況を確認\n\n"
        message += "💡 クイズの回答は「1」「2」「3」「4」で送信してください。"
        
        return message
    
    def check_question_limit(self, user_id):
        """質問回数制限をチェック"""
        try:
            # 今日の質問回数を取得
            today = datetime.now().date()
            daily_count = self.db.get_daily_question_count(user_id, today)
            
            # ユーザーのサブスクリプション状態を取得
            subscription = self.db.get_user_subscription(user_id)
            user_plan = subscription['plan_type']
            question_limit = self.db.get_question_limit_for_user(user_id)
            
            if daily_count >= question_limit:
                if user_plan == "free":
                    return False, f"❌ 無料プランは1日{question_limit}回までです。\n\n💎 プレミアムプランなら1日10回まで質問可能！\n「プレミアム」と送信してアップグレードしませんか？"
                else:
                    return False, f"❌ 本日の質問上限（{question_limit}回）に達しました。\n\n明日またお試しください！"
            
            return True, None
        except Exception as e:
            print(f"質問制限チェックエラー: {e}")
            return True, None
    
    def is_appropriate_question(self, question):
        """質問内容が適切かチェック"""
        inappropriate_keywords = [
            "政治", "宗教", "暴力", "差別", "個人情報", "パスワード", "クレジットカード",
            "政治", "宗教", "暴力", "差別", "個人情報", "パスワード", "クレジットカード",
            "politics", "religion", "violence", "discrimination", "personal info", "password", "credit card"
        ]
        
        question_lower = question.lower()
        for keyword in inappropriate_keywords:
            if keyword in question_lower:
                return False
        
        return True
    
    def handle_ai_question(self, user_id, question):
        """AI質問回答機能"""
        try:
            # 質問制限チェック
            can_ask, limit_message = self.check_question_limit(user_id)
            if not can_ask:
                return limit_message
            
            # 不適切な質問チェック
            if not self.is_appropriate_question(question):
                return "❌ 申し訳ございませんが、その質問にはお答えできません。\n\nプロンプトエンジニアリングやAI活用に関する質問にお答えします。"
            
            # OpenAI APIが利用可能かチェック
            if not self.openai_api_key:
                return "❌ AI回答機能は現在利用できません。\n\nプロンプトエンジニアリングに関する質問は、学習コンテンツで確認してください。"
            
            # 記録前の質問回数を取得
            current_count = self.db.get_daily_question_count(user_id, datetime.now().date())
            print(f"🔍 デバッグ: 記録前の質問回数 = {current_count}")
            
            # 質問回数を記録
            self.db.record_question_asked(user_id)
            print(f"🔍 デバッグ: 質問を記録しました")
            
            # 記録後の質問回数を確認
            after_count = self.db.get_daily_question_count(user_id, datetime.now().date())
            print(f"🔍 デバッグ: 記録後の質問回数 = {after_count}")
            
            # AI回答を生成（記録前の回数を使用）
            response = self.generate_ai_response(user_id, question, current_count)
            
            return response
            
        except Exception as e:
            print(f"AI質問処理エラー: {e}")
            return "❌ 申し訳ございませんが、回答の生成中にエラーが発生しました。\n\nしばらく時間をおいてから再度お試しください。"
    
    def generate_ai_response(self, user_id, question, current_count):
        """AI回答を生成"""
        try:
            # プロンプトエンジニアリングに特化したシステムプロンプト
            system_prompt = """あなたはプロンプトエンジニアリングの専門家です。
以下のガイドラインに従って回答してください：

1. プロンプトエンジニアリングやAI活用に関する質問に専門的に回答
2. 実践的で具体的な例を交えて説明
3. 日本語で丁寧に回答
4. 学習者のレベルに合わせた説明
5. 不適切な内容には回答しない

質問："""

            # OpenAI APIで回答を生成
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # 回答に制限情報を追加（記録前の回数を使用）
            question_limit = self.db.get_question_limit_for_user(user_id)
            remaining = max(0, question_limit - (current_count + 1))  # +1は今回の質問
            subscription = self.db.get_user_subscription(user_id)
            plan_name = "プレミアム" if subscription['plan_type'] == 'premium' else "無料"
            
            print(f"🔍 デバッグ: 計算された残り回数 = {remaining} (current_count={current_count})")
            
            response_with_info = f"🤖 AI回答：\n\n{ai_response}\n\n---\n📊 今日の質問残り回数: {remaining}回（{plan_name}プラン）"
            
            return response_with_info
            
        except Exception as e:
            print(f"AI回答生成エラー: {e}")
            return "❌ AI回答の生成に失敗しました。\n\nプロンプトエンジニアリングに関する質問は、学習コンテンツで確認してください。"
    
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
    
    def handle_premium_upgrade(self, user_id):
        """プレミアムアップグレードを処理"""
        subscription = self.db.get_user_subscription(user_id)
        
        if subscription['plan_type'] == 'premium' and subscription['status'] == 'active':
            return "✅ 既にプレミアムプランをご利用中です！\n\n💎 1日10回まで質問可能\n📚 すべての機能がご利用いただけます"
        
        # Stripe決済リンクを生成
        payment_url = self.generate_stripe_payment_link(user_id)
        
        message = "💎 プレミアムプランのご案内\n\n"
        message += "【特典】\n"
        message += "🔸 AI質問回数: 3回 → 10回/日\n"
        message += "🔸 月額: 480円（税込）\n"
        message += "🔸 いつでもキャンセル可能\n\n"
        message += "【決済方法】\n"
        message += f"以下のリンクからお申し込みください：\n{payment_url}\n\n"
        message += "※決済完了後、すぐにプレミアム機能がご利用いただけます"
        
        return message
    
    def get_plan_info(self, user_id):
        """プラン情報を取得"""
        subscription = self.db.get_user_subscription(user_id)
        today = datetime.now().date()
        daily_count = self.db.get_daily_question_count(user_id, today)
        question_limit = self.db.get_question_limit_for_user(user_id)
        
        if subscription['plan_type'] == 'premium' and subscription['status'] == 'active':
            expires_at = subscription['expires_at']
            message = "💎 プレミアムプランご利用中\n\n"
            message += f"📊 本日の質問回数: {daily_count}/{question_limit}回\n"
            message += f"📅 有効期限: {expires_at}\n\n"
            message += "プレミアムプランの特典:\n"
            message += "🔸 AI質問回数: 10回/日\n"
            message += "🔸 すべての機能が利用可能"
        else:
            message = "📝 無料プランご利用中\n\n"
            message += f"📊 本日の質問回数: {daily_count}/{question_limit}回\n\n"
            message += "💎 プレミアムプランにアップグレードしませんか？\n"
            message += "🔸 AI質問回数: 3回 → 10回/日\n"
            message += "🔸 月額: 480円（税込）\n\n"
            message += "「プレミアム」と送信してお申し込み！"
        
        return message
    
    def generate_stripe_payment_link(self, user_id):
        """Stripe決済リンクを生成"""
        base_url = os.getenv('APP_URL', 'https://your-app.com')
        return f"{base_url}/stripe/checkout?user_id={user_id}"
    
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
            print("Webhook受信: body=", body)
            self.handler.handle(body, signature)
        except InvalidSignatureError:
            print("Invalid signature")
            return False
        except Exception as e:
            print(f"Webhook処理エラー: {e}")
            return False
        
        return True 