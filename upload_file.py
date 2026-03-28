import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from rich.console import Console

console = Console()

def run_notebooklm_upload(file_path):
    if not os.path.exists(file_path):
        console.print(f"[red]❌ 파일을 찾을 수 없습니다: {file_path}[/red]")
        return

    # 1. 크롬 옵션 설정 (로그인 세션 유지를 위해 사용자 프로필 사용 권장)
    chrome_options = Options()
    # 주의: 아래 경로는 본인의 맥북 사용자 이름에 맞게 수정이 필요할 수 있습니다.
    # chrome_options.add_argument(f"user-data-dir=/Users/kimgahyun/Library/Application Support/Google/Chrome/Default") 
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    wait = WebDriverWait(driver, 20)

    try:
        console.print("[yellow]🌐 NotebookLM 접속 중...[/yellow]")
        driver.get("https://notebooklm.google.com/")
        
        # 2. 로그인 확인 (수동 로그인이 필요할 경우 여기서 대기)
        console.print("[bold cyan]💡 만약 로그인이 안 되어 있다면, 지금 브라우저에서 로그인해 주세요! (60초 대기)[/bold cyan]")
        time.sleep(10) # 페이지 로딩 대기

        # 3. '새 노트' 또는 기존 노트 선택 (Selector는 페이지 업데이트에 따라 변할 수 있음)
        # 여기서는 가장 안전하게 "소스 추가" 버튼이 나올 때까지 기다립니다.
        console.print("[magenta]📂 소스 업로드 시퀀스 시작...[/magenta]")
        
        # 파일 업로드 input 요소 찾기 (NotebookLM의 실제 DOM 구조에 맞춰 조정 필요)
        # 보통 직접 클릭보다 파일을 전송(send_keys)하는 방식이 가장 확실합니다.
        upload_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='file']")))
        
        # 절대 경로로 파일 전송
        abs_path = os.path.abspath(file_path)
        upload_input.send_keys(abs_path)
        
        console.print(f"[bold green]✅ {file_path} 업로드 완료![/bold green]")
        
        # 4. 오디오 생성 버튼 클릭 (Deep Dive Audio)
        # 이 부분은 페이지 내 'Generate' 버튼의 정확한 텍스트나 ID가 필요합니다.
        console.print("[yellow]🎧 팟캐스트 생성 버튼을 찾고 있습니다...[/yellow]")
        # (실제 버튼 클릭 로직은 NotebookLM 화면 구성에 따라 추가 구현)

    except Exception as e:
        console.print(f"[red]❌ 업로드 중 에러 발생: {e}[/red]")
    finally:
        console.print("[blue]ℹ️ 브라우저를 유지합니다. 생성이 완료되면 직접 확인해 보세요![/blue]")
        # driver.quit() # 자동으로 꺼지지 않게 주석 처리

if __name__ == "__main__":
    # 1단계에서 생성된 최신 파일명을 여기에 입력하세요
    latest_file = "Android_개발_최신_트렌드_source.txt" 
    run_notebooklm_upload(latest_file)