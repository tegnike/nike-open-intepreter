from fastapi import WebSocket
from ..adapters.mongo_adapter import MongoAdapter
from ..adapters.openai_adapter import OpenAIAdapter
import asyncio
import json
from fastapi import WebSocketDisconnect
from ..services.websocket_service import is_websocket_connected


async def stream_openai(
    websocket: WebSocket,
    openai_adapter: OpenAIAdapter,
    mongo_adapter: MongoAdapter,
):
    while True:
        try:
            # 1秒待機
            await asyncio.sleep(1)

            if not await is_websocket_connected(websocket):
                print("WebSocket connection lost")
                break

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

            # WebSocketメッセージの確認とログの処理を並行して実行
            try:
                message = await asyncio.wait_for(
                    websocket.receive_text(), timeout=0.1  # 100ミリ秒のタイムアウト
                )
                # メッセージを受信した場合の処理をここに書く
                print(f"Received message: {message}")
                await openai_adapter.stream_chat(websocket, message)
            except TimeoutError:
                # タイムアウトは正常なケース - ログの処理を継続
                pass

        except WebSocketDisconnect:
            print("WebSocket disconnected")
            break
        except Exception as e:
            print("stream_openai error:", e)
