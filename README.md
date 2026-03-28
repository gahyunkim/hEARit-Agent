# hEARit-Agent v2.0

AI와 웹 자동화를 사용하여 최신 IT 트렌드 및 다양한 카테고리의 기술 팟캐스트를 생성하는 자동화 에이전트입니다.

## 개요

hEARit-Agent는 IT 전문 팟캐스트의 콘텐츠 제작 전체 과정을 자동화하는 Python 기반 도구입니다. 
Google Gemini API를 사용하여 주제 선정 및 대본을 생성하고, Google의 NotebookLM을 통해 텍스트를 음성으로 변환하며, 
Selenium을 활용하여 원본 자료 업로드부터 최종 오디오 파일의 관리자 대시보드 게시까지 모든 웹 기반 상호작용을 자동화합니다.

## 주요 기능

-   **AI 기반 콘텐츠 제작:** Gemini API와 Google 검색을 연동하여 최신 IT 트렌드에 대한 주제를 자동으로 제안하고 상세한 대본을 생성합니다.
-   **자동화된 오디오 합성:** 생성된 텍스트를 NotebookLM에 업로드하고 AI 오디오 오버뷰(팟캐스트) 생성을 실행합니다.
-   **지속적인 모니터링 및 다운로드:** 생성 상태를 모니터링하고 완성된 오디오 파일을 자동으로 다운로드합니다.
-   **오디오 처리:** FFmpeg를 사용하여 대용량 오디오 파일을 웹 친화적인 포맷으로 압축합니다.
-   **자동화된 게시:** 지정된 관리자 대시보드에 로그인하여 최종 팟캐스트 오디오 파일을 업로드합니다.
-   **모듈식 아키텍처:** 코드가 명확한 관심사 분리 원칙에 따라 구조화되어 있어 유지보수 및 확장이 용이합니다.
-   **대화형 CLI:** 전체 파이프라인 또는 개별 단계를 별도로 실행할 수 있는 간단한 명령줄 인터페이스를 제공합니다.

## 사전 준비 사항

시작하기 전에, 시스템에 다음 프로그램들이 설치되어 있는지 확인하세요:
-   [Python](https://www.python.org/downloads/) (3.9 이상)
-   [Google Chrome](https://www.google.com/chrome/)
-   [FFmpeg](https://ffmpeg.org/download.html) (시스템의 PATH에서 접근 가능해야 합니다)

## 설치 및 설정

1.  **리포지토리 복제:**
    ```bash
    git clone <your-repository-url>
    cd joigent
    ```

2.  **가상 환경 생성 및 활성화:**
    ```bash
    # macOS/Linux
    python3 -m venv .venv
    source .venv/bin/activate

    # Windows
    python -m venv .venv
    .venv\Scripts\activate
    ```

3.  **의존성 설치:**
    아래 내용으로 `requirements.txt` 파일을 생성하고, 설치 명령어를 실행하세요.

    **`requirements.txt`**
    ```
    google-generativeai
    selenium
    webdriver-manager
    rich
    python-dotenv
    ```

    ```bash
    pip install -r requirements.txt
    ```

4.  **환경 변수 설정:**
    프로젝트 최상위 경로에 `.env` 파일을 생성하고 다음 설정을 추가하세요. 이 파일은 보안을 위해 Git에 의해 무시됩니다.

    ```env
    # Google Gemini API 키
    API_KEY="your_google_ai_api_key"

    # 관리자 페이지 URL
    ADMIN_LOGIN_URL="https://your-admin-page.com/login"

    # 관리자 페이지 연결을 위한 로그인 정보
    ADMIN_ID="your_admin_username"
    ADMIN_PW="your_admin_password"

    # 오디오 생성용 커스텀 프롬프트
    CUSTOM_AUDIO_PROMPT="NotebookLM에서 팟캐스트 생성 시 추가해주던 프롬프트"
    ```

## 사용법

프로젝트의 최상위 디렉토리에서 메인 스크립트를 실행하세요:

```bash
python main.py
```

실행 시 다음과 같은 메뉴가 나타납니다:
-   **[1] 전체 실행:** 주제 생성부터 관리자 페이지 업로드까지 전체 파이프라인을 실행합니다.
-   **[2] 1단계(텍스트) (Step 1: Text):** 주제를 바탕으로 딥리서치한 원본 텍스트만 생성합니다.
-   **[3] 2~3단계(생성/다운로드) (Step 2-3: Create/Download):** 가장 최근의 리서치된 텍스트를 사용하여 팟캐스트를 생성하고 다운로드합니다.
-   **[4] 4단계(어드민 업로드) (Step 4: Admin Upload):** 가장 최근의 오디오 파일을 관리자 페이지에 업로드합니다.

이 스크립트는 로그인 세션을 유지하기 위해 전용 크롬 프로필(automation_chrome_profile)을 사용합니다. 
처음 실행 시 자동화된 브라우저 창 내에서 Google 및 관리자 페이지에 수동으로 로그인해야 할 수 있습니다. 이후 실행부터는 저장된 세션을 사용합니다.

## 프로젝트 구조

이 프로젝트는 각 모듈의 역할을 명확히 분리하는 구조를 따릅니다:

```
joigent/
├── .venv/                  # 가상 환경
├── downloads/              # 텍스트 및 오디오 파일 출력 디렉토리 (Git 제외)
├── automation_chrome_profile/ # Selenium 브라우저 프로필 (Git 제외)
├── .env                    # 환경 변수 (Git 제외)
├── .gitignore              # Git 무시 설정 파일
├── main.py                 # 메인 컨트롤러 및 CLI 진입점
├── ai_service.py           # Gemini API와의 모든 상호작용 처리
├── automation.py           # 웹 자동화(Selenium) 로직 포함
├── utils.py                # 파일/시스템 작업을 위한 유틸리티 함수
├── config.py               # 설정 변수 로드 및 제공
└── README.md               # 프로젝트에 대한 설명
```
