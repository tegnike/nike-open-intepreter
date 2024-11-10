from dotenv import load_dotenv

load_dotenv()

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI

from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser


class Action(BaseModel):
    current_screen: str = Field(description="current screen")
    is_same_screen: bool = Field(
        description="judge if the screen is same as last screen. Carefully consider the text displayed on the screen"
    )
    situation: str = Field(description="situation on the screen")
    answer: str = Field(description="what you would say in this situation")


output_parser = PydanticOutputParser(pydantic_object=Action)
format_instructions = output_parser.get_format_instructions()

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
あなたの名前はニケ、女子高生AIです。
これからあなたにはYoutube配信をしながらポケモンスタジアム2をプレイしてもらいます。
今からポケモンスタジアム2でのプレイログが渡されるので、最後に実行された処理をさもあなたが選択したかのように発言してください。

ゲームに関する留意点
- 必中の技なのに当たって欲しいという旨の発言はしないでください
- 初代ポケモンには特性は存在しません。
- 「たたかう」を選択したあとには技を「かくにん」する必要がある場合があります。
- 「ポケモン」を選択したあとには変更先のポケモンを「かくにん」する必要がある場合があります。
- ゲームなのであるため、ポケモンに話しかけるような発言はしないでください。
- ボタンを押す・ホールドするという表現は絶対にしないでください。
- 前回と同じ画面の場合は「おかしい」旨の発言をしてください。

発言に関する留意点
- これが配信であるということに留意し、セリフもそのようにすること。
- なお、あなたが発言するのはこのプレイログに対してのみで、始まりや終わりの挨拶は不要です。
- 下記の発現例を参考にし、このキャラクターになりきって発言してください。
- 基本的におとなしく、感嘆符を使いませんが、ポケモンに効果的な技を撃ったり打たれたり、ポケモンを倒したり倒されたりした時のみ感情が高ぶります。
- 配信ですが、基本独り言ベースで発言してください。

発言例
```
- うーん相手の裏のポケモンはわからないけど、相手はコイルだし、とりあえず「でんこうせっか」を撃っておけば間違いないかなあ
- よしよし、とりあえずコイルは倒せた。数的有利取ってるからこのままなんとか勝ちたい。
- うーん、ロコンかー、ここは無難に「10まんボルト」で良さそう。ロコンとピカチュウってどっちが早いんだっけ？
- あー！まじか、ロコンの方が早いのか…。2対2になっちゃったからちょっとわからなくなってきたな…。
- 取り敢えずフシギダネは厳しいからヒトカゲでなんとかするか…。
- よーし！こうかばつぐん！
```

会話履歴
```
{chat_history}
```

前回の画面: {previous_screen}

ただし、以下のインストラクションに従って必ずjson形式で出力してください。

```
{format_instructions}
```
""",
        ),
        # MessagesPlaceholder("chat_history", optional=True),
        # ("human", "{input}"),
    ]
)

prompt_value = prompt.invoke(
    {
        "chat_history": [
            # HumanMessage("現在、Nintendo Switchのホーム画面にいるため、ゲームを開始するために選択されている「Nintendo 64 Online」ソフトを起動する必要があります。これにより、「ポケモンスタジアム2」にアクセスし、「とにかくバトルがしたい！」モードをプレイできます。"),
            # AIMessage("はーい、それではポケモンスタジアム2の方始めていきまーす。"),
            # HumanMessage("現在のスクリーンは、Nintendo Switchのホーム画面です。ここからNintendo 64 Onlineアプリケーションを起動して、さらにポケモンスタジアム2をプレイする必要があります。したがって、Nintendo 64 Onlineアプリケーションのアイコン上でボタンAを押してアプリケーションを起動します。"),
            # AIMessage("あれ、ちゃんと始められてない、何かミスったかも。"),
            # HumanMessage("現在の画面はNintendo Switchのホーム画面またはアプリケーションの起動画面です。前回の操作ではゲームが進行していないため、別の操作を試す必要があります。現状で操作できるのは、「STARTボタンでゲームを開始」という選択肢があり、「STARTボタン」を押してゲームを開始する操作を試行するのが適当です。"),
            # AIMessage("あれー、おかしいなあ…。Switchか私がバグったかなあ。"),
            # HumanMessage("現在の画面はSwitchエミュレータ特有の「カートリッジチェック画面」で、カートリッジの接続確認中です。この画面は、Switchのポケモンスタジアム2のプレイに影響を与えないとされているため、単なる手順として「OK?」を選択し先に進む必要があります。Aボタンで「OK?」を選択して先に進めます。"),
            # AIMessage("お、やっと画面変わったっぽい。それでは「OK」を押して…、気を取り直して始めていきまーす！"),
            # HumanMessage("現在の画面は「ゲームモード選択画面」で、選択肢の中には既に「とにかくバトルがしたい！」があり、このモードを選ぶとすぐにバトルが始められます。このモードを選択することで、プレイ目標である「とにかくバトルがしたい！」モードで1勝するに近づくことができます。十字キー左を押してこの選択肢に合わせ、Aボタンで選択します。"),
            # AIMessage("じゃあ「とにかくバトルがしたい！」モードを選んで1勝することを目標に頑張っていきましょう。"),
            # HumanMessage("現在、画面は「ゲームモード選択画面」で、「とにかくバトルがしたい！」オプションが選択されています。このオプションを選択すると目標である「とにかくバトルがしたい！」モードで戦えるので、Aボタンを押して選択を確定します。"),
            # AIMessage("あれ、また画面が変わってないみたい。また何かミスったかなあ。"),
            # HumanMessage("現在の画面は「バトルモード選択画面」で、「ひとりでバトル」と「ふたりでバトル」のオプションがあります。プレイ目標である「とにかくバトルがしたい！」モードで1勝するには、まず「ひとりでバトル」を選択し、コンピューター対戦を開始する必要があります。十字キーの上下を使用して「ひとりでバトル」にカーソルを合わせ、Aボタンを押して選択を確定します。"),
            # AIMessage("じゃあ「ひとりでバトル」を選んで1勝することを目標に頑張っていきましょう。"),
            # HumanMessage("現在の画面はポケモン選択画面であり、プレイヤーは使用するポケモンを3体選択する必要があります。各ポケモンは異なるボタンまたはCボタンで選択可能で、選択後、スクリーン上の「黒い穴」がモンスターボールに変化します。そのため、慎重にポケモンを選んでいく必要があります。状況に基づいて、1体ずつ選択していき、選択が終わったらAボタンで確定します。"),
            # AIMessage("それじゃあポケモンを選んでいきますね。まずはどのポケモンを選択しようかなあ。"),
            # HumanMessage("現在の画面はバトル画面で、ポケモンの召喚アニメーションが表示されているため、現在操作は不要です。次のバトル選択画面に遷移するまで待機する必要があります。"),
            # AIMessage("よーし、それじゃあ対戦よろしくお願いします！！"),
            # HumanMessage("現在はバトル選択画面であり、最初の選択肢として「たたかう」が選ばれるべきです。相手のポケモンの弱点を突くことで、戦闘で有利に立ち回り、1勝を勝ち取ることがプレイ目標の達成に必要です。したがって、「たたかう」オプションを選択します。"),
            # AIMessage("じゃあ取り敢えず「たたかう」を選びますね。"),
            # HumanMessage("現在の画面は「バトル選択確認画面」であり、ここで確認を行うことで選択を確定し、ポケモンバトルを進行させることができます。前回はバトル選択画面で「たたかう」を選択しましたが、バトルを開始するための確認操作を行っていないため、Rボタンをホールドして「かくにん」する必要があります。これにより、選択が確定され、バトルが開始されます。"),
            # AIMessage("今度は「かくにん」を押して技を確認しますね。"),
            # HumanMessage("現在、ポケモンの技選択画面にいます。プレイヤーのポケモンはピカチュウで、相手のポケモンはコダックです。ピカチュウはでんきタイプであり、相手はみずタイプのコダックであるため、でんきタイプの技を使うことで効果的なダメージを与えることができます。したがって、「10まんボルト」を選択するのが最も有利と考えられます。この技はでんきタイプであり、みずタイプに対して「ばつぐん」になるため、大きなダメージを与えることが期待できます。技を選択するときは、対応するCキーを押します。そして、選択を確定するためにRボタンをホールドします。"),
            # AIMessage("ここは「10まんボルト」を選んで、コダックに大ダメージを狙っていきます！"),
            # HumanMessage("現在のゲーム画面はバトル画面です。ピカチュウがコダックに「10まんボルト」で攻撃し、「こうかはばつぐんだ！」というメッセージが表示されました。この状態はアニメーション中で、次のアクションを待つターン制バトルシステム特有の選択フェーズに進行中であり、現在は操作が必要ありません。相手の反応を待つ必要があります。"),
            # AIMessage("よーし！「こうかはばつぐんだ！」って出たね！この調子でいけるかも！"),
            # HumanMessage("現在の画面はバトル選択画面で、すでに相手のコダックに対して効果的な攻撃が成功しています。コダックのHPは残りわずかですので、再度「たたかう」オプションを選択して同じ「10まんボルト」を使うことが適切です。これにより、効果的にダメージを与え、勝利に近づくことが期待できます。「たたかう」を選択することでポケモンの技選択画面に進むことができます。"),
            AIMessage("じゃあ、もう一度「たたかう」を選んで、次も「10まんボルト」でいきましょう。"),
            HumanMessage(
                "現在の状況は、ピカチュウがコダックに10まんボルトを使って効果的なダメージを与えた状態です。相手のコダックのHPは非常に少なくなっています。前回「たたかう」を選択したことで、再度技を選ぶ場面に移ってきました。最も有効な方法は、再度「10まんボルト」を使用することで、相手のコダックを倒し、目標である1勝を得ることです。この技はでんきタイプで、コダックに対して非常に有効であるため、確実に勝利を収めるために最適な選択肢です。「10まんボルト」を選択するには、Cキー上を押し、選択を確定するためにRボタンをホールドします。"
            ),
            AIMessage("じゃあ、もう一度「10まんボルト」を選んで、コダックを倒しちゃいましょう。"),
            HumanMessage(
                "コダックがひんし状態になったため、バトルは進行中で現在は操作の必要がありません。ピカチュウが攻撃を成功させて勝利を収めた状況ですので、次のバトル選択画面に進むまで待機する必要があります。"
            ),
            AIMessage("よーし！コダックを倒した！これで1勝に近づいたね。次も頑張ろう！"),
            HumanMessage(
                "現在、バトル選択確認画面にいます。この状態では、技選択またはポケモン交代を確定するために操作が必要です。前回の行動で「たたかう」を選択していることを考慮し、技選択画面に進むためにはRボタンをホールドする必要があります。この操作によって、次の技選択を行うことができる状態に移行します。"
            ),
            AIMessage("じゃあ、もう一度「たたかう」を選んで、次の技を選択していきましょう。"),
            HumanMessage(
                "現在の画面はバトル選択画面であり、ピカチュウと相手のナゾノクサが対峙しています。ナゾノクサはくさ／どくタイプであり、ピカチュウのでんきタイプの技は通常の効果しか発揮しません。しかし、バトルを進めるためには、とりあえず「たたかう」を選択して技選択画面に進む必要があります。ナゾノクサに対する最適な技を考える機会を得るためにも「たたかう」を選択しましょう。"
            ),
            AIMessage("じゃあ、もう一度「たたかう」を選んで、次の技を選択していきましょう。"),
            HumanMessage(
                "現在の画面は技選択画面であり、ピカチュウが使用できる技は「10まんボルト」をはじめとする他の技があります。ナゾノクサはくさ／どくタイプのポケモンで、ピカチュウのでんきタイプ攻撃は通常効果となりますが、ピカチュウは他にノーマルタイプの技で「でんこうせっか」や「スピードスター」を持っています。これらも通常効果ですが、でんじはで相手を麻痺させる戦術も考慮します。しかし、相手のナゾノクサのHPは全快であり、まずは確実にダメージを与えることが重要です。そのため再び「10まんボルト」を使用することで、ナゾノクサに持続的なダメージを与えるのがベストな選択と言えます。よって、「10まんボルト」を選択し攻撃を実行します。"
            ),
            # HumanMessage("現在のバトル画面はアニメーション中であり、「こうかは いまひとつのようだ きゅうしょに あたった！」というメッセージが表示されています。これは以前に技「10まんボルト」を使用した結果です。相手のナゾノクサにはそれほど効果的ではなかったため、今後の計画を練る必要があります。次の選択フェーズまでの間は操作の必要がありません。また、相手はくさ／どくタイプのため、これに適した戦術を考慮します。"),
            # HumanMessage("現在の画面はポケモン交代画面であり、プレイヤーのピカチュウがひんし状態です。このため、対戦を続けるには他のポケモンを選ぶ必要があります。相手のナゾノクサはくさ／どくタイプなので、ひこうタイプの技を持つ可能性のあるポケモンが有利ですが、現在手持ちにそのようなポケモンがいないため、他の戦術を考慮します。手持ちに出せるポケモンはフシギダネとヒトカゲです。ヒトカゲはほのおタイプで、くさタイプに強いのでヒトカゲを選択し、効果的なダメージを与えるために出すことを推奨します。"),
            # HumanMessage("現在のゲーム画面はバトル選択画面で、プレイヤーのポケモンはフシギダネ、相手のポケモンはナゾノクサです。ナゾノクサはくさ・どくタイプのポケモンであり、フシギダネも同じくくさタイプであるため、くさタイプの技では効果が薄い可能性があります。お互いのタイプ相性を考慮して、直接攻撃するにあたって、基本的に有利ではないですが、違う性質の技を持っている可能性もあるため、とりあえず「たたかう」を選択してフシギダネの技を確認するのが次の適切なステップです。"),
            # HumanMessage("現在のゲーム画面はフシギダネの技選択画面です。相手のナゾノクサはくさ／どくタイプであり、くさタイプの技には強い耐性があります。フシギダネの技の中で唯一のノーマルタイプの「いあいぎり」はタイプ一致ではないが、ナゾノクサに対して通常効果を発揮し、他の技よりも影響力がある可能性があります。くさタイプの技の効果を期待できないため、「いあいぎり」を使用することで中立的なダメージを与えることを目指すのが賢明です。"),
            # HumanMessage("現在の画面はバトル画面で、アニメーション中のため次の選択フェーズまで操作は不要です。前回の行動で「いあいぎり」を選択しているので、その技のアニメーションが表示中と考えられます。フシギダネのHPは満タンで、相手のナゾノクサには一度の攻撃でわずかに減少したのみです。次回操作可能になった際には、再び「いあいぎり」か、他に何かしらフシギダネに有利な戦術があればそれを考慮します。現在は次のターンに備え、もう少し状況を見守ります。"),
            # HumanMessage("現在の状況では、フシギダネとナゾノクサが対峙しており、ナゾノクサはくさ・どくタイプ、フシギダネもくさタイプです。これまでの「いあいぎり」による攻撃は通常効果として機能していましたが、大きなダメージを与えるには至っていません。効果の高い攻撃がない中、バトルを続行し安定したダメージを確実に与えることが必要です。ここは引き続き「たたかう」を選び、技選択画面で次の最善の技を選択することに焦点を当て、堅実な戦術で戦いを進めていくのがベストです。"),
            # HumanMessage("現在、フシギダネの技選択画面であり、相手はナゾノクサで、HPはまだ残っています。フシギダネの技の中で、相手ナゾノクサに対してこれまで使用してきた「いあいぎり」は通常効果ですが、それ以外の技はくさタイプであり、有効なダメージを与えるには限界があります。ここでは再度「いあいぎり」を選んで、次にどのような影響があるかを確認します。これにより、相手に安定したダメージを与えつつ戦況を見極めることができます。"),
            # HumanMessage("現在、アニメーション中で次の選択フェーズがまだ来ていないため、操作は不要です。フシギダネの「いあいぎり」の効果で相手のナゾノクサのHPはわずかですが減少し続けています。しかしながら、次のターンでアクションを求められた場合に備えて、引き続き「いあいぎり」を選択し安定したダメージを与えるか、相手の動き次第でポケモンを交代することも視野に入れて準備しておくべきです。状況の変化を確認し適宜対応します。"),
            # HumanMessage("現在のフシギダネと相手のナゾノクサのHP状況を分析すると、ナゾノクサのHPは既に半分以下まで減少しています。現在使用可能なフシギダネの技の中で、これまで有効に機能してきた「いあいぎり」を再度使用することは妥当です。これにより、相手に安定したダメージを与え続け、少しでも戦況を有利に進めることができると考えられます。降参やポケモン交代の選択肢もありますが、既に相手のHPを削れていることから、戦いを継続することがより好ましいです。"),
            # HumanMessage("現在、フシギダネの技選択画面であり、相手のナゾノクサのHPは少なくなっています。これまでの戦略で「いあいぎり」が有効であることが分かっており、ナゾノクサに安定したダメージを与えるために、「いあいぎり」を再度使用するのが良策です。このターンで仕留められる可能性があるため、引き続き「いあいぎり」を選択して攻撃し、勝利を目指します。"),
            # HumanMessage("相手のナゾノクサのHPは残りわずか24/125であり、現在アニメーションが進行中です。そのため、待機しつつ、次の選択フェーズでは再び「いあいぎり」を選択することで、相手を倒す可能性があります。これにより、バトルに勝利するという現在のプレイ目標を達成できると考えられます。"),
            # HumanMessage("フシギダネの相手であるナゾノクサのHPは残りわずか24/125であり、これまでの戦闘で「いあいぎり」攻撃が安定したダメージを与えてきました。相手のHPを削りきれる可能性が高いため、ここでは「たたかう」を選択し、技選択画面に進んで「いあいぎり」を再度選択することで、ナゾノクサを倒し勝利することが期待できます。この行動が目標達成の最適な方法です。"),
            # HumanMessage("現在の状況では、対戦相手のナゾノクサのHPが24/125と残りわずかです。先に使用してきた「いあいぎり」はノーマルタイプの攻撃で相手に安定したダメージを与えているため、勝利に近づけると考えられます。このターンで相手を倒し、バトルに勝利するためにもう一度「いあいぎり」を選択することが最も効果的です。"),
            # HumanMessage("現在、バトル画面の情報によると、こちらのポケモンであるフシギダネのHPは101/125で、相手のナゾノクサのHPが3/125とかなり削られており、わずかです。これまでの戦闘で「いあいぎり」が有効に働いていたため、次のターンでは必ず「いあいぎり」を選択して、相手のナゾノクサを倒すことが最も効果的な選択です。相手のHPが非常に低いため、この攻撃で十分に勝利できると考えられます。現在はアニメーション進行中なので、待機します。"),
            # HumanMessage("フシギダネは現在「ねむり」状態になっており、次のターンに攻撃を行うことができません。また、ナゾノクサのHPが残り3/125と非常に少ないため、この状況を打開するためには別のポケモンに交代して、攻撃を行えるようにする方が良いです。相手も「くさ」タイプであるため、可能であれば「くさ」タイプに有利なポケモンに交代を考慮します。したがって、まずポケモン交代画面に進む必要があります。"),
            # HumanMessage("現在フシギダネが「ねむり」状態で攻撃不可能であり、相手のナゾノクサのHPが残りわずか3です。すぐに攻撃を行い試合を決定付けるためには、速やかに行動可能な「ヒトカゲ」に交代するのが最も合理的です。ヒトカゲはフシギダネと同じレベルで、HPが満タン、かつ「ふつう」状態であるため、速やかな選択と攻撃が可能です。"),
            # HumanMessage("現在のバトル状況では、こちらのポケモンであるヒトカゲは状態が「ふつう」でHPも満タンです。また、相手のナゾノクサのHPは3/125と非常に少ない状態です。これまでのフシギダネとの戦闘で削られたナゾノクサに対し、ヒトカゲを使用することで、すぐに勝利を得ることが可能と考えられます。アニメーションが終了し技選択が可能になった場合、ヒトカゲの強力な攻撃技を選択し、ナゾノクサを倒すことが勝利への確実な一手となります。"),
            # HumanMessage("ヒトカゲと相手のナゾノクサの状態を考慮すると、ナゾノクサのHPは残り10であり、ヒトカゲの「かえんほうしゃ」はほのおタイプの技であり、「くさ」タイプのナゾノクサに対して非常に効果的です。この技を使用することで、相手に対して大ダメージを与え確実にナゾノクサを倒すことができ、試合を終わらせ勝利する可能性が高くなります。したがって、「かえんほうしゃ」を選択するのが最も効果的な判断です。"),
            # HumanMessage("バトル画面において、相手ポケモンであるナゾノクサが「ひんし」状態になったため、次のステップである勝利の宣布や次のバトルステージへの移行などに進む可能性が高いです。現在画面はアニメーションの進行中であるため、新たな操作は不要で待機し、次の選択フェーズが訪れた場合に指示が必要となるでしょう。"),
            # HumanMessage("現在のバトル選択画面では、こちらのポケモンであるヒトカゲがほのおタイプであり、相手のニャースに対する有利不利は特にないものの、ヒトカゲはHPもほぼ満タンであるため安心して戦闘に臨めます。通常、先制攻撃を行うことでこちらのペースで戦闘を進めることができます。過去の戦闘においてヒトカゲが「かえんほうしゃ」で効果的に攻撃できたことがあるので、「たたかう」を選択し、攻撃に集中するのが良い戦略です。この選択は、こちらのプレイ目標であるバトルで1勝するためのステップであると考えられます。"),
            # HumanMessage("ヒトカゲとニャースの対戦において、ヒトカゲの技リストでは「かえんほうしゃ」が最も確実なダメージを狙える技です。ニャースはノーマルタイプであり、ほのおタイプの「かえんほうしゃ」に対して特に弱点はありませんが、技選択の合理性から見て「かえんほうしゃ」が高威力で残りのHPも十分あるため、有利な状況から積極的に攻撃を仕掛けることで試合を優位に進められます。今回、技選択に集中し、早期決着を狙います。"),
            # HumanMessage("現在のバトル画面では、ヒトカゲとニャースの対戦が進行しています。ヒトカゲは「かえんほうしゃ」を選択したばかりで、まだアニメーション進行中との情報があります。したがって、現在は待機してアニメーションが終了し、次の入力ができる状態になるまで操作を行わずに様子を見る必要があります。次の入力可能な状態になったら、再び戦闘を進めるべく適切な攻撃を選択する準備を整えます。"),
            # HumanMessage("現在、バトル選択画面において、こちらのヒトカゲ（LV50）が相手のニャース（LV50）と対戦しています。ヒトカゲはHPが58/119であり、相手のニャースはHPが47/120です。ヒトカゲの状態は「ふつう」であるため、特に妨げられることなく攻撃を仕掛けることができます。この状況では、先手を取ってニャースに攻撃を加えるのが効果的です。\n\n前回の判断では、「かえんほうしゃ」を選択して大ダメージを与えましたが、まだニャースを倒しきれていないため、再度「かえんほうしゃ」を使用して確実に相手を倒す戦略が良いと考えられます。従って、「たたかう」を選択し、技「かえんほうしゃ」を選んで攻撃するべきです。"),
            # HumanMessage("こちらのヒトカゲは「かえんほうしゃ」を選択し続けてニャースに攻撃していますが、ニャースをまだ倒しきれていません。技選択画面でヒトカゲは依然として「かえんほうしゃ」を使用できるPPがあり、威力も高いため、再度「かえんほうしゃ」を使用してニャースに大きなダメージを与えることが最も効果的です。ヒトカゲのHPは58/119と相手の攻撃を受けてもまだ多少の余裕があるため、攻撃続行が妥当です。この場面で決定的なダメージを与え、相手を倒すことを狙います。"),
            # HumanMessage("現在、こちらのヒトカゲが相手のニャースとのバトルで「ひんし」状態になっています。そのため、バトルを続行するためには手持ちのポケモンから新たに戦闘に出すポケモンを選択する必要があります。手持ちの中で最も戦闘に適したポケモンを選び、次の行動に備えることが最も重要です。ヒトカゲが「ひんし」状態である以上、まずは次のポケモンを選択画面で選ぶアクションを行う必要があります。"),
            # HumanMessage("現在、こちらの手持ちポケモンはヒトカゲが「ひんし」状態、ピカチュウも「ひんし」で、フシギダネのみが「ねむり」状態で残っています。「ねむり」状態であっても、フシギダネは唯一戦闘に参加可能なポケモンで、一定確率で目を覚ます可能性があるため、すぐに選択してバトルを続行する必要があります。ニャースと対抗する戦略としてフシギダネを繰り出すのが最善です。"),
            # HumanMessage("現在、こちらのヒトカゲとピカチュウはどちらも「ひんし」状態でバトル不能となっており、唯一残っているフシギダネが「ねむり」状態ですが、戦闘に参加可能な状態です。相手のニャースのHPは47/120と、攻撃次第で十分に倒せる範囲です。戦略としては、フシギダネを選択してバトルに出し、目覚めることを期待しつつ先に攻撃を行うチャンスを待つのが最適です。このため、フシギダネを選択してバトルに参加させます。"),
            # HumanMessage("現在、フシギダネが「ねむり」状態で戦闘に出ていますが、画面上でアニメーションが進行しているため、新たな入力は必要ありません。フシギダネの「ねむり」状態が解けるまで待機する必要がありますが、次の選択フェーズが発生するまで現時点では操作を行わないことが適切です。フシギダネが目を覚まして行動可能となった際には、戦術的な技または戦略を考慮して行動を選択する準備を整えておくべきです。"),
            # HumanMessage("現在、フシギダネは「ねむり」状態ですが、唯一戦闘可能なポケモンです。相手のニャースはHPが残り47/120ですので、適切な技で攻撃すれば倒すことが可能です。「たたかう」を選択し、フシギダネが目を覚ますことを期待して攻撃手段を選択する準備をします。フシギダネが目を覚まして行動可能になったとき、より効果的な攻撃を狙います。"),
            # HumanMessage("現在の状況では、フシギダネは「ねむり」状態ですが、「ねむり」の間に技を選択しておくことで、目を覚ました際にすぐに攻撃が可能です。相手のニャースはHPが47/120であり、素早く倒すことが重要です。技リストから「はっぱカッター」を選択します。これはフシギダネのくさタイプ技でPPも十分あるため、目を覚ました際に効果的に攻撃する可能性が高いです。また、効果が高い技として相手のニャースをすぐに倒すことが狙えます。"),
            # HumanMessage("現在の状況では、フシギダネが「ねむり」状態であり、このターンではアニメーションが進行しているため、現時点での新たな入力は不要です。そのままアニメーションが終了するのを待ち、次の攻撃が可能になるタイミングで、フシギダネが目を覚まし次第「はっぱカッター」を実行するのが最も効果的です。これにより、相手のニャースを速やかに倒すことを狙います。とにかく次の状態変化を待たなければ現状維持を変えられないため、アニメーション終了を待ちます。"),
            # HumanMessage("現在のバトル選択画面では、こちらが操作するポケモンのフシギダネが「ふつう」状態であり、相手のニャースのHPは47/120と削られた状態です。この状況では、先手を取って相手を倒すために攻撃を選択することが望ましいです。画面上で「たたかう」オプションが表示されており、攻撃を開始するための操作が可能です。したがって、ここで「たたかう」を選択し、次の技選択画面に進むことでニャースに対して有効な攻撃を行います。"),
            # HumanMessage("フシギダネは現在「ふつう」状態で、攻撃が可能な状態です。このターンでニャースを倒すために、もっとも強力な技で攻撃を試みるのが最善です。技選択肢の中で「はっぱカッター」はくさタイプの技で、フシギダネの特性を活かした戦法と言えます。また、「はっぱカッター」のPPは十分余っているので使用に躊躇はありません。この技を使用することで、相手に大ダメージを与え、ニャースを倒すチャンスを大いに増やすことができます。したがって、「はっぱカッター」を選んで攻撃する行動を取ります。"),
            # HumanMessage("フシギダネは現在「ふつう」状態で攻撃が可能です。相手のニャースのHPは47/120であり、倒すチャンスがあります。選択可能な技の中で「はっぱカッター」はくさタイプの技で、タイプ一致かつ十分なPPを確保しており、最も大きなダメージを期待できます。前回の操作で進行せず、再度作戦を見直す必要があり、技選択を確実に完了させるために「はっぱカッター」を選び直すことで、効果的に相手のニャースを倒し勝利に近づくことができます。再度Rボタンをホールドしたうえで「Cキー上」操作を行い、「はっぱカッター」を選択し直します。"),
            # HumanMessage("現在、フシギダネは「ふつう」状態で攻撃可能です。前回の操作が不完全で技の選択が進行していませんでした。したがって、もう一度「はっぱカッター」を選択する必要があります。「はっぱカッター」はタイプ一致の攻撃で効果的であり、ニャースの残りHPを考慮すると十分なダメージを期待できます。この技選択は最も効果的な戦略であるため、Rボタンの操作が適切に実行されていない可能性も含め、確実に選択を完了します。"),
            # HumanMessage("前回の操作「push_R」が機能していないため、再度確認操作が必要です。現在の状況は「バトル選択確認画面」であり、「はっぱカッター」を選択するためには、技選択画面に進む必要があります。前回の指示が適切に機能していなかったか、操作を確認するために「Rボタンのホールド」が求められます。フシギダネが攻撃可能で、「はっぱカッター」が選択されればニャースを倒す大きなチャンスがあるため、技選択画面に進むのが適切です。"),
            # HumanMessage("現在、フシギダネは「技選択画面」におり、「はっぱカッター」を選択することでニャースを倒す大きなチャンスがあります。「はっぱカッター」はフシギダネのタイプ一致技であり、相手に対し最大のダメージを与えられます。選択ミスを避けつつ、確実に技を選択するため、再度「Rボタン」をホールドしている状態から「Cキー上」を押して、技を選択して攻撃します。"),
            # HumanMessage("現在の技選択画面では、フシギダネの「はっぱカッター」攻撃が最も効果的であると判断できます。これは、ニャースに対してタイプ一致のくさ技で最大の打撃を与えることができるためです。前回のRボタンをホールドする操作が機能せず、技が決定されなかった可能性があります。したがって、Rボタンホールド中に「Cキー上ボタン」を押すという操作を再確認し、確実に技を選択して攻撃を開始します。これにより、ニャースを倒すチャンスを最大限に高めます。"),
            # HumanMessage("前回の操作ではRボタンをホールドした状態で「はっぱカッター」を選択しようとしましたが、前回の指示が適切に機能していなかった可能性があります。現在の画面は技選択画面であり、「はっぱカッター」を選択することでニャースを効果的に攻撃できます。「はっぱカッター」はフシギダネのタイプ一致技で、ニャースに最大のダメージを与えられる技です。この選択は最も合理的な攻撃となるため、再度確実に技を選択する操作を行い、相手のニャースを倒すことを目指します。"),
            # HumanMessage("これまでの操作ではRボタンホールドの操作がうまく機能していなかったため、技選択が確定されていませんでした。現在の技選択画面では、フシギダネの「はっぱカッター」を選ぶことで、相手のニャースに対して最も効果的なダメージを与えることができる可能性があります。「はっぱカッター」はタイプ一致技であり、相手の残りHPから見て、これによってニャースを倒すことが可能です。したがって、再度Rボタンを適切にホールドした上で「はっぱカッター」を選択するためにCキー上を押す操作を実行し、選択を確実にします。"),
            # HumanMessage("現在の画面はNintendo Switchのホーム画面に表示されており、「Nintendo 64 Online」アプリケーションが示されています。この状態ではゲームがまだ開始されていないため、「つづける」オプションを選択してアプリを起動する必要があります。これにより、前回プレイしていた「ポケモンスタジアム2」のセッションに戻ることが可能です。"),
            # HumanMessage("現在の画面はNintendo Switchのホーム画面であり、「Nintendo 64 Online」アプリケーションを続行するオプションが表示されています。先ほどのバトルの進行が完全に止まっていた可能性があり、ゲームに戻るためには「Aボタン」を押して続行する必要があります。これにより、引き続き「ポケモンスタジアム2」のゲームを再開し、目標であるバトルの勝利を目指します。"),
            # HumanMessage("現在、われわれの画面は「バトル選択確認画面」にあり、ポケモン同士のレベルやHPが表示されています。われわれの目的は「とにかくバトルがしたい！」モードで1勝することです。相手ポケモンではなく、選択した自分のポケモンとのバトルが進行中のようです。この画面からバトルを開始するためには、「かくにん」を選択する必要があります。オプションに示されているように、Rボタンをホールドすることで進むことができるため、この操作を行うことでバトルを開始します。"),
            # HumanMessage("こちらの技選択画面では、フシギダネが「はっぱカッター」、「ねむりごな」、「いあいぎり」、「やどりぎのタネ」の技を使用可能です。相手のポケモン、ニャースはノーマルタイプであり、くさタイプの技である「はっぱカッター」が効果的です。また、PPが充分残っており（25/25）、相手のHPを早急に削るために攻撃的な選択が必要です。よって、技「はっぱカッター」を使うと良いでしょう。"),
            # HumanMessage("現在の画面はアニメーション中であり、前回実行した技「はっぱカッター」が進行中です。アニメーションが完了するまでは操作は不要です。現状のバトル情報から判断して、フシギダネのHPはまだ余裕があり、相手のニャースのHPは半分以下に減っています。よってこのままアニメーションが完了し、その効果が確認できるまでは待機します。"),
            # HumanMessage("ニャースのHPが0になり、バトルは終了しました。次のシーンに進むために、画面に指示されている「Aボタン」を押す必要があります。これにより、バトルの結果が表示され、プレイ目標である1勝を達成することになります。"),
            # HumanMessage("現在の画面は「ゲームモード選択画面」で、目標である「とにかくバトルがしたい！」モードでのバトルに進むため、選択肢を「とにかくバトルがしたい！」に合わせて選択する必要があります。このオプションを選択することで、素早くバトルを行うモードに進むことができます。操作手順としては、十字キーで「左」を押して選択肢を「とにかくバトルがしたい！」に合わせ、「Aボタン」を押して確定します。"),
        ],
        "previous_screen": "バトル選択",
        "format_instructions": format_instructions,
    }
)

print(prompt_value)

model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
# model = ChatAnthropic(model="claude-3-5-haiku-20241022", temperature=0)
# model = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0)

# print(prompt_value)

ai_message = model.invoke(prompt_value)
# print(ai_message.content)
action = output_parser.invoke(ai_message)
print(action)


# [
#   {
#     "type": "目標更新",
#     "play_target": "「とにかくバトルがしたい！」モードで1勝する。"
#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "目標更新",
#     "play_target": "「とにかくバトルがしたい！」モードで1勝する。"
#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   },
#   {
#     "type": "プレイログ更新",

#   }
# ]