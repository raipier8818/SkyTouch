"""
Settings window for the Hand Tracking Trackpad application.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any

from ..config import config
from ..utils.logger import get_logger

logger = get_logger(__name__)


class SettingsWindow:
    """설정 창"""
    
    def __init__(self, parent, on_settings_changed=None):
        """
        설정 창 초기화
        
        Args:
            parent: 부모 윈도우
            on_settings_changed: 설정 변경 콜백 함수
        """
        self.parent = parent
        self.on_settings_changed = on_settings_changed
        self.settings_window = None
        self.create_window()
    
    def create_window(self) -> None:
        """설정 창 생성"""
        self.settings_window = tk.Toplevel(self.parent)
        self.settings_window.title("설정")
        self.settings_window.geometry("500x500")
        self.settings_window.resizable(True, True)
        
        # 모달 창으로 설정
        self.settings_window.transient(self.parent)
        self.settings_window.grab_set()
        
        # 창을 화면 중앙에 배치
        self.center_window()
        
        # 최소 크기 설정
        self.settings_window.minsize(400, 400)
        
        self.create_widgets()
        
        # 창 종료 이벤트 바인딩
        self.settings_window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        logger.info("설정 창이 생성되었습니다.")
    
    def center_window(self) -> None:
        """창을 화면 중앙에 배치"""
        self.settings_window.update_idletasks()
        width = self.settings_window.winfo_width()
        height = self.settings_window.winfo_height()
        x = (self.settings_window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.settings_window.winfo_screenheight() // 2) - (height // 2)
        self.settings_window.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_widgets(self) -> None:
        """위젯 생성"""
        # 메인 컨테이너
        main_frame = ttk.Frame(self.settings_window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 스크롤 가능한 캔버스 생성
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 제목
        title_label = ttk.Label(scrollable_frame, text="Hand Tracking Trackpad 설정", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # 제스처 설정 섹션
        self.create_gesture_settings(scrollable_frame)
        
        # 카메라 설정 섹션
        self.create_camera_settings(scrollable_frame)
        
        # 손 트래킹 설정 섹션
        self.create_tracking_settings(scrollable_frame)
        
        # 디버그 설정 섹션
        self.create_debug_settings(scrollable_frame)
        
        # 버튼 프레임
        self.create_buttons(scrollable_frame)
        
        # 캔버스와 스크롤바 배치
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 그리드 가중치 설정
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        self.settings_window.columnconfigure(0, weight=1)
        self.settings_window.rowconfigure(0, weight=1)
        
        # 마우스 휠 스크롤 바인딩
        def _on_mousewheel(event):
            try:
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except tk.TclError:
                # 캔버스가 이미 파괴된 경우 무시
                pass
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # 스크롤바가 필요할 때만 표시
        def _configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        scrollable_frame.bind("<Configure>", _configure_scroll_region)
    
    def create_gesture_settings(self, parent) -> None:
        """제스처 설정 섹션 생성"""
        gesture_frame = ttk.LabelFrame(parent, text="제스처 설정", padding="15")
        gesture_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # 감도 설정
        ttk.Label(gesture_frame, text="감도:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.sensitivity_var = tk.DoubleVar(value=config.gesture.sensitivity)
        self.sensitivity_scale = ttk.Scale(
            gesture_frame, 
            from_=0.1, 
            to=3.0, 
            variable=self.sensitivity_var, 
            orient=tk.HORIZONTAL,
            command=self.on_sensitivity_change
        )
        self.sensitivity_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(0, 5))
        
        self.sensitivity_label = ttk.Label(gesture_frame, text=f"{config.gesture.sensitivity:.1f}")
        self.sensitivity_label.grid(row=0, column=2, padx=(5, 0), pady=(0, 5))
        
        # 스무딩 설정
        ttk.Label(gesture_frame, text="스무딩:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        
        self.smoothing_var = tk.DoubleVar(value=config.gesture.smoothing_factor)
        self.smoothing_scale = ttk.Scale(
            gesture_frame, 
            from_=0.0, 
            to=1.0, 
            variable=self.smoothing_var, 
            orient=tk.HORIZONTAL,
            command=self.on_smoothing_change
        )
        self.smoothing_scale.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(0, 5))
        
        self.smoothing_label = ttk.Label(gesture_frame, text=f"{config.gesture.smoothing_factor:.1f}")
        self.smoothing_label.grid(row=1, column=2, padx=(5, 0), pady=(0, 5))
        
        # 클릭 임계값 설정
        ttk.Label(gesture_frame, text="클릭 임계값:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        
        self.click_threshold_var = tk.DoubleVar(value=config.gesture.click_threshold)
        self.click_threshold_scale = ttk.Scale(
            gesture_frame, 
            from_=0.01, 
            to=0.2, 
            variable=self.click_threshold_var, 
            orient=tk.HORIZONTAL,
            command=self.on_click_threshold_change
        )
        self.click_threshold_scale.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(0, 5))
        
        self.click_threshold_label = ttk.Label(gesture_frame, text=f"{config.gesture.click_threshold:.2f}")
        self.click_threshold_label.grid(row=2, column=2, padx=(5, 0), pady=(0, 5))
        

        
        # 스크롤 임계값 설정
        ttk.Label(gesture_frame, text="스크롤 임계값:").grid(row=3, column=0, sticky=tk.W, pady=(0, 5))
        
        self.scroll_threshold_var = tk.DoubleVar(value=config.gesture.scroll_threshold)
        self.scroll_threshold_scale = ttk.Scale(
            gesture_frame, 
            from_=0.05, 
            to=0.3, 
            variable=self.scroll_threshold_var, 
            orient=tk.HORIZONTAL,
            command=self.on_scroll_threshold_change
        )
        self.scroll_threshold_scale.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(0, 5))
        
        self.scroll_threshold_label = ttk.Label(gesture_frame, text=f"{config.gesture.scroll_threshold:.2f}")
        self.scroll_threshold_label.grid(row=3, column=2, padx=(5, 0), pady=(0, 5))
        
        # 스와이프 임계값 설정
        ttk.Label(gesture_frame, text="스와이프 임계값:").grid(row=4, column=0, sticky=tk.W, pady=(0, 5))
        
        self.swipe_threshold_var = tk.DoubleVar(value=config.gesture.swipe_threshold)
        self.swipe_threshold_scale = ttk.Scale(
            gesture_frame, 
            from_=0.1, 
            to=0.5, 
            variable=self.swipe_threshold_var, 
            orient=tk.HORIZONTAL,
            command=self.on_swipe_threshold_change
        )
        self.swipe_threshold_scale.grid(row=4, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(0, 5))
        
        self.swipe_threshold_label = ttk.Label(gesture_frame, text=f"{config.gesture.swipe_threshold:.2f}")
        self.swipe_threshold_label.grid(row=4, column=2, padx=(5, 0), pady=(0, 5))
        
        # 스와이프 시간 제한 설정
        ttk.Label(gesture_frame, text="스와이프 시간 제한:").grid(row=5, column=0, sticky=tk.W, pady=(0, 5))
        
        self.swipe_time_limit_var = tk.DoubleVar(value=config.gesture.swipe_time_limit)
        self.swipe_time_limit_scale = ttk.Scale(
            gesture_frame, 
            from_=0.5, 
            to=5.0, 
            variable=self.swipe_time_limit_var, 
            orient=tk.HORIZONTAL,
            command=self.on_swipe_time_limit_change
        )
        self.swipe_time_limit_scale.grid(row=5, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(0, 5))
        
        self.swipe_time_limit_label = ttk.Label(gesture_frame, text=f"{config.gesture.swipe_time_limit:.1f}초")
        self.swipe_time_limit_label.grid(row=5, column=2, padx=(5, 0), pady=(0, 5))
        
        # 마우스 반전 설정
        ttk.Label(gesture_frame, text="마우스 반전:").grid(row=6, column=0, sticky=tk.W, pady=(10, 5))
        
        # 반전 설정 프레임
        invert_frame = ttk.Frame(gesture_frame)
        invert_frame.grid(row=6, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=(10, 0), pady=(10, 5))
        
        # X축 좌우 반전
        self.invert_x_var = tk.BooleanVar(value=config.gesture.invert_x)
        invert_x_check = ttk.Checkbutton(
            invert_frame, 
            text="좌우 반전 (X축)", 
            variable=self.invert_x_var
        )
        invert_x_check.grid(row=0, column=0, sticky=tk.W, padx=(0, 20))
        
        # Y축 상하 반전
        self.invert_y_var = tk.BooleanVar(value=config.gesture.invert_y)
        invert_y_check = ttk.Checkbutton(
            invert_frame, 
            text="상하 반전 (Y축)", 
            variable=self.invert_y_var
        )
        invert_y_check.grid(row=0, column=1, sticky=tk.W)
        
        # 그리드 가중치 설정
        gesture_frame.columnconfigure(1, weight=1)
    
    def create_camera_settings(self, parent) -> None:
        """카메라 설정 섹션 생성"""
        camera_frame = ttk.LabelFrame(parent, text="카메라 설정", padding="15")
        camera_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # 카메라 해상도 설정
        ttk.Label(camera_frame, text="카메라 해상도:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        current_resolution = f"{config.camera.width}x{config.camera.height}"
        self.resolution_var = tk.StringVar(value=current_resolution)
        resolution_combo = ttk.Combobox(
            camera_frame, 
            textvariable=self.resolution_var,
            values=["320x240", "480x360", "640x480", "800x600"],
            state="readonly"
        )
        resolution_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(0, 5))
        
        # FPS 설정
        ttk.Label(camera_frame, text="FPS:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        
        self.fps_var = tk.IntVar(value=config.camera.fps)
        fps_combo = ttk.Combobox(
            camera_frame, 
            textvariable=self.fps_var,
            values=[15, 24, 30, 60],
            state="readonly"
        )
        fps_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(0, 5))
        
        # 그리드 가중치 설정
        camera_frame.columnconfigure(1, weight=1)
    
    def create_tracking_settings(self, parent) -> None:
        """손 트래킹 설정 섹션 생성"""
        tracking_frame = ttk.LabelFrame(parent, text="손 트래킹 설정", padding="15")
        tracking_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # 최대 손 개수
        ttk.Label(tracking_frame, text="최대 손 개수:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.max_hands_var = tk.IntVar(value=config.hand_tracking.max_num_hands)
        max_hands_combo = ttk.Combobox(
            tracking_frame, 
            textvariable=self.max_hands_var,
            values=[1, 2],
            state="readonly"
        )
        max_hands_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(0, 5))
        
        # 감지 신뢰도
        ttk.Label(tracking_frame, text="감지 신뢰도:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        
        self.detection_confidence_var = tk.DoubleVar(value=config.hand_tracking.min_detection_confidence)
        detection_confidence_scale = ttk.Scale(
            tracking_frame, 
            from_=0.1, 
            to=1.0, 
            variable=self.detection_confidence_var, 
            orient=tk.HORIZONTAL
        )
        detection_confidence_scale.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(0, 5))
        
        # 추적 신뢰도
        ttk.Label(tracking_frame, text="추적 신뢰도:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        
        self.tracking_confidence_var = tk.DoubleVar(value=config.hand_tracking.min_tracking_confidence)
        tracking_confidence_scale = ttk.Scale(
            tracking_frame, 
            from_=0.1, 
            to=1.0, 
            variable=self.tracking_confidence_var, 
            orient=tk.HORIZONTAL
        )
        tracking_confidence_scale.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(0, 5))
        
        # 그리드 가중치 설정
        tracking_frame.columnconfigure(1, weight=1)
    
    def create_debug_settings(self, parent) -> None:
        """디버그 설정 섹션 생성"""
        debug_frame = ttk.LabelFrame(parent, text="디버그 설정", padding="15")
        debug_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # 디버그 모드 체크박스
        self.debug_mode_var = tk.BooleanVar(value=config.ui.debug_mode)
        debug_check = ttk.Checkbutton(
            debug_frame, 
            text="디버그 모드 활성화 (시작 시 디버그 창 자동 열기)", 
            variable=self.debug_mode_var
        )
        debug_check.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # 디버그 모드 설명
        debug_info = ttk.Label(
            debug_frame, 
            text="디버그 모드를 활성화하면 트래킹 시작 시 실시간 로그 창이 자동으로 열립니다.",
            foreground="gray",
            wraplength=400
        )
        debug_info.grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        
        # 그리드 가중치 설정
        debug_frame.columnconfigure(0, weight=1)
    
    def create_buttons(self, parent) -> None:
        """버튼 프레임 생성"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=5, column=0, columnspan=2, pady=(20, 0))
        
        # 적용 버튼
        apply_button = ttk.Button(button_frame, text="적용", command=self.apply_settings)
        apply_button.grid(row=0, column=0, padx=(0, 10))
        
        # 취소 버튼
        cancel_button = ttk.Button(button_frame, text="취소", command=self.on_closing)
        cancel_button.grid(row=0, column=1, padx=(10, 0))
        
        # 기본값 복원 버튼
        reset_button = ttk.Button(button_frame, text="기본값 복원", command=self.reset_to_defaults)
        reset_button.grid(row=0, column=2, padx=(10, 0))
    
    def on_sensitivity_change(self, value) -> None:
        """감도 변경 콜백"""
        sensitivity = float(value)
        self.sensitivity_label.config(text=f"{sensitivity:.1f}")
        
        # 실시간으로 감도 적용
        config.gesture.sensitivity = sensitivity
        logger.debug(f"감도 실시간 적용: {sensitivity}")
    
    def on_smoothing_change(self, value) -> None:
        """스무딩 변경 콜백"""
        smoothing = float(value)
        self.smoothing_label.config(text=f"{smoothing:.1f}")
        
        # 실시간으로 스무딩 적용
        config.gesture.smoothing_factor = smoothing
        logger.debug(f"스무딩 실시간 적용: {smoothing}")
    

    
    def on_click_threshold_change(self, value) -> None:
        """클릭 임계값 변경 콜백"""
        self.click_threshold_label.config(text=f"{float(value):.2f}")
    
    def on_scroll_threshold_change(self, value) -> None:
        """스크롤 임계값 변경 콜백"""
        self.scroll_threshold_label.config(text=f"{float(value):.2f}")
    
    def on_swipe_threshold_change(self, value) -> None:
        """스와이프 임계값 변경 콜백"""
        self.swipe_threshold_label.config(text=f"{float(value):.2f}")
    
    def on_swipe_time_limit_change(self, value) -> None:
        """스와이프 시간 제한 변경 콜백"""
        time_limit = float(value)
        self.swipe_time_limit_label.config(text=f"{time_limit:.1f}초")
        
        # 실시간으로 시간 제한 적용
        config.gesture.swipe_time_limit = time_limit
        logger.debug(f"스와이프 시간 제한 실시간 적용: {time_limit}초")
    
    def apply_settings(self) -> None:
        """설정 적용"""
        try:
            # 제스처 설정 업데이트
            config.gesture.sensitivity = self.sensitivity_var.get()
            config.gesture.smoothing_factor = self.smoothing_var.get()

            config.gesture.click_threshold = self.click_threshold_var.get()
            config.gesture.scroll_threshold = self.scroll_threshold_var.get()
            config.gesture.swipe_threshold = self.swipe_threshold_var.get()
            config.gesture.swipe_time_limit = self.swipe_time_limit_var.get()
            config.gesture.invert_x = self.invert_x_var.get()
            config.gesture.invert_y = self.invert_y_var.get()
            
            # 카메라 설정 업데이트
            resolution = self.resolution_var.get().split('x')
            config.camera.width = int(resolution[0])
            config.camera.height = int(resolution[1])
            config.camera.fps = self.fps_var.get()
            
            # 손 트래킹 설정 업데이트
            config.hand_tracking.max_num_hands = self.max_hands_var.get()
            config.hand_tracking.min_detection_confidence = self.detection_confidence_var.get()
            config.hand_tracking.min_tracking_confidence = self.tracking_confidence_var.get()
            
            # 디버그 설정 업데이트
            config.ui.debug_mode = self.debug_mode_var.get()
            
            # 설정 파일 저장
            config.save_config()
            
            # 설정 변경 콜백 호출
            if self.on_settings_changed:
                self.on_settings_changed()
            
            messagebox.showinfo("성공", "설정이 적용되었습니다.")
            logger.info("설정이 적용되었습니다.")
            
        except Exception as e:
            logger.error(f"설정 적용 중 오류: {e}")
            messagebox.showerror("오류", f"설정 적용 실패: {e}")
    
    def reset_to_defaults(self) -> None:
        """기본값으로 복원"""
        try:
            # 기본값으로 설정
            self.sensitivity_var.set(1.0)
            self.smoothing_var.set(0.5)

            self.click_threshold_var.set(0.05)
            self.scroll_threshold_var.set(0.1)
            self.swipe_threshold_var.set(0.3)
            self.swipe_time_limit_var.set(2.0)
            self.resolution_var.set("640x480")
            self.fps_var.set(30)
            self.max_hands_var.set(1)
            self.detection_confidence_var.set(0.7)
            self.tracking_confidence_var.set(0.5)
            self.debug_mode_var.set(False)
            self.invert_x_var.set(False)
            self.invert_y_var.set(False)
            
            # 라벨 업데이트
            self.sensitivity_label.config(text="1.0")
            self.smoothing_label.config(text="0.5")

            self.click_threshold_label.config(text="0.05")
            self.scroll_threshold_label.config(text="0.10")
            self.swipe_threshold_label.config(text="0.30")
            self.swipe_time_limit_label.config(text="2.0초")
            
            messagebox.showinfo("성공", "기본값으로 복원되었습니다.")
            logger.info("설정이 기본값으로 복원되었습니다.")
            
        except Exception as e:
            logger.error(f"기본값 복원 중 오류: {e}")
            messagebox.showerror("오류", f"기본값 복원 실패: {e}")
    
    def on_closing(self) -> None:
        """창 종료 처리"""
        try:
            # 마우스 휠 바인딩 해제
            try:
                self.settings_window.unbind_all("<MouseWheel>")
            except:
                pass
            
            self.settings_window.destroy()
            logger.info("설정 창이 종료되었습니다.")
        except Exception as e:
            logger.error(f"설정 창 종료 중 오류: {e}")
        finally:
            # 참조 정리
            self.settings_window = None
    
    def show(self) -> None:
        """설정 창 표시"""
        self.settings_window.deiconify()
        self.settings_window.focus_set() 