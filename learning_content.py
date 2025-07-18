import json
import random
from datetime import datetime, timedelta
from database import LearningDatabase

class LearningContentManager:
    def __init__(self, learning_data_path="data/learning_data.json"):
        self.learning_data_path = learning_data_path
        self.db = LearningDatabase()
        self.load_learning_data()
    
    def load_learning_data(self):
        """学習データを読み込み"""
        try:
            with open(self.learning_data_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
                # 配列形式のデータをレベル別に分類
                self.learning_data = {"beginner": [], "intermediate": [], "advanced": []}
                
                # すべてのレッスンをbeginnerレベルとして分類（簡易対応）
                for lesson in raw_data:
                    # lesson_idを追加（lessonフィールドから生成）
                    if 'lesson' in lesson:
                        lesson['id'] = lesson['lesson']
                    # contentフィールドを追加（pointフィールドを使用）
                    if 'point' in lesson:
                        lesson['content'] = lesson['point']
                    # levelフィールドを追加
                    lesson['level'] = 'beginner'
                    
                    self.learning_data['beginner'].append(lesson)
                    
        except FileNotFoundError:
            print(f"学習データファイルが見つかりません: {self.learning_data_path}")
            self.learning_data = {"beginner": [], "intermediate": [], "advanced": []}
        except Exception as e:
            print(f"学習データ読み込みエラー: {e}")
            self.learning_data = {"beginner": [], "intermediate": [], "advanced": []}
    
    def get_lesson_by_id(self, lesson_id):
        """IDでレッスンを取得"""
        for level in self.learning_data.values():
            for lesson in level:
                if lesson.get('id') == lesson_id or lesson.get('lesson') == lesson_id:
                    return lesson
        return None
    
    def get_random_lesson(self, level, exclude_ids=None):
        """指定レベルからランダムにレッスンを取得"""
        if exclude_ids is None:
            exclude_ids = []
        
        available_lessons = [
            lesson for lesson in self.learning_data.get(level, [])
            if lesson.get('id') not in exclude_ids and lesson.get('lesson') not in exclude_ids
        ]
        
        if not available_lessons:
            return None
        
        return random.choice(available_lessons)
    
    def get_next_lesson(self, user_id):
        """ユーザーの次のレッスンを取得"""
        user_level = self.db.get_user_level(user_id)
        recent_lessons = self.db.get_recent_lessons(user_id, days=7)
        recent_ids = [lesson[0] for lesson in recent_lessons]
        
        # 復習アイテムを優先
        review_items = self.db.get_review_items(user_id, limit=3)
        if review_items:
            lesson_id = review_items[0][0]
            lesson = self.get_lesson_by_id(lesson_id)
            if lesson:
                return lesson
        
        # 新しいレッスンを取得
        lesson = self.get_random_lesson(user_level, exclude_ids=recent_ids)
        if lesson:
            return lesson
        
        # 最近のレッスンがない場合は、同じレベルから再選択
        return self.get_random_lesson(user_level)
    
    def format_lesson_message(self, lesson):
        """レッスンをメッセージ形式にフォーマット"""
        if not lesson:
            return "今日の学習コンテンツを準備中です..."
        
        message = f"📚 {lesson['title']}\n\n"
        
        # pointフィールドを使用
        if 'point' in lesson:
            message += lesson['point']
        elif 'content' in lesson:
            message += lesson['content']
        else:
            message += "学習コンテンツの詳細がありません。"
        
        # 例文があれば追加
        if 'examples' in lesson and lesson['examples']:
            message += "\n\n📝 例文:\n"
            for i, example in enumerate(lesson['examples'][:3], 1):  # 最大3つまで
                message += f"{i}. {example}\n"
        
        # タグがあれば追加
        if 'tags' in lesson and lesson['tags']:
            message += f"\n🏷️ タグ: {', '.join(lesson['tags'])}"
        
        return message
    
    def send_daily_lesson(self, user_id, line_bot):
        """毎日の学習メッセージを送信"""
        lesson = self.get_next_lesson(user_id)
        if not lesson:
            return False
        
        message = self.format_lesson_message(lesson)
        
        # LINEにメッセージを送信
        try:
            line_bot.push_message(user_id, message)
            
            # データベースに記録
            lesson_id = lesson.get('id') or lesson.get('lesson')
            self.db.record_lesson_sent(user_id, lesson_id, lesson.get('level', 'beginner'))
            
            return True
        except Exception as e:
            print(f"メッセージ送信エラー: {e}")
            return False
    
    def get_level_progress(self, user_id):
        """レベル別の進捗を取得"""
        user_level = self.db.get_user_level(user_id)
        recent_lessons = self.db.get_recent_lessons(user_id, days=30)
        
        level_counts = {}
        for lesson in recent_lessons:
            level = lesson[1]
            level_counts[level] = level_counts.get(level, 0) + 1
        
        return {
            'current_level': user_level,
            'level_counts': level_counts,
            'total_recent': len(recent_lessons)
        }
    
    def should_level_up(self, user_id):
        """レベルアップの判定"""
        progress = self.get_level_progress(user_id)
        quiz_stats = self.db.get_quiz_statistics(user_id, days=30)
        
        if not quiz_stats or quiz_stats[0] < 5:  # テストが5回未満
            return False
        
        accuracy = quiz_stats[2]
        current_level = progress['current_level']
        
        # レベルアップ条件
        if current_level == "beginner" and accuracy >= 80:
            return "intermediate"
        elif current_level == "intermediate" and accuracy >= 85:
            return "advanced"
        
        return False
    
    def get_review_lesson(self, user_id):
        """復習用レッスンを取得"""
        review_items = self.db.get_review_items(user_id, limit=1)
        if not review_items:
            return None
        
        lesson_id = review_items[0][0]
        return self.get_lesson_by_id(lesson_id)
    
    def add_weak_areas_to_review(self, user_id):
        """苦手分野を復習キューに追加"""
        weak_areas = self.db.get_weak_areas(user_id, days=30)
        
        for quiz_id, total_attempts, correct_attempts in weak_areas:
            if total_attempts > 0:
                accuracy = correct_attempts / total_attempts
                if accuracy < 0.7:  # 70%未満の場合
                    # 関連するレッスンを復習キューに追加
                    self.db.add_to_review_queue(
                        user_id, 
                        quiz_id, 
                        "intermediate", 
                        f"テスト正答率{accuracy*100:.1f}%", 
                        priority=2
                    )
    
    def get_weekly_summary(self, user_id):
        """週間学習サマリーを取得"""
        progress = self.db.get_learning_progress(user_id)
        level_progress = self.get_level_progress(user_id)
        
        summary = f"📊 今週の学習サマリー\n\n"
        summary += f"📚 学習回数: {progress['weekly_lessons']}回\n"
        summary += f"🎯 テスト正答率: {progress['quiz_accuracy']:.1f}%\n"
        summary += f"📈 現在のレベル: {level_progress['current_level']}\n"
        
        # レベルアップ判定
        new_level = self.should_level_up(user_id)
        if new_level:
            summary += f"\n🎉 レベルアップ！{new_level}に進級しました！\n"
            self.db.update_user_level(user_id, new_level)
        
        return summary
    
    def get_motivational_message(self):
        """モチベーション向上メッセージを取得"""
        messages = [
            "💪 毎日の小さな積み重ねが、大きな成長につながります！",
            "🚀 今日もプロンプトエンジニアリングのスキルを磨きましょう！",
            "🎯 継続は力なり。今日の学習も頑張りましょう！",
            "🌟 あなたのAI活用力が日々向上しています！",
            "📚 知識は使うことで身につきます。実践を心がけましょう！"
        ]
        return random.choice(messages) 