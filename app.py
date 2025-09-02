from flask import Flask, request, abort, redirect, render_template_string
import os
from dotenv import load_dotenv
from line_bot import LineBotHandler
from scheduler import LearningScheduler
import threading
import sys
from database import LearningDatabase
from stripe_handler import StripeHandler
from datetime import datetime

# 環境変数を読み込み
load_dotenv()

app = Flask(__name__)

# LINE Botハンドラーを初期化
try:
    line_bot_handler = LineBotHandler()
    print("✅ LINE Botハンドラーを初期化しました")
except Exception as e:
    print(f"❌ LINE Botハンドラーの初期化に失敗しました: {e}")
    print("💡 環境変数が設定されていないため、LINE Bot機能は無効化されます")
    line_bot_handler = None

# Stripeハンドラーを初期化
try:
    stripe_handler = StripeHandler()
    print("✅ Stripeハンドラーを初期化しました")
except Exception as e:
    print(f"❌ Stripeハンドラーの初期化に失敗しました: {e}")
    stripe_handler = None

# スケジューラーを初期化
scheduler = LearningScheduler()

# スケジューラーをバックグラウンドで起動
def start_scheduler_in_background():
    try:
        print("🚀 バックグラウンドでスケジューラーを起動中...")
        scheduler.start()
        print("✅ スケジューラーの起動が完了しました")
        # スケジューラーループを開始
        scheduler.run_scheduler()
    except Exception as e:
        print(f"❌ スケジューラーの開始に失敗しました: {e}")

# Flaskアプリ起動時にスケジューラーを自動起動
print("🔄 スケジューラースレッドを開始中...")
scheduler_thread = threading.Thread(target=start_scheduler_in_background)
scheduler_thread.daemon = True
scheduler_thread.start()
print("✅ スケジューラースレッドを開始しました")

@app.route('/')
def home():
    return "LINE Bot is running!"

@app.route('/privacy')
def privacy():
    return """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>プライバシーポリシー - プロンプト学習支援LINEボット</title>
    <style>
        body {
            font-family: 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #00B900;
            border-bottom: 3px solid #00B900;
            padding-bottom: 10px;
        }
        h2 {
            color: #333;
            margin-top: 30px;
        }
        h3 {
            color: #555;
            margin-top: 20px;
        }
        ul {
            padding-left: 20px;
        }
        li {
            margin-bottom: 8px;
        }
        .highlight {
            background-color: #f0f8ff;
            padding: 15px;
            border-left: 4px solid #00B900;
            margin: 20px 0;
        }
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #666;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>プライバシーポリシー</h1>
        
        <div class="highlight">
            <strong>最終更新日:</strong> 2025年8月1日
        </div>

        <h2>1. 基本方針</h2>
        <p>プロンプト学習支援LINEボット（以下「本サービス」）は、ユーザーの個人情報の保護を最重要事項として取り扱います。</p>

        <h2>2. 収集する個人情報</h2>
        
        <h3>自動収集情報</h3>
        <ul>
            <li>LINEユーザーID</li>
            <li>メッセージ送受信履歴</li>
            <li>学習進捗データ</li>
            <li>クイズ回答履歴</li>
            <li>質問履歴</li>
        </ul>

        <h3>手動収集情報</h3>
        <p>なし（現在のところ）</p>

        <h2>3. 個人情報の使用目的</h2>
        
        <h3>主要な使用目的</h3>
        <ol>
            <li><strong>学習支援サービスの提供</strong>
                <ul>
                    <li>個別学習メッセージの配信</li>
                    <li>学習進捗の管理</li>
                    <li>復習メッセージの提供</li>
                </ul>
            </li>
            <li><strong>サービス改善</strong>
                <ul>
                    <li>機能の最適化</li>
                    <li>ユーザー体験の向上</li>
                    <li>新機能の開発</li>
                </ul>
            </li>
            <li><strong>サポート対応</strong>
                <ul>
                    <li>ユーザーからの問い合わせ対応</li>
                    <li>技術的問題の解決</li>
                </ul>
            </li>
        </ol>

        <h2>4. 個人情報の管理</h2>
        
        <h3>データ保護措置</h3>
        <ul>
            <li>データベースの暗号化</li>
            <li>アクセス権限の制限</li>
            <li>定期的なセキュリティ監査</li>
            <li>バックアップの暗号化</li>
        </ul>

        <h3>データ保存期間</h3>
        <ul>
            <li>サービス利用期間中</li>
            <li>アカウント削除後30日以内に完全削除</li>
        </ul>

        <h2>5. 個人情報の第三者提供</h2>
        
        <h3>提供しない場合</h3>
        <ul>
            <li>ユーザーの同意がない限り、個人情報を第三者に提供しません</li>
            <li>法令に基づく場合を除きます</li>
        </ul>

        <h3>委託先</h3>
        <ul>
            <li><strong>Render.com</strong>: ホスティングサービス</li>
            <li><strong>OpenAI</strong>: AI質問機能</li>
            <li><strong>LINE</strong>: メッセージングサービス</li>
        </ul>

        <h2>6. ユーザーの権利</h2>
        
        <h3>アクセス権</h3>
        <ul>
            <li>ご自身の個人情報の確認</li>
            <li>データの修正・削除要求</li>
        </ul>

        <h3>削除権</h3>
        <ul>
            <li>アカウント削除による全データの削除</li>
            <li>特定データの削除要求</li>
        </ul>

        <h2>7. お問い合わせ</h2>
        
        <h3>個人情報に関するお問い合わせ</h3>
        <ul>
            <li>LINEメッセージでの直接連絡</li>
            <li>プライバシーに関する質問・要望</li>
        </ul>

        <h2>8. 改定について</h2>
        <p>本プライバシーポリシーは、必要に応じて改定される場合があります。改定時は、LINEメッセージでお知らせします。</p>

        <div class="footer">
            <p><strong>制定日:</strong> 2025年8月1日</p>
            <p><strong>最終更新日:</strong> 2025年8月1日</p>
        </div>
    </div>
</body>
</html>
    """

@app.route('/terms')
def terms():
    return """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>利用規約 - プロンプト学習支援LINEボット</title>
    <style>
        body {
            font-family: 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #00B900;
            border-bottom: 3px solid #00B900;
            padding-bottom: 10px;
        }
        h2 {
            color: #333;
            margin-top: 30px;
        }
        h3 {
            color: #555;
            margin-top: 20px;
        }
        ul {
            padding-left: 20px;
        }
        li {
            margin-bottom: 8px;
        }
        .highlight {
            background-color: #f0f8ff;
            padding: 15px;
            border-left: 4px solid #00B900;
            margin: 20px 0;
        }
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #666;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>利用規約</h1>
        
        <div class="highlight">
            <strong>最終更新日:</strong> 2025年8月1日
        </div>

        <h2>1. 総則</h2>
        
        <h3>適用範囲</h3>
        <p>本規約は、プロンプト学習支援LINEボット（以下「本サービス」）の利用に関する条件を定めるものです。</p>

        <h3>規約の変更</h3>
        <p>本規約は、事前の通知なく変更される場合があります。変更後は、LINEメッセージでお知らせします。</p>

        <h2>2. サービスの内容</h2>
        
        <h3>提供サービス</h3>
        <ol>
            <li><strong>学習メッセージ配信</strong>
                <ul>
                    <li>毎日の学習コンテンツ配信</li>
                    <li>個別学習進捗に応じたメッセージ</li>
                </ul>
            </li>
            <li><strong>週間クイズ</strong>
                <ul>
                    <li>学習内容の確認クイズ</li>
                    <li>正答率の記録・分析</li>
                </ul>
            </li>
            <li><strong>AI質問機能</strong>
                <ul>
                    <li>学習に関する質問への回答</li>
                    <li>1日5回までの制限</li>
                </ul>
            </li>
            <li><strong>学習進捗管理</strong>
                <ul>
                    <li>学習履歴の記録</li>
                    <li>復習メッセージの提供</li>
                </ul>
            </li>
        </ol>

        <h2>3. 利用条件</h2>
        
        <h3>利用資格</h3>
        <ul>
            <li>LINEアカウントを保有している方</li>
            <li>本規約に同意する方</li>
            <li>法令に違反しない方</li>
        </ul>

        <h3>禁止事項</h3>
        <p>以下の行為は禁止します：</p>
        <ul>
            <li>法令違反行為</li>
            <li>他のユーザーへの迷惑行為</li>
            <li>システムへの攻撃行為</li>
            <li>不適切な内容の投稿</li>
            <li>営業目的での利用</li>
        </ul>

        <h2>4. 利用料金</h2>
        
        <h3>現在の料金体系</h3>
        <ul>
            <li><strong>基本サービス</strong>: 無料</li>
            <li><strong>追加料金</strong>: なし</li>
        </ul>

        <h3>将来の料金変更</h3>
        <ul>
            <li>料金変更時は事前に通知</li>
            <li>ユーザーの同意を得て変更</li>
        </ul>

        <h2>5. サービスの利用</h2>
        
        <h3>利用時間</h3>
        <ul>
            <li>24時間利用可能</li>
            <li>メンテナンス時は事前通知</li>
        </ul>

        <h3>利用制限</h3>
        <ul>
            <li>1日5回までのAI質問</li>
            <li>適切な利用を心がける</li>
        </ul>

        <h2>6. 免責事項</h2>
        
        <h3>サービスの提供</h3>
        <ul>
            <li>サービスの完全性を保証しません</li>
            <li>予告なくサービスを変更・停止する場合があります</li>
        </ul>

        <h3>データの損失</h3>
        <ul>
            <li>データの損失について責任を負いません</li>
            <li>重要なデータはご自身でバックアップしてください</li>
        </ul>

        <h3>外部サービス</h3>
        <p>LINE、OpenAI等の外部サービスの利用については、各サービスの利用規約に従います</p>

        <h2>7. 知的財産権</h2>
        
        <h3>権利の帰属</h3>
        <ul>
            <li>本サービスの著作権は提供者に帰属</li>
            <li>ユーザーが投稿した内容の権利はユーザーに帰属</li>
        </ul>

        <h3>利用許諾</h3>
        <p>本サービスの利用により、学習コンテンツの利用を許諾</p>

        <h2>8. プライバシー</h2>
        
        <h3>個人情報の取り扱い</h3>
        <ul>
            <li>プライバシーポリシーに従って取り扱います</li>
            <li>詳細は別途プライバシーポリシーをご確認ください</li>
        </ul>

        <h2>9. サービスの停止・終了</h2>
        
        <h3>停止事由</h3>
        <ul>
            <li>システムメンテナンス</li>
            <li>法令違反の疑いがある場合</li>
            <li>その他、運営上必要と判断される場合</li>
        </ul>

        <h3>終了事由</h3>
        <ul>
            <li>サービスの廃止</li>
            <li>利用規約違反</li>
            <li>その他、運営上必要と判断される場合</li>
        </ul>

        <h2>10. 準拠法・管轄裁判所</h2>
        
        <h3>準拠法</h3>
        <p>日本法</p>

        <h3>管轄裁判所</h3>
        <p>東京地方裁判所</p>

        <h2>11. お問い合わせ</h2>
        
        <h3>連絡方法</h3>
        <ul>
            <li>LINEメッセージでの直接連絡</li>
            <li>利用規約に関する質問・要望</li>
        </ul>

        <div class="footer">
            <p><strong>制定日:</strong> 2025年8月1日</p>
            <p><strong>最終更新日:</strong> 2025年8月1日</p>
        </div>
    </div>
</body>
</html>
    """

@app.route('/health')
def health_check():
    """ヘルスチェックエンドポイント（UptimeRobot用）"""
    try:
        # スケジューラーの状態を確認
        scheduler_status = "running" if scheduler.running else "stopped"
        
        # データベースの状態を確認
        db = LearningDatabase()
        user_count = len(db.get_all_users())
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "scheduler": scheduler_status,
            "active_users": user_count,
            "uptime": "online"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }, 500

@app.route('/callback', methods=['POST'])
def callback():
    db = LearningDatabase()  # ここで必ずインスタンス化
    print("==> /callback受信", file=sys.stderr, flush=True)
    if line_bot_handler is None:
        print("line_bot_handler is None!", flush=True)
        abort(500)
    body = request.get_data(as_text=True)
    signature = request.headers.get('X-Line-Signature', '')
    print(f"body: {body}", flush=True)
    print(f"signature: {signature}", flush=True)
    if line_bot_handler.handle_webhook(body, signature):
        print("Webhook処理成功", flush=True)
        return 'OK'
    else:
        print("Webhook処理失敗", flush=True)
        abort(400)

@app.route('/test/lesson/<user_id>')
def test_lesson(user_id):
    """テスト用：レッスンを手動送信"""
    if scheduler.manual_send_lesson(user_id):
        return f"✅ ユーザー {user_id} にレッスンを送信しました"
    else:
        return f"❌ ユーザー {user_id} へのレッスン送信に失敗しました"

@app.route('/test/quiz/<user_id>')
def test_quiz(user_id):
    """テスト用：クイズを手動送信"""
    if scheduler.manual_send_quiz(user_id):
        return f"✅ ユーザー {user_id} にクイズを送信しました"
    else:
        return f"❌ ユーザー {user_id} へのクイズ送信に失敗しました"

@app.route('/status')
def status():
    """システムステータスを表示"""
    if line_bot_handler is None:
        return "❌ LINE Botハンドラーが初期化されていません"
    
    next_tasks = scheduler.get_next_scheduled_tasks()
    
    status_html = """
    <h1>📊 システムステータス</h1>
    <h2>✅ LINE Bot</h2>
    <p>ステータス: 正常</p>
    <h2>📅 スケジュール</h2>
    <ul>
    """
    
    for task in next_tasks:
        status_html += f"<li>{task['function']}: {task['next_run']}</li>"
    
    status_html += """
    </ul>
    <h2>🔧 管理機能</h2>
    <ul>
        <li><a href="/test/lesson/test_user_1">テストレッスン送信</a></li>
        <li><a href="/test/quiz/test_user_1">テストクイズ送信</a></li>
    </ul>
    """
    
    return status_html

@app.route('/start_scheduler')
def start_scheduler():
    """スケジューラーを開始"""
    try:
        scheduler.start()
        return "✅ スケジューラーを開始しました"
    except Exception as e:
        return f"❌ スケジューラーの開始に失敗しました: {e}"

@app.route('/stop_scheduler')
def stop_scheduler():
    """スケジューラーを停止"""
    try:
        scheduler.stop()
        return "⏹️ スケジューラーを停止しました"
    except Exception as e:
        return f"❌ スケジューラーの停止に失敗しました: {e}"

@app.route('/scheduler/status')
def scheduler_status():
    """スケジューラーの詳細ステータスを表示"""
    db = LearningDatabase()  # ここで必ずインスタンス化
    try:
        next_tasks = scheduler.get_next_scheduled_tasks()
        active_users = scheduler.get_active_users()
        
        status_html = """
        <h1>📊 スケジューラー詳細ステータス</h1>
        <h2>📅 スケジュール</h2>
        <ul>
        """
        
        for task in next_tasks:
            status_html += f"<li>{task['function']}: {task['next_run']}</li>"
        
        status_html += f"""
        </ul>
        <h2>👥 アクティブユーザー</h2>
        <p>ユーザー数: {len(active_users)}</p>
        <ul>
        """
        
        for user_id in active_users:
            status_html += f"<li>{user_id}</li>"
        
        status_html += """
        </ul>
        <h2>🔧 管理機能</h2>
        <ul>
            <li><a href="/scheduler/test/04:30">04:30のジョブを手動実行</a></li>
            <li><a href="/scheduler/restart">スケジューラーを再起動</a></li>
        </ul>
        """
        
        users = db.get_all_users()
        print(f"get_all_users返り値: {users}", flush=True)
        
        return status_html
    except Exception as e:
        return f"❌ エラー: {e}"

@app.route('/scheduler/test/<time>')
def test_scheduler_job(time):
    """指定時刻のジョブを手動実行"""
    try:
        if time == "04:30":
            scheduler.send_evening_lesson()
            return "✅ 04:30のジョブを手動実行しました"
        else:
            return f"❌ 未対応の時刻: {time}"
    except Exception as e:
        return f"❌ エラー: {e}"

@app.route('/scheduler/restart')
def restart_scheduler():
    """スケジューラーを再起動"""
    try:
        scheduler.stop()
        scheduler.start()
        return "✅ スケジューラーを再起動しました"
    except Exception as e:
        return f"❌ エラー: {e}"

# Stripeエンドポイント
@app.route('/stripe/checkout')
def stripe_checkout():
    """Stripe Checkoutページにリダイレクト"""
    if not stripe_handler:
        return "❌ Stripe機能が利用できません", 500
    
    user_id = request.args.get('user_id')
    if not user_id:
        return "❌ ユーザーIDが指定されていません", 400
    
    checkout_url = stripe_handler.create_checkout_session(user_id)
    if checkout_url:
        return redirect(checkout_url)
    else:
        return "❌ 決済セッションの作成に失敗しました", 500

@app.route('/stripe/success')
def stripe_success():
    """Stripe決済成功ページ"""
    session_id = request.args.get('session_id')
    
    success_html = """
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>決済完了 - プロンプト学習支援Bot</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                text-align: center; 
                padding: 50px;
                background-color: #f5f5f5;
            }
            .success-container {
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                max-width: 500px;
                margin: 0 auto;
            }
            .success-icon { font-size: 64px; color: #00B900; margin-bottom: 20px; }
            h1 { color: #00B900; }
            p { color: #666; line-height: 1.6; }
            .line-link {
                display: inline-block;
                background: #00B900;
                color: white;
                padding: 15px 30px;
                text-decoration: none;
                border-radius: 5px;
                margin-top: 20px;
            }
        </style>
    </head>
    <body>
        <div class="success-container">
            <div class="success-icon">🎉</div>
            <h1>プレミアムプラン開始！</h1>
            <p>お支払いが正常に完了しました。</p>
            <p>プレミアムプラン（月額480円）が開始されました。</p>
            
            <h3>新しい特典</h3>
            <ul style="text-align: left; margin: 20px 0;">
                <li>🔸 AI質問回数: 3回 → 10回/日</li>
                <li>🔸 すべての機能が利用可能</li>
                <li>🔸 いつでもキャンセル可能</li>
            </ul>
            
            <p>LINE Botで「プラン」と送信して新機能をお試しください！</p>
            
            <a href="#" class="line-link" onclick="window.close()">LINEアプリに戻る</a>
        </div>
    </body>
    </html>
    """
    
    return success_html

@app.route('/stripe/cancel')
def stripe_cancel():
    """Stripe決済キャンセルページ"""
    cancel_html = """
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>決済キャンセル - プロンプト学習支援Bot</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                text-align: center; 
                padding: 50px;
                background-color: #f5f5f5;
            }
            .cancel-container {
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                max-width: 500px;
                margin: 0 auto;
            }
            .cancel-icon { font-size: 64px; color: #999; margin-bottom: 20px; }
            h1 { color: #666; }
            p { color: #666; line-height: 1.6; }
            .line-link {
                display: inline-block;
                background: #00B900;
                color: white;
                padding: 15px 30px;
                text-decoration: none;
                border-radius: 5px;
                margin-top: 20px;
            }
        </style>
    </head>
    <body>
        <div class="cancel-container">
            <div class="cancel-icon">📝</div>
            <h1>決済がキャンセルされました</h1>
            <p>プレミアムプランへのアップグレードがキャンセルされました。</p>
            <p>引き続き無料プラン（1日3回まで質問可能）でご利用いただけます。</p>
            
            <p>プレミアムプランが必要になりましたら、LINE Botで「プレミアム」と送信してください。</p>
            
            <a href="#" class="line-link" onclick="window.close()">LINEアプリに戻る</a>
        </div>
    </body>
    </html>
    """
    
    return cancel_html

@app.route('/stripe/webhook', methods=['POST'])
def stripe_webhook():
    """Stripe Webhookエンドポイント"""
    if not stripe_handler:
        return "❌ Stripe機能が利用できません", 500
    
    payload = request.get_data()
    signature = request.headers.get('Stripe-Signature')
    
    if stripe_handler.handle_webhook(payload, signature):
        return 'OK'
    else:
        abort(400)

if __name__ == '__main__':
    # Flaskアプリケーションを開始
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"🚀 アプリケーションを開始します (ポート: {port})")
    print(f"🌐 ローカルURL: http://localhost:{port}")
    print(f"📱 LINE Webhook URL: http://localhost:{port}/callback")
    print(f"🏥 ヘルスチェック: http://localhost:{port}/health")
    print(f"📊 ステータス: http://localhost:{port}/status")
    
    # 有料プラン対応のログ
    print(f"💎 Render.com有料プラン対応: スリープなし、24時間稼働")
    print(f"📈 リソース強化: メモリ増加、CPU強化")
    
    app.run(host='0.0.0.0', port=port, debug=debug) 