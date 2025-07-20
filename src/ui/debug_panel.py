import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
from typing import Optional
import logging

class DebugPanel(tk.Toplevel):
    """디버그 로그를 실시간으로 표시하는 팝업 패널"""
    
    def __init__(self, parent, title="디버그 로그"):
        super().__init__(parent)
        self.parent = parent
        self.title(title)
        self.is_running = False
        self.log_queue = []
        self.max_logs = 100  # 최대 로그 개수
        
        self.setup_window()
        self.create_widgets()
        self.setup_logging()
        
        # 자동으로 로깅 시작
        self.start_logging()
        
        # 창이 닫힐 때 부모 창에 알림
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_window(self):
        """창 설정"""
        # 창 크기 및 위치 설정
        self.geometry("400x300")
        self.resizable(True, True)
        self.minsize(300, 200)
        
        # 부모 창 옆에 위치
        self.parent.update_idletasks()
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        
        # 부모 창 오른쪽에 배치
        self.geometry(f"+{parent_x + parent_width + 10}+{parent_y}")
        
        # 항상 위에 표시
        self.attributes('-topmost', True)
    
    def create_widgets(self):
        """위젯 생성"""
        # 메인 프레임
        main_frame = ttk.Frame(self, padding="5")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 제목
        title_label = ttk.Label(main_frame, text="실시간 디버그 로그", 
                               font=("Arial", 12, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 5))
        
        # 컨트롤 버튼들
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # 로그 지우기 버튼
        clear_button = ttk.Button(button_frame, text="로그 지우기", 
                                 command=self.clear_logs)
        clear_button.grid(row=0, column=0, padx=(0, 5))
        
        # 로그 전체 복사 버튼
        copy_button = ttk.Button(button_frame, text="전체 복사", 
                                command=self.copy_all_logs)
        copy_button.grid(row=0, column=1, padx=(0, 5))
        
        # 자동 스크롤 체크박스
        self.auto_scroll_var = tk.BooleanVar(value=True)
        auto_scroll_check = ttk.Checkbutton(button_frame, text="자동 스크롤", 
                                           variable=self.auto_scroll_var)
        auto_scroll_check.grid(row=0, column=2)
        
        # 로그 텍스트 영역
        self.log_text = scrolledtext.ScrolledText(main_frame, height=15, width=50,
                                                 font=("Consolas", 9))
        self.log_text.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 상태 표시
        self.status_label = ttk.Label(main_frame, text="상태: 로깅 중", 
                                     foreground="green")
        self.status_label.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # 그리드 가중치 설정
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
    
    def setup_logging(self):
        """로깅 설정"""
        # 커스텀 핸들러 생성
        self.debug_handler = DebugLogHandler(self)
        self.debug_handler.setLevel(logging.DEBUG)
        
        # 포매터 설정
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', 
                                     datefmt='%H:%M:%S')
        self.debug_handler.setFormatter(formatter)
        
        # 루트 로거에 핸들러 추가
        logging.getLogger().addHandler(self.debug_handler)
    
    def start_logging(self):
        """로깅 시작"""
        if not self.is_running:
            self.is_running = True
            
            # 로그 업데이트 스레드 시작
            self.update_thread = threading.Thread(target=self._update_logs, daemon=True)
            self.update_thread.start()
            
            self.add_log("INFO", "디버그 로깅이 시작되었습니다.")
    
    def stop_logging(self):
        """로깅 정지"""
        if self.is_running:
            self.is_running = False
            self.add_log("INFO", "디버그 로깅이 정지되었습니다.")
    
    def add_log(self, level: str, message: str):
        """로그 추가"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        
        # 로그 큐에 추가
        self.log_queue.append(log_entry)
        
        # 최대 로그 개수 제한
        if len(self.log_queue) > self.max_logs:
            self.log_queue.pop(0)
    
    def _update_logs(self):
        """로그 업데이트 스레드"""
        while self.is_running:
            try:
                # GUI 스레드에서 안전하게 업데이트
                self.after(0, self._update_display)
                time.sleep(0.1)  # 100ms마다 업데이트
            except Exception as e:
                print(f"로그 업데이트 오류: {e}")
                break
    
    def _update_display(self):
        """화면 업데이트"""
        try:
            # 위젯이 유효한지 확인
            if not self.winfo_exists() or not self.log_text.winfo_exists():
                return
            
            # 현재 텍스트 가져오기
            current_text = self.log_text.get("1.0", tk.END).strip()
            
            # 새로운 로그들만 추가
            new_logs = []
            for log in self.log_queue:
                if log not in current_text:
                    new_logs.append(log)
            
            if new_logs:
                # 새 로그 추가
                for log in new_logs:
                    self.log_text.insert(tk.END, log + "\n")
                
                # 자동 스크롤
                if self.auto_scroll_var.get():
                    self.log_text.see(tk.END)
                
                # 최대 라인 수 제한
                lines = self.log_text.get("1.0", tk.END).split('\n')
                if len(lines) > self.max_logs:
                    # 처음부터 삭제
                    self.log_text.delete("1.0", f"{len(lines) - self.max_logs}.0")
        
        except Exception as e:
            print(f"화면 업데이트 오류: {e}")
    
    def clear_logs(self):
        """로그 지우기"""
        self.log_text.delete("1.0", tk.END)
        self.log_queue.clear()
        self.add_log("INFO", "로그가 지워졌습니다.")
    
    def copy_all_logs(self):
        """로그 전체 복사"""
        try:
            # 텍스트 위젯의 모든 내용 가져오기
            all_logs = self.log_text.get("1.0", tk.END).strip()
            
            if all_logs:
                # 클립보드에 복사
                self.clipboard_clear()
                self.clipboard_append(all_logs)
                
                # 복사 완료 메시지
                self.add_log("INFO", "로그 전체가 클립보드에 복사되었습니다.")
                
                # 상태 표시 업데이트
                self.status_label.config(text="상태: 로그 복사 완료", foreground="blue")
                
                # 2초 후 상태 복원
                self.after(2000, lambda: self.status_label.config(text="상태: 로깅 중", foreground="green"))
            else:
                self.add_log("WARNING", "복사할 로그가 없습니다.")
                
        except Exception as e:
            self.add_log("ERROR", f"로그 복사 중 오류: {e}")
    
    def on_closing(self):
        """창 닫기"""
        try:
            # 로깅 중단
            self.stop_logging()
            
            # 로그 핸들러 제거
            if hasattr(self, 'debug_handler'):
                logging.getLogger().removeHandler(self.debug_handler)
            
            # 창 파괴
            self.destroy()
        except Exception as e:
            print(f"디버그 창 닫기 오류: {e}")
            self.destroy()
    
    def show(self):
        """창 표시"""
        self.deiconify()
        self.lift()
        self.focus_force()
    
    def hide(self):
        """창 숨기기"""
        self.withdraw()


class DebugLogHandler(logging.Handler):
    """디버그 패널용 로그 핸들러"""
    
    def __init__(self, debug_panel):
        super().__init__()
        self.debug_panel = debug_panel
    
    def emit(self, record):
        """로그 레코드 처리"""
        try:
            msg = self.format(record)
            self.debug_panel.add_log(record.levelname, record.getMessage())
        except Exception:
            self.handleError(record) 