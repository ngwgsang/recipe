import requests

from pydantic import BaseModel
from typing import Literal
from pydantic import BaseModel
from dotenv import dotenv_values
from typing import Literal

env = dotenv_values()

class Feedback(BaseModel):
    sentiment: Literal["positive", "neutral", "negative"]
    summary: str

def openrouter_with_struture(text: str, schemaModel: BaseModel):    
    schema = schemaModel.model_json_schema()
    payload = {
        "model": "tngtech/tng-r1t-chimera:free",
        "messages": [{"role": "user", "content": text}],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "weather",
                "strict": True,
                "schema": schema,
            },
        },
    }
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {env['OPENROUTER_API_KEY']}",
            "Content-Type": "application/json",
        },
        json=payload,
    )
    data = response.json()
    weather_info = data["choices"][0]["message"]["content"]
    weather = schemaModel.model_validate_json(weather_info)
    return weather.model_dump()

res = openrouter_with_struture("Tôi rất thích sản phẩm này", Feedback)
print(res)
