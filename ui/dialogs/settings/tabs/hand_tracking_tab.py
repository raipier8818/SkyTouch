"""
Hand tracking settings tab for SkyTouch application.
"""
from PyQt5.QtWidgets import (QWidget, QFormLayout, QComboBox, 
                             QSlider, QLabel, QHBoxLayout, QCheckBox)
from PyQt5.QtCore import Qt

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
        self._load_settings()
    
    def _setup_ui(self):
        """UI 설정"""
        layout = QFormLayout(self)
        
        # 최대 손 개수
        self.max_hands_combo = QComboBox()
        self.max_hands_combo.addItems([f"{i}개" for i in range(1, 5)])
        self.max_hands_combo.setToolTip("동시에 인식할 수 있는 최대 손 개수")
        layout.addRow("최대 손 개수:", self.max_hands_combo)
        
        # 검출 신뢰도 (슬라이더)
        detection_layout = QHBoxLayout()
        self.detection_slider = QSlider(Qt.Horizontal)
        self.detection_slider.setRange(50, 100)
        self.detection_slider.setTickPosition(QSlider.TicksBelow)
        self.detection_slider.setTickInterval(10)
        self.detection_label = QLabel("70%")
        self.detection_slider.valueChanged.connect(
            lambda v: self.detection_label.setText(f"{v}%")
        )
        detection_layout.addWidget(self.detection_slider)
        detection_layout.addWidget(self.detection_label)
        layout.addRow("검출 신뢰도:", detection_layout)
        
        # 추적 신뢰도 (슬라이더)
        tracking_layout = QHBoxLayout()
        self.tracking_slider = QSlider(Qt.Horizontal)
        self.tracking_slider.setRange(10, 100)
        self.tracking_slider.setTickPosition(QSlider.TicksBelow)
        self.tracking_slider.setTickInterval(10)
        self.tracking_label = QLabel("50%")
        self.tracking_slider.valueChanged.connect(
            lambda v: self.tracking_label.setText(f"{v}%")
        )
        tracking_layout.addWidget(self.tracking_slider)
        tracking_layout.addWidget(self.tracking_label)
        layout.addRow("추적 신뢰도:", tracking_layout)
        
        # 정적 이미지 모드
        self.static_mode_check = QCheckBox("정적 이미지 모드")
        self.static_mode_check.setToolTip("정적 이미지에서 손을 검출할 때 사용 (실시간보다 느림)")
        layout.addRow("", self.static_mode_check)
    
    def _load_settings(self):
        """설정 로드"""
        try:
            config = self.config_manager.get_hand_tracking_config()
            
            # 최대 손 개수
            max_hands = config.get('max_num_hands', 1)
            self.max_hands_combo.setCurrentIndex(max_hands - 1)
            
            # 검출 신뢰도
            detection_conf = int(config.get('min_detection_confidence', 0.7) * 100)
            self.detection_slider.setValue(detection_conf)
            
            # 추적 신뢰도
            tracking_conf = int(config.get('min_tracking_confidence', 0.5) * 100)
            self.tracking_slider.setValue(tracking_conf)
            
            # 정적 이미지 모드
            static_mode = config.get('static_image_mode', False)
            self.static_mode_check.setChecked(static_mode)
            
            logger.info("손 트래킹 설정이 로드되었습니다.")
            
        except Exception as e:
            logger.error(f"손 트래킹 설정 로드 실패: {e}")
    
    def get_settings(self):
        """설정 값 반환"""
        try:
            return {
                'max_num_hands': self.max_hands_combo.currentIndex() + 1,
                'min_detection_confidence': self.detection_slider.value() / 100.0,
                'min_tracking_confidence': self.tracking_slider.value() / 100.0,
                'static_image_mode': self.static_mode_check.isChecked()
            }
            
        except Exception as e:
            logger.error(f"손 트래킹 설정 값 반환 실패: {e}")
            return {} 