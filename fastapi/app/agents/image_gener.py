from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, HumanMessagePromptTemplate
from agents.base_agent import BaseAgent
from dotenv import load_dotenv;load_dotenv(override=True)
import os
from langchain_core.runnables import Runnable
from typing import AsyncGenerator
import base64
from langchain_core.output_parsers import StrOutputParser


class ImageGener(BaseAgent):
    
    def __init__(self):
        self.chain = self.create_agent()

    def create_agent(self) -> Runnable:
        openai = ChatOpenAI(
            model='gpt-4o', 
            base_url=os.getenv("OPENAI_API"),
            api_key=os.getenv("OPENAI_KEY"),
            temperature=0.7,
        )
        prompt = ChatPromptTemplate.from_messages([
            ('system', open("./prompts/image-gen-agent.md").read()),
            HumanMessagePromptTemplate.from_template(
                template=[{"type": "image_url", "image_url": {"url": "{image_url}"}}]
            ),
            ("human", "{platform}"),
            ("human", "{prompt} 字数 {text-length}")
        ])
        chain = prompt | openai | StrOutputParser()
        return chain

    def invoke(self, 
               image_path: str, 
               prompt: str, 
               platform: str, 
               text_length: str):
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
        encoded_image = f"data:image/jpeg;base64,{encoded_image}"
        result =  self.chain.invoke(
            {
                "image_url": encoded_image, 
                "prompt": prompt, 
                "platform": platform, 
                "text-length": text_length
            })
        return result