import os
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

import ai_service
import automation
import utils

console = Console()

def run_step1():
    console.print(Panel("[bold cyan]Step 1: 트렌드 분석 및 소스 생성[/bold cyan]"))
    topic = ai_service.generate_topic()
    console.print(f"🎯 AI 추천: [bold white]{topic}[/bold white]")
    
    user_in = Prompt.ask("[cyan]주제 변경 시 입력, 그대로는 [Enter][/cyan]")
    if user_in.strip(): 
        topic = user_in.strip()

    project_dir = utils.create_project_dir(topic)
    content = ai_service.generate_source_text(topic)
    
    txt_path = os.path.join(project_dir, "source.txt")
    with open(txt_path, "w", encoding="utf-8") as f: 
        f.write(content)
    console.print(f"✅ 텍스트 소스 생성 완료: {txt_path}")
    return txt_path

def run_step2_3(txt_path):
    console.print(Panel("[bold magenta]Step 2~3: NotebookLM 팟캐스트 생성 및 다운로드[/bold magenta]"))
    project_dir = os.path.dirname(txt_path)
    audio_path = automation.create_podcast_and_download(txt_path, project_dir)
    if audio_path:
        console.print(f"🎉 다운로드 성공: {audio_path}")
    return audio_path

def run_step4(audio_path):
    console.print(Panel("[bold yellow]Step 4: 관리자 페이지 업로드[/bold yellow]"))
    final_file = utils.compress_audio(audio_path)
    automation.upload_to_admin(final_file)
    console.print("[bold green]🌟 모든 파이프라인이 성공적으로 종료되었습니다![/bold green]")

if __name__ == "__main__":
    console.print(Panel.fit("[bold cyan]🤖 hEARit-Agent v2.0[/bold cyan]"))
    console.print("[1] 전체 실행 [2] 1단계(텍스트) [3] 2~3단계(생성/다운로드) [4] 4단계(어드민 업로드)")
    c = Prompt.ask("선택", choices=["1", "2", "3", "4"], default="1")

    if c == "1":
        p1 = run_step1()
        if p1:
            p2_3 = run_step2_3(p1)
            if p2_3: run_step4(p2_3)
    elif c == "2": 
        run_step1()
    elif c == "3":
        src = utils.get_latest_source_file()
        if src: run_step2_3(src)
        else: console.print("[red]소스 파일을 찾을 수 없습니다.[/red]")
    elif c == "4":
        aud = utils.get_latest_audio_file()
        if aud: run_step4(aud)
        else: console.print("[red]오디오 파일을 찾을 수 없습니다.[/red]")
        
    # 모든 작업이 완료된 후 최종적으로 브라우저 종료
    automation.quit_driver()