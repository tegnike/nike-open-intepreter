import json
import asyncio


async def is_websocket_connected(websocket) -> bool:
    """WebSocketの接続状態を確認する"""
    try:
        return websocket and not websocket.client_state.name == "DISCONNECTED"
    except Exception:
        return False


async def send_websocket_message(websocket, message, role, type="", emotion="neutral"):
    if not await is_websocket_connected(websocket):
        print("WebSocket connection is closed or invalid")
        return

    role = "assistant" if role == "message" else role
    if type == "" and message == "":
        print("Can't send message, message is empty.")
        return

    try:
        json_data = json.dumps(
            {"role": role, "text": message, "emotion": emotion, "type": type},
            ensure_ascii=False,
        )
        print(f"Sending message: {json_data}")
        await websocket.send_text(json_data)
        await asyncio.sleep(0.01)
        print("Send complete.")
    except Exception as e:
        print(f"Error sending WebSocket message: {e}")
