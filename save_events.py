import json
import time
from app.adapters.mongo_adapter import MongoAdapter

# 定数定義
GAME_TITLE = "nike_test"
SAVE_NAME = "save6"
PLAY_TARGET = "「とにかくバトルがしたい！」モードで1勝する"


def load_events():
    """イベントデータをJSONファイルから読み込む"""
    with open("events.json", "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    # MongoAdapterのインスタンス作成
    mongo = MongoAdapter(GAME_TITLE, SAVE_NAME, PLAY_TARGET)

    # イベントデータ読み込み
    events = load_events()

    try:
        # 15秒毎にイベントを1つずつ保存
        for event in events:
            # イベントデータから必要な情報を抽出
            reasoning = event.get("ai_reasoning", "")
            operation = ""  # events.jsonには operation_instruction が含まれていないため空文字を設定
            buttons = []  # events.jsonには button_commands が含まれていないため空リストを設定

            # MongoDBに保存
            mongo.update_log(reasoning, operation, buttons)
            print(f"Saved event: {reasoning[:50]}...")  # 最初の50文字のみ表示

            # 次のイベントまで15秒待機
            time.sleep(15)

        print("All events have been saved successfully!")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

    finally:
        # DB接続を閉じる
        mongo.disconnect_db()


if __name__ == "__main__":
    main()
