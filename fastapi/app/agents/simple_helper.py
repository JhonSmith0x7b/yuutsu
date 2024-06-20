from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_fix.redis_history import RedisChatMessageHistory
from agents.base_agent import BaseAgent
from dotenv import load_dotenv;load_dotenv(override=True)
import os
from langchain_core.runnables import Runnable
from typing import AsyncGenerator


class SimpleHelper(BaseAgent):
    
    def __init__(self):
        self.chain = self.create_agent()

    def create_agent(self) -> Runnable:
        openai = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL"), 
            base_url=os.getenv("OPENAI_API"),
            api_key=os.getenv("OPENAI_KEY"),
            temperature=0.7,
        )
        prompt = ChatPromptTemplate.from_messages([
            ('system', open("./prompts/simple-helper.md").read()),
            MessagesPlaceholder(variable_name="history"),
            ('human', '{input}'),
        ])
        chain = RunnableWithMessageHistory(
            prompt | openai,
            lambda session_id: RedisChatMessageHistory(
                session_id, url=os.getenv("REDIS_URL"), ttl=60*60*24*7, capacity=10
            ),
            input_messages_key="input",
            history_messages_key="history"
        )
        return chain
    
    async def astream(self, input: str, session_id: str) -> AsyncGenerator:
        async for s in self.chain.astream(
            {"input": input},
            config={"configurable": {"session_id": session_id}}
        ):
            yield s.content
