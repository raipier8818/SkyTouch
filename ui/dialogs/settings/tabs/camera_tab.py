"""
Camera settings tab for SkyTouch application.
"""
from PyQt5.QtWidgets import QWidget, QFormLayout, QLineEdit

from ui.styles.style_manager import StyleManager
from utils.logging.logger import get_logger

logger = get_logger(__name__)


class CameraTab(QWidget):
    """카메라 설정 탭"""
    
    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager
        
        # 스타일 적용
        self.style_manager = StyleManager()
        self.style_manager.apply_theme_to_widget(self, "dark_theme")
        
        self._setup_ui()
    
    def _setup_ui(self):
        """UI 설정"""
        layout = QFormLayout(self)
        cam_cfg = self.config_manager.get_camera_config()
        
        # 카메라 설정 필드들
        self.camera_width = QLineEdit(str(cam_cfg.get('width', '')))
        self.camera_height = QLineEdit(str(cam_cfg.get('height', '')))
        self.fps = QLineEdit(str(cam_cfg.get('fps', '')))
        self.device_id = QLineEdit(str(cam_cfg.get('device_id', '')))
        
        # 폼에 추가
        layout.addRow("해상도 (너비)", self.camera_width)
        layout.addRow("해상도 (높이)", self.camera_height)
        layout.addRow("FPS", self.fps)
        layout.addRow("장치 ID", self.device_id)
    
    def get_settings(self):
        """설정 값 반환"""
        return {
            'width': int(self.camera_width.text()),
            'height': int(self.camera_height.text()),
            'fps': int(self.fps.text()),
            'device_id': int(self.device_id.text())
        } 