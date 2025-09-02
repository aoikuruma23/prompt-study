#!/usr/bin/env python3
"""
Stripe Webhookテスト用スクリプト
実際の決済セッションIDを使ってWebhook処理をテスト
"""

import requests
import json
import os
from datetime import datetime

# 実際の決済セッションID（ログから取得）
SESSION_ID = "cs_live_a1yqHh7xkbURh5bHXbZoJazXkVLtIAYIA7KvlzDzrpojXqOUGwrIwQXBbF"
USER_ID = "Uc41759cc216a45cc7b8757483d6b10ef"
APP_URL = "https://prompt-study.onrender.com"

def test_webhook_manual():
    """手動でWebhook処理をテスト"""
    
    # checkout.session.completed イベントのサンプルペイロード
    test_payload = {
        "id": "evt_test_webhook",
        "object": "event",
        "api_version": "2020-08-27",
        "created": int(datetime.now().timestamp()),
        "data": {
            "object": {
                "id": SESSION_ID,
                "object": "checkout.session",
                "client_reference_id": USER_ID,
                "customer": "cus_test_customer",
                "subscription": "sub_test_subscription",
                "payment_status": "paid",
                "metadata": {
                    "line_user_id": USER_ID
                }
            }
        },
        "livemode": True,
        "pending_webhooks": 1,
        "request": {
            "id": None,
            "idempotency_key": None
        },
        "type": "checkout.session.completed"
    }
    
    print(f"Webhookテスト開始")
    print(f"URL: {APP_URL}/stripe/webhook")
    print(f"User ID: {USER_ID}")
    print(f"Session ID: {SESSION_ID}")
    
    try:
        # Webhookエンドポイントに送信
        response = requests.post(
            f"{APP_URL}/stripe/webhook",
            json=test_payload,
            headers={
                "Content-Type": "application/json",
                "Stripe-Signature": "t=test,v1=test_signature"  # テスト用
            },
            timeout=10
        )
        
        print(f"レスポンス: {response.status_code}")
        print(f"内容: {response.text}")
        
        if response.status_code == 200:
            print("Webhook処理成功！")
        else:
            print(f"Webhook処理失敗: {response.status_code}")
            
    except Exception as e:
        print(f"エラー: {e}")

if __name__ == "__main__":
    test_webhook_manual()