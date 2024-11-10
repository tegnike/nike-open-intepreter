from datetime import datetime, timezone, timedelta
import json


def convert_timestamp_to_jst(timestamp_ms):
    # ミリ秒からUTCのdatetimeオブジェクトを作成
    utc_dt = datetime.fromtimestamp(timestamp_ms / 1000, timezone.utc)

    # JSTのタイムゾーンを作成（UTC+9）
    jst = timezone(timedelta(hours=9))

    # UTCからJSTに変換
    jst_dt = utc_dt.astimezone(jst)

    # フォーマット変換（年-月-日 時:分:秒）
    return jst_dt.strftime("%Y-%m-%d %H:%M:%S")


def convert_timestamps_in_json(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if key == "$date" and "$numberLong" in value:
                # numberLongの値を日本時間の文字列に変換
                return convert_timestamp_to_jst(int(value["$numberLong"]))
            elif isinstance(value, (dict, list)):
                data[key] = convert_timestamps_in_json(value)
    elif isinstance(data, list):
        return [convert_timestamps_in_json(item) for item in data]
    return data


# JSONファイルを読み込む
with open("logs.json", "r", encoding="utf-8") as file:
    json_data = json.load(file)

# タイムスタンプを変換
converted_data = convert_timestamps_in_json(json_data)

# 変換後のJSONを整形して書き込む
with open("logs.json", "w", encoding="utf-8") as file:
    json.dump(converted_data, file, ensure_ascii=False, indent=2)
