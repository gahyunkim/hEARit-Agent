import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 전역 설정 변수
API_KEY = os.environ.get("API_KEY")
ADMIN_URL = os.environ.get("ADMIN_LOGIN_URL")
NOTEBOOK_URL = os.environ.get("NOTEBOOK_LM_URL", "https://notebooklm.google.com/")
PROFILE_PATH = os.path.abspath(os.environ.get("CHROME_PROFILE_NAME", "automation_chrome_profile"))
ADMIN_ID = os.environ.get("ADMIN_ID")
ADMIN_PW = os.environ.get("ADMIN_PW")