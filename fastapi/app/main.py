from fastapi import FastAPI, Request
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


app = FastAPI()
simple_helper = None

def init_agents() -> None:
    global simple_helper
    simple_helper = SimpleHelper()

@app.get("/simple-helper")
async def get(request: Request) -> Response:
    query_params = request.query_params
    input = query_params.get("input")
    headers = request.headers
    session_id = headers["session_id"]
    if not session_id:
        return Response(content="session_id is required", status_code=500)
    return StreamingResponse(
        content=simple_helper.astream(input, session_id), 
        media_type="text/plain"
        )


init_agents()


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
