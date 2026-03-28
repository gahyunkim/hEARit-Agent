from google import genai
from google.genai import types
from config import API_KEY
from rich.console import Console

client = genai.Client(api_key=API_KEY)
console = Console()

_BEST_MODEL = None

def get_cost_effective_model():
    """사용 가능한 모델 목록을 조회하여 가장 가성비가 좋은(Flash) 모델을 동적으로 선택합니다."""
    global _BEST_MODEL
    if _BEST_MODEL:
        return _BEST_MODEL
        
    try:
        flash_models = []
        for m in client.models.list():
            name = m.name.replace('models/', '')
            # Flash 모델이 속도가 빠르고 비용이 가장 저렴함
            if 'flash' in name.lower() and 'thinking' not in name.lower():
                flash_models.append(name)
        
        if flash_models:
            # 문자열 기준 역순 정렬로 최신 버전을 1순위로 배치 (예: 2.5-flash > 2.0-flash > 1.5-flash)
            flash_models.sort(reverse=True)
            _BEST_MODEL = flash_models[0]
        else:
            _BEST_MODEL = "gemini-2.0-flash" # Fallback
            
        console.print(f"[dim cyan]🤖 API 조회 완료: 가성비 최적화 모델({_BEST_MODEL})을 사용합니다.[/dim cyan]")
    except Exception:
        _BEST_MODEL = "gemini-2.0-flash"
        
    return _BEST_MODEL

def generate_topic():
    topic_prompt = "현재 IT 생태계(안드로이드, 스프링 등) 핵심 기술 주제 1개 선정. 주제명만 출력."
    model_name = get_cost_effective_model()

    res = client.models.generate_content(
        model=model_name, 
        contents=topic_prompt,
        config={'tools': [types.Tool(google_search=types.GoogleSearch())]}
    )
    return res.text.strip()

def generate_source_text(topic):
    instruction = "IT 기술 정보 추출 전문가로서 데이터 밀도가 높은 원천 정보를 수집하라."
    model_name = get_cost_effective_model()
    resp = client.models.generate_content(
        model=model_name, 
        config={'system_instruction': instruction, 'tools': [types.Tool(google_search=types.GoogleSearch())]},
        contents=f"'{topic}'에 대한 2026년 최신 기술 정보를 상세히 정리해줘."
    )
    return resp.text