# nmgm/agents/wrappers.py
from pydantic import BaseModel

# 신 SDK (google-genai) 우선 사용, 실패 시 구 SDK(google-generativeai)로 폴백
try:
    from google import genai                   # google-genai
    from google.genai import types
    _USE_NEW = True
except Exception:
    import google.generativeai as genai        # google-generativeai
    types = None
    _USE_NEW = False


class GoogleWrapper:
    def __init__(self, api_key: str):
        self.api_key = api_key
        if _USE_NEW:
            # google-genai
            self.client = genai.Client(api_key=api_key)
        else:
            # google-generativeai
            genai.configure(api_key=api_key)
            self.client = None  # 구 SDK는 client 객체 없이 사용

    def generate(
        self,
        model_name: str = "gemini-2.0-flash",
        prompt: str = "",
        structure: type[BaseModel] | None = None,
        temperature: float = 0.2,
        tools: list = [],
    ):
        if _USE_NEW:
            # --- NEW SDK PATH ---
            if structure is None:
                resp = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=temperature,
                        tools=tools,
                    ),
                )
                return resp.text
            else:
                resp = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=temperature,
                        tools=tools,
                        response_mime_type="application/json",
                        response_schema=structure,
                    ),
                )
                # google-genai의 .parsed 는 pydantic 모델 인스턴스/리스트로 파싱됨
                return resp.parsed
        else:
            # --- OLD SDK PATH (google-generativeai) ---
            # 구 SDK는 response_schema/parsed 같은 구조화 반환이 없습니다.
            # 구조를 요구한 경우에도 text를 그대로 반환하도록 하고,
            # 호출부(agents.py)는 .model_dump() 등을 기대하면 안 됩니다.
            model = genai.GenerativeModel(model_name)
            resp = model.generate_content(
                prompt,
                generation_config={"temperature": temperature}
            )
            return resp.text
