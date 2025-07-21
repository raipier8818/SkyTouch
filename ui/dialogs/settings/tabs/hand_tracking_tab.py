"""
Hand tracking settings tab for SkyTouch application.
"""
from PyQt5.QtWidgets import QWidget, QFormLayout, QLineEdit

from ui.styles.style_manager import StyleManager
from utils.logging.logger import get_logger

logger = get_logger(__name__)


class HandTrackingTab(QWidget):
    """손 트래킹 설정 탭"""
    
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
        hand_cfg = self.config_manager.get_hand_tracking_config()
        
        # 손 트래킹 설정 필드들
        self.max_hands = QLineEdit(str(hand_cfg.get('max_num_hands', '')))
        self.detection_conf = QLineEdit(str(hand_cfg.get('min_detection_confidence', '')))
        self.tracking_conf = QLineEdit(str(hand_cfg.get('min_tracking_confidence', '')))
        
        # 폼에 추가
        layout.addRow("최대 손 개수", self.max_hands)
        layout.addRow("감지 신뢰도", self.detection_conf)
        layout.addRow("추적 신뢰도", self.tracking_conf)
    
    def get_settings(self):
        """설정 값 반환"""
        return {
            'max_num_hands': int(self.max_hands.text()),
            'min_detection_confidence': float(self.detection_conf.text()),
            'min_tracking_confidence': float(self.tracking_conf.text())
        } 