#!/usr/bin/env python3
"""
シンプルなプレミアム機能テスト
"""

import sqlite3
from datetime import datetime, timedelta
import os

def test_premium():
    """プレミアム機能を直接テスト"""
    
    user_id = "Uc41759cc216a45cc7b8757483d6b10ef"
    db_path = os.path.abspath("database/learning.db")
    
    print(f"Testing premium functionality...")
    print(f"User ID: {user_id}")
    print(f"DB Path: {db_path}")
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # 現在のサブスクリプション状態確認
            cursor.execute('''
                SELECT plan_type, status, expires_at 
                FROM premium_subscriptions 
                WHERE user_id = ? AND status = 'active'
                ORDER BY created_at DESC LIMIT 1
            ''', (user_id,))
            
            result = cursor.fetchone()
            
            if result:
                print(f"Current plan: {result[0]}")
                print(f"Status: {result[1]}")
                print(f"Expires: {result[2]}")
                
                # 質問制限確認
                if result[0] == 'premium':
                    print("Question limit: 10 per day")
                else:
                    print("Question limit: 3 per day")
            else:
                print("No premium subscription found - using free plan")
                print("Question limit: 3 per day")
                
                # プレミアム登録を作成
                print("Creating premium subscription...")
                
                started_at = datetime.now()
                expires_at = started_at + timedelta(days=30)
                
                cursor.execute('''
                    INSERT INTO premium_subscriptions 
                    (user_id, stripe_subscription_id, stripe_customer_id, plan_type, status, started_at, expires_at)
                    VALUES (?, ?, ?, 'premium', 'active', ?, ?)
                ''', (user_id, 'sub_manual_test', 'cus_manual_test', started_at, expires_at))
                
                conn.commit()
                print("Premium subscription created successfully!")
                print("Question limit now: 10 per day")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_premium()