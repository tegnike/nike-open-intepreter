from openai import OpenAI
from fastapi import WebSocket
from ..services.websocket_service import send_websocket_message


class OpenAIAdapter:
    def __init__(self):
        self.client = OpenAI()

    async def stream_chat(self, websocket: WebSocket, user_message: str):
        await send_websocket_message(websocket, "", "assistant", "start")

        stream = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_message},
            ],
            stream=True,
        )

        message = ""
        for chunk in stream:
            content = chunk.choices[0].delta.content
            if not isinstance(content, str):
                continue
            message += content
            if (
                message
                and message != ""
                and (
                    len(message) > 15
                    and message[-1] in ["、", "。", "！", "？", "；", "…", "："]
                    or message[-1] == "\n"
                )
            ):
                await send_websocket_message(websocket, message, "assistant")
                message = ""

        if message != "":
            await send_websocket_message(websocket, message, "assistant")
        await send_websocket_message(websocket, "", "assistant", "end")
