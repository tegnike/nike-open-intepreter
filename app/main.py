from fastapi import FastAPI
from app.routers import base
from app.adapters.mongo_adapter import MongoAdapter
from app.adapters.openai_adapter import OpenAIAdapter
import ptvsd
import os

if os.getenv("DEBUG_MODE") == "1":
    # デバッグ用コード
    ptvsd.enable_attach(address=("0.0.0.0", 5678), redirect_output=True)
    ptvsd.wait_for_attach()

# アダプターのグローバルインスタンスを作成
mongo_adapter = MongoAdapter("default_game", "default_save", "default_target")
openai_adapter = OpenAIAdapter()

app = FastAPI()
app.include_router(base.router)

# アダプターインスタンスをrouterで使えるようにする
app.state.mongo_adapter = mongo_adapter
app.state.openai_adapter = openai_adapter
