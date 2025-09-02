#!/usr/bin/env python3
"""
手動プレミアム登録スクリプト
Webhook問題解決前の動作テスト用
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from database import LearningDatabase
from datetime import datetime

def activate_premium():
    """手動でプレミアム登録を実行"""
    
    user_id = "Uc41759cc216a45cc7b8757483d6b10ef"
    stripe_subscription_id = "sub_test_manual_activation"
    stripe_customer_id = "cus_test_manual_activation"
    
    print("Manual premium registration started...")
    print(f"User ID: {user_id}")
    
    try:
        db = LearningDatabase()
        
        # プレミアムサブスクリプション作成
        success = db.create_premium_subscription(
            user_id=user_id,
            stripe_subscription_id=stripe_subscription_id,
            stripe_customer_id=stripe_customer_id
        )
        
        if success:
            print("Premium registration successful!")
            
            # 確認
            subscription = db.get_user_subscription(user_id)
            print(f"Plan type: {subscription['plan_type']}")
            print(f"Status: {subscription['status']}")
            print(f"Expires: {subscription['expires_at']}")
            
            # 質問制限確認
            limit = db.get_question_limit_for_user(user_id)
            print(f"Question limit: {limit} per day")
            
        else:
            print("Premium registration failed")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    activate_premium()