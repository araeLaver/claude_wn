import os
import anthropic  # 추가
from anthropic import Anthropic, APIError
from dotenv import load_dotenv

load_dotenv()

CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY")

if not CLAUDE_API_KEY:
    raise ValueError("CLAUDE_API_KEY가 설정되지 않았습니다.")

client = Anthropic(api_key=CLAUDE_API_KEY)

def call_claude_api(messages):
    """
    Claude API를 호출하여 응답을 반환합니다.

    Parameters:
        messages (list): 대화의 메시지 리스트

    Returns:
        str: Claude의 응답 또는 오류 메시지
    """
    try:
        # 메시지를 Anthropic의 메시지 형식으로 변환
        formatted_messages = []
        for message in messages:
            role = message['role']
            formatted_messages.append({
                "role": role,
                "content": [
                    {
                        "type": "text",
                        "text": message['content']
                    }
                ]
            })

        # 시스템 메시지 설정 (선택 사항)
        system_prompt = "당신은 친절한 도우미입니다."

        # API 호출
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",  # 사용 가능한 모델 이름으로 변경
            max_tokens=4000,
            temperature=0.7,
            system=system_prompt,
            messages=formatted_messages
        )
        print("@@@@@@@@@ ::", response)
        # 응답 내용 반환
        # response.content는 리스트 형태이며, 각 요소는 딕셔너리입니다.
        # content 중에서 type이 'text'인 것의 'text' 값을 이어붙입니다.
        assistant_response = ''
        for content_part in response.content:
            if content_part.type == 'text':
                assistant_response += content_part.text

        return assistant_response.strip()
    except APIError as e:
        print(f"Anthropic API 예외 발생: {e}")
        return "API 요청 중 문제가 발생했습니다. 잠시 후 다시 시도해주세요."
    except Exception as e:
        print(f"알 수 없는 오류 발생: {e}")
        return "예기치 못한 오류가 발생했습니다."

