import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from rich.console import Console
from config import NOTEBOOK_URL, ADMIN_URL, PROFILE_PATH, ADMIN_ID, ADMIN_PW, CUSTOM_AUDIO_PROMPT

console = Console()

_driver = None

def get_driver(download_path=None):
    """전역(Global) 드라이버를 유지하며, 다운로드 경로만 동적으로 변경합니다."""
    global _driver
    if _driver is None:
        chrome_options = Options()
        chrome_options.add_argument(f"--user-data-dir={PROFILE_PATH}")
        if download_path:
            prefs = {"download.default_directory": os.path.abspath(download_path), "download.prompt_for_download": False}
            chrome_options.add_experimental_option("prefs", prefs)
        _driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    else:
        if download_path:
            # 열려있는 브라우저를 끄지 않고 다운로드 폴더 위치만 변경
            _driver.execute_cdp_cmd("Page.setDownloadBehavior", {
                "behavior": "allow",
                "downloadPath": os.path.abspath(download_path)
            })
    return _driver

def quit_driver():
    """모든 파이프라인이 끝난 후 브라우저를 안전하게 종료합니다."""
    global _driver
    if _driver:
        _driver.quit()
        _driver = None

def create_podcast_and_download(txt_path, project_dir):
    """NotebookLM에 소스를 업로드하고 생성 대기 후 오디오를 다운로드합니다."""
    driver = get_driver(download_path=project_dir)
    wait = WebDriverWait(driver, 60)
    try:
        driver.get(NOTEBOOK_URL)
        time.sleep(5)
        
        # 로그인 상태 확인 및 로그인 시도
        try:
            login_xpath = "//*[(contains(text(), 'Sign in') or contains(text(), '로그인') or contains(text(), 'Sign In') or contains(text(), 'Try NotebookLM')) and not(contains(text(), '로그아웃') or contains(text(), 'Sign out'))]"
            login_btns = driver.find_elements(By.XPATH, login_xpath)
            for btn in login_btns:
                if btn.is_displayed():
                    console.print("[yellow]🔒 로그인이 필요합니다. '로그인' 버튼을 클릭하여 시도합니다...[/yellow]")
                    driver.execute_script("arguments[0].click();", btn)
                    time.sleep(7) # 로그인 처리 및 리다이렉트 대기
                    break
        except: pass
        
        console.print("[yellow]🔍 '새 노트' 버튼 찾는 중...[/yellow]")
        try:
            # 에러 원인: '+'나 '만들기' 같은 너무 포괄적인 단어 제거 (숨겨진 엉뚱한 요소 클릭 방지)
            new_btn_xpath = "//*[contains(text(), 'New Notebook') or contains(text(), '새 노트') or contains(text(), '만들기') or contains(text(), 'New')]"
            # 화면에 보이는 진짜 버튼을 역순으로 찾아서 클릭
            new_btns = wait.until(EC.presence_of_all_elements_located((By.XPATH, new_btn_xpath)))
            for btn in reversed(new_btns):
                if btn.is_displayed():
                    driver.execute_script("arguments[0].click();", btn)
                    console.print("[green]✅ '새 노트' 만들기 진입 성공[/green]")
                    break
            time.sleep(4)
        except Exception:
            console.print("[red]⚠️ '새 노트' 버튼을 찾지 못했습니다. 이미 노트북 내부이거나 UI가 변경되었을 수 있습니다.[/red]")

        console.print("[cyan]📝 텍스트 복사/붙여넣기로 소스를 입력합니다.[/cyan]")
        with open(txt_path, "r", encoding="utf-8") as f: content = f.read()
        
        try:
            paste_btn_xpath = "//*[contains(text(), '복사된 텍스트') or contains(text(), 'Copied text')]"
            paste_btns = wait.until(EC.presence_of_all_elements_located((By.XPATH, paste_btn_xpath)))
            for btn in reversed(paste_btns):
                if btn.is_displayed():
                    driver.execute_script("arguments[0].click();", btn)
                    break
            time.sleep(3)
        except: pass
        
        try:
            modal_ta = wait.until(EC.visibility_of_element_located((By.XPATH, "//textarea[contains(@placeholder, '여기에 텍스트를') or contains(@placeholder, 'Paste')]")))
            driver.execute_script("arguments[0].value = arguments[1];", modal_ta, content)
            modal_ta.send_keys(" ")
        except:
            textareas = driver.find_elements(By.TAG_NAME, "textarea")
            for ta in reversed(textareas):
                if ta.is_displayed():
                    ta.send_keys(content)
                    break
        time.sleep(2)
        
        insert_btns = driver.find_elements(By.XPATH, "//*[contains(text(), '삽입') or contains(text(), 'Insert')]")
        for btn in reversed(insert_btns):
            if btn.is_displayed() and btn.is_enabled():
                driver.execute_script("arguments[0].click();", btn)
                break
        
        time.sleep(15) # 소스 분석 대기
        
        console.print("[yellow]🎧 스튜디오 패널에서 팟캐스트 생성을 요청합니다...[/yellow]")
        audio_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'AI 오디오 오버뷰')]")))
        driver.execute_script("arguments[0].click();", audio_btn)
        time.sleep(4)
        
        custom_prompt = CUSTOM_AUDIO_PROMPT
        textareas = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "textarea")))
        for ta in reversed(textareas):
            if ta.is_displayed():
                driver.execute_script("arguments[0].value = arguments[1];", ta, custom_prompt)
                ta.send_keys(" ")
                break
        time.sleep(2)
        
        gen_btns = driver.find_elements(By.XPATH, "//*[contains(text(), '생성') or contains(text(), 'Generate')]")
        for btn in reversed(gen_btns):
            if btn.is_displayed() and btn.is_enabled():
                driver.execute_script("arguments[0].click();", btn)
                break
                
        console.print("[bold green]✅ 팟캐스트 생성이 시작되었습니다![/bold green]")
        
        console.print("[yellow]⏳ 재생 버튼이 뜰 때까지 대기합니다... (최대 30분)[/yellow]")
        start = time.time()
        kebab_btn = None
        while time.time() - start < 1800:
            try:
                play_btns = driver.find_elements(By.XPATH, "//mat-icon[text()='play_arrow'] | //button[contains(@aria-label, '재생')]")
                if play_btns and play_btns[-1].is_displayed():
                    console.print("[green]✅ 생성 완료 감지![/green]")
                    btns = driver.find_elements(By.XPATH, "//*[text()='more_vert' or contains(@aria-label, '옵션')]")
                    for btn in reversed(btns):
                        if btn.is_displayed() and btn.is_enabled(): 
                            kebab_btn = btn
                            break
                    if kebab_btn:
                        driver.execute_script("arguments[0].click();", kebab_btn)
                        time.sleep(2)
                        break
            except: pass
            time.sleep(10)
            
        if not kebab_btn: 
            console.print("[red]❌ 생성 실패 또는 다운로드 버튼을 찾지 못했습니다.[/red]")
            return None

        down = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), '다운로드') or contains(text(), 'Download')]")))
        driver.execute_script("arguments[0].click();", down)
        
        timeout = 600
        dl_start = time.time()
        while time.time() - dl_start < timeout:
            files = [f for f in os.listdir(project_dir) if f.endswith(('.wav', '.mp3', '.m4a'))]
            if files and not any(f.endswith('.crdownload') for f in os.listdir(project_dir)):
                audio_path = os.path.join(project_dir, files[0])
                return audio_path
            time.sleep(5)
    except Exception as e:
        console.print(f"[red]❌ 에러 발생: {e}[/red]")
        raise

def upload_to_admin(audio_file):
    """관리자 페이지에 완성된 오디오를 업로드합니다."""
    driver = get_driver()
    wait = WebDriverWait(driver, 60)
    try:
        driver.get(ADMIN_URL)
        time.sleep(3)
        
        # 어드민 페이지 로그인 상태 확인 및 로그인 시도
        try:
            id_xpath = "//input[(@type='text' or @type='email' or contains(translate(@name, 'USER', 'user'), 'user') or contains(translate(@name, 'EMAIL', 'email'), 'email')) and not(contains(@name, 'search'))]"
            pw_xpath = "//input[@type='password']"
            
            id_inputs = driver.find_elements(By.XPATH, id_xpath)
            pw_inputs = driver.find_elements(By.XPATH, pw_xpath)
            id_field = next((inp for inp in id_inputs if inp.is_displayed()), None)
            pw_field = next((inp for inp in pw_inputs if inp.is_displayed()), None)
            
            # 1. 폼은 보이지 않는데 '로그인' 버튼만 보인다면 우선 클릭 (SSO 방식이거나 폼 이동 버튼)
            if not (id_field and pw_field):
                login_btns = driver.find_elements(By.XPATH, "//*[(contains(text(), '로그인') or contains(text(), 'Login') or contains(text(), 'Sign in')) and not(contains(text(), '로그아웃') or contains(text(), 'Logout'))]")
                for btn in login_btns:
                    if btn.is_displayed():
                        console.print("[yellow]🔒 로그인이 풀려있습니다. '로그인' 버튼을 우선 클릭합니다.[/yellow]")
                        driver.execute_script("arguments[0].click();", btn)
                        time.sleep(5) # 폼이 열리거나 페이지 이동 대기
                        
                        # 버튼 클릭 후 폼이 새로 나타났을 수 있으니 다시 탐색
                        id_inputs = driver.find_elements(By.XPATH, id_xpath)
                        pw_inputs = driver.find_elements(By.XPATH, pw_xpath)
                        id_field = next((inp for inp in id_inputs if inp.is_displayed()), None)
                        pw_field = next((inp for inp in pw_inputs if inp.is_displayed()), None)
                        break
            
            # 2. 폼이 화면에 존재한다면 환경 변수 값으로 자동 입력 진행
            if id_field and pw_field:
                # 중요: 크롬 자동완성은 사용자가 화면을 한 번 클릭해야만 실제 HTML에 값을 주입합니다!
                try:
                    driver.execute_script("arguments[0].focus();", id_field)
                    id_field.click()
                    time.sleep(1) # 자동완성 값이 주입될 시간 부여
                except: pass

                # 자바스크립트로 현재 폼에 채워진 실제 값을 가져옵니다 (크롬 자동완성 완벽 인식)
                id_val = driver.execute_script("return arguments[0].value;", id_field) or id_field.get_attribute('value')
                pw_val = driver.execute_script("return arguments[0].value;", pw_field) or pw_field.get_attribute('value')
                
                if id_val and pw_val:
                    console.print("[green]🔑 크롬 자동완성 값이 감지되었습니다. 바로 로그인 버튼을 클릭합니다.[/green]")
                else:
                    console.print("[yellow]🔑 어드민 로그인 폼 일부가 비어있습니다. 직접 입력을 시도합니다.[/yellow]")
                    if not id_val and ADMIN_ID:
                        id_field.click()
                        id_field.send_keys(Keys.COMMAND, 'a') # Mac 전체 선택
                        id_field.send_keys(Keys.CONTROL, 'a') # Win 전체 선택
                        id_field.send_keys(Keys.BACKSPACE)    # 완전 삭제 (버그 방지)
                        id_field.send_keys(ADMIN_ID)
                        time.sleep(0.5)
                    if not pw_val and ADMIN_PW:
                        pw_field.click()
                        pw_field.send_keys(Keys.COMMAND, 'a')
                        pw_field.send_keys(Keys.CONTROL, 'a')
                        pw_field.send_keys(Keys.BACKSPACE)
                        pw_field.send_keys(ADMIN_PW)
                        time.sleep(0.5)
                        
                # 가장 확실한 방법 1순위: 비밀번호 칸에서 바로 엔터(Enter) 키 입력
                console.print("[cyan]⌨️ 로그인 폼 제출 시도 (1/2): 엔터 키 입력[/cyan]")
                try:
                    pw_field.send_keys(Keys.RETURN)
                    time.sleep(2)
                except: pass
                    
                # 방법 2순위: 엔터로 안 넘어갈 경우를 대비해 로그인 버튼들을 찾아 JS 강제 클릭
                submit_xpath = "//*[(contains(translate(text(), 'LOGIN', 'login'), 'login') or contains(text(), '로그인') or contains(translate(text(), 'SIGN IN', 'sign in'), 'sign in') or contains(translate(@value, 'LOGIN', 'login'), 'login')) and not(contains(text(), '로그아웃') or contains(text(), 'Logout'))]"
                submit_btns = driver.find_elements(By.XPATH, submit_xpath)
                
                for btn in submit_btns:
                    if btn.is_displayed() and btn.is_enabled():
                        try:
                            console.print("[yellow]🖱️ 로그인 폼 제출 시도 (2/2): 버튼 JS 클릭[/yellow]")
                            driver.execute_script("arguments[0].click();", btn)
                            break
                        except: pass
                time.sleep(5)
        except: pass
        
        console.print("[cyan]⏳ 'AI 콘텐츠 생성' 메뉴 접근 대기 중...[/cyan]")
        
        time.sleep(2) # 로그인 직후 화면 전환/애니메이션 대기
        menus = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//*[contains(text(), 'AI 콘텐츠 생성')]")))
        
        menu_clicked = False
        # 요소들 중 화면에 보이고 가장 안쪽(보통 리스트의 마지막)에 있는 진짜 버튼/링크를 찾습니다.
        for menu in reversed(menus):
            if menu.is_displayed():
                try:
                    # 메뉴가 화면 밖에 있을 수 있으므로 스크롤해서 중앙에 맞춥니다.
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", menu)
                    time.sleep(0.5)
                    
                    try: menu.click() # 1. 일반 클릭
                    except: driver.execute_script("arguments[0].click();", menu) # 2. JS 클릭
                    
                    console.print("[green]✅ 'AI 콘텐츠 생성' 메뉴 클릭 성공[/green]")
                    menu_clicked = True
                    break
                except: pass
                
        if not menu_clicked:
            console.print("[red]❌ 'AI 콘텐츠 생성' 메뉴를 클릭하지 못했습니다. 구조를 확인해 주세요.[/red]")
            
        time.sleep(3)
        console.print("[cyan]📤 오디오 파일을 업로드합니다...[/cyan]")
        driver.find_element(By.CSS_SELECTOR, "input[type='file']").send_keys(audio_file)
        time.sleep(5)
        
        try:
            alert = driver.switch_to.alert
            alert.accept()
        except: pass
        
        try:
            console.print("[yellow]🔍 'AI 처리 시작' 버튼을 찾아 클릭합니다...[/yellow]")
            # text() 대신 . (마침표)와 normalize-space()를 사용하여 공백/태그 꼬임 완벽 방지
            btns = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//*[contains(normalize-space(.), 'AI 처리 시작') or contains(., '처리 시작')]")))
            
            btn_clicked = False
            for btn in reversed(btns):
                if btn.is_displayed():
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                    time.sleep(1)
                    try: btn.click()
                    except: driver.execute_script("arguments[0].click();", btn)
                    btn_clicked = True
                    break
                    
            if not btn_clicked: raise Exception("버튼 요소를 찾았으나 클릭할 수 없습니다.")
                
            console.print("[green]✅ 'AI 처리 시작' 버튼 클릭 완료! 처리가 끝날 때까지 대기합니다 (최대 10분)...[/green]")
            
            wait_start = time.time()
            process_complete = False
            screen_transitioned = False
            while time.time() - wait_start < 600:
                try:
                    alert = driver.switch_to.alert
                    alert_msg = alert.text
                    alert.accept()
                    console.print(f"[green]✅ 처리 완료 메시지: {alert_msg}[/green]")
                    process_complete = True
                    break
                except: pass
                
                if not screen_transitioned:
                    try:
                        if not btn.is_displayed():
                            console.print("[cyan]🔄 화면이 전환되었습니다. 서버 처리가 끝날 때까지 계속 대기합니다...[/cyan]")
                            screen_transitioned = True
                    except:
                        console.print("[cyan]🔄 화면이 전환되었습니다. 서버 처리가 끝날 때까지 계속 대기합니다...[/cyan]")
                        screen_transitioned = True
                        
                if screen_transitioned:
                    try:
                        page_text = driver.find_element(By.TAG_NAME, "body").text
                        if "처리가 완료" in page_text or "생성 완료" in page_text or "성공적으로" in page_text or "완료되었습니다" in page_text:
                            console.print("[green]✅ 화면에서 처리 완료 상태를 감지했습니다![/green]")
                            process_complete = True
                            break
                    except: pass
                        
                time.sleep(5)
                
            if not process_complete:
                console.print("[yellow]⚠️ 10분이 지났거나 명시적인 완료 알림을 찾지 못했습니다.[/yellow]")
        except Exception as e:
            console.print(f"[red]❌ 'AI 처리 시작' 버튼을 누르지 못했습니다: {e}[/red]")
    except Exception as e:
        console.print(f"[red]❌ 에러 발생: {e}[/red]")
        raise