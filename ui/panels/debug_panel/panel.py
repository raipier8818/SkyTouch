"""
Debug panel for Hand Tracking Trackpad application.
"""
import tkinter as tk
from tkinter import ttk
import time

from utils.logging.logger import get_logger

logger = get_logger(__name__)


class DebugPanel(tk.Toplevel):
    """디버그 패널 창"""
    
    def __init__(self, parent):
        """
        디버그 패널 초기화
        
        Args:
            parent: 부모 윈도우
        """
        super().__init__(parent)
        
        self.parent = parent
        self.is_visible = False
        
        self.setup_window()
        self.create_widgets()
        
        # 윈도우 종료 이벤트 바인딩
        self.protocol("WM_DELETE_WINDOW", self.close)
    
    def setup_window(self) -> None:
        """윈도우 설정"""
        self.title("디버그 패널")
        self.geometry("400x300")
        self.resizable(True, True)
        
        # 모달 창으로 설정 (디버그 패널은 모달이 아니므로 제거)
        # self.transient(self.parent)
        # self.grab_set()
        
        # 화면 중앙에 배치
        self.center_window()
    
    def center_window(self) -> None:
        """윈도우를 화면 중앙에 배치"""
        self.update_idletasks()
        
        # 화면 크기 가져오기
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # 윈도우 크기
        window_width = 400
        window_height = 300
        
        # 중앙 위치 계산
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        
        # 윈도우 위치 설정
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    def create_widgets(self) -> None:
        """위젯 생성"""
        # 메인 프레임
        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 제목
        title_label = ttk.Label(main_frame, text="디버그 정보", style="Title.TLabel")
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        # 디버그 정보 표시 영역
        self.debug_text = tk.Text(main_frame, height=15, width=50, wrap=tk.WORD,
                                 font=("Consolas", 10), bg="white", fg="black")
        self.debug_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 스크롤바
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.debug_text.yview)
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.debug_text.configure(yscrollcommand=scrollbar.set)
        
        # 버튼 프레임
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(10, 0))
        
        # 새로고침 버튼
        refresh_button = ttk.Button(button_frame, text="새로고침", command=self.refresh_debug_info)
        refresh_button.grid(row=0, column=0, padx=5)
        
        # 지우기 버튼
        clear_button = ttk.Button(button_frame, text="지우기", command=self.clear_debug_info)
        clear_button.grid(row=0, column=1, padx=5)
        
        # 닫기 버튼
        close_button = ttk.Button(button_frame, text="닫기", command=self.close)
        close_button.grid(row=0, column=2, padx=5)
        
        # 그리드 가중치 설정
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
    
    def show(self) -> None:
        """디버그 패널 표시"""
        if not self.is_visible:
            self.deiconify()
            self.is_visible = True
            self.refresh_debug_info()
            logger.info("디버그 패널이 표시되었습니다.")
    
    def hide(self) -> None:
        """디버그 패널 숨기기"""
        if self.is_visible:
            self.withdraw()
            self.is_visible = False
            logger.info("디버그 패널이 숨겨졌습니다.")
    
    def close(self) -> None:
        """디버그 패널 완전히 닫기"""
        self.destroy()
        logger.info("디버그 패널이 닫혔습니다.")
    
    def refresh_debug_info(self) -> None:
        """디버그 정보 새로고침"""
        try:
            # 기존 내용 지우기
            self.debug_text.delete(1.0, tk.END)
            
            # 현재 시간
            current_time = time.strftime("%Y-%m-%d %H:%M:%S")
            self.debug_text.insert(tk.END, f"=== 디버그 정보 ({current_time}) ===\n\n")
            
            # 시스템 정보
            self.debug_text.insert(tk.END, "시스템 정보:\n")
            self.debug_text.insert(tk.END, f"  - Python 버전: {self.get_python_version()}\n")
            self.debug_text.insert(tk.END, f"  - OpenCV 버전: {self.get_opencv_version()}\n")
            self.debug_text.insert(tk.END, f"  - MediaPipe 버전: {self.get_mediapipe_version()}\n")
            self.debug_text.insert(tk.END, f"  - PyAutoGUI 버전: {self.get_pyautogui_version()}\n\n")
            
            # 카메라 정보
            self.debug_text.insert(tk.END, "카메라 정보:\n")
            self.debug_text.insert(tk.END, "  - 상태: 확인 중...\n")
            self.debug_text.insert(tk.END, "  - 해상도: 확인 중...\n\n")
            
            # 메모리 사용량
            self.debug_text.insert(tk.END, "메모리 사용량:\n")
            self.debug_text.insert(tk.END, f"  - 사용 가능한 메모리: {self.get_memory_info()}\n\n")
            
            # 로그 정보
            self.debug_text.insert(tk.END, "로그 정보:\n")
            self.debug_text.insert(tk.END, "  - 최근 로그: 확인 중...\n")
            
            # 스크롤을 맨 위로
            self.debug_text.see(1.0)
            
        except Exception as e:
            logger.error(f"디버그 정보 새로고침 실패: {e}")
            self.debug_text.insert(tk.END, f"오류: {e}\n")
    
    def clear_debug_info(self) -> None:
        """디버그 정보 지우기"""
        self.debug_text.delete(1.0, tk.END)
    
    def add_debug_message(self, message: str) -> None:
        """
        디버그 메시지 추가
        
        Args:
            message: 디버그 메시지
        """
        if self.is_visible:
            current_time = time.strftime("%H:%M:%S")
            self.debug_text.insert(tk.END, f"[{current_time}] {message}\n")
            self.debug_text.see(tk.END)
    
    def get_python_version(self) -> str:
        """Python 버전 반환"""
        import sys
        return sys.version.split()[0]
    
    def get_opencv_version(self) -> str:
        """OpenCV 버전 반환"""
        try:
            import cv2
            return cv2.__version__
        except:
            return "설치되지 않음"
    
    def get_mediapipe_version(self) -> str:
        """MediaPipe 버전 반환"""
        try:
            import mediapipe as mp
            return mp.__version__
        except:
            return "설치되지 않음"
    
    def get_pyautogui_version(self) -> str:
        """PyAutoGUI 버전 반환"""
        try:
            import pyautogui
            return pyautogui.__version__
        except:
            return "설치되지 않음"
    
    def get_memory_info(self) -> str:
        """메모리 정보 반환"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            return f"{memory.available // (1024**3)} GB"
        except:
            return "확인 불가" 