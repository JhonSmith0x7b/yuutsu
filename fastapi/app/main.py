from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import StreamingResponse
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
import asyncio
import uvicorn
import logging
from langchain_fix.redis_history import RedisChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from agents import SimpleHelper
from fastapi import Response
import shutil
import os
from utils import simple_asr, simple_tts
from fastapi.staticfiles import StaticFiles


app = FastAPI()
simple_helper = None
os.path.exists("./audios") or os.makedirs("./audios")
app.mount("/audios", StaticFiles(directory="./audios"), name="audios")


def init_agents() -> None:
    global simple_helper
    simple_helper = SimpleHelper()


@app.get("/simple-helper")
async def get(request: Request) -> Response:
    query_params = request.query_params
    input = query_params.get("input")
    headers = request.headers
    session_id = query_params.get("session_id")
    if not session_id:
        return Response(content="session_id is required", status_code=501)
    return StreamingResponse(
        content=simple_helper.astream(input, session_id), 
        media_type="text/plain"
        )


@app.post("/uploadfile")
async def create_upload_file(file: UploadFile = File(...)) -> Response:
    os.path.exists("./uploads") or os.makedirs("./uploads")
    with open(f"uploads/{file.filename}", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    result = await simple_asr(f"uploads/{file.filename}")
    text = result['payload_msg']['result'][0]['text']
    return {"text": text}


@app.get("/tts")
async def tts(request: Request) -> Response:
    query_params = request.query_params
    text = query_params.get("text")
    result = simple_tts(text)
    if not result:
        return Response(content="Error occurred during TTS", status_code=501)
    file_url = str(request.base_url) + result[2:]
    return {"tts_url": file_url}


@app.get("/test")
async def test() -> Response:
    result = await simple_asr("./uploads/tmp.mp3")
    print(result)
    return {"message": "Hello, World!"}


init_agents()


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
