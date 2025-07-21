"""
Settings dialog for Hand Tracking Trackpad application.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable

from utils.logging.logger import get_logger
from config.manager import ConfigManager

logger = get_logger(__name__)


class SettingsDialog(tk.Toplevel):
    """설정 다이얼로그"""
    
    def __init__(self, parent, config_manager: ConfigManager, on_settings_changed: Callable = None):
        """
        설정 다이얼로그 초기화
        
        Args:
            parent: 부모 윈도우
            config_manager: 설정 관리자
            on_settings_changed: 설정 변경 콜백
        """
        super().__init__(parent)
        
        self.parent = parent
        self.config_manager = config_manager
        self.on_settings_changed = on_settings_changed
        
        self.setup_window()
        self.create_widgets()
        self.load_settings()
        
        # 윈도우 종료 이벤트 바인딩
        self.protocol("WM_DELETE_WINDOW", self.close)
    
    def setup_window(self) -> None:
        """윈도우 설정"""
        self.title("설정")
        self.geometry("500x600")
        self.resizable(True, True)
        
        # 모달 창으로 설정 (설정 창은 모달이 아니므로 제거)
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
        window_width = 600
        window_height = 700
        
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
        title_label = ttk.Label(main_frame, text="설정", style="Title.TLabel")
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        # 설명
        description_label = ttk.Label(main_frame, text="각 모드별 세부 설정을 조정할 수 있습니다.", 
                                     font=("Arial", 9), foreground="gray")
        description_label.grid(row=1, column=0, pady=(0, 20))
        
        # 노트북 (탭) 생성
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        
        # 카메라 설정 탭
        self.create_camera_tab()
        
        # 손 트래킹 설정 탭
        self.create_hand_tracking_tab()
        
        # 제스처 설정 탭
        self.create_gesture_tab()
        
        # 모드별 설정 탭
        self.create_mode_tab()
        
        # UI 설정 탭
        self.create_ui_tab()
        
        # 버튼 프레임
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, pady=(0, 10))
        
        # 저장 버튼
        save_button = ttk.Button(button_frame, text="저장", command=self.save_settings)
        save_button.grid(row=0, column=0, padx=5)
        
        # 취소 버튼
        cancel_button = ttk.Button(button_frame, text="취소", command=self.close)
        cancel_button.grid(row=0, column=1, padx=5)
        
        # 기본값으로 초기화 버튼
        reset_button = ttk.Button(button_frame, text="기본값", command=self.reset_to_defaults)
        reset_button.grid(row=0, column=2, padx=5)
        
        # 그리드 가중치 설정
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
    
    def create_camera_tab(self) -> None:
        """카메라 설정 탭 생성"""
        camera_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(camera_frame, text="카메라")
        
        # 카메라 설정 위젯들
        ttk.Label(camera_frame, text="카메라 설정", style="Title.TLabel").grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # 해상도
        ttk.Label(camera_frame, text="해상도:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.camera_width_var = tk.StringVar()
        self.camera_height_var = tk.StringVar()
        width_frame = ttk.Frame(camera_frame)
        width_frame.grid(row=1, column=1, sticky=tk.W, pady=2)
        ttk.Entry(width_frame, textvariable=self.camera_width_var, width=8).grid(row=0, column=0)
        ttk.Label(width_frame, text="x").grid(row=0, column=1, padx=5)
        ttk.Entry(width_frame, textvariable=self.camera_height_var, width=8).grid(row=0, column=2)
        
        # FPS
        ttk.Label(camera_frame, text="FPS:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.camera_fps_var = tk.StringVar()
        ttk.Entry(camera_frame, textvariable=self.camera_fps_var, width=10).grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # 장치 ID
        ttk.Label(camera_frame, text="장치 ID:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.camera_device_var = tk.StringVar()
        ttk.Entry(camera_frame, textvariable=self.camera_device_var, width=10).grid(row=3, column=1, sticky=tk.W, pady=2)
    
    def create_hand_tracking_tab(self) -> None:
        """손 트래킹 설정 탭 생성"""
        tracking_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tracking_frame, text="손 트래킹")
        
        # 손 트래킹 설정 위젯들
        ttk.Label(tracking_frame, text="손 트래킹 설정", style="Title.TLabel").grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # 최대 손 개수
        ttk.Label(tracking_frame, text="최대 손 개수:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.max_hands_var = tk.StringVar()
        ttk.Entry(tracking_frame, textvariable=self.max_hands_var, width=10).grid(row=1, column=1, sticky=tk.W, pady=2)
        
        # 감지 신뢰도
        ttk.Label(tracking_frame, text="감지 신뢰도:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.detection_confidence_var = tk.StringVar()
        ttk.Entry(tracking_frame, textvariable=self.detection_confidence_var, width=10).grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # 추적 신뢰도
        ttk.Label(tracking_frame, text="추적 신뢰도:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.tracking_confidence_var = tk.StringVar()
        ttk.Entry(tracking_frame, textvariable=self.tracking_confidence_var, width=10).grid(row=3, column=1, sticky=tk.W, pady=2)
    
    def create_gesture_tab(self) -> None:
        """제스처 설정 탭 생성"""
        gesture_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(gesture_frame, text="제스처")
        
        # 제스처 설정 위젯들
        ttk.Label(gesture_frame, text="제스처 설정", style="Title.TLabel").grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # 클릭 임계값
        ttk.Label(gesture_frame, text="클릭 임계값:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.click_threshold_var = tk.StringVar()
        ttk.Entry(gesture_frame, textvariable=self.click_threshold_var, width=10).grid(row=1, column=1, sticky=tk.W, pady=2)
        
        # 감도
        ttk.Label(gesture_frame, text="감도:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.sensitivity_var = tk.StringVar()
        ttk.Entry(gesture_frame, textvariable=self.sensitivity_var, width=10).grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # 스무딩 팩터
        ttk.Label(gesture_frame, text="스무딩 팩터:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.smoothing_var = tk.StringVar()
        ttk.Entry(gesture_frame, textvariable=self.smoothing_var, width=10).grid(row=3, column=1, sticky=tk.W, pady=2)
        
        # 반전 설정
        self.invert_x_var = tk.BooleanVar()
        ttk.Checkbutton(gesture_frame, text="X축 반전", variable=self.invert_x_var).grid(row=4, column=0, sticky=tk.W, pady=2)
        
        self.invert_y_var = tk.BooleanVar()
        ttk.Checkbutton(gesture_frame, text="Y축 반전", variable=self.invert_y_var).grid(row=5, column=0, sticky=tk.W, pady=2)
        
        # 손가락 임계값
        ttk.Label(gesture_frame, text="손가락 임계값:").grid(row=6, column=0, sticky=tk.W, pady=2)
        self.finger_threshold_var = tk.StringVar()
        ttk.Entry(gesture_frame, textvariable=self.finger_threshold_var, width=10).grid(row=6, column=1, sticky=tk.W, pady=2)
    
    def create_mode_tab(self) -> None:
        """모드별 설정 탭 생성"""
        mode_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(mode_frame, text="모드별 설정")
        
        # 스크롤 가능한 프레임 생성
        canvas = tk.Canvas(mode_frame)
        scrollbar = ttk.Scrollbar(mode_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 클릭 모드 설정
        self.create_click_mode_settings(scrollable_frame)
        
        # 스크롤 모드 설정
        self.create_scroll_mode_settings(scrollable_frame)
        
        # 스와이프 모드 설정
        self.create_swipe_mode_settings(scrollable_frame)
        
        # 이동 모드 설정
        self.create_move_mode_settings(scrollable_frame)
        
        # 그리드 배치
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 그리드 가중치 설정
        mode_frame.columnconfigure(0, weight=1)
        mode_frame.rowconfigure(0, weight=1)
    
    def create_click_mode_settings(self, parent) -> None:
        """클릭 모드 설정"""
        click_frame = ttk.LabelFrame(parent, text="클릭 모드 설정", padding="10")
        click_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 클릭 임계값
        ttk.Label(click_frame, text="클릭 임계값:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.click_threshold_mode_var = tk.StringVar()
        ttk.Entry(click_frame, textvariable=self.click_threshold_mode_var, width=10).grid(row=0, column=1, sticky=tk.W, pady=2)
        ttk.Label(click_frame, text="(엄지-검지/중지 거리 임계값)").grid(row=0, column=2, sticky=tk.W, padx=(5, 0), pady=2)
        
        # 더블클릭 시간
        ttk.Label(click_frame, text="더블클릭 시간:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.double_click_time_var = tk.StringVar()
        ttk.Entry(click_frame, textvariable=self.double_click_time_var, width=10).grid(row=1, column=1, sticky=tk.W, pady=2)
        ttk.Label(click_frame, text="(초)").grid(row=1, column=2, sticky=tk.W, padx=(5, 0), pady=2)
        
        # 클릭 모드 안정화 시간
        ttk.Label(click_frame, text="모드 안정화 시간:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.click_stabilization_time_var = tk.StringVar()
        ttk.Entry(click_frame, textvariable=self.click_stabilization_time_var, width=10).grid(row=2, column=1, sticky=tk.W, pady=2)
        ttk.Label(click_frame, text="(초)").grid(row=2, column=2, sticky=tk.W, padx=(5, 0), pady=2)
    
    def create_scroll_mode_settings(self, parent) -> None:
        """스크롤 모드 설정"""
        scroll_frame = ttk.LabelFrame(parent, text="스크롤 모드 설정", padding="10")
        scroll_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 스크롤 거리 임계값
        ttk.Label(scroll_frame, text="스크롤 거리 임계값:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.scroll_distance_threshold_var = tk.StringVar()
        ttk.Entry(scroll_frame, textvariable=self.scroll_distance_threshold_var, width=10).grid(row=0, column=1, sticky=tk.W, pady=2)
        ttk.Label(scroll_frame, text="(최소 이동 거리)").grid(row=0, column=2, sticky=tk.W, padx=(5, 0), pady=2)
        
        # 스크롤 필요 프레임 수
        ttk.Label(scroll_frame, text="필요 프레임 수:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.scroll_required_frames_var = tk.StringVar()
        ttk.Entry(scroll_frame, textvariable=self.scroll_required_frames_var, width=10).grid(row=1, column=1, sticky=tk.W, pady=2)
        ttk.Label(scroll_frame, text="(연속 이동 프레임)").grid(row=1, column=2, sticky=tk.W, padx=(5, 0), pady=2)
        
        # 스크롤 반전 설정
        self.invert_scroll_x_var = tk.BooleanVar()
        ttk.Checkbutton(scroll_frame, text="스크롤 X축 반전", variable=self.invert_scroll_x_var).grid(row=2, column=0, sticky=tk.W, pady=2)
        
        self.invert_scroll_y_var = tk.BooleanVar()
        ttk.Checkbutton(scroll_frame, text="스크롤 Y축 반전", variable=self.invert_scroll_y_var).grid(row=3, column=0, sticky=tk.W, pady=2)
    
    def create_swipe_mode_settings(self, parent) -> None:
        """스와이프 모드 설정"""
        swipe_frame = ttk.LabelFrame(parent, text="스와이프 모드 설정", padding="10")
        swipe_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 스와이프 거리 임계값
        ttk.Label(swipe_frame, text="스와이프 거리 임계값:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.swipe_distance_threshold_var = tk.StringVar()
        ttk.Entry(swipe_frame, textvariable=self.swipe_distance_threshold_var, width=10).grid(row=0, column=1, sticky=tk.W, pady=2)
        ttk.Label(swipe_frame, text="(최소 이동 거리)").grid(row=0, column=2, sticky=tk.W, padx=(5, 0), pady=2)
        
        # 스와이프 필요 프레임 수
        ttk.Label(swipe_frame, text="필요 프레임 수:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.swipe_required_frames_var = tk.StringVar()
        ttk.Entry(swipe_frame, textvariable=self.swipe_required_frames_var, width=10).grid(row=1, column=1, sticky=tk.W, pady=2)
        ttk.Label(swipe_frame, text="(연속 이동 프레임)").grid(row=1, column=2, sticky=tk.W, padx=(5, 0), pady=2)
        
        # 스와이프 쿨타임
        ttk.Label(swipe_frame, text="스와이프 쿨타임:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.swipe_cooldown_var = tk.StringVar()
        ttk.Entry(swipe_frame, textvariable=self.swipe_cooldown_var, width=10).grid(row=2, column=1, sticky=tk.W, pady=2)
        ttk.Label(swipe_frame, text="(초)").grid(row=2, column=2, sticky=tk.W, padx=(5, 0), pady=2)
        
        # 스와이프 반전 설정
        self.invert_swipe_x_var = tk.BooleanVar()
        ttk.Checkbutton(swipe_frame, text="스와이프 X축 반전", variable=self.invert_swipe_x_var).grid(row=3, column=0, sticky=tk.W, pady=2)
        
        self.invert_swipe_y_var = tk.BooleanVar()
        ttk.Checkbutton(swipe_frame, text="스와이프 Y축 반전", variable=self.invert_swipe_y_var).grid(row=4, column=0, sticky=tk.W, pady=2)
    
    def create_move_mode_settings(self, parent) -> None:
        """이동 모드 설정"""
        move_frame = ttk.LabelFrame(parent, text="이동 모드 설정", padding="10")
        move_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 이동 모드 안정화 시간
        ttk.Label(move_frame, text="모드 안정화 시간:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.move_stabilization_time_var = tk.StringVar()
        ttk.Entry(move_frame, textvariable=self.move_stabilization_time_var, width=10).grid(row=0, column=1, sticky=tk.W, pady=2)
        ttk.Label(move_frame, text="(초)").grid(row=0, column=2, sticky=tk.W, padx=(5, 0), pady=2)
        
        # 최소 이동 임계값
        ttk.Label(move_frame, text="최소 이동 임계값:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.min_movement_threshold_var = tk.StringVar()
        ttk.Entry(move_frame, textvariable=self.min_movement_threshold_var, width=10).grid(row=1, column=1, sticky=tk.W, pady=2)
        ttk.Label(move_frame, text="(무시할 최소 움직임)").grid(row=1, column=2, sticky=tk.W, padx=(5, 0), pady=2)
    
    def create_ui_tab(self) -> None:
        """UI 설정 탭 생성"""
        ui_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(ui_frame, text="UI")
        
        # UI 설정 위젯들
        ttk.Label(ui_frame, text="UI 설정", style="Title.TLabel").grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # 윈도우 크기
        ttk.Label(ui_frame, text="윈도우 크기:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.window_width_var = tk.StringVar()
        self.window_height_var = tk.StringVar()
        size_frame = ttk.Frame(ui_frame)
        size_frame.grid(row=1, column=1, sticky=tk.W, pady=2)
        ttk.Entry(size_frame, textvariable=self.window_width_var, width=8).grid(row=0, column=0)
        ttk.Label(size_frame, text="x").grid(row=0, column=1, padx=5)
        ttk.Entry(size_frame, textvariable=self.window_height_var, width=8).grid(row=0, column=2)
        
        # 테마
        ttk.Label(ui_frame, text="테마:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.theme_var = tk.StringVar()
        theme_combo = ttk.Combobox(ui_frame, textvariable=self.theme_var, values=["clam", "alt", "default", "classic"])
        theme_combo.grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # 디버그 모드
        self.debug_mode_var = tk.BooleanVar()
        ttk.Checkbutton(ui_frame, text="디버그 모드", variable=self.debug_mode_var).grid(row=3, column=0, sticky=tk.W, pady=2)
    
    def load_settings(self) -> None:
        """설정 로드"""
        try:
            # 카메라 설정
            camera_config = self.config_manager.get_camera_config()
            self.camera_width_var.set(str(camera_config.get('width', 480)))
            self.camera_height_var.set(str(camera_config.get('height', 360)))
            self.camera_fps_var.set(str(camera_config.get('fps', 30)))
            self.camera_device_var.set(str(camera_config.get('device_id', 0)))
            
            # 손 트래킹 설정
            hand_tracking_config = self.config_manager.get_hand_tracking_config()
            self.max_hands_var.set(str(hand_tracking_config.get('max_num_hands', 1)))
            self.detection_confidence_var.set(str(hand_tracking_config.get('min_detection_confidence', 0.7)))
            self.tracking_confidence_var.set(str(hand_tracking_config.get('min_tracking_confidence', 0.5)))
            
            # 제스처 설정
            gesture_config = self.config_manager.get_gesture_config()
            self.click_threshold_var.set(str(gesture_config.get('click_threshold', 0.12)))
            self.sensitivity_var.set(str(gesture_config.get('sensitivity', 1.5)))
            self.smoothing_var.set(str(gesture_config.get('smoothing_factor', 0.5)))
            self.invert_x_var.set(gesture_config.get('invert_x', False))
            self.invert_y_var.set(gesture_config.get('invert_y', False))
            self.finger_threshold_var.set(str(gesture_config.get('finger_threshold', 0.02)))
            
            # 모드별 설정
            self.click_threshold_mode_var.set(str(gesture_config.get('click_threshold', 0.12)))
            self.double_click_time_var.set(str(gesture_config.get('double_click_time', 0.5)))
            self.click_stabilization_time_var.set(str(gesture_config.get('mode_stabilization_time', 0.2)))
            
            self.scroll_distance_threshold_var.set(str(gesture_config.get('scroll_distance_threshold', 0.003)))
            self.scroll_required_frames_var.set(str(gesture_config.get('scroll_required_frames', 1)))
            self.invert_scroll_x_var.set(gesture_config.get('invert_scroll_x', True))
            self.invert_scroll_y_var.set(gesture_config.get('invert_scroll_y', False))
            
            self.swipe_distance_threshold_var.set(str(gesture_config.get('swipe_distance_threshold', 0.008)))
            self.swipe_required_frames_var.set(str(gesture_config.get('swipe_required_frames', 3)))
            self.swipe_cooldown_var.set(str(gesture_config.get('swipe_cooldown', 0.5)))
            self.invert_swipe_x_var.set(gesture_config.get('invert_swipe_x', True))
            self.invert_swipe_y_var.set(gesture_config.get('invert_swipe_y', False))
            
            self.move_stabilization_time_var.set(str(gesture_config.get('mode_stabilization_time', 0.2)))
            self.min_movement_threshold_var.set(str(gesture_config.get('min_movement_threshold', 0.001)))
            
            # UI 설정
            ui_config = self.config_manager.get_ui_config()
            self.window_width_var.set(str(ui_config.get('window_width', 520)))
            self.window_height_var.set(str(ui_config.get('window_height', 800)))
            self.theme_var.set(ui_config.get('theme', 'clam'))
            self.debug_mode_var.set(ui_config.get('debug_mode', True))
            
            logger.info("설정이 로드되었습니다.")
            
        except Exception as e:
            logger.error(f"설정 로드 실패: {e}")
            messagebox.showerror("오류", f"설정 로드 실패: {e}")
    
    def save_settings(self) -> None:
        """설정 저장"""
        try:
            # 카메라 설정
            self.config_manager.update_config('camera', 'width', int(self.camera_width_var.get()))
            self.config_manager.update_config('camera', 'height', int(self.camera_height_var.get()))
            self.config_manager.update_config('camera', 'fps', int(self.camera_fps_var.get()))
            self.config_manager.update_config('camera', 'device_id', int(self.camera_device_var.get()))
            
            # 손 트래킹 설정
            self.config_manager.update_config('hand_tracking', 'max_num_hands', int(self.max_hands_var.get()))
            self.config_manager.update_config('hand_tracking', 'min_detection_confidence', float(self.detection_confidence_var.get()))
            self.config_manager.update_config('hand_tracking', 'min_tracking_confidence', float(self.tracking_confidence_var.get()))
            
            # 제스처 설정
            self.config_manager.update_config('gesture', 'click_threshold', float(self.click_threshold_var.get()))
            self.config_manager.update_config('gesture', 'sensitivity', float(self.sensitivity_var.get()))
            self.config_manager.update_config('gesture', 'smoothing_factor', float(self.smoothing_var.get()))
            self.config_manager.update_config('gesture', 'invert_x', self.invert_x_var.get())
            self.config_manager.update_config('gesture', 'invert_y', self.invert_y_var.get())
            self.config_manager.update_config('gesture', 'finger_threshold', float(self.finger_threshold_var.get()))
            
            # 모드별 설정
            self.config_manager.update_config('gesture', 'double_click_time', float(self.double_click_time_var.get()))
            self.config_manager.update_config('gesture', 'mode_stabilization_time', float(self.click_stabilization_time_var.get()))
            
            self.config_manager.update_config('gesture', 'scroll_distance_threshold', float(self.scroll_distance_threshold_var.get()))
            self.config_manager.update_config('gesture', 'scroll_required_frames', int(self.scroll_required_frames_var.get()))
            self.config_manager.update_config('gesture', 'invert_scroll_x', self.invert_scroll_x_var.get())
            self.config_manager.update_config('gesture', 'invert_scroll_y', self.invert_scroll_y_var.get())
            
            self.config_manager.update_config('gesture', 'swipe_distance_threshold', float(self.swipe_distance_threshold_var.get()))
            self.config_manager.update_config('gesture', 'swipe_required_frames', int(self.swipe_required_frames_var.get()))
            self.config_manager.update_config('gesture', 'swipe_cooldown', float(self.swipe_cooldown_var.get()))
            self.config_manager.update_config('gesture', 'invert_swipe_x', self.invert_swipe_x_var.get())
            self.config_manager.update_config('gesture', 'invert_swipe_y', self.invert_swipe_y_var.get())
            
            self.config_manager.update_config('gesture', 'min_movement_threshold', float(self.min_movement_threshold_var.get()))
            
            # UI 설정
            self.config_manager.update_config('ui', 'window_width', int(self.window_width_var.get()))
            self.config_manager.update_config('ui', 'window_height', int(self.window_height_var.get()))
            self.config_manager.update_config('ui', 'theme', self.theme_var.get())
            self.config_manager.update_config('ui', 'debug_mode', self.debug_mode_var.get())
            
            # 설정 파일 저장
            self.config_manager.save_config()
            
            # 설정 변경 콜백 호출
            if self.on_settings_changed:
                self.on_settings_changed()
            
            messagebox.showinfo("성공", "설정이 저장되었습니다.")
            logger.info("설정이 저장되었습니다.")
            
        except ValueError as e:
            logger.error(f"설정 값 오류: {e}")
            messagebox.showerror("오류", f"잘못된 설정 값: {e}")
        except Exception as e:
            logger.error(f"설정 저장 실패: {e}")
            messagebox.showerror("오류", f"설정 저장 실패: {e}")
    
    def reset_to_defaults(self) -> None:
        """기본값으로 초기화"""
        try:
            if messagebox.askyesno("확인", "모든 설정을 기본값으로 초기화하시겠습니까?"):
                self.config_manager.reset_to_defaults()
                self.load_settings()
                messagebox.showinfo("성공", "설정이 기본값으로 초기화되었습니다.")
                logger.info("설정이 기본값으로 초기화되었습니다.")
                
        except Exception as e:
            logger.error(f"설정 초기화 실패: {e}")
            messagebox.showerror("오류", f"설정 초기화 실패: {e}")
    
    def show(self) -> None:
        """설정 창 표시"""
        # 모달 상태 해제 (혹시 모달로 설정되어 있다면)
        try:
            if self.grab_status():
                self.grab_release()
                logger.debug("설정 창 모달 상태 해제됨")
        except:
            pass
        
        self.deiconify()
        self.lift()
        self.focus_set()
        logger.info("설정 창이 표시되었습니다.")
    
    def close(self) -> None:
        """설정 창 닫기"""
        # 모달 상태 해제 (혹시 모달로 설정되어 있다면)
        try:
            self.grab_release()
        except:
            pass
        
        self.withdraw()
        logger.info("설정 창이 닫혔습니다.") 