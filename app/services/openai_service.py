from fastapi import WebSocket
from ..adapters.mongo_adapter import MongoAdapter
from ..adapters.openai_adapter import OpenAIAdapter
import asyncio
import json


async def stream_openai(
    websocket: WebSocket,
    openai_adapter: OpenAIAdapter,
    mongo_adapter: MongoAdapter,
):
    while True:
        try:
            if websocket.closed:
                break

            # 1秒待機
            await asyncio.sleep(1)

            # ログを取得
            print("fetch_logs")
            logs = mongo_adapter.fetch_logs()
            if not logs:
                continue

            current_log_count = len(logs)

            # 新しいログが追加された場合
            if current_log_count > openai_adapter.previous_log_count:
                print("current_log_count", current_log_count)
                print("previous_log_count", openai_adapter.previous_log_count)

                openai_adapter.previous_log_count = current_log_count

                # 最新のログを取得
                latest_log = logs[-1]  # すでにdictの場合はjson.loadsは不要
                if isinstance(latest_log, str):
                    latest_log = json.loads(latest_log)

                # OpenAIにストリーミング送信し、完了を待つ
                await openai_adapter.chat(websocket, latest_log)

        except Exception as e:
            print("stream_openai error:", e)
