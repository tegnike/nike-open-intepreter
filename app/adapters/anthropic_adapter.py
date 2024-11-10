import anthropic
from fastapi import WebSocket
from ..services.websocket_service import send_websocket_message


class AnthropicAdapter:
    def __init__(self):
        self.client = anthropic.Anthropic()

    async def stream_chat(self, websocket: WebSocket, user_message: str):
        await send_websocket_message(websocket, "", "assistant", "start")

        stream = self.client.messages.stream(
            model="claude-3-5-haiku-20241022",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_message},
            ],
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
