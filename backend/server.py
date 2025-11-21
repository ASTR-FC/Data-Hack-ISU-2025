from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
import os

app = FastAPI()

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
)

class Query(BaseModel):
    messages: list
    model: str = "qwen-plus"

@app.post("/ask")
def ask(query: Query):
    completion = client.chat.completions.create(
        model=query.model,
        messages=query.messages
    )
    return {"response": completion.choices[0].message.content.strip()}
