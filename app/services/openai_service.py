from fastapi import WebSocket
from ..adapters.mongo_adapter import MongoAdapter
from ..adapters.openai_adapter import OpenAIAdapter


async def stream_openai(
    websocket: WebSocket, mongo_adapter: MongoAdapter, openai_adapter: OpenAIAdapter
):
    while True:
        print("Waiting for user message...!!")
        user_message = await websocket.receive_text()
        print(f"Received user message: {user_message}")

        await openai_adapter.stream_chat(websocket, user_message)
