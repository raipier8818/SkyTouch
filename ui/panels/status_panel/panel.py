"""
Status panel for Hand Tracking Trackpad application.
"""
import tkinter as tk
from tkinter import ttk

from utils.logging.logger import get_logger

logger = get_logger(__name__)


class StatusPanel(ttk.Frame):
    """상태 패널 위젯"""
    
    def __init__(self, parent):
        """
        상태 패널 초기화
        
        Args:
            parent: 부모 위젯
        """
        super().__init__(parent)
        
        self.create_widgets()
    
    def create_widgets(self) -> None:
        """위젯 생성"""
        # 상태 라벨
        self.status_label = ttk.Label(
            self, 
            text="상태: 대기 중", 
            style="Status.TLabel"
        )
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        # 상태 표시기
        self.status_indicator = ttk.Label(
            self, 
            text="●", 
            foreground="gray",
            font=("Arial", 12)
        )
        self.status_indicator.grid(row=0, column=1, padx=(10, 0))
        
        # 그리드 가중치 설정
        self.columnconfigure(0, weight=1)
    
    def update_status(self, status: str) -> None:
        """
        상태 업데이트
        
        Args:
            status: 새로운 상태 메시지
        """
        self.status_label.config(text=f"상태: {status}")
        
        # 상태에 따른 표시기 색상 변경
        if "트래킹" in status:
            self.status_indicator.config(foreground="green")
        elif "오류" in status:
            self.status_indicator.config(foreground="red")
        else:
            self.status_indicator.config(foreground="gray")
        
        logger.debug(f"상태가 '{status}'로 업데이트되었습니다.")
    
    def set_error_status(self, error_message: str) -> None:
        """
        오류 상태 설정
        
        Args:
            error_message: 오류 메시지
        """
        self.update_status(f"오류: {error_message}")
    
    def set_success_status(self, message: str) -> None:
        """
        성공 상태 설정
        
        Args:
            message: 성공 메시지
        """
        self.update_status(message) 