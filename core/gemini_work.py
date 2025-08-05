from google import genai
from google.genai import types
import json
import time

def call_gemini(api_key: str, prompt: str, model: str = "gemini-2.5-pro", retries: int = 3) -> dict:
    try:
        result = ""
        client = genai.Client(
            api_key=api_key,
        )

        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=prompt),
                ],
            ),
        ]
        tools = [
            types.Tool(googleSearch=types.GoogleSearch(
            )),
        ]
        generate_content_config = types.GenerateContentConfig(
            max_output_tokens=8192,
            thinking_config = types.ThinkingConfig(
                thinking_budget=-1,
            ),
            tools=tools,
        )

        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            result += chunk.text
        print(f'gemini result: {result}')
        if not result:
            print('no result from gemini')
            raise Exception("No result from Gemini")
        return result
    except Exception as e:
        # 오류가 발생했을 때 재시도 로직 실행
        print(f"An error occurred: {e}")
        
        # 1. 남은 재시도 횟수 확인
        if retries > 0:
            print(f"Retrying... ({retries} attempts left)")
            # 2. 잠시 대기 (API 서버에 부담을 주지 않기 위함)
            time.sleep(2)
            # 3. 재시도 횟수를 1 감소시켜 자기 자신을 다시 호출
            return call_gemini(api_key, prompt, model, retries - 1)
        else:
            # 4. 재시도를 모두 소진하면 최종 실패 메시지 반환
            print("All retries failed.")
            return json.dumps({"error": f"The request failed after multiple retries. Last error: {e}"})


if __name__ == "__main__":
    test_api_key = "AIzaSyDRg_55NEhdT0ur0L_xzw24_n5H002MaDo"
    result = call_gemini(test_api_key, prompt="What is the main purpose of Streamlit?", model="gemini-2.5-pro")
    print(f'out result: {result}')
