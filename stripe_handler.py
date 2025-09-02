import os
import stripe
from database import LearningDatabase
from datetime import datetime
import json

class StripeHandler:
    def __init__(self):
        # Stripe APIキーを設定
        stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
        self.webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
        self.price_id = os.getenv('STRIPE_PRICE_ID')  # プレミアムプランの価格ID
        self.db = LearningDatabase()
        
        # 開発環境での設定
        if not stripe.api_key:
            print("⚠️ STRIPE_SECRET_KEYが設定されていません")
        if not self.price_id:
            print("⚠️ STRIPE_PRICE_IDが設定されていません")
    
    def create_checkout_session(self, user_id):
        """Stripe Checkoutセッションを作成"""
        try:
            # 成功/キャンセルURL
            base_url = os.getenv('APP_URL', 'https://your-app.com')
            success_url = f"{base_url}/stripe/success?session_id={{CHECKOUT_SESSION_ID}}"
            cancel_url = f"{base_url}/stripe/cancel"
            
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': self.price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url,
                cancel_url=cancel_url,
                client_reference_id=user_id,  # LINE User IDを保存
                metadata={
                    'line_user_id': user_id
                }
            )
            
            return session.url
            
        except Exception as e:
            print(f"❌ Checkoutセッション作成エラー: {e}")
            return None
    
    def handle_webhook(self, payload, signature):
        """Stripe Webhookを処理"""
        try:
            # Webhookイベントを検証
            event = stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )
            
            print(f"📥 Webhook受信: {event['type']}")
            
            # イベントタイプに応じて処理
            if event['type'] == 'checkout.session.completed':
                self.handle_checkout_completed(event['data']['object'])
            
            elif event['type'] == 'invoice.payment_succeeded':
                self.handle_payment_succeeded(event['data']['object'])
            
            elif event['type'] == 'customer.subscription.deleted':
                self.handle_subscription_cancelled(event['data']['object'])
            
            elif event['type'] == 'invoice.payment_failed':
                self.handle_payment_failed(event['data']['object'])
            
            return True
            
        except ValueError as e:
            print(f"❌ Webhookペイロードエラー: {e}")
            return False
        except stripe.error.SignatureVerificationError as e:
            print(f"❌ Webhook署名検証エラー: {e}")
            return False
        except Exception as e:
            print(f"❌ Webhook処理エラー: {e}")
            return False
    
    def handle_checkout_completed(self, session):
        """チェックアウト完了を処理"""
        try:
            user_id = session.get('client_reference_id') or session.get('metadata', {}).get('line_user_id')
            
            if not user_id:
                print("❌ ユーザーIDが見つかりません")
                return False
            
            # サブスクリプション情報を取得
            subscription_id = session.get('subscription')
            customer_id = session.get('customer')
            
            if subscription_id and customer_id:
                # データベースにプレミアムサブスクリプションを記録
                success = self.db.create_premium_subscription(
                    user_id=user_id,
                    stripe_subscription_id=subscription_id,
                    stripe_customer_id=customer_id
                )
                
                if success:
                    print(f"✅ プレミアムサブスクリプション開始: {user_id}")
                    
                    # 通知メッセージをユーザーに送信（別途実装）
                    self.send_premium_welcome_message(user_id)
                    
                    return True
            
            return False
            
        except Exception as e:
            print(f"❌ チェックアウト完了処理エラー: {e}")
            return False
    
    def handle_payment_succeeded(self, invoice):
        """支払い成功を処理"""
        try:
            subscription_id = invoice.get('subscription')
            
            if subscription_id:
                # サブスクリプション情報を更新
                print(f"✅ 支払い成功: {subscription_id}")
                # 必要に応じて更新処理を実装
                
            return True
            
        except Exception as e:
            print(f"❌ 支払い成功処理エラー: {e}")
            return False
    
    def handle_subscription_cancelled(self, subscription):
        """サブスクリプションキャンセルを処理"""
        try:
            subscription_id = subscription.get('id')
            
            # データベースでサブスクリプションをキャンセル状態に更新
            # user_idを取得するためにデータベースを検索
            import sqlite3
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT user_id FROM premium_subscriptions 
                    WHERE stripe_subscription_id = ?
                ''', (subscription_id,))
                result = cursor.fetchone()
                
                if result:
                    user_id = result[0]
                    self.db.cancel_premium_subscription(user_id, subscription_id)
                    
                    # キャンセル通知をユーザーに送信
                    self.send_cancellation_message(user_id)
                    
                    print(f"✅ サブスクリプションキャンセル: {user_id}")
                    return True
            
            return False
            
        except Exception as e:
            print(f"❌ サブスクリプションキャンセル処理エラー: {e}")
            return False
    
    def handle_payment_failed(self, invoice):
        """支払い失敗を処理"""
        try:
            subscription_id = invoice.get('subscription')
            print(f"⚠️ 支払い失敗: {subscription_id}")
            
            # 必要に応じて通知処理を実装
            return True
            
        except Exception as e:
            print(f"❌ 支払い失敗処理エラー: {e}")
            return False
    
    def send_premium_welcome_message(self, user_id):
        """プレミアムプラン開始通知メッセージを送信"""
        # LINE Bot経由でメッセージ送信（別途実装）
        message = """🎉 プレミアムプランへようこそ！

✅ アップグレードが完了しました

【新しい特典】
🔸 AI質問回数: 3回 → 10回/日
🔸 全機能がご利用可能

💬 早速、プロンプトエンジニアリングについて質問してみませんか？"""
        
        print(f"📤 プレミアム開始通知: {user_id}")
        # 実際のLINE Bot送信は line_bot.py で実装
    
    def send_cancellation_message(self, user_id):
        """キャンセル通知メッセージを送信"""
        message = """📝 プレミアムプランがキャンセルされました

お疲れ様でした。プレミアムプランは現在の期間終了まで引き続きご利用いただけます。

今後は無料プラン（1日3回まで）でのご利用となります。

またのご利用をお待ちしております。"""
        
        print(f"📤 キャンセル通知: {user_id}")
        # 実際のLINE Bot送信は line_bot.py で実装
    
    def get_customer_portal_url(self, user_id):
        """顧客ポータルURLを取得（サブスク管理用）"""
        try:
            subscription = self.db.get_user_subscription(user_id)
            
            if subscription['plan_type'] != 'premium' or not subscription['stripe_subscription_id']:
                return None
            
            # Stripe Customer IDを取得
            import sqlite3
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT stripe_customer_id FROM premium_subscriptions 
                    WHERE user_id = ? AND stripe_subscription_id = ?
                ''', (user_id, subscription['stripe_subscription_id']))
                result = cursor.fetchone()
                
                if not result:
                    return None
                
                customer_id = result[0]
            
            # 顧客ポータルセッションを作成
            base_url = os.getenv('APP_URL', 'https://your-app.com')
            
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=f"{base_url}/",
            )
            
            return session.url
            
        except Exception as e:
            print(f"❌ 顧客ポータルURL作成エラー: {e}")
            return None