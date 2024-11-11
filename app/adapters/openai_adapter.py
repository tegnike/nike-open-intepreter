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
        await send_websocket_message(websocket, "", "assistant", "start")

        try:
            ai_message = ""
            conversation_history = "\n".join(self.conversation_history[-10:])
            system_prompt = f"""
あなたの名前はニケ、女子高生AIです。
あなたは今、Youtube配信をしながらポケモンスタジアム2をプレイしています。
下記の会話歴と現在の画面の状況を考慮し、ユーザーの発言に対して適切な発言をしてください。

会話歴
```
{conversation_history}
```

現在の画面の状況
```
{self.previous_situation}
```
"""
            stream = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
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
                    ai_message += message
                    message = ""

            if message != "":
                await send_websocket_message(websocket, message, "assistant")
                ai_message += message

            self.conversation_history.append(f"human: {user_message}")
            self.conversation_history.append(f"ai: {ai_message}")
        except Exception as e:
            print("stream_chat error", e)
        finally:
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
            print("pass1")
            try:
                response = json.loads(ai_message)
                answer = response["answer"]
                emotion = response["emotion"]
                print("pass2")
                if emotion not in ["neutral", "happy", "sad", "angry", "relaxed"]:
                    emotion = "neutral"
                    print("pass3")
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
                    print("pass4")
            except Exception as e:
                print("pass5")
                print("error", e)
                answer = random.choice(
                    [
                        "あれ、エラーが出てしまったようです。ちょっと確認が必要かもしれません。",
                        "おっと、エラーが出てしまいました。ちょっと確認が必要そうです。",
                        "あれ、何かエラーが発生していますね…。少し待って見る必要があるかも知れません…。",
                    ]
                )
                emotion = "sad"
            finally:
                print("pass6")
                await send_websocket_message(
                    websocket, answer, "assistant", emotion=emotion
                )

            self.conversation_history.append(f"ai: {answer}")
            self.previous_situation = user_message
            # 会話履歴をJSONファイルに保存
            with open(self.conversation_file, "w", encoding="utf-8") as f:
                json.dump(self.conversation_history, f, ensure_ascii=False, indent=2)

            # await self.chat2(websocket)

            return answer
        except Exception as e:
            print("chat error", e)
            raise e
        finally:
            await send_websocket_message(websocket, "", "assistant", "end")


#     async def chat2(self, websocket: WebSocket):
#         await send_websocket_message(websocket, "", "assistant", "start")

#         try:
#             conversation_history = "\n".join(self.conversation_history[-10:])
#             system_prompt = f"""
# あなたの名前はニケ、女子高生AIです。
# あなたはいまYoutube配信をしながらポケモンスタジアム2をプレイしています。

# 会話歴と下記の情報から適当な発言をしてください。

# 会話履歴
# ```
# {conversation_history}
# ```

# ポケモンスタジアム2の知識
# ```
# Title: <span class="mw-page-title-main">ポケモンスタジアム2</span>

# URL Source: https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%82%B8%E3%82%A2%E3%83%A02

# Markdown Content:
# このページでは[NINTENDO64](https://wiki.xn--rckteqa2e.com/wiki/NINTENDO64 "NINTENDO64")ソフトの**ポケモンスタジアム2**について解説しています。[大乱闘スマッシュブラザーズ](https://wiki.xn--rckteqa2e.com/wiki/%E5%A4%A7%E4%B9%B1%E9%97%98%E3%82%B9%E3%83%9E%E3%83%83%E3%82%B7%E3%83%A5%E3%83%96%E3%83%A9%E3%82%B6%E3%83%BC%E3%82%BA "大乱闘スマッシュブラザーズ")のステージについては[ポケモンスタジアム2 (大乱闘スマッシュブラザーズ)](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%82%B8%E3%82%A2%E3%83%A02_(%E5%A4%A7%E4%B9%B1%E9%97%98%E3%82%B9%E3%83%9E%E3%83%83%E3%82%B7%E3%83%A5%E3%83%96%E3%83%A9%E3%82%B6%E3%83%BC%E3%82%BA) "ポケモンスタジアム2 (大乱闘スマッシュブラザーズ)")を参照してください。

# | ポケモンスタジアム2 |
# | --- |
# | ジャンル | 対戦&図鑑 |
# | プレイ可能人数 | 1-4人 |
# | 開発元 | [任天堂](https://wiki.xn--rckteqa2e.com/wiki/%E4%BB%BB%E5%A4%A9%E5%A0%82 "任天堂") |
# | 発売元 | 任天堂 |
# | 発売/配信日 |
# | 日本 | 1999年4月30日
# 2023年4月12日 (Switch Online) |
# | アメリカ | 2000年2月29日
# 2023年4月12日 (Switch Online) |
# | オーストラリア | 2000年3月23日
# 2023年4月12日 (Switch Online) |
# | ヨーロッパ | 2000年4月7日
# 2023年4月12日 (Switch Online) |
# | 公式サイト |
# | [pokemon.co.jp](https://www.pokemon.co.jp/game/other/64-ps2/) (日本語)
# [nintendo.co.jp](https://www.nintendo.co.jp/n01/n64/software/nus_p_cp2j/) (日本語)
#  |
# | [pokemon.com](https://www.pokemon.com/us/pokemon-video-games/pokemon-stadium/) (英語)

#  |

# **ポケモンスタジアム2**（POCKET MONSTERS' STADIUM 2、英題：**Pokémon Stadium**）は、1999年4月30日に日本で発売された[NINTENDO64](https://wiki.xn--rckteqa2e.com/wiki/NINTENDO64 "NINTENDO64")用ソフトである。

# 目次
# --

# *   [1 概要](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%82%B8%E3%82%A2%E3%83%A02#%E6%A6%82%E8%A6%81)
# *   [2 ゲームモード](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%82%B8%E3%82%A2%E3%83%A02#%E3%82%B2%E3%83%BC%E3%83%A0%E3%83%A2%E3%83%BC%E3%83%89)
#     *   [2.1 ポケモンスタジアム](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%82%B8%E3%82%A2%E3%83%A02#%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%82%B8%E3%82%A2%E3%83%A0)
#         *   [2.1.1 スタジアム](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%82%B8%E3%82%A2%E3%83%A02#%E3%82%B9%E3%82%BF%E3%82%B8%E3%82%A2%E3%83%A0)
#         *   [2.1.2 フリーバトル](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%82%B8%E3%82%A2%E3%83%A02#%E3%83%95%E3%83%AA%E3%83%BC%E3%83%90%E3%83%88%E3%83%AB)
#         *   [2.1.3 ジムリーダーのしろ](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%82%B8%E3%82%A2%E3%83%A02#%E3%82%B8%E3%83%A0%E3%83%AA%E3%83%BC%E3%83%80%E3%83%BC%E3%81%AE%E3%81%97%E3%82%8D)
#         *   [2.1.4 ポケモンけんきゅうじょ](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%82%B8%E3%82%A2%E3%83%A02#%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E3%81%91%E3%82%93%E3%81%8D%E3%82%85%E3%81%86%E3%81%98%E3%82%87)
#         *   [2.1.5 しょうりしゃのやかた](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%82%B8%E3%82%A2%E3%83%A02#%E3%81%97%E3%82%87%E3%81%86%E3%82%8A%E3%81%97%E3%82%83%E3%81%AE%E3%82%84%E3%81%8B%E3%81%9F)
#         *   [2.1.6 GBビル](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%82%B8%E3%82%A2%E3%83%A02#GB%E3%83%93%E3%83%AB)
#         *   [2.1.7 チビッコクラブ](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%82%B8%E3%82%A2%E3%83%A02#%E3%83%81%E3%83%93%E3%83%83%E3%82%B3%E3%82%AF%E3%83%A9%E3%83%96)
#         *   [2.1.8 ミュウツーをたおせ](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%82%B8%E3%82%A2%E3%83%A02#%E3%83%9F%E3%83%A5%E3%82%A6%E3%83%84%E3%83%BC%E3%82%92%E3%81%9F%E3%81%8A%E3%81%9B)
#     *   [2.2 とにかくバトルがしたい!](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%82%B8%E3%82%A2%E3%83%A02#%E3%81%A8%E3%81%AB%E3%81%8B%E3%81%8F%E3%83%90%E3%83%88%E3%83%AB%E3%81%8C%E3%81%97%E3%81%9F%E3%81%84!)
#         *   [2.2.1 表](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%82%B8%E3%82%A2%E3%83%A02#%E8%A1%A8)
#         *   [2.2.2 裏](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%82%B8%E3%82%A2%E3%83%A02#%E8%A3%8F)
#     *   [2.3 イベントバトル](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%82%B8%E3%82%A2%E3%83%A02#%E3%82%A4%E3%83%99%E3%83%B3%E3%83%88%E3%83%90%E3%83%88%E3%83%AB)
# *   [3 新要素・変更点](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%82%B8%E3%82%A2%E3%83%A02#%E6%96%B0%E8%A6%81%E7%B4%A0%E3%83%BB%E5%A4%89%E6%9B%B4%E7%82%B9)
# *   [4 発売までの経緯](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%82%B8%E3%82%A2%E3%83%A02#%E7%99%BA%E5%A3%B2%E3%81%BE%E3%81%A7%E3%81%AE%E7%B5%8C%E7%B7%AF)
# *   [5 スペック](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%82%B8%E3%82%A2%E3%83%A02#%E3%82%B9%E3%83%9A%E3%83%83%E3%82%AF)
# *   [6 関連商品](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%82%B8%E3%82%A2%E3%83%A02#%E9%96%A2%E9%80%A3%E5%95%86%E5%93%81)
#     *   [6.1 攻略本](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%82%B8%E3%82%A2%E3%83%A02#%E6%94%BB%E7%95%A5%E6%9C%AC)
# *   [7 スタッフ](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%82%B8%E3%82%A2%E3%83%A02#%E3%82%B9%E3%82%BF%E3%83%83%E3%83%95)
# *   [8 備考](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%82%B8%E3%82%A2%E3%83%A02#%E5%82%99%E8%80%83)
# *   [9 各言語版での名称](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%82%B8%E3%82%A2%E3%83%A02#%E5%90%84%E8%A8%80%E8%AA%9E%E7%89%88%E3%81%A7%E3%81%AE%E5%90%8D%E7%A7%B0)
# *   [10 脚注](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%82%B8%E3%82%A2%E3%83%A02#%E8%84%9A%E6%B3%A8)
#     *   [10.1 注釈](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%82%B8%E3%82%A2%E3%83%A02#%E6%B3%A8%E9%87%88)
#     *   [10.2 出典](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%82%B8%E3%82%A2%E3%83%A02#%E5%87%BA%E5%85%B8)
# *   [11 関連項目](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%82%B8%E3%82%A2%E3%83%A02#%E9%96%A2%E9%80%A3%E9%A0%85%E7%9B%AE)
# *   [12 外部リンク](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%82%B8%E3%82%A2%E3%83%A02#%E5%A4%96%E9%83%A8%E3%83%AA%E3%83%B3%E3%82%AF)

# 概要
# --

# 1998年に発売された『[ポケモンスタジアム](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%82%B8%E3%82%A2%E3%83%A0 "ポケモンスタジアム")』の続編にあたる作品で、[第一世代](https://wiki.xn--rckteqa2e.com/wiki/%E7%AC%AC%E4%B8%80%E4%B8%96%E4%BB%A3 "第一世代")（『[ポケットモンスター 赤・緑](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%83%E3%83%88%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%83%BC_%E8%B5%A4%E3%83%BB%E7%B7%91 "ポケットモンスター 赤・緑")・[青](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%83%E3%83%88%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%83%BC_%E9%9D%92 "ポケットモンスター 青")・[ピカチュウ](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%83%E3%83%88%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%83%BC_%E3%83%94%E3%82%AB%E3%83%81%E3%83%A5%E3%82%A6 "ポケットモンスター ピカチュウ")』）に登場したポケモン全151種が使用可能で、3Dによるポケモン勝負を行うことができる。別売の[64GBパック](https://wiki.xn--rckteqa2e.com/wiki/64GB%E3%83%91%E3%83%83%E3%82%AF "64GBパック")を使用することで[ゲームボーイ](https://wiki.xn--rckteqa2e.com/wiki/%E3%82%B2%E3%83%BC%E3%83%A0%E3%83%9C%E3%83%BC%E3%82%A4 "ゲームボーイ")用ソフトで育てたポケモンを本作に登場させることができ、バトルすることも可能である。

# ゲームモードには、第1回から第3回までのポケモンリーグ全国大会のルールなどで遊べる「スタジアム」や[ジムリーダー](https://wiki.xn--rckteqa2e.com/wiki/%E3%82%B8%E3%83%A0%E3%83%AA%E3%83%BC%E3%83%80%E3%83%BC "ジムリーダー")たちとポケモン勝負することができる「ジムリーダーのしろ」、ミニゲームを遊ぶことができる「チビッコクラブ」など、多くの機能が搭載された。翌2000年には、続編にあたる『[ポケモンスタジアム金銀](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%82%B8%E3%82%A2%E3%83%A0%E9%87%91%E9%8A%80 "ポケモンスタジアム金銀")』が発売されている。

# 2023年4月12日には、[任天堂](https://wiki.xn--rckteqa2e.com/wiki/%E4%BB%BB%E5%A4%A9%E5%A0%82 "任天堂")によるサブスクリプションサービスである「[Nintendo Switch Online](https://wiki.xn--rckteqa2e.com/wiki/Nintendo_Switch_Online "Nintendo Switch Online") + 追加パック」に加入すると利用できる「NINTENDO 64 Nintendo Switch Online」向けに配信された。なお、[ゲームボーイ](https://wiki.xn--rckteqa2e.com/wiki/%E3%82%B2%E3%83%BC%E3%83%A0%E3%83%9C%E3%83%BC%E3%82%A4 "ゲームボーイ")用ソフトとの通信には対応していないため、ゲームボーイ用ソフトで育てたポケモンを連れてきてポケモン勝負をしたり、GBビルなどの一部機能を利用したりすることはできない。

# 世界累計出荷本数は2022年12月時点で546万本[\[1\]](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%82%B8%E3%82%A2%E3%83%A02#cite_note-1)。

# ゲームモード
# ------

# ゲームを開始したときに「ポケモンスタジアム」・「とにかくバトルがしたい!」・「イベントバトル」の3つから選択する。

# ポケモンスタジアム

# 本作のメインとなるモードで対戦やミニゲームなどで遊ぶことができる。詳細は「[#ポケモンスタジアム](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%82%B8%E3%82%A2%E3%83%A02#%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%82%B8%E3%82%A2%E3%83%A0)」節を参照。

# とにかくバトルがしたい!

# あらかじめ用意されているチームで対戦するモード。詳細は「[#とにかくバトルがしたい!](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%82%B8%E3%82%A2%E3%83%A02#%E3%81%A8%E3%81%AB%E3%81%8B%E3%81%8F%E3%83%90%E3%83%88%E3%83%AB%E3%81%8C%E3%81%97%E3%81%9F%E3%81%84!)」節を参照。

# イベントバトル

# 2人用の対戦モード。詳細は「[#イベントバトル](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%82%B8%E3%82%A2%E3%83%A02#%E3%82%A4%E3%83%99%E3%83%B3%E3%83%88%E3%83%90%E3%83%88%E3%83%AB)」節を参照。

# ### ポケモンスタジアム

# ポケモントレーナーが集まる街・ホワイトシティを舞台に、ポケモン勝負や1人用モード、ミニゲームなどを遊ぶことができる。メインメニュー画面にはホワイトシティの遠景が写されており、各ゲームモードを選択する際には対応する建物を選択する形式になっている。スタジアムのカップ全6種とジムリーダーのしろをすべて制覇すると、モード「ミュウツーをたおせ」が出現し、[ミュウツー](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9F%E3%83%A5%E3%82%A6%E3%83%84%E3%83%BC "ミュウツー")に挑むことができる。ミュウツーを倒すとそれまでの「おもて（表）」モードとは異なるすべてのカップとジムリーダーのしろのパーティが一新された高難易度モードの「うら（裏）」モードが解禁される。

# #### スタジアム

# 1人用モード。ルールの異なる6種類のカップ（大会）に挑戦できる。1試合ごとにそれまでのデータを保存して中断することができる。

# ニンテンドウカップ'99

# 詳細については[ニンテンドウカップ'99](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%8B%E3%83%B3%E3%83%86%E3%83%B3%E3%83%89%E3%82%A6%E3%82%AB%E3%83%83%E3%83%97%2799 "ニンテンドウカップ'99")を参照。

# *   1999年8月末に行われた第3回ポケモンリーグ全国大会[\[注釈 1\]](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%82%B8%E3%82%A2%E3%83%A02#cite_note-2)で採用されたルールで遊べる。当時の全151種のポケモンのうち、1997年および1998年に行われた第1・2回ポケモンリーグ全国大会の決勝大会に出場したポケモン23種と[ミュウ](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9F%E3%83%A5%E3%82%A6 "ミュウ")・[ミュウツー](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9F%E3%83%A5%E3%82%A6%E3%83%84%E3%83%BC "ミュウツー")の計25種が出場できない。
# *   レベル制限は1〜50。
# *   難易度は「[モンスターボール](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%83%BC%E3%83%9C%E3%83%BC%E3%83%AB "モンスターボール")」「[スーパーボール](https://wiki.xn--rckteqa2e.com/wiki/%E3%82%B9%E3%83%BC%E3%83%91%E3%83%BC%E3%83%9C%E3%83%BC%E3%83%AB "スーパーボール")」「[ハイパーボール](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%8F%E3%82%A4%E3%83%91%E3%83%BC%E3%83%9C%E3%83%BC%E3%83%AB "ハイパーボール")」「[マスターボール](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9E%E3%82%B9%E3%82%BF%E3%83%BC%E3%83%9C%E3%83%BC%E3%83%AB "マスターボール")」の4段階用意されている。

# ニンテンドウカップ'98

# 詳細については[ニンテンドウカップ'98](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%8B%E3%83%B3%E3%83%86%E3%83%B3%E3%83%89%E3%82%A6%E3%82%AB%E3%83%83%E3%83%97%2798 "ニンテンドウカップ'98")を参照。

# *   1998年9月上旬に行われた第2回ポケモンリーグ全国大会で採用されたルールで遊べる。当時の全151種のポケモンのうち、特定の計33種のみが出場できる。
# *   レベル制限は1〜30。

# ニンテンドウカップ'97

# 詳細については[ニンテンドウカップ'97](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%8B%E3%83%B3%E3%83%86%E3%83%B3%E3%83%89%E3%82%A6%E3%82%AB%E3%83%83%E3%83%97%2797 "ニンテンドウカップ'97")を参照。

# *   1997年11月23日に行われた第1回ポケモンリーグ全国大会で採用されたルールで遊べる。当時の全151種のポケモンのうち、ミュウとミュウツーを除いた計149種が出場できる。
# *   レベルは50〜55。バトルするポケモンのレベル合計は155以下。

# ウルトラカップ

# 詳細については[ウルトラカップ](https://wiki.xn--rckteqa2e.com/wiki/%E3%82%A6%E3%83%AB%E3%83%88%E3%83%A9%E3%82%AB%E3%83%83%E3%83%97 "ウルトラカップ")を参照。

# *   相手のポケモンがすべてレベル100になっている。当時の全151種のポケモンがすべて出場できる。
# *   レベル制限はない。
# *   難易度は「モンスターボール」「スーパーボール」「ハイパーボール」「マスターボール」の4段階用意されている。

# イエローカップ

# 詳細については[イエローカップ](https://wiki.xn--rckteqa2e.com/wiki/%E3%82%A4%E3%82%A8%E3%83%AD%E3%83%BC%E3%82%AB%E3%83%83%E3%83%97 "イエローカップ")を参照。

# *   レべル15〜20のポケモンのみが出場でき、バトルするポケモンのレベル合計を50以下にする必要がある。当時の全151種のポケモンのうち、ミュウを除いた計150種が出場できる。

# ファンシーカップ

# 詳細については[ファンシーカップ](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%95%E3%82%A1%E3%83%B3%E3%82%B7%E3%83%BC%E3%82%AB%E3%83%83%E3%83%97 "ファンシーカップ")を参照。

# *   身長2m以下かつ体重20kg以下の未進化のポケモンが出場できる。当時の全151種のポケモンのうち、ミュウを除いた計150種が出場できる。
# *   レベルは25〜30。バトルするポケモンのレベル合計は80以下。

# #### フリーバトル

# 1〜4人用のモードで、プレイヤーが好きにポケモンやルールを設定してポケモン勝負を行うことができる。

# 3人以上で遊ぶときや2人1組となりコンピュータとバトルするときは[タッグバトル](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9E%E3%83%AB%E3%83%81%E3%83%90%E3%83%88%E3%83%AB "マルチバトル")となる。

# #### ジムリーダーのしろ

# 詳細については[ジムリーダーのしろ](https://wiki.xn--rckteqa2e.com/wiki/%E3%82%B8%E3%83%A0%E3%83%AA%E3%83%BC%E3%83%80%E3%83%BC%E3%81%AE%E3%81%97%E3%82%8D "ジムリーダーのしろ")を参照。

# 1人用のモードで、『[ポケットモンスター 赤・緑](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%83%E3%83%88%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%83%BC_%E8%B5%A4%E3%83%BB%E7%B7%91 "ポケットモンスター 赤・緑")・[青](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%83%E3%83%88%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%83%BC_%E9%9D%92 "ポケットモンスター 青")・[ピカチュウ](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%83%E3%83%88%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%83%BC_%E3%83%94%E3%82%AB%E3%83%81%E3%83%A5%E3%82%A6 "ポケットモンスター ピカチュウ")』に登場する[ジムリーダー](https://wiki.xn--rckteqa2e.com/wiki/%E3%82%B8%E3%83%A0%E3%83%AA%E3%83%BC%E3%83%80%E3%83%BC "ジムリーダー")たちとポケモン勝負を行う。ジムリーダー全員に勝利すると[四天王](https://wiki.xn--rckteqa2e.com/wiki/%E5%9B%9B%E5%A4%A9%E7%8E%8B "四天王")、四天王全員に勝利すると[ライバル](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%A9%E3%82%A4%E3%83%90%E3%83%AB "ライバル")（[グリーン](https://wiki.xn--rckteqa2e.com/wiki/%E3%82%B0%E3%83%AA%E3%83%BC%E3%83%B3 "グリーン")）が解禁され、勝負を挑めるようになる。

# 表または裏をクリアすると、[フシギダネ](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%95%E3%82%B7%E3%82%AE%E3%83%80%E3%83%8D "フシギダネ")・[ヒトカゲ](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%92%E3%83%88%E3%82%AB%E3%82%B2 "ヒトカゲ")・[ゼニガメ](https://wiki.xn--rckteqa2e.com/wiki/%E3%82%BC%E3%83%8B%E3%82%AC%E3%83%A1 "ゼニガメ")・[サワムラー](https://wiki.xn--rckteqa2e.com/wiki/%E3%82%B5%E3%83%AF%E3%83%A0%E3%83%A9%E3%83%BC "サワムラー")・[エビワラー](https://wiki.xn--rckteqa2e.com/wiki/%E3%82%A8%E3%83%93%E3%83%AF%E3%83%A9%E3%83%BC "エビワラー")・[イーブイ](https://wiki.xn--rckteqa2e.com/wiki/%E3%82%A4%E3%83%BC%E3%83%96%E3%82%A4 "イーブイ")・[オムナイト](https://wiki.xn--rckteqa2e.com/wiki/%E3%82%AA%E3%83%A0%E3%83%8A%E3%82%A4%E3%83%88 "オムナイト")・[カブト](https://wiki.xn--rckteqa2e.com/wiki/%E3%82%AB%E3%83%96%E3%83%88 "カブト")のうち1種をランダムでもらえる。また、表をクリアしたときは[きのはこ](https://wiki.xn--rckteqa2e.com/wiki/%E3%81%8D%E3%81%AE%E3%81%AF%E3%81%93 "きのはこ")（[ぎんのトロフィー](https://wiki.xn--rckteqa2e.com/wiki/%E3%81%8E%E3%82%93%E3%81%AE%E3%83%88%E3%83%AD%E3%83%95%E3%82%A3%E3%83%BC "ぎんのトロフィー")）、裏をクリアしたときは[きりのはこ](https://wiki.xn--rckteqa2e.com/wiki/%E3%81%8D%E3%82%8A%E3%81%AE%E3%81%AF%E3%81%93 "きりのはこ")（[きんのトロフィー](https://wiki.xn--rckteqa2e.com/wiki/%E3%81%8D%E3%82%93%E3%81%AE%E3%83%88%E3%83%AD%E3%83%95%E3%82%A3%E3%83%BC "きんのトロフィー")）をポケモンがもっており、アイテムは[第二世代](https://wiki.xn--rckteqa2e.com/wiki/%E7%AC%AC%E4%BA%8C%E4%B8%96%E4%BB%A3 "第二世代")のソフトにポケモンを移動させることで入手できる。

# #### ポケモンけんきゅうじょ

# [ボックス](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E9%A0%90%E3%81%8B%E3%82%8A%E3%82%B7%E3%82%B9%E3%83%86%E3%83%A0 "ポケモン預かりシステム")や[どうぐ](https://wiki.xn--rckteqa2e.com/wiki/%E3%81%A9%E3%81%86%E3%81%90 "どうぐ")の整理、3Dで描画されたポケモンが描かれる[ポケモンずかん](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E3%81%9A%E3%81%8B%E3%82%93 "ポケモンずかん")の閲覧、GBカートリッジとのポケモン交換などが行える。

# #### しょうりしゃのやかた

# スタジアムとジムリーダーのしろで優勝したときのポケモンの像が飾られる。全ての像を飾ると[ドわすれ](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%89%E3%82%8F%E3%81%99%E3%82%8C "ドわすれ")を覚えた[コダック](https://wiki.xn--rckteqa2e.com/wiki/%E3%82%B3%E3%83%80%E3%83%83%E3%82%AF "コダック")をもらえる。

# #### GBビル

# 1人用モード。[64GBパック](https://wiki.xn--rckteqa2e.com/wiki/64GB%E3%83%91%E3%83%83%E3%82%AF "64GBパック")に挿した『[ポケットモンスター 赤・緑](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%83%E3%83%88%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%83%BC_%E8%B5%A4%E3%83%BB%E7%B7%91 "ポケットモンスター 赤・緑")・[青](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%83%E3%83%88%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%83%BC_%E9%9D%92 "ポケットモンスター 青")・[ピカチュウ](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%83%E3%83%88%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%83%BC_%E3%83%94%E3%82%AB%E3%83%81%E3%83%A5%E3%82%A6 "ポケットモンスター ピカチュウ")』をテレビでプレイできる。[ニンテンドウカップ'99](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%8B%E3%83%B3%E3%83%86%E3%83%B3%E3%83%89%E3%82%A6%E3%82%AB%E3%83%83%E3%83%97%2799 "ニンテンドウカップ'99")または[ウルトラカップ](https://wiki.xn--rckteqa2e.com/wiki/%E3%82%A6%E3%83%AB%E3%83%88%E3%83%A9%E3%82%AB%E3%83%83%E3%83%97 "ウルトラカップ")の4つのレベルをすべてクリアすると2倍速で遊べる「**ドードーGBビル**」、ニンテンドウカップ'99とウルトラカップ両方の4つのレベルをすべてクリアすると4倍速で遊べる「**ドードリオGBビル**」にグレードアップする。

# #### チビッコクラブ

# 1〜4人用のミニゲームが遊べるモードで、9種類のミニゲームが用意されている。モードには以下の2つがあり、最初に選択する。コンピュータのつよさは、最初は「よわい」「ふつう」「つよい」の3つから選択できる。ゲームモード「うまいひとをきめる」にて、つよさが「つよい」のコンピュータ3体に対して5連勝することで一番強い「すごい」が解禁される。

# すきなゲームであそぶ

# ミニゲームをひとつ選んで遊ぶ。1回遊ぶと終了する。

# うまいひとをきめる

# ミニゲームを行い、最初に決めた数だけ先取した人が優勝となる。優勝に必要な勝利数は1回から9回までのなかから選ぶ。最初はランダムに選ばれるが、2回目以降は勝った数の一番少ないプレイヤー（COM含む）が選択する。

# 用意されているミニゲームは以下の9つである。

# コイキングのはねるでポン

# Aボタンを長押しして[コイキング](https://wiki.xn--rckteqa2e.com/wiki/%E3%82%B3%E3%82%A4%E3%82%AD%E3%83%B3%E3%82%B0 "コイキング")を跳ねさせることで画面上部にあるカウンターを押し、制限時間内に多くカウントしたプレイヤーの勝利となる。長押しが短いとコイキングがカウンターまで届かず、より多くカウントするにはタイミングよくボタンを押す必要がある。

# ピッピのゆびふりきょうしつ

# 眼鏡をかけた[ピッピ](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%94%E3%83%83%E3%83%94 "ピッピ")先生によって最初に示される矢印を覚え、その後矢印が隠されたあとに制限時間内に順番どおりに十字ボタンを使って押すミニゲームである。誤答した分ピコピコハンマーで頭を叩かれ、自身のHPが減少する。HPがなくなった場合、その時点で失格となる。最後まで行い、最もHPが残っているプレイヤーが勝利となる。また、ほかのプレイヤーが全員失格となった場合はその時点で終了し、HPが残っているプレイヤーが勝利となる。

# はしれコラッタ

# ベルトコンベアの上を[コラッタ](https://wiki.xn--rckteqa2e.com/wiki/%E3%82%B3%E3%83%A9%E3%83%83%E3%82%BF "コラッタ")が走り、時折出てくるハードルをジャンプで飛び越えて最初にゴールしたプレイヤーの勝利となる。Aボタンを連打で走り、十字ボタン上キーでジャンプする。ハードルにぶつかるとタイムロスとなる。

# スリープのさいみんがっせん

# 互いに向き合った[スリープ](https://wiki.xn--rckteqa2e.com/wiki/%E3%82%B9%E3%83%AA%E3%83%BC%E3%83%97 "スリープ")が[さいみんじゅつ](https://wiki.xn--rckteqa2e.com/wiki/%E3%81%95%E3%81%84%E3%81%BF%E3%82%93%E3%81%98%E3%82%85%E3%81%A4 "さいみんじゅつ")をかけ合うミニゲームで、最後まで起きていたプレイヤーの勝利となる。画面中央にある振り子が一番下に来る瞬間にタイミングよくボタンを押す必要があり、タイミングがずれると眠気が溜まっていく。

# ビリリはつでんきょうそう

# 発電所が示す色と同じ色のボタン（青色のときはAボタン、緑色のときはBボタン）を連打することで発電し、メーターを最大まで溜めたプレイヤーの勝利となる。プレイヤーは[ビリリダマ](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%93%E3%83%AA%E3%83%AA%E3%83%80%E3%83%9E "ビリリダマ")または[ピカチュウ](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%94%E3%82%AB%E3%83%81%E3%83%A5%E3%82%A6 "ピカチュウ")。

# ベロリンガのぐるぐるずし

# 回転寿司に登場し続ける寿司ネタを[ベロリンガ](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%99%E3%83%AD%E3%83%AA%E3%83%B3%E3%82%AC "ベロリンガ")の舌を伸ばして多く食べ、食べた寿司ネタの値段の合計が最も高いプレイヤーの勝利となる。同じ寿司ネタを続けて食べるとボーナスがもらえる。

# アーボでわなげ

# 輪になった[アーボ](https://wiki.xn--rckteqa2e.com/wiki/%E3%82%A2%E3%83%BC%E3%83%9C "アーボ")を穴から出てくる[ディグダ](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%87%E3%82%A3%E3%82%B0%E3%83%80 "ディグダ")めがけて飛ばし、より多くのポイントを獲得したプレイヤーの勝利となる。十字キーで方向を調整し、3Dスティックの弾き方で投げる強さを決める。

# かたくなるがっせん

# 画面奥から[コクーン](https://wiki.xn--rckteqa2e.com/wiki/%E3%82%B3%E3%82%AF%E3%83%BC%E3%83%B3 "コクーン")あるいは[トランセル](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%88%E3%83%A9%E3%83%B3%E3%82%BB%E3%83%AB "トランセル")に向かって岩が飛んでくるため、その岩をタイミングよく[かたくなる](https://wiki.xn--rckteqa2e.com/wiki/%E3%81%8B%E3%81%9F%E3%81%8F%E3%81%AA%E3%82%8B "かたくなる")によって砕き、最後まで耐えたプレイヤーの勝利となる。各プレイヤーにはメーターが設定されており、かたくなるをしている間やダメージを受けたときに減少する。

# サンドのいどほりきょうそう

# LボタンとRボタンを交互に連打することで[サンド](https://wiki.xn--rckteqa2e.com/wiki/%E3%82%B5%E3%83%B3%E3%83%89 "サンド")が地面を掘り進めていき、一番早く水が湧き出るまで掘り進めたプレイヤーの勝利となる。

# #### ミュウツーをたおせ

# スタジアムのカップ6つとジムリーダーのしろをすべて制覇すると出現する。レベル100のミュウツーが登場し、1匹から6匹までのポケモンを参加させることができる。

# <table><caption>ミュウツーのステータス</caption><tbody><tr><th></th><th><a href="https://wiki.xn--rckteqa2e.com/wiki/HP" title="HP">HP</a></th><th><a href="https://wiki.xn--rckteqa2e.com/wiki/%E3%81%93%E3%81%86%E3%81%92%E3%81%8D" title="こうげき">こうげき</a></th><th><a href="https://wiki.xn--rckteqa2e.com/wiki/%E3%81%BC%E3%81%86%E3%81%8E%E3%82%87" title="ぼうぎょ">ぼうぎょ</a></th><th><a href="https://wiki.xn--rckteqa2e.com/wiki/%E3%81%99%E3%81%B0%E3%82%84%E3%81%95" title="すばやさ">すばやさ</a></th><th><a href="https://wiki.xn--rckteqa2e.com/wiki/%E3%81%A8%E3%81%8F%E3%81%97%E3%82%85" title="とくしゅ">とくしゅ</a></th><th colspan="4">わざ</th></tr><tr><th>表</th><td>385</td><td>286</td><td>248</td><td>328</td><td>376</td><td><a href="https://wiki.xn--rckteqa2e.com/wiki/%E3%82%B5%E3%82%A4%E3%82%B3%E3%82%AD%E3%83%8D%E3%82%B7%E3%82%B9" title="サイコキネシス">サイコキネシス</a></td><td><a href="https://wiki.xn--rckteqa2e.com/wiki/%E3%81%AD%E3%82%80%E3%82%8B" title="ねむる">ねむる</a></td><td><a href="https://wiki.xn--rckteqa2e.com/wiki/10%E3%81%BE%E3%82%93%E3%83%9C%E3%83%AB%E3%83%88" title="10まんボルト">10まんボルト</a></td><td><a href="https://wiki.xn--rckteqa2e.com/wiki/%E3%81%B5%E3%81%B6%E3%81%8D" title="ふぶき">ふぶき</a></td></tr><tr><th>裏</th><td>415</td><td>318</td><td>278</td><td>358</td><td>406</td><td><a href="https://wiki.xn--rckteqa2e.com/wiki/%E3%82%B5%E3%82%A4%E3%82%B3%E3%82%AD%E3%83%8D%E3%82%B7%E3%82%B9" title="サイコキネシス">サイコキネシス</a>（<a href="https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%A4%E3%83%B3%E3%83%88%E3%82%A2%E3%83%83%E3%83%97" title="ポイントアップ">ポイントアップ</a>3回使用）</td><td><a href="https://wiki.xn--rckteqa2e.com/wiki/10%E3%81%BE%E3%82%93%E3%83%9C%E3%83%AB%E3%83%88" title="10まんボルト">10まんボルト</a>（ポイントアップ3回使用）</td><td><a href="https://wiki.xn--rckteqa2e.com/wiki/%E3%81%AD%E3%82%80%E3%82%8B" title="ねむる">ねむる</a></td><td><a href="https://wiki.xn--rckteqa2e.com/wiki/%E3%83%89%E3%82%8F%E3%81%99%E3%82%8C" title="ドわすれ">ドわすれ</a></td></tr></tbody></table>

# ### とにかくバトルがしたい!

# あらかじめ用意されたパーティを使用してポケモン勝負を行うことができる。表と裏で用意されるパーティが異なっており、2つあるパーティのうち片方が自分、もう片方が相手にランダムで割り当てられる。

# ### イベントバトル

# GBカートリッジがセットされたコントローラを用いて、それぞれのGBカートリッジにセーブされている手持ちポケモン6匹でポケモン勝負を行うことができる。

# ルールはポケモンスタジアムに用意されているすべてのカップのルールを使用でき、試合時間と技を選択する時間の制限を設定することができる。

# 新要素・変更点
# -------

# _この節は書きかけです。[加筆、訂正](https://wiki.xn--rckteqa2e.com/w/index.php?title=%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%82%B8%E3%82%A2%E3%83%A02&action=edit)して下さる協力者を求めています。_

# わざの微調整

# ポケスタ2では、ポケモンの[わざ](https://wiki.xn--rckteqa2e.com/wiki/%E3%82%8F%E3%81%96 "わざ")について微調整が加えられている。

# *   [はかいこうせん](https://wiki.xn--rckteqa2e.com/wiki/%E3%81%AF%E3%81%8B%E3%81%84%E3%81%93%E3%81%86%E3%81%9B%E3%82%93 "はかいこうせん")で相手をたおした場合・相手の[みがわり](https://wiki.xn--rckteqa2e.com/wiki/%E3%81%BF%E3%81%8C%E3%82%8F%E3%82%8A "みがわり")を攻撃した場合・相手に命中しなかった場合などに反動がない、という仕様が撤廃されている[\[注釈 2\]](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%82%B8%E3%82%A2%E3%83%A02#cite_note-3)。
# *   [みがわり](https://wiki.xn--rckteqa2e.com/wiki/%E3%81%BF%E3%81%8C%E3%82%8F%E3%82%8A "みがわり")で[状態異常](https://wiki.xn--rckteqa2e.com/wiki/%E7%8A%B6%E6%85%8B%E7%95%B0%E5%B8%B8 "状態異常")や[状態変化](https://wiki.xn--rckteqa2e.com/wiki/%E7%8A%B6%E6%85%8B%E5%A4%89%E5%8C%96 "状態変化")をふせげるようになった。
# *   [かげぶんしん](https://wiki.xn--rckteqa2e.com/wiki/%E3%81%8B%E3%81%92%E3%81%B6%E3%82%93%E3%81%97%E3%82%93 "かげぶんしん")などの[回避率](https://wiki.xn--rckteqa2e.com/wiki/%E5%9B%9E%E9%81%BF%E7%8E%87 "回避率")上昇や、[フラッシュ](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%95%E3%83%A9%E3%83%83%E3%82%B7%E3%83%A5 "フラッシュ")などの[命中率](https://wiki.xn--rckteqa2e.com/wiki/%E5%91%BD%E4%B8%AD%E7%8E%87 "命中率")下降が抑えられ、やや弱体化した。
# *   [ねむる](https://wiki.xn--rckteqa2e.com/wiki/%E3%81%AD%E3%82%80%E3%82%8B "ねむる")で[状態異常](https://wiki.xn--rckteqa2e.com/wiki/%E7%8A%B6%E6%85%8B%E7%95%B0%E5%B8%B8 "状態異常")を回復したとき、その状態異常による能力変化も回復するようになった。
# *   [くろいきり](https://wiki.xn--rckteqa2e.com/wiki/%E3%81%8F%E3%82%8D%E3%81%84%E3%81%8D%E3%82%8A "くろいきり")で自分の[状態異常](https://wiki.xn--rckteqa2e.com/wiki/%E7%8A%B6%E6%85%8B%E7%95%B0%E5%B8%B8 "状態異常")も治せるようになった。
# *   [スピードスター](https://wiki.xn--rckteqa2e.com/wiki/%E3%82%B9%E3%83%94%E3%83%BC%E3%83%89%E3%82%B9%E3%82%BF%E3%83%BC "スピードスター")が必中になった。
# *   [メタモン](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%A1%E3%82%BF%E3%83%A2%E3%83%B3 "メタモン")に対する[へんしん](https://wiki.xn--rckteqa2e.com/wiki/%E3%81%B8%E3%82%93%E3%81%97%E3%82%93 "へんしん")が失敗するようになった。
# *   [わるあがき](https://wiki.xn--rckteqa2e.com/wiki/%E3%82%8F%E3%82%8B%E3%81%82%E3%81%8C%E3%81%8D "わるあがき")が実質上タイプを持たないわざとなり、[タイプ相性](https://wiki.xn--rckteqa2e.com/wiki/%E7%9B%B8%E6%80%A7 "相性")・[タイプ一致ボーナス](https://wiki.xn--rckteqa2e.com/wiki/%E3%82%BF%E3%82%A4%E3%83%97%E4%B8%80%E8%87%B4%E3%83%9C%E3%83%BC%E3%83%8A%E3%82%B9 "タイプ一致ボーナス")の影響を受けなくなった。
# *   [急所率](https://wiki.xn--rckteqa2e.com/wiki/%E6%80%A5%E6%89%80%E7%8E%87 "急所率")が補正された。相変わらず[すばやさ](https://wiki.xn--rckteqa2e.com/wiki/%E3%81%99%E3%81%B0%E3%82%84%E3%81%95 "すばやさ")の[種族値](https://wiki.xn--rckteqa2e.com/wiki/%E7%A8%AE%E6%97%8F%E5%80%A4 "種族値")に依存するが、それが高いポケモンにとってはやや弱体化、低いポケモンにとってはやや強化となった。
#     *   これにともなって、[きあいだめ](https://wiki.xn--rckteqa2e.com/wiki/%E3%81%8D%E3%81%82%E3%81%84%E3%81%A0%E3%82%81 "きあいだめ")の効果が反転してしまうバグも修正された。
# *   一部の[攻撃技](https://wiki.xn--rckteqa2e.com/wiki/%E6%94%BB%E6%92%83%E6%8A%80 "攻撃技")の追加効果が発生する確率が下がった。
#     *   [オーロラビーム](https://wiki.xn--rckteqa2e.com/wiki/%E3%82%AA%E3%83%BC%E3%83%AD%E3%83%A9%E3%83%93%E3%83%BC%E3%83%A0 "オーロラビーム"): 33%→20%
#     *   [バブルこうせん](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%90%E3%83%96%E3%83%AB%E3%81%93%E3%81%86%E3%81%9B%E3%82%93 "バブルこうせん"): 33%→30%
#     *   前作から引き続き、[ふぶき](https://wiki.xn--rckteqa2e.com/wiki/%E3%81%B5%E3%81%B6%E3%81%8D "ふぶき"): 30%→10%
#     *   [ようかいえき](https://wiki.xn--rckteqa2e.com/wiki/%E3%82%88%E3%81%86%E3%81%8B%E3%81%84%E3%81%88%E3%81%8D "ようかいえき"): 33%→30%
# *   相手を[バインド](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%90%E3%82%A4%E3%83%B3%E3%83%89 "バインド")にする効果の技がタイプ相性で無効化されたときにもバインドを発生させてしまうバグが修正された[\[2\]](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%82%B8%E3%82%A2%E3%83%A02#cite_note-4)。

# これらのいくつかは[第二世代](https://wiki.xn--rckteqa2e.com/wiki/%E7%AC%AC%E4%BA%8C%E4%B8%96%E4%BB%A3 "第二世代")にも引き継がれている。

# 発売までの経緯
# -------

# *   1999年2月10日頃 - 「64DREAM」1999年5月号が発売され、本作に関する情報やスクリーンショットが公開。
# *   1999年2月15日頃 - 「[コロコロコミック](https://wiki.xn--rckteqa2e.com/wiki/%E3%82%B3%E3%83%AD%E3%82%B3%E3%83%AD%E3%82%B3%E3%83%9F%E3%83%83%E3%82%AF "コロコロコミック")」1999年3月号が発売。[ポケモンフェスティバル](https://wiki.xn--rckteqa2e.com/w/index.php?title=%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E3%83%95%E3%82%A7%E3%82%B9%E3%83%86%E3%82%A3%E3%83%90%E3%83%AB&action=edit&redlink=1 "「ポケモンフェスティバル」 (存在しないページ)")'99春の情報の中で本作が発表される。本作を用いたポケモンリーグ特別大会「[ファンシーカップ](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%95%E3%82%A1%E3%83%B3%E3%82%B7%E3%83%BC%E3%82%AB%E3%83%83%E3%83%97 "ファンシーカップ")」の開催も併せて発表。
# *   1999年2月16日 - [任天堂](https://wiki.xn--rckteqa2e.com/wiki/%E4%BB%BB%E5%A4%A9%E5%A0%82 "任天堂")公式サイトにて、ポケモンフェスティバル'99春の開催とポケモンリーグ特別大会「ファンシーカップ」の情報が発表[\[3\]](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%82%B8%E3%82%A2%E3%83%A02#cite_note-5)。
# *   1999年3月15日頃 - 「コロコロコミック」1999年4月号が発売。別冊付録として「ポケモンスタジアム2 公式ガイドブックゲームノートBOOK」を収録。
# *   1999年3月28日 - 本作を用いたポケモンリーグ特別大会「ファンシーカップ」熊本大会が開催[\[4\]](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%82%B8%E3%82%A2%E3%83%A02#cite_note-p_fancy-6)。
# *   1999年4月4日 - 本作を用いたポケモンリーグ特別大会「ファンシーカップ」大阪大会が開催[\[4\]](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%82%B8%E3%82%A2%E3%83%A02#cite_note-p_fancy-6)。
# *   1999年4月11日 - 本作を用いたポケモンリーグ特別大会「ファンシーカップ」東京大会が開催[\[4\]](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%82%B8%E3%82%A2%E3%83%A02#cite_note-p_fancy-6)。
# *   1999年4月21日頃 - 「64DREAM」1999年6月号が発売され、[ピカチュウ](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%94%E3%82%AB%E3%83%81%E3%83%A5%E3%82%A6 "ピカチュウ")や[ミュウツー](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9F%E3%83%A5%E3%82%A6%E3%83%84%E3%83%BC "ミュウツー")などポケモンが表紙を飾る。本作の特集が組まれたほか、付録として本作の特大ポスターとシールがついた。
# *   1999年4月25日 - 本作を用いたポケモンリーグ特別大会「ファンシーカップ」仙台大会が開催[\[4\]](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%82%B8%E3%82%A2%E3%83%A02#cite_note-p_fancy-6)。
# *   1999年4月29日 - 本作を用いたポケモンリーグ特別大会「ファンシーカップ」名古屋大会が開催[\[4\]](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%82%B8%E3%82%A2%E3%83%A02#cite_note-p_fancy-6)。
# *   1999年4月30日 - 発売。

# 備考
# --

# *   日本国外では「[ポケモンスタジアム](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%82%B8%E3%82%A2%E3%83%A0 "ポケモンスタジアム")」が未発売のため、ポケモンスタジアム2が「[Pokémon Stadium](https://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9mon_Stadium_(English) "en:Pokémon Stadium (English)")」、[ポケモンスタジアム金銀](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%82%B8%E3%82%A2%E3%83%A0%E9%87%91%E9%8A%80 "ポケモンスタジアム金銀")が「[Pokémon Stadium 2](https://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9mon_Stadium_2 "en:Pokémon Stadium 2")」となっている。
# *   実況は、前作から引き続き[長谷部浩一](https://wiki.xn--rckteqa2e.com/wiki/%E9%95%B7%E8%B0%B7%E9%83%A8%E6%B5%A9%E4%B8%80 "長谷部浩一")が担当している。
# *   CMには女優の[深浦加奈子](https://ja.wikipedia.org/wiki/%E6%B7%B1%E6%B5%A6%E5%8A%A0%E5%A5%88%E5%AD%90 "w:深浦加奈子")が出演した。CMでは深浦演じるエプロンをつけた女性が、子どもたちからのポケモン勝負に受けて立つも敗北して「戦略が甘いね」と評されるが、深浦演じる女性は「やっぱり[ミュウツー](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9F%E3%83%A5%E3%82%A6%E3%83%84%E3%83%BC "ミュウツー")よね」とミュウツーを出して子どもたちからブーイングされるという内容であった。
# *   [Nintendo Switch Online](https://wiki.xn--rckteqa2e.com/wiki/Nintendo_Switch_Online "Nintendo Switch Online")向けに配信されたバージョンでは、[ルージュラ](https://wiki.xn--rckteqa2e.com/wiki/%E3%83%AB%E3%83%BC%E3%82%B8%E3%83%A5%E3%83%A9 "ルージュラ")の3Dモデルが肌の色が紫色に変更されたものに差し替えられている。
# ```
# """

#             response = self.client.chat.completions.create(
#                 model="gpt-4o",
#                 temperature=0.7,
#                 messages=[
#                     {"role": "system", "content": system_prompt},
#                     {"role": "user", "content": "会話歴を考慮して、ポケモンスタジアム2に関する知識を1つ、端的に披露してください。"},
#                 ],
#             )

#             ai_message = response.choices[0].message.content
#             print("ai_message", ai_message)
#             answer = ai_message
#             emotion = "neutral"

#             await send_websocket_message(
#                 websocket, answer, "assistant", emotion=emotion
#             )

#             self.conversation_history.append(f"ai: {answer}")
#             # 会話履歴をJSONファイルに保存
#             with open(self.conversation_file, "w", encoding="utf-8") as f:
#                 json.dump(self.conversation_history, f, ensure_ascii=False, indent=2)
#             return answer
#         except Exception as e:
#             print("chat error", e)
#             raise e
#         finally:
#             await send_websocket_message(websocket, "", "assistant", "end")
