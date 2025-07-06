from flask import Flask, request, abort
import os
from dotenv import load_dotenv
from line_bot import LineBotHandler
from scheduler import LearningScheduler
import threading

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

# スケジューラーを初期化
scheduler = LearningScheduler()

# スケジューラーをバックグラウンドで起動
def start_scheduler_in_background():
    try:
        scheduler.start()
    except Exception as e:
        print(f"❌ スケジューラーの開始に失敗しました: {e}")

# Flaskアプリ起動時にスケジューラーを自動起動
scheduler_thread = threading.Thread(target=start_scheduler_in_background)
scheduler_thread.daemon = True
scheduler_thread.start()

@app.route('/')
def index():
    """ホームページ"""
    return """
    <h1>🤖 プロンプトエンジニアリング学習LINE Bot</h1>
    <p>毎日3回の学習メッセージと週1回のテストを自動配信します。</p>
    <h2>📅 スケジュール</h2>
    <ul>
        <li>毎日 10:00, 15:00, 20:00: 学習メッセージ</li>
        <li>日曜 20:00: 週間クイズ</li>
        <li>土曜 21:00: 週間サマリー</li>
        <li>水曜 19:00: 復習リマインダー</li>
    </ul>
    <h2>📝 利用可能なコマンド</h2>
    <ul>
        <li>レッスン - 学習コンテンツを表示</li>
        <li>クイズ - 理解度テストを開始</li>
        <li>復習 - 復習コンテンツを表示</li>
        <li>進捗 - 学習進捗を確認</li>
        <li>統計 - テスト結果を確認</li>
        <li>苦手 - 苦手分野を確認</li>
        <li>レベル - 現在のレベルを確認</li>
        <li>モチベーション - 励ましメッセージ</li>
        <li>ヘルプ - ヘルプを表示</li>
    </ul>
    """

@app.route('/callback', methods=['POST'])
def callback():
    """LINE Webhookエンドポイント"""
    if line_bot_handler is None:
        abort(500)
    
    # リクエストボディを取得
    body = request.get_data(as_text=True)
    
    # 署名を取得
    signature = request.headers.get('X-Line-Signature', '')
    
    # Webhookを処理
    if line_bot_handler.handle_webhook(body, signature):
        return 'OK'
    else:
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

if __name__ == '__main__':
    # Flaskアプリケーションを開始
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"🚀 アプリケーションを開始します (ポート: {port})")
    print(f"🌐 ローカルURL: http://localhost:{port}")
    print(f"📱 LINE Webhook URL: http://localhost:{port}/callback")
    
    app.run(host='0.0.0.0', port=port, debug=debug) 