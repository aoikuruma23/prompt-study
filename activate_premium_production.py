#!/usr/bin/env python3
"""
本番環境でプレミアム登録を実行するスクリプト
Render.comのデータベースに直接アクセス
"""

import requests
import json

def activate_premium_production():
    """本番環境でプレミアム登録を実行"""
    
    user_id = "Uc41759cc216a45cc7b8757483d6b10ef"
    app_url = "https://prompt-study.onrender.com"
    
    print("Production premium activation started...")
    print(f"User ID: {user_id}")
    print(f"App URL: {app_url}")
    
    # 特別なエンドポイントを作成して本番DBに直接アクセス
    # まずは現在のプラン状態を確認
    try:
        # カスタムエンドポイント作成が必要
        print("Need to create custom endpoint for production DB access...")
        print("Adding admin endpoint to app.py...")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    activate_premium_production()