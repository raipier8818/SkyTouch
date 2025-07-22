"""
Gesture settings tab for SkyTouch application.
"""
from PyQt5.QtWidgets import (QWidget, QFormLayout, QComboBox, 
                             QSlider, QLabel, QHBoxLayout,
                             QGroupBox, QVBoxLayout)
from PyQt5.QtCore import Qt

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
        self._load_settings()
    
    def _setup_ui(self):
        """UI 설정"""
        layout = QVBoxLayout(self)
        
        # 클릭 설정 그룹
        click_group = QGroupBox("클릭 설정")
        click_layout = QFormLayout(click_group)
        
        # 클릭 임계값 (슬라이더)
        click_threshold_layout = QHBoxLayout()
        self.click_threshold_slider = QSlider(Qt.Horizontal)
        self.click_threshold_slider.setRange(5, 30)
        self.click_threshold_slider.setTickPosition(QSlider.TicksBelow)
        self.click_threshold_slider.setTickInterval(5)
        self.click_threshold_label = QLabel("0.12")
        self.click_threshold_slider.valueChanged.connect(
            lambda v: self.click_threshold_label.setText(f"{v/100:.2f}")
        )
        click_threshold_layout.addWidget(self.click_threshold_slider)
        click_threshold_layout.addWidget(self.click_threshold_label)
        click_layout.addRow("클릭 임계값:", click_threshold_layout)
        
        # 더블클릭 시간 (슬라이더)
        double_click_layout = QHBoxLayout()
        self.double_click_slider = QSlider(Qt.Horizontal)
        self.double_click_slider.setRange(20, 100)
        self.double_click_slider.setTickPosition(QSlider.TicksBelow)
        self.double_click_slider.setTickInterval(20)
        self.double_click_label = QLabel("0.5s")
        self.double_click_slider.valueChanged.connect(
            lambda v: self.double_click_label.setText(f"{v/100:.1f}s")
        )
        double_click_layout.addWidget(self.double_click_slider)
        double_click_layout.addWidget(self.double_click_label)
        click_layout.addRow("더블클릭 시간:", double_click_layout)
        
        layout.addWidget(click_group)
        
        # 스크롤 설정 그룹
        scroll_group = QGroupBox("스크롤 설정")
        scroll_layout = QFormLayout(scroll_group)
        
        # 스크롤 거리 임계값 (슬라이더)
        scroll_distance_layout = QHBoxLayout()
        self.scroll_distance_slider = QSlider(Qt.Horizontal)
        self.scroll_distance_slider.setRange(1, 10)
        self.scroll_distance_slider.setTickPosition(QSlider.TicksBelow)
        self.scroll_distance_slider.setTickInterval(1)
        self.scroll_distance_label = QLabel("0.003")
        self.scroll_distance_slider.valueChanged.connect(
            lambda v: self.scroll_distance_label.setText(f"{v/1000:.3f}")
        )
        scroll_distance_layout.addWidget(self.scroll_distance_slider)
        scroll_distance_layout.addWidget(self.scroll_distance_label)
        scroll_layout.addRow("스크롤 거리 임계값:", scroll_distance_layout)
        
        # 스크롤 필요 프레임 수
        self.scroll_frames_combo = QComboBox()
        self.scroll_frames_combo.addItems([f"{i} 프레임" for i in range(1, 11)])
        self.scroll_frames_combo.setToolTip("스크롤 인식에 필요한 연속 프레임 수")
        scroll_layout.addRow("스크롤 필요 프레임:", self.scroll_frames_combo)
        
        # 스크롤 정도 (슬라이더)
        scroll_amount_layout = QHBoxLayout()
        self.scroll_amount_slider = QSlider(Qt.Horizontal)
        self.scroll_amount_slider.setRange(1, 20)
        self.scroll_amount_slider.setTickPosition(QSlider.TicksBelow)
        self.scroll_amount_slider.setTickInterval(5)
        self.scroll_amount_label = QLabel("5")
        self.scroll_amount_slider.valueChanged.connect(
            lambda v: self.scroll_amount_label.setText(f"{v}")
        )
        scroll_amount_layout.addWidget(self.scroll_amount_slider)
        scroll_amount_layout.addWidget(self.scroll_amount_label)
        scroll_layout.addRow("스크롤 정도:", scroll_amount_layout)
        
        layout.addWidget(scroll_group)
        
        # 스와이프 설정 그룹
        swipe_group = QGroupBox("스와이프 설정")
        swipe_layout = QFormLayout(swipe_group)
        
        # 스와이프 거리 임계값 (슬라이더)
        swipe_distance_layout = QHBoxLayout()
        self.swipe_distance_slider = QSlider(Qt.Horizontal)
        self.swipe_distance_slider.setRange(5, 20)
        self.swipe_distance_slider.setTickPosition(QSlider.TicksBelow)
        self.swipe_distance_slider.setTickInterval(5)
        self.swipe_distance_label = QLabel("0.008")
        self.swipe_distance_slider.valueChanged.connect(
            lambda v: self.swipe_distance_label.setText(f"{v/1000:.3f}")
        )
        swipe_distance_layout.addWidget(self.swipe_distance_slider)
        swipe_distance_layout.addWidget(self.swipe_distance_label)
        swipe_layout.addRow("스와이프 거리 임계값:", swipe_distance_layout)
        
        # 스와이프 필요 프레임 수
        self.swipe_frames_combo = QComboBox()
        self.swipe_frames_combo.addItems([f"{i} 프레임" for i in range(1, 11)])
        self.swipe_frames_combo.setToolTip("스와이프 인식에 필요한 연속 프레임 수")
        swipe_layout.addRow("스와이프 필요 프레임:", self.swipe_frames_combo)
        
        # 스와이프 쿨다운 (슬라이더)
        swipe_cooldown_layout = QHBoxLayout()
        self.swipe_cooldown_slider = QSlider(Qt.Horizontal)
        self.swipe_cooldown_slider.setRange(10, 100)
        self.swipe_cooldown_slider.setTickPosition(QSlider.TicksBelow)
        self.swipe_cooldown_slider.setTickInterval(10)
        self.swipe_cooldown_label = QLabel("0.5s")
        self.swipe_cooldown_slider.valueChanged.connect(
            lambda v: self.swipe_cooldown_label.setText(f"{v/100:.1f}s")
        )
        swipe_cooldown_layout.addWidget(self.swipe_cooldown_slider)
        swipe_cooldown_layout.addWidget(self.swipe_cooldown_label)
        swipe_layout.addRow("스와이프 쿨다운:", swipe_cooldown_layout)
        
        layout.addWidget(swipe_group)
        
        # 일반 설정 그룹
        general_group = QGroupBox("일반 설정")
        general_layout = QFormLayout(general_group)
        
        # 민감도 (슬라이더)
        sensitivity_layout = QHBoxLayout()
        self.sensitivity_slider = QSlider(Qt.Horizontal)
        self.sensitivity_slider.setRange(50, 300)
        self.sensitivity_slider.setTickPosition(QSlider.TicksBelow)
        self.sensitivity_slider.setTickInterval(50)
        self.sensitivity_label = QLabel("1.5")
        self.sensitivity_slider.valueChanged.connect(
            lambda v: self.sensitivity_label.setText(f"{v/100:.1f}")
        )
        sensitivity_layout.addWidget(self.sensitivity_slider)
        sensitivity_layout.addWidget(self.sensitivity_label)
        general_layout.addRow("민감도:", sensitivity_layout)
        
        # 스무딩 팩터 (슬라이더)
        smoothing_layout = QHBoxLayout()
        self.smoothing_slider = QSlider(Qt.Horizontal)
        self.smoothing_slider.setRange(10, 90)
        self.smoothing_slider.setTickPosition(QSlider.TicksBelow)
        self.smoothing_slider.setTickInterval(10)
        self.smoothing_label = QLabel("0.5")
        self.smoothing_slider.valueChanged.connect(
            lambda v: self.smoothing_label.setText(f"{v/100:.1f}")
        )
        smoothing_layout.addWidget(self.smoothing_slider)
        smoothing_layout.addWidget(self.smoothing_label)
        general_layout.addRow("스무딩 팩터:", smoothing_layout)
        
        layout.addWidget(general_group)
    
    def _load_settings(self):
        """설정 로드"""
        try:
            config = self.config_manager.get_gesture_config()
            
            # 클릭 설정
            click_threshold = int(config.get('click_threshold', 0.12) * 100)
            self.click_threshold_slider.setValue(click_threshold)
            
            double_click_time = int(config.get('double_click_time', 0.5) * 100)
            self.double_click_slider.setValue(double_click_time)
            
            # 스크롤 설정
            scroll_distance = int(config.get('scroll_distance_threshold', 0.003) * 1000)
            self.scroll_distance_slider.setValue(scroll_distance)
            
            scroll_frames = config.get('scroll_required_frames', 1)
            self.scroll_frames_combo.setCurrentIndex(scroll_frames - 1)
            
            scroll_amount = config.get('scroll_amount', 5)
            self.scroll_amount_slider.setValue(scroll_amount)
            
            # 스와이프 설정
            swipe_distance = int(config.get('swipe_distance_threshold', 0.008) * 1000)
            self.swipe_distance_slider.setValue(swipe_distance)
            
            swipe_frames = config.get('swipe_required_frames', 3)
            self.swipe_frames_combo.setCurrentIndex(swipe_frames - 1)
            
            swipe_cooldown = int(config.get('swipe_cooldown', 0.5) * 100)
            self.swipe_cooldown_slider.setValue(swipe_cooldown)
            
            # 일반 설정
            sensitivity = int(config.get('sensitivity', 1.5) * 100)
            self.sensitivity_slider.setValue(sensitivity)
            
            smoothing = int(config.get('smoothing_factor', 0.5) * 100)
            self.smoothing_slider.setValue(smoothing)
            
            logger.info("제스처 설정이 로드되었습니다.")
            
        except Exception as e:
            logger.error(f"제스처 설정 로드 실패: {e}")
    
    def get_settings(self):
        """설정 값 반환"""
        try:
            return {
                'click_threshold': self.click_threshold_slider.value() / 100.0,
                'double_click_time': self.double_click_slider.value() / 100.0,
                'scroll_distance_threshold': self.scroll_distance_slider.value() / 1000.0,
                'scroll_required_frames': self.scroll_frames_combo.currentIndex() + 1,
                'scroll_amount': self.scroll_amount_slider.value(),
                'swipe_distance_threshold': self.swipe_distance_slider.value() / 1000.0,
                'swipe_required_frames': self.swipe_frames_combo.currentIndex() + 1,
                'swipe_cooldown': self.swipe_cooldown_slider.value() / 100.0,
                'sensitivity': self.sensitivity_slider.value() / 100.0,
                'smoothing_factor': self.smoothing_slider.value() / 100.0
            }
            
        except Exception as e:
            logger.error(f"제스처 설정 값 반환 실패: {e}")
            return {} 