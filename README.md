# プロンプトエンジニアリング学習LINEアプリ

## 📚 概要
毎日3回の学習メッセージと週1回のテストを自動配信するLINEアプリです。
プロンプトエンジニアリングの知識を段階的に学習できます。

## ⚠️ 重要：Render.com無料プランの制限
**Render.comの無料プランでは15分間アクセスがないと自動的にスリープ状態になります。**

### 解決策：UptimeRobotの設定
1. [UptimeRobot](https://uptimerobot.com/)に無料アカウントで登録
2. 新しいモニターを作成
3. モニタータイプ：HTTP(s)
4. URL：`https://your-app-name.onrender.com/health`
5. チェック間隔：5分
6. これにより15分以内にアクセスが発生し、スリープを防げます

**重要：** `/health`エンドポイントを使用することで、アプリケーションの健全性も同時に監視できます。

### 🚀 アプリ起動時のアクティベーション機能
**Render.comでデプロイ後にLINE Botが「利用されていない」と判断される問題を解決するため、アプリ起動時にダミーのpushメッセージを送信します。**

#### 設定方法：
1. **LINE DevelopersでユーザーIDを取得**
   - LINE Botにメッセージを送信
   - ログでユーザーIDを確認（例：`U1234567890abcdef`）

2. **環境変数に設定**
   - `LINE_ACTIVATION_USER_ID=your_line_user_id_here`
   - Render.comのEnvironmentタブで設定

3. **動作確認**
   - アプリ起動時にアクティベーションメッセージが送信される
   - LINE Botが「利用中」として認識される

#### アクティベーションメッセージ例：
```
🤖 プロンプトエンジニアリング学習Botが起動しました！

毎日3回の学習メッセージと週1回のテストを自動配信します。

何かメッセージを送信すると、学習が始まります！
```

#### 有料プランアップグレード後の設定：
- ✅ **スリープなし** - UptimeRobotの頻繁なチェックは不要
- ✅ **チェック間隔** - 10分に変更可能（より効率的）
- ✅ **ヘルスチェック** - `/health`エンドポイントで詳細監視
- ✅ **アラート設定** - ダウンタイム時の通知設定

### 有料プランへの移行
より安定した運用のため、Render.comの有料プラン（$7/月）への移行を推奨：
- スリープなし
- より多くのリソース
- より安定したパフォーマンス

#### アップグレード手順：
1. **Render.comダッシュボードにアクセス**
   - https://dashboard.render.com/
   - アカウントにログイン

2. **プロジェクトを選択**
   - `prompt-study`プロジェクトをクリック

3. **Instance Type変更**
   - 左サイドバーの「Settings」をクリック
   - 「Instance Type」セクションで「Free」→「Starter」に変更
   - 「Save Changes」をクリック

4. **支払い情報の設定**
   - クレジットカード情報を入力
   - 請求先住所を設定

5. **アップグレード完了**
   - 即座に有料プランに移行
   - スリープ機能が無効化される

#### 有料プランのメリット：
- ✅ **スリープなし** - 24時間稼働
- ✅ **メモリ増加** - 512MB → 1GB
- ✅ **CPU強化** - より高速な処理
- ✅ **同時接続数増加** - より多くのユーザー対応
- ✅ **カスタムドメイン** - 独自ドメイン使用可能
- ✅ **SSL証明書** - 自動更新
- ✅ **バックアップ** - データ保護強化

#### 有料プランでの監視設定：
- ✅ **UptimeRobot不要** - スリープなしのため監視不要
- ✅ **ヘルスチェック** - `/health`エンドポイントで内部監視
- ✅ **ログ監視** - Render.comのログで問題検出
- ✅ **自動復旧** - クラッシュ時の自動再起動

#### トラブルシューティング：
**ステータスが「Live」にならない場合：**

1. **Logsタブの確認**
   - エラーメッセージを確認
   - アプリケーション起動ログを確認

2. **Environmentタブの確認**
   - `LINE_CHANNEL_ACCESS_TOKEN`が設定されているか
   - `LINE_CHANNEL_SECRET`が設定されているか
   - `PORT`環境変数が設定されているか

3. **Settingsタブの確認**
   - Instance Typeが「Starter」になっているか
   - Build Commandが正しく設定されているか

4. **手動再デプロイ**
   - 「Manual Deploy」ボタンをクリック
   - 最新のコードで再デプロイ

5. **ヘルスチェック**
   - `https://prompt-study.onrender.com/health`にアクセス
   - 正常なJSONレスポンスが返ってくるか確認

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