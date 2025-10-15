from google import genai
from google.genai import types
from pydantic import BaseModel

class GoogleWrapper:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = genai.Client(api_key=api_key)

    def generate(
        self,
        model_name: str = "gemini-2.0-flash",
        prompt: str = "",
        structure: BaseModel = None,
        temperature: float = 0.2,
        tools: list = [],
    ):
        if not structure:
            response = self.client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    tools=tools,
                ),
            )
            return response.text
        else:
            response = self.client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    tools=tools,
                    response_mime_type="application/json",
                    response_schema=structure,
                ),
            )
            return response.parsed