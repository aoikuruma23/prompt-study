from database import LearningDatabase

# データベースパスを明示的に指定
DB_PATH = "/var/data/learning.db"
db = LearningDatabase(db_path=DB_PATH)

# 登録したいユーザーIDリスト
user_ids = [
    "U21ac96eb410a790216be190966e1dc44",
    "Uc41759cc216a45cc7b8757483d6b10ef"
]

for user_id in user_ids:
    db.add_user(user_id)
    print(f"登録完了: {user_id}") 