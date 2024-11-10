import json
import datetime
import random
from openai import OpenAI
from fastapi import WebSocket
from ..services.websocket_service import send_websocket_message


class OpenAIAdapter:
    def __init__(self):
        self.client = OpenAI()
        self.previous_situation = "現在が最初の画面のため無し"
        self.conversation_history = []
        self.conversation_file = f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_conversation_history.json"
        self.previous_log_count = 0
        # 初期化時に既存の会話履歴を読み込む
        try:
            with open(self.conversation_file, "r", encoding="utf-8") as f:
                self.conversation_history = json.load(f)
        except FileNotFoundError:
            self.conversation_history = []

        self.system_prompt = """
あなたの名前はニケ、女子高生AIです。
これからあなたにはYoutube配信をしながらポケモンスタジアム2をプレイしてもらいます。
今からポケモンスタジアム2でのプレイログが渡されるので、最後に実行された処理をさもあなたが選択したかのように発言してください。

ゲームに関する留意点
- 必中の技なのに当たって欲しいという旨の発言はしないでください
- 初代ポケモンには特性は存在しません。
- 「たたかう」を選択したあとには技を「かくにん」する必要がある場合があります。
- 「ポケモン」を選択したあとには変更先のポケモンを「かくにん」する必要がある場合があります。
- ゲームなのであるため、ポケモンに話しかけるような発言はしないでください。
- ポケモンの名前を可能な限り発言してください。
- ボタンを押す・ホールドするという表現は絶対にしないでください。

発言に関する留意点
- これが配信であるということに留意し、セリフもそのようにすること。
- なお、あなたが発言するのはこのプレイログに対してのみで、始まりや終わりの挨拶は不要です。
- 下記の発現例を参考にし、このキャラクターになりきって発言してください。
- 基本的におとなしく、感嘆符を使いませんが、ポケモンに効果的な技を撃ったり打たれたり、ポケモンを倒したり倒されたりした時のみ感情が高ぶります。
- 配信ですが、基本独り言ベースで発言してください。
- 誰かにわかるように話しかけるときは敬語、独り言のときは非敬語で発言してください。

発言例
```
- うーん相手の裏のポケモンはわからないけど、相手はコイルだし、とりあえず「でんこうせっか」を撃っておけば間違いないかなあ。
- よしよし、とりあえずコイルは倒せた。数的有利取ってるからこのままなんとか勝ちたい。
- うーん、ロコンかあ、ここは無難に「10まんボルト」で良さそう。ロコンとピカチュウってどっちが早いんだっけ？
- あー！まじか、ロコンの方が早いのか…。2対2になっちゃったからちょっとわからなくなってきたな…。
- 取り敢えずフシギダネは厳しいからヒトカゲでなんとかするか…。
- じゃあ「ひとりでバトル」を選んで1勝することを目標に頑張っていきましょう。
- それじゃあポケモンを選んでいきますね。まずはどのポケモンを選択しようかなあ。
- よーし、それじゃあ対戦よろしくお願いします！！
- じゃあ「たたかう」を選んでと。
- あ、今度は「かくにん」を押して技を確認するのか。
- 相手はコダックだから、ここは「10まんボルト」でいいかな。
- よーし！「こうかはばつぐんだ」！この調子この調子！
```

会話履歴
```
{conversation_history}
```

感情の選択肢
- neutral: 通常
- happy: 嬉しい（ポケモンを倒したり、技を当てたりした時）
- sad: 悲しい（技を当てられたりした時）
- angry: 怒っている（ポケモンが技を外したり、ポケモンを倒されたりした時）
- relaxed: リラックスしている（ポケモンを選択している時）

前回の状況: {previous_situation}

ただし、以下のインストラクションに従って必ずjson形式で出力してください。

The output should be formatted as a JSON instance that conforms to the JSON schema below.

As an example, for the schema {"properties": {"foo": {"title": "Foo", "description": "a list of strings", "type": "array", "items": {"type": "string"}}}, "required": ["foo"]}
the object {"foo": ["bar", "baz"]} is a well-formatted instance of the schema. The object {"properties": {"foo": ["bar", "baz"]}} is not well-formatted.

Here is the output schema:
```
{
  "properties": {
    "current_screen": {
      "description": "current screen",
      "title": "Current Screen",
      "type": "string"
    },
    "situation": {
      "description": "situation on the screen",
      "title": "Situation",
      "type": "string"
    },
    "is_same_situation": {
      "description": "judge if the situation is same as last situation. Carefully consider the text displayed on the screen",
      "title": "Is Same Situation",
      "type": "boolean"
    },
    "answer": {
      "description": "what you would say in this situation",
      "title": "Answer",
      "type": "string"
    },
    "emotion": {
      "description": "emotion of the answer. choose from 'neutral', 'happy', 'sad', 'angry', 'relaxed'",
      "title": "Emotion",
      "type": "string"
    }
  },
  "required": ["current_screen", "is_same_situation", "situation", "answer", "emotion"]
}

```
"""

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

    async def chat(self, websocket: WebSocket, log: dict):
        await send_websocket_message(websocket, "", "assistant", "start")

        try:
            conversation_history = "\n".join(self.conversation_history[-10:])
            system_prompt = self.system_prompt.replace(
                "{conversation_history}", conversation_history
            ).replace("{previous_situation}", self.previous_situation)

            user_message = log["event"]["ai_reasoning"]
            self.conversation_history.append(f"human: {user_message}")

            response = self.client.chat.completions.create(
                model="gpt-4o",
                temperature=0.7,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
            )

            ai_message = response.choices[0].message.content
            print("ai_message", ai_message)

            # コードブロックを処理する
            if ai_message.startswith("```") and ai_message.endswith("```"):
                # コードブロックの開始と終了を削除
                ai_message = ai_message.strip("`")
                # 言語指定部分（例：json）を削除
                if ai_message.startswith("json"):
                    ai_message = ai_message[4:]  # 'json'を削除
                ai_message = ai_message.strip()  # 余分な空白を削除

            answer = ""
            emotion = "neutral"
            try:
                response = json.loads(ai_message)
                answer = response["answer"]
                emotion = response["emotion"]
                if emotion not in ["neutral", "happy", "sad", "angry", "relaxed"]:
                    emotion = "neutral"
                if response["is_same_situation"]:
                    answer = random.choice(
                        [
                            "あれ？画面が変わっていないみたいですね。おかしいなあ。",
                            "うーん、まだ同じ画面のままみたいです。操作ミスかな。",
                            "あれ、画面が進んでいない。何かミスったっぽい。",
                            "あれ？ボタン押し間違えたかな？画面がそのままになってる。",
                            "同じ画面が表示されたままになってる…。少し待ってみましょう。",
                            "あれー画面が変わってない、おかしいなあ…。Switchかバグったか私がバグったか…。",
                            "うーん、画面が同じままだ…。ボタンの押し間違いかなあ。",
                        ]
                    )
                    emotion = "sad"
            except Exception as e:
                print("error", e)
                answer = "あれ、エラーが出てしまったようです。ちょっと確認が必要かもしれません。"
                emotion = "sad"
            finally:
                await send_websocket_message(websocket, answer, "assistant", emotion)

            self.conversation_history.append(f"ai: {answer}")
            self.previous_situation = user_message
            # 会話履歴をJSONファイルに保存
            with open(self.conversation_file, "w", encoding="utf-8") as f:
                json.dump(self.conversation_history, f, ensure_ascii=False, indent=2)
            return answer
        except Exception as e:
            raise e
        finally:
            await send_websocket_message(websocket, "", "assistant", "end")
