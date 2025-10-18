from pydantic import BaseModel

try:
    # 신규 SDK (google-genai)
    from google import genai
    from google.genai import types
    _USE_NEW = True
except Exception:
    # 구버전 SDK (google-generativeai) fallback
    import google.generativeai as genai  # type: ignore
    types = None  # 구버전엔 types 모듈 없음
    _USE_NEW = False

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