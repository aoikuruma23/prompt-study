# プロンプトエンジニアリング学習LINEアプリ

## 📚 概要
毎日3回の学習メッセージと週1回のテストを自動配信するLINEアプリです。
プロンプトエンジニアリングの知識を段階的に学習できます。

## 🎯 機能
- 毎日3回の学習メッセージ配信（10時、15時、20時）
- 週1回の理解度テスト（日曜20時）
- ユーザーの回答履歴管理
- 理解不足項目の自動復習
- 初級→中級→上級の段階的学習

## 🛠 セットアップ

### 1. 環境準備
```bash
# 仮想環境作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係インストール
pip install -r requirements.txt
```

### 2. LINE Developers設定
1. [LINE Developers Console](https://developers.line.biz/)にアクセス
2. 新しいチャネルを作成
3. チャネルアクセストークンを取得
4. Webhook URLを設定

### 3. 環境変数設定
`.env`ファイルを作成し、以下を設定：
```
LINE_CHANNEL_ACCESS_TOKEN=your_channel_access_token
LINE_CHANNEL_SECRET=your_channel_secret
```

### 4. アプリ起動
```bash
python app.py
```

## 📁 プロジェクト構造
```
├── app.py                 # メインアプリケーション
├── line_bot.py           # LINE Bot処理
├── scheduler.py          # スケジューラー
├── database.py           # データベース管理
├── learning_content.py   # 学習コンテンツ
├── quiz_manager.py       # テスト管理
├── data/                 # データファイル
│   ├── learning_data.json
│   └── quiz_data.json
└── database/             # SQLiteデータベース
    └── learning.db
```

## 🚀 開発ロードマップ
1. ✅ LINE Messaging API接続
2. 🔄 定時実行スケジューラー構築
3. 📝 学習コンテンツデータ構造作成
4. 🧪 週1回テスト出題機能実装
5. 📊 進捗・理解度管理と可視化 