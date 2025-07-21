"""
Main window for Hand Tracking Trackpad application.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from typing import Optional, Callable

from utils.logging.logger import get_logger
from exceptions.base import UIError
from core.hand_tracking import HandDetector
from core.gesture import GestureDetector
from core.mouse import MouseController
from core.camera import CameraCapture
from config.manager import ConfigManager

logger = get_logger(__name__)


class MainWindow:
    """메인 애플리케이션 윈도우"""
    
    def __init__(self, camera_capture: CameraCapture, hand_detector: HandDetector,
                 gesture_detector: GestureDetector, mouse_controller: MouseController,
                 config_manager: ConfigManager, tracking_callback: Callable = None):
        """
        메인 윈도우 초기화
        
        Args:
            camera_capture: 카메라 캡처 객체
            hand_detector: 손 감지기
            gesture_detector: 제스처 감지기
            mouse_controller: 마우스 컨트롤러
            config_manager: 설정 관리자
            tracking_callback: 트래킹 콜백 함수
        """
        try:
            # 컴포넌트 저장
            self.camera_capture = camera_capture
            self.hand_detector = hand_detector
            self.gesture_detector = gesture_detector
            self.mouse_controller = mouse_controller
            self.config_manager = config_manager
            self.tracking_callback = tracking_callback
            
            # 트래킹 상태
            self.tracking_active = False
            
            # UI 컴포넌트
            self.root = None
            self.status_panel = None
            self.control_panel = None
            self.camera_panel = None
            self.settings_window = None
            self.debug_panel = None
            
            # 메인 윈도우 생성
            self._create_window()
            self._setup_styles()
            self._create_widgets()
            
            # 윈도우 종료 이벤트 바인딩
            self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
            
            logger.info("메인 윈도우가 생성되었습니다.")
            
        except Exception as e:
            logger.error(f"메인 윈도우 초기화 실패: {e}")
            raise UIError(f"메인 윈도우 초기화 실패: {e}")
    
    def _create_window(self) -> None:
        """윈도우 생성"""
        self.root = tk.Tk()
        
        # 윈도우 설정
        ui_config = self.config_manager.get_ui_config()
        self.root.title(ui_config.get('title', 'Hand Tracking Trackpad'))
        self.root.resizable(True, True)
        
        # 최소 크기 설정
        self.root.minsize(520, 800)
        
        # 윈도우를 화면 중앙에 배치
        self._center_window()
        
        # 윈도우 크기 설정 (중앙 배치 후)
        window_width = ui_config.get('window_width', 520)
        window_height = ui_config.get('window_height', 800)
        self.root.geometry(f"{window_width}x{window_height}")
    
    def _center_window(self) -> None:
        """윈도우를 화면 중앙에 배치"""
        # 윈도우가 완전히 생성될 때까지 대기
        self.root.update_idletasks()
        
        # 화면 크기 가져오기
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # 윈도우 크기
        ui_config = self.config_manager.get_ui_config()
        window_width = ui_config.get('window_width', 520)
        window_height = ui_config.get('window_height', 800)
        
        # 중앙 위치 계산 (약간 위쪽으로 조정)
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2) - 50  # 50픽셀 위로
        
        # 윈도우 위치 설정
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    def _setup_styles(self) -> None:
        """UI 스타일 설정"""
        style = ttk.Style()
        ui_config = self.config_manager.get_ui_config()
        style.theme_use(ui_config.get('theme', 'clam'))
        
        # 커스텀 스타일 정의
        font_family = ui_config.get('font_family', 'Arial')
        style.configure("Title.TLabel", 
                       font=(font_family, 16, "bold"))
        style.configure("Status.TLabel", 
                       font=(font_family, 12))
        style.configure("Info.TLabel", 
                       font=(font_family, 10))
        style.configure("Accent.TButton", 
                       background="#007bff", foreground="white")
        style.configure("Danger.TButton", 
                       background="#dc3545", foreground="white")
    
    def _create_widgets(self) -> None:
        """위젯 생성 및 배치"""
        # 메인 컨테이너
        main_container = ttk.Frame(self.root, padding="10")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 제목
        ui_config = self.config_manager.get_ui_config()
        title_label = ttk.Label(main_container, 
                               text=ui_config.get('title', 'Hand Tracking Trackpad'), 
                               style="Title.TLabel")
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # 상태 패널
        from ui.panels.status_panel.panel import StatusPanel
        self.status_panel = StatusPanel(main_container)
        self.status_panel.grid(row=1, column=0, columnspan=2, 
                              sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 제어 패널
        from ui.panels.control_panel.panel import ControlPanel
        self.control_panel = ControlPanel(main_container, 
                                         on_toggle=self._toggle_tracking)
        self.control_panel.grid(row=2, column=0, columnspan=2, 
                               sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 설정 버튼
        self._create_settings_button(main_container)
        
        # 정보 패널
        self._create_info_panel(main_container)
        
        # 카메라 패널
        from ui.panels.camera_panel.panel import CameraPanel
        self.camera_panel = CameraPanel(
            main_container, 
            camera_capture=self.camera_capture,
            hand_detector=self.hand_detector,
            gesture_detector=self.gesture_detector,
            mouse_controller=self.mouse_controller,
            config_manager=self.config_manager,
            control_panel=self.control_panel
        )
        self.camera_panel.grid(row=5, column=0, columnspan=2, 
                              sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 그리드 가중치 설정
        main_container.columnconfigure(0, weight=1)
        main_container.columnconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # 모든 위젯이 생성된 후 윈도우를 다시 중앙에 배치
        self.root.after(100, self._center_window)
    
    def _create_info_panel(self, parent) -> None:
        """정보 패널 생성"""
        info_frame = ttk.LabelFrame(parent, text="사용법", padding="15")
        info_frame.grid(row=4, column=0, columnspan=2, 
                       sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 스크롤 가능한 텍스트 위젯 생성
        text_widget = tk.Text(info_frame, height=8, width=50, wrap=tk.WORD, 
                             font=("Arial", 10), bg="white", relief="flat", 
                             borderwidth=0, padx=5, pady=5)
        text_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        info_text = """• 손바닥을 움직여 마우스 커서 이동

제스처 모드:
• 이동 모드: 검지만 펴진 상태
  - 손을 움직여 마우스 커서 이동

• 클릭 모드: 약지와 새끼손가락이 펴진 상태
  - 엄지와 검지를 붙임 → 클릭
  - 엄지와 중지를 붙임 → 우클릭

• 스크롤 모드: 검지와 중지만 펴진 상태
  - 손을 움직여 상하좌우 스크롤

• 스와이프 모드: 주먹을 쥔 상태 (모든 손가락 접음)
  - 좌우 스와이프 → 데스크탑 전환

• ESC 키로 트래킹 종료"""
        
        text_widget.insert(tk.END, info_text)
        text_widget.config(state=tk.DISABLED)  # 읽기 전용으로 설정
        
        # 스크롤바 추가
        scrollbar = ttk.Scrollbar(info_frame, orient="vertical", command=text_widget.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        info_frame.columnconfigure(0, weight=1)
        info_frame.rowconfigure(0, weight=1)
    
    def _create_settings_button(self, parent) -> None:
        """설정 버튼 생성"""
        settings_frame = ttk.Frame(parent)
        settings_frame.grid(row=3, column=0, columnspan=2, 
                           sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 설정 버튼
        settings_button = ttk.Button(settings_frame, text="⚙️ 설정", 
                                    command=self._open_settings)
        settings_button.grid(row=0, column=0, padx=5, pady=5)
        
        # 설정 프레임 가중치 설정
        settings_frame.columnconfigure(0, weight=1)
    
    def _open_settings(self) -> None:
        """설정 창 열기"""
        try:
            # 설정 창이 존재하지 않으면 새로 생성
            if not hasattr(self, 'settings_window') or not self.settings_window:
                from ui.dialogs.settings.dialog import SettingsDialog
                self.settings_window = SettingsDialog(
                    self.root, 
                    config_manager=self.config_manager,
                    on_settings_changed=self._on_settings_changed
                )
            
            # 설정 창 표시
            self.settings_window.show()
            
            # 모달 상태 확인 및 해제 (혹시 모달로 설정되어 있다면)
            try:
                if self.settings_window.grab_status():
                    self.settings_window.grab_release()
                    logger.debug("설정 창 모달 상태 해제됨")
            except:
                pass
            
            logger.info("설정 창이 열렸습니다.")
            
        except Exception as e:
            logger.error(f"설정 창 열기 실패: {e}")
            # 오류 발생 시 설정 창 참조 초기화
            if hasattr(self, 'settings_window'):
                self.settings_window = None
    
    def _open_debug_panel(self) -> None:
        """디버그 패널 열기"""
        try:
            # 디버그 패널이 존재하지 않거나 이미 종료된 경우 새로 생성
            if not hasattr(self, 'debug_panel') or not self.debug_panel or not self.debug_panel.winfo_exists():
                from ui.panels.debug_panel.panel import DebugPanel
                self.debug_panel = DebugPanel(self.root)
            else:
                self.debug_panel.show()
            
            logger.info("디버그 패널이 열렸습니다.")
            
        except Exception as e:
            logger.error(f"디버그 패널 열기 실패: {e}")
            # 오류 발생 시 디버그 패널 참조 초기화
            if hasattr(self, 'debug_panel'):
                self.debug_panel = None
    
    def _on_settings_changed(self) -> None:
        """설정 변경 시 호출되는 콜백"""
        try:
            # 손 감지기 설정 업데이트
            if self.hand_detector:
                hand_tracking_config = self.config_manager.get_hand_tracking_config()
                self.hand_detector.update_config(hand_tracking_config)
            
            # 제스처 감지기 설정 업데이트
            if self.gesture_detector:
                gesture_config = self.config_manager.get_gesture_config()
                self.gesture_detector.update_config(gesture_config)
            
            # 카메라 캡처 설정 업데이트
            if self.camera_capture:
                camera_config = self.config_manager.get_camera_config()
                self.camera_capture.update_config(camera_config)
            
            # 카메라 패널 설정 업데이트
            if self.camera_panel:
                self.camera_panel.update_config()
            
            # 마우스 컨트롤러 설정 업데이트
            if self.mouse_controller:
                self.mouse_controller.update_config()
            
            logger.info("설정이 실시간으로 적용되었습니다.")
            
        except Exception as e:
            logger.error(f"설정 적용 중 오류: {e}")
    
    def _start_tracking(self) -> None:
        """트래킹 시작"""
        try:
            if not self.tracking_active:
                self.tracking_active = True
                self.control_panel.set_tracking_state(True)
                self.status_panel.update_status("트래킹 중")
                
                # 디버그 모드가 활성화되어 있으면 디버그 패널 자동 열기
                ui_config = self.config_manager.get_ui_config()
                if ui_config.get('debug_mode', False):
                    self._open_debug_panel()
                
                # 카메라 화면 표시 시작
                self.camera_panel.start_display()
                
                if self.tracking_callback:
                    # 별도 스레드에서 트래킹 시작
                    tracking_thread = threading.Thread(
                        target=self.tracking_callback,
                        daemon=True
                    )
                    tracking_thread.start()
                
                logger.info("트래킹이 시작되었습니다.")
            
        except Exception as e:
            logger.error(f"트래킹 시작 실패: {e}")
            messagebox.showerror("오류", f"트래킹 시작 실패: {e}")
    
    def _toggle_tracking(self) -> None:
        """트래킹 토글 (시작/정지)"""
        if self.tracking_active:
            self._stop_tracking()
        else:
            self._start_tracking()
    
    def _stop_tracking(self) -> None:
        """트래킹 정지"""
        try:
            if self.tracking_active:
                logger.info("트래킹 정지 시작...")
                self.tracking_active = False
                
                # 버튼 비활성화
                self.control_panel.set_loading_state(True)
                self.status_panel.update_status("정지 중...")
                
                # 카메라 화면 표시 정지
                logger.info("카메라 패널 정지 요청...")
                self.camera_panel.stop_display()
                
                # 카메라 패널에서 자동으로 로딩 상태를 해제하므로 지연 없이 바로 완료 처리
                self.root.after(100, self._on_stop_complete)
                
                logger.info("트래킹 정지 요청 완료")
            
        except Exception as e:
            logger.error(f"트래킹 정지 실패: {e}")
            messagebox.showerror("오류", f"트래킹 정지 실패: {e}")
            # 오류 발생 시에도 버튼 활성화
            self.control_panel.set_loading_state(False)
    
    def _on_stop_complete(self) -> None:
        """트래킹 정지 완료 후 호출"""
        try:
            # 로딩 상태 해제 (버튼 활성화)
            self.control_panel.set_loading_state(False)
            # 트래킹 상태 설정
            self.control_panel.set_tracking_state(False)
            self.status_panel.update_status("대기 중")
            logger.info("트래킹이 완전히 정지되었습니다.")
            
        except Exception as e:
            logger.error(f"트래킹 정지 완료 처리 중 오류: {e}")
            # 오류 발생 시에도 버튼 활성화
            self.control_panel.set_loading_state(False)
    
    def set_error_status(self, error_message: str) -> None:
        """오류 상태 설정"""
        if self.status_panel:
            self.status_panel.set_error_status(error_message)
    
    def _update_settings(self) -> None:
        """설정 업데이트"""
        try:
            # 설정 파일 저장
            self.config_manager.save_config()
            
            logger.info("설정이 업데이트되었습니다.")
            
        except Exception as e:
            logger.error(f"설정 업데이트 실패: {e}")
            messagebox.showerror("오류", f"설정 업데이트 실패: {e}")
    
    def _on_closing(self) -> None:
        """윈도우 종료 처리"""
        try:
            if self.tracking_active:
                self._stop_tracking()
            
            # 카메라 패널 리소스 해제
            if self.camera_panel:
                self.camera_panel.stop_display()
            
            # 설정 저장
            self._update_settings()
            
            # 모든 OpenCV 창 닫기
            import cv2
            cv2.destroyAllWindows()
            
            logger.info("애플리케이션이 종료됩니다.")
            self.root.destroy()
            
        except Exception as e:
            logger.error(f"윈도우 종료 처리 중 오류: {e}")
            # 오류 발생 시에도 리소스 정리
            try:
                import cv2
                cv2.destroyAllWindows()
            except:
                pass
            self.root.destroy()
    
    def run(self) -> None:
        """애플리케이션 실행"""
        try:
            self.root.mainloop()
        except Exception as e:
            logger.error(f"애플리케이션 실행 중 오류: {e}")
            raise UIError(f"애플리케이션 실행 실패: {e}")
    
    def get_tracking_state(self) -> bool:
        """트래킹 상태 반환"""
        return self.tracking_active 