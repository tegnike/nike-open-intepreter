# %%
import os
import json
import datetime
from pymongo import MongoClient
from dotenv import load_dotenv


class MongoAdapter:
    def __init__(self, game_title, save_name, play_target):
        self.load_settings()
        # MongoDB接続
        self.connect_db()
        self.db = self.client[self.app_name]
        self.game_title = game_title
        self.save_name = save_name
        self.set_save(game_title, save_name)
        self.set_target(play_target)

    def load_settings(self):
        load_dotenv()
        self.log_limit = int(os.getenv("LOG_LIMIT", "10"))
        self.user_name = os.getenv("MONGODB_USER_NAME")
        self.password = os.getenv("MONGODB_PASSWORD")
        self.app_name = os.getenv("MONGODB_APP_NAME", "game_logs")

    def connect_db(self):
        connection_string = f"mongodb+srv://{self.user_name}:{self.password}@{self.app_name}.xanhg.mongodb.net/?retryWrites=true&w=majority&appName={self.app_name}"
        self.client = MongoClient(connection_string)

    def disconnect_db(self):
        if hasattr(self, "client"):
            self.client.close()

    def set_save(self, game_title, save_name):
        if game_title not in self.db.list_collection_names():
            self.collection = self.db[game_title]
        else:
            self.collection = self.db[game_title]

        self.current_doc = self.collection.find_one({"save_name": save_name})
        if not self.current_doc:
            self.current_doc = {
                "save_name": save_name,
                "created_at": datetime.datetime.now(datetime.timezone.utc),
                "logs": [],
            }
            self.collection.insert_one(self.current_doc)

    def set_target(self, play_target):
        if not self.current_doc:
            return

        log_entry = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc),
            "event": {"type": "目標更新", "play_target": play_target},
        }

        self.collection.update_one(
            {"save_name": self.save_name},
            {
                "$push": {"logs": log_entry},
                "$set": {"updated_at": datetime.datetime.now(datetime.timezone.utc)},
            },
        )

    def update_log(self, rs, op, bu):
        if not self.current_doc:
            return

        log_entry = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc),
            "event": {
                "type": "プレイログ更新",
                "ai_reasoning": rs,
                "operation_instruction": op,
                "button_commands": ",".join(bu),
            },
        }

        self.collection.update_one(
            {"save_name": self.save_name},
            {
                "$push": {"logs": log_entry},
                "$set": {"updated_at": datetime.datetime.now(datetime.timezone.utc)},
            },
        )

        return json.dumps(log_entry, ensure_ascii=False, indent=2, cls=DateTimeEncoder)

    def fetch_logs(self):
        if not self.current_doc:
            return None

        doc = self.collection.find_one({"save_name": self.save_name})
        if not doc or "logs" not in doc or not doc["logs"]:
            return None

        # 指定件数分のログを取得
        logs = doc["logs"][-self.log_limit :]
        log_list = []
        for log in logs:
            # JSONにダンプ
            text_log = json.dumps(
                log, ensure_ascii=False, indent=2, cls=DateTimeEncoder
            )
            log_list.append(text_log)
        return "\n".join(log_list)


# エンコーダ
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return super().default(obj)


if __name__ == "__main__":
    # テスト用コード
    ma = MongoAdapter("test_game", "test_save", "test_target")
    rs = "test_reasoning"
    op = "test_operation"
    bu = ["button1", "button3"]
    # ログを追加
    ma.update_log(rs, op, bu)
    # ログを取得
    logs = ma.fetch_logs()
    print(logs)
