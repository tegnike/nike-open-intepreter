import json


def extract_events(json_file_path):
    # JSONファイルを読み込む
    with open(json_file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    # eventの内容から特定のキーを除外して抽出
    events = []
    for log in data["logs"]:
        event = log["event"].copy()
        # 指定されたキーを削除
        event.pop("operation_instruction", None)
        event.pop("button_commands", None)
        events.append(event)

    # 結果をJSONファイルとして保存
    output_path = "events.json"
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(events, file, ensure_ascii=False, indent=2)

    print(f"イベントを {output_path} に保存しました")


# 実行
extract_events("logs.json")
