"""
Settings dialog for SkyTouch application.
"""
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTabWidget, QSizePolicy, QPushButton

from .tabs import CameraTab, HandTrackingTab, GestureTab, ModeTab
from ui.styles.style_manager import StyleManager

from utils.logging.logger import get_logger

logger = get_logger(__name__)


class SettingsDialog(QDialog):
    """설정 대화상자 클래스"""
    
    def __init__(self, app_logic, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SkyTouch 설정")
        self.resize(400, 200)
        self.app_logic = app_logic
        self.config_manager = app_logic.config_manager
        
        # 스타일 적용
        self.style_manager = StyleManager()
        self.style_manager.apply_theme_to_widget(self, "dark_theme")
        
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self):
        """UI 설정"""
        layout = QVBoxLayout(self)
        tabs = QTabWidget()
        tabs.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # 각 설정 탭 생성
        self.camera_tab = CameraTab(self.config_manager)
        self.hand_tracking_tab = HandTrackingTab(self.config_manager)
        self.gesture_tab = GestureTab(self.config_manager)
        self.mode_tab = ModeTab(self.config_manager)

        # 탭 추가
        tabs.addTab(self.camera_tab, "카메라")
        tabs.addTab(self.hand_tracking_tab, "손 트래킹")
        tabs.addTab(self.gesture_tab, "제스처")
        tabs.addTab(self.mode_tab, "모드별 설정")

        layout.addWidget(tabs)
        
        # 저장 버튼
        save_btn = QPushButton("저장")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)
    
    def _load_settings(self):
        """설정 로드"""
        try:
            # 설정을 UI에 로드하는 로직
            logger.info("설정이 로드되었습니다.")
        except Exception as e:
            logger.error(f"설정 로드 실패: {e}")
    
    def save_settings(self):
        """설정 저장"""
        try:
            # 각 탭에서 설정 값 가져오기
            cam_cfg = self.camera_tab.get_settings()
            hand_cfg = self.hand_tracking_tab.get_settings()
            gesture_cfg = self.gesture_tab.get_settings()
            mode_cfg = self.mode_tab.get_settings()
            
            # 설정 업데이트
            self.config_manager.config['camera'].update(cam_cfg)
            self.config_manager.config['hand_tracking'].update(hand_cfg)
            self.config_manager.config['gesture'].update(gesture_cfg)
            self.config_manager.config['gesture'].update(mode_cfg)
            
            # 설정 저장
            self.config_manager.save_config()
            
            # 컴포넌트 설정 업데이트
            if self.app_logic.camera_capture:
                self.app_logic.camera_capture.update_config(cam_cfg)
            if self.app_logic.hand_detector:
                self.app_logic.hand_detector.update_config(hand_cfg)
            if self.app_logic.gesture_detector:
                self.app_logic.gesture_detector.update_config(gesture_cfg)
            
            logger.info("설정이 저장되었습니다.")
            self.accept()
            
        except Exception as e:
            logger.error(f"설정 저장 실패: {e}")
            # 에러 처리 (사용자에게 알림 등) 