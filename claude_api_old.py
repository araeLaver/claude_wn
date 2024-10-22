import anthropic

CLAUDE_API_KEY = "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"

client = anthropic.Client(api_key=CLAUDE_API_KEY)

def call_claude_api(prompt):
    try:
        # Messages API를 이용한 요청 구성
        response = client.completions.create(
            model="claude-2",  # 지원되는 최신 모델 사용
            max_tokens_to_sample=300,
            prompt=f"{anthropic.HUMAN_PROMPT} {prompt} {anthropic.AI_PROMPT}",
            temperature=0.7
        )
        # 응답에서 생성된 텍스트 추출
        return response.completion
    except Exception as e:
        # 오류 발생 시 로그 출력
        print(f"API 호출 중 오류 발생: {e}")
        return f"Error: {str(e)}"
