from database import LearningDatabase

# データベースパスを明示的に指定
DB_PATH = "/var/data/learning.db"
db = LearningDatabase(db_path=DB_PATH)

# 現在登録されているユーザーID（確認済み）
current_users = [
    "U21ac96eb410a790216be190966e1dc44",
    "U278684b7cd562003ae89186f1f1260f3", 
    "Ua8425275d3472f29691848c9978f329f",
    "Uc41759cc216a45cc7b8757483d6b10ef"
]

# 不足しているユーザーID（ここに追加）
missing_users = [
    # 元々7人いたユーザーのうち、不足している3人のユーザーIDをここに追加
    # "不足しているユーザーID1",
    # "不足しているユーザーID2", 
    # "不足しているユーザーID3"
]

# 全ユーザーを登録
all_users = current_users + missing_users

for user_id in all_users:
    db.add_user(user_id)
    print(f"登録完了: {user_id}") 