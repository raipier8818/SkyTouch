"""
Control panel UI component for the Hand Tracking Trackpad application.
"""
import tkinter as tk
from tkinter import ttk
from typing import Callable

from ..utils.logger import get_logger

logger = get_logger(__name__)


class ControlPanel(ttk.Frame):
    """제어 패널 위젯"""
    
    def __init__(self, parent, on_toggle: Callable = None):
        """
        제어 패널 초기화
        
        Args:
            parent: 부모 위젯
            on_toggle: 토글 버튼 콜백 (시작/정지)
        """
        super().__init__(parent)
        
        self.on_toggle = on_toggle
        self.is_tracking = False
        self.is_loading = False
        
        self.create_widgets()
    
    def create_widgets(self) -> None:
        """위젯 생성"""
        # 토글 버튼 (시작/정지)
        self.toggle_button = ttk.Button(
            self, 
            text="▶ 시작", 
            command=self.toggle_tracking,
            style="Accent.TButton"
        )
        self.toggle_button.grid(row=0, column=0, pady=5, sticky=(tk.W, tk.E))
        
        # 그리드 가중치 설정
        self.columnconfigure(0, weight=1)
    
    def toggle_tracking(self) -> None:
        """트래킹 토글"""
        if self.on_toggle and not self.is_loading:
            self.on_toggle()
    
    def set_tracking_state(self, is_tracking: bool) -> None:
        """
        트래킹 상태에 따라 버튼 상태 변경
        
        Args:
            is_tracking: 트래킹 활성화 여부
        """
        self.is_tracking = is_tracking
        
        if is_tracking:
            self.toggle_button.config(text="⏹ 정지", style="Danger.TButton")
        else:
            self.toggle_button.config(text="▶ 시작", style="Accent.TButton")
    
    def set_loading_state(self, is_loading: bool) -> None:
        """
        로딩 상태에 따라 버튼 상태 변경
        
        Args:
            is_loading: 로딩 중 여부
        """
        self.is_loading = is_loading
        
        if is_loading:
            self.toggle_button.config(text="⏳ 초기화 중...", state="disabled")
        else:
            # 로딩이 끝나면 현재 트래킹 상태에 따라 버튼 상태 복원
            if self.is_tracking:
                self.toggle_button.config(text="⏹ 정지", style="Danger.TButton", state="normal")
            else:
                self.toggle_button.config(text="▶ 시작", style="Accent.TButton", state="normal") 