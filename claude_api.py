import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY")

if not CLAUDE_API_KEY:
    raise ValueError("CLAUDE_API_KEY가 설정되지 않았습니다.")

client = anthropic.Client(api_key=CLAUDE_API_KEY)

MODEL_NAME = "claude-2"
MAX_TOKENS = 300
TEMPERATURE = 0.7

def call_claude_api(messages):
    """
    Claude API를 호출하여 응답을 반환합니다.

    Parameters:
        messages (list): 대화의 메시지 리스트

    Returns:
        str: Claude의 응답 또는 오류 메시지
    """
    prompt = ''
    for msg in messages:
        if msg['role'] == 'user':
            prompt += f"{anthropic.HUMAN_PROMPT} {msg['content']}\n"
        else:
            prompt += f"{anthropic.AI_PROMPT} {msg['content']}\n"
    prompt += anthropic.AI_PROMPT

    try:
        response = client.completions.create(
            model=MODEL_NAME,
            max_tokens_to_sample=MAX_TOKENS,
            prompt=prompt,
            temperature=TEMPERATURE
        )
        return response.completion.strip()
    except anthropic.ApiException as e:
        print(f"Anthropic API 예외 발생: {e}")
        return "API 요청 중 문제가 발생했습니다. 잠시 후 다시 시도해주세요."
    except Exception as e:
        print(f"알 수 없는 오류 발생: {e}")
        return "예기치 못한 오류가 발생했습니다."
