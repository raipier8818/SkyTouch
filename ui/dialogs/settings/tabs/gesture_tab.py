"""
Gesture settings tab for SkyTouch application.
"""
from PyQt5.QtWidgets import QWidget, QFormLayout, QLineEdit, QCheckBox

from ui.styles.style_manager import StyleManager
from utils.logging.logger import get_logger

logger = get_logger(__name__)


class GestureTab(QWidget):
    """제스처 설정 탭"""
    
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
        gesture_cfg = self.config_manager.get_gesture_config()
        
        # 제스처 설정 필드들
        self.click_threshold = QLineEdit(str(gesture_cfg.get('click_threshold', '')))
        self.sensitivity = QLineEdit(str(gesture_cfg.get('sensitivity', '')))
        self.smoothing = QLineEdit(str(gesture_cfg.get('smoothing_factor', '')))
        self.invert_x = QCheckBox()
        self.invert_x.setChecked(gesture_cfg.get('invert_x', False))
        self.invert_y = QCheckBox()
        self.invert_y.setChecked(gesture_cfg.get('invert_y', False))
        self.finger_threshold = QLineEdit(str(gesture_cfg.get('finger_threshold', '')))
        
        # 폼에 추가
        layout.addRow("클릭 임계값", self.click_threshold)
        layout.addRow("감도", self.sensitivity)
        layout.addRow("스무딩 팩터", self.smoothing)
        layout.addRow("X축 반전", self.invert_x)
        layout.addRow("Y축 반전", self.invert_y)
        layout.addRow("손가락 임계값", self.finger_threshold)
    
    def get_settings(self):
        """설정 값 반환"""
        return {
            'click_threshold': float(self.click_threshold.text()),
            'sensitivity': float(self.sensitivity.text()),
            'smoothing_factor': float(self.smoothing.text()),
            'invert_x': self.invert_x.isChecked(),
            'invert_y': self.invert_y.isChecked(),
            'finger_threshold': float(self.finger_threshold.text())
        } 