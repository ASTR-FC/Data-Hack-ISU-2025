import requests

import os

# Disable proxies completely
os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""
os.environ["http_proxy"] = ""
os.environ["https_proxy"] = ""


BACKEND_URL = "http://8.211.16.127/ask"


def ask_qwen(prompt: str):
    response = requests.post(
        BACKEND_URL,
        json={
            "model": "qwen-plus",
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
    )
    data = response.json()
    return data.get("response", "Error: no response")
