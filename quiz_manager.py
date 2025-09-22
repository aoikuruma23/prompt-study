import json
import random
from datetime import datetime, timedelta
from database import LearningDatabase

class QuizManager:
    def __init__(self, quiz_data_path="data/quiz_data.json"):
        self.quiz_data_path = quiz_data_path
        self.db = LearningDatabase()
        self.load_quiz_data()
    
    def load_quiz_data(self):
        """クイズデータを読み込み"""
        try:
            with open(self.quiz_data_path, 'r', encoding='utf-8') as f:
                self.quiz_data = json.load(f)
        except FileNotFoundError:
            print(f"クイズデータファイルが見つかりません: {self.quiz_data_path}")
            self.quiz_data = {"beginner_quiz": [], "intermediate_quiz": [], "advanced_quiz": []}
    
    def get_quiz_by_id(self, quiz_id):
        """IDでクイズを取得"""
        for level_quizzes in self.quiz_data.values():
            for quiz in level_quizzes:
                if quiz['id'] == quiz_id:
                    return quiz
        return None
    
    def get_weekly_quiz(self, user_id):
        """ユーザーのレベルに応じた週間クイズを取得し、出題IDを保存"""
        user_level = self.db.get_user_level(user_id)
        if user_level == "beginner":
            quiz_set = "beginner_quiz"
        elif user_level == "intermediate":
            quiz_set = "intermediate_quiz"
        else:
            quiz_set = "advanced_quiz"
        available_quizzes = self.quiz_data.get(quiz_set, [])
        if not available_quizzes:
            return None
        quiz = random.choice(available_quizzes)
        # 出題したクイズIDを保存
        self.db.set_last_quiz_id(user_id, quiz['id'])
        return quiz
    
    def format_quiz_message(self, quiz):
        """クイズをメッセージ形式にフォーマット"""
        if not quiz:
            return "今週のクイズを準備中です..."
        
        message = f"🧪 今週のクイズ\n\n"
        message += f"❓ {quiz['question']}\n\n"
        
        # 選択肢を追加
        for i, option in enumerate(quiz['options']):
            message += f"{i+1}. {option}\n"
        
        message += f"\n📝 回答は「1」「2」「3」「4」で送信してください。"
        
        return message
    
    def send_weekly_quiz(self, user_id, line_bot):
        """週間クイズを送信"""
        quiz = self.get_weekly_quiz(user_id)
        if not quiz:
            return False
        
        message = self.format_quiz_message(quiz)
        
        try:
            line_bot.push_message(user_id, message)
            return True
        except Exception as e:
            print(f"クイズ送信エラー: {e}")
            return False
    
    def process_quiz_answer(self, user_id, answer_text, line_bot=None):
        """クイズの回答を処理し、昇格判定も行う。出題時のクイズIDで判定"""
        try:
            user_answer = int(answer_text) - 1  # 0ベースに変換
        except ValueError:
            return "❌ 1〜4の数字で回答してください。"
        if user_answer < 0 or user_answer > 3:
            return "❌ 1〜4の数字で回答してください。"
        # 直近出題したクイズIDを取得
        quiz_id = self.db.get_last_quiz_id(user_id)
        quiz = self.get_quiz_by_id(quiz_id) if quiz_id else None
        if not quiz:
            return "❌ 有効なクイズが見つかりません。再度クイズを受けてください。"
        # 結果を記録
        self.db.record_quiz_result(
            user_id, 
            quiz['id'], 
            user_answer, 
            quiz['correct_answer']
        )
        # 結果メッセージを作成
        is_correct = user_answer == quiz['correct_answer']
        if is_correct:
            message = "✅ 正解です！\n\n"
        else:
            message = f"❌ 不正解です。\n正解は {quiz['correct_answer'] + 1} でした。\n\n"
        message += f"💡 解説：\n{quiz['explanation']}"
        # 昇格判定：10回正解でレベルアップ
        stats = self.db.get_quiz_statistics(user_id, days=365)
        if stats and is_correct:
            total_quizzes, correct_answers, _ = stats
            user_level = self.db.get_user_level(user_id)
            if user_level == "beginner" and correct_answers >= 10:
                self.db.update_user_level(user_id, "intermediate")
                message += f"\n\n🎉 おめでとうございます！{correct_answers}回正解達成で中級レベルに昇格しました！"
                if line_bot:
                    line_bot.push_message(user_id, f"🎉 おめでとうございます！{correct_answers}回正解達成で中級レベルに昇格しました！")
            elif user_level == "intermediate" and correct_answers >= 10:
                self.db.update_user_level(user_id, "advanced")
                message += f"\n\n🎉 素晴らしい！{correct_answers}回正解達成で上級レベルに昇格しました！"
                if line_bot:
                    line_bot.push_message(user_id, f"🎉 素晴らしい！{correct_answers}回正解達成で上級レベルに昇格しました！")
        return message
    
    def get_quiz_statistics_message(self, user_id):
        """クイズ統計メッセージを取得"""
        stats = self.db.get_quiz_statistics(user_id, days=30)
        
        if not stats or stats[0] == 0:
            return "📊 まだクイズに回答していません。週間クイズに参加してみましょう！"
        
        total_quizzes, correct_answers, accuracy = stats
        
        message = f"📊 クイズ統計（過去30日）\n\n"
        message += f"📝 回答数: {total_quizzes}問\n"
        message += f"✅ 正解数: {correct_answers}問\n"
        message += f"🎯 正答率: {accuracy:.1f}%\n\n"
        
        if accuracy >= 90:
            message += "🌟 素晴らしい成績です！"
        elif accuracy >= 70:
            message += "👍 良い成績です！"
        else:
            message += "💪 復習を頑張りましょう！"
        
        return message
    
    def get_weak_areas_message(self, user_id):
        """苦手分野のメッセージを取得"""
        weak_areas = self.db.get_weak_areas(user_id, days=30)
        
        if not weak_areas:
            return "🎉 苦手分野はありません！素晴らしいです！"
        
        message = "📚 復習が必要な分野：\n\n"
        
        for quiz_id, total_attempts, correct_attempts in weak_areas[:3]:  # 上位3つ
            accuracy = (correct_attempts / total_attempts) * 100
            quiz = self.get_quiz_by_id(quiz_id)
            
            if quiz:
                message += f"• {quiz['question'][:30]}...\n"
                message += f"  正答率: {accuracy:.1f}%\n\n"
        
        message += "💡 これらの分野を重点的に復習しましょう！"
        
        return message
    
    def should_send_review_quiz(self, user_id):
        """復習クイズを送信すべきか判定"""
        stats = self.db.get_quiz_statistics(user_id, days=7)
        
        if not stats or stats[0] < 2:  # 1週間で2問未満
            return False
        
        accuracy = stats[2]
        return accuracy < 70  # 70%未満の場合
    
    def get_review_quiz(self, user_id):
        """復習用クイズを取得"""
        weak_areas = self.db.get_weak_areas(user_id, days=30)
        
        if not weak_areas:
            return None
        
        # 最も正答率の低いクイズを選択
        weakest_quiz_id = weak_areas[0][0]
        return self.get_quiz_by_id(weakest_quiz_id)
    
    def format_review_quiz_message(self, quiz):
        """復習クイズをメッセージ形式にフォーマット"""
        if not quiz:
            return "復習クイズを準備中です..."
        
        message = f"🔄 復習クイズ\n\n"
        message += f"❓ {quiz['question']}\n\n"
        
        for i, option in enumerate(quiz['options']):
            message += f"{i+1}. {option}\n"
        
        message += f"\n📝 回答は「1」「2」「3」「4」で送信してください。"
        
        return message 