import os
import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

# 커스텀 모듈 임포트
import ai_service
import automation
import utils

console = Console()

def start_knowledge_discovery():
    """Step 1: 트렌드 분석 및 리서치 소스 생성"""
    console.print(Panel("[bold cyan]Step 1: AI 지식 탐색 및 리서치 대본 생성[/bold cyan]"))
    
    # 1. 주제 선정
    suggested_topic = ai_service.generate_topic()
    console.print(f"🎯 AI 추천 토픽: [bold white]{suggested_topic}[/bold white]")
    
    user_in = Prompt.ask("[cyan]주제를 변경하시겠습니까? (입력 시 변경, 미입력 시 유지)[/cyan]")
    final_topic = user_in.strip() if user_in.strip() else suggested_topic

    # 2. 프로젝트 폴더 생성 (utils 사용)
    project_dir = utils.create_project_dir(final_topic)
    
    # 3. 상세 콘텐츠 생성
    content = ai_service.generate_source_text(final_topic)
    
    # 4. 파일 저장
    txt_path = os.path.join(project_dir, "source_research.txt")
    with open(txt_path, "w", encoding="utf-8") as f: 
        f.write(content)
        
    console.print(f"✅ 리서치 완료! 파일 저장: [bold green]{txt_path}[/bold green]")
    return txt_path

def start_podcast_generation(txt_path):
    """Step 2: NotebookLM 업로드 및 팟캐스트 생성 요청"""
    console.print(Panel("[bold magenta]Step 2: NotebookLM 오디오 생성 엔진 가동[/bold magenta]"))
    
    # NotebookLM에 접속하여 오디오 생성 버튼 클릭까지 수행
    automation.request_podcast_creation(txt_path)
    
    # 다음 단계(다운로드)를 위해 폴더 경로 반환
    return os.path.dirname(txt_path)

def start_podcast_download(project_dir):
    """Step 3: 생성 완료 확인 및 로컬 다운로드"""
    console.print(Panel("[bold blue]Step 3: 오디오 파일 상태 모니터링 및 다운로드[/bold blue]"))
    
    audio_path = automation.wait_and_download_podcast(project_dir)
    if audio_path:
        console.print(f"🎉 오디오 확보 성공: [bold green]{audio_path}[/bold green]")
        return audio_path
    else:
        console.print("[red]❌ 오디오 다운로드에 실패했습니다.[/red]")
        return None

def start_admin_deployment(audio_path):
    """Step 4: 오디오 압축 및 관리자 대시보드 배포"""
    console.print(Panel("[bold yellow]Step 4: 최종 배포 파이프라인 (압축 및 업로드)[/bold yellow]"))
    
    # 1. FFmpeg를 통한 용량 다이어트
    compressed_file = utils.compress_audio(audio_path)
    
    # 2. 사내 어드민 페이지 업로드
    automation.deploy_to_admin_dashboard(compressed_file)
    
    console.print(Panel("[bold green]🌟 hEARit-Agent: 모든 미션이 성공적으로 완료되었습니다![/bold green]", expand=False))

if __name__ == "__main__":
    try:
        console.print(Panel.fit("[bold cyan]🤖 hEARit-Agent v2.0[/bold cyan]\n[white]Autonomous IT Podcast Creator[/white]"))
        console.print("[1] 🚀 전체 파이프라인 실행\n[2] 📝 Step 1: 리서치만 수행\n[3] 🎧 Step 2~3: 팟캐스트 생성/다운로드\n[4] 📤 Step 4: 어드민 페이지 배포")
        
        choice = Prompt.ask("\n[bold yellow]원하는 작업 번호를 입력하세요[/bold yellow]", choices=["1", "2", "3", "4"], default="1")

        if choice == "1":
            # 1 -> 2 -> 3 -> 4 순차 실행
            research_txt = start_knowledge_discovery()
            if research_txt:
                proj_dir = start_podcast_generation(research_txt)
                podcast_audio = start_podcast_download(proj_dir)
                if podcast_audio:
                    start_admin_deployment(podcast_audio)

        elif choice == "2":
            start_knowledge_discovery()

        elif choice == "3":
            # 가장 최근의 연구 텍스트를 찾아 이어서 실행
            latest_src = utils.get_latest_source_file()
            if latest_src:
                proj_dir = start_podcast_generation(latest_src)
                start_podcast_download(proj_dir)
            else:
                console.print("[red]최근 리서치 파일을 찾을 수 없습니다. 1단계를 먼저 실행하세요.[/red]")

        elif choice == "4":
            # 가장 최근의 오디오 파일을 찾아 배포
            latest_aud = utils.get_latest_audio_file()
            if latest_aud:
                start_admin_deployment(latest_aud)
            else:
                console.print("[red]배포할 오디오 파일을 찾을 수 없습니다.[/red]")

    except KeyboardInterrupt:
        console.print("\n[bold red]⚠️ 사용자에 의해 프로그램이 중단되었습니다.[/bold red]")
    except Exception as e:
        console.print(f"\n[bold red]❌ 시스템 에러 발생: {e}[/bold red]")
    finally:
        automation.quit_driver()
        console.print("[dim]시스템 리소스를 정리하고 종료합니다.[/dim]")