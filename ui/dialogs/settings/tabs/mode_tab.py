"""
Mode-specific settings tab for SkyTouch application.
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTabWidget, QFormLayout, 
                             QLineEdit, QCheckBox, QSlider, QLabel, QHBoxLayout,
                             QSpinBox, QGroupBox)
from PyQt5.QtCore import Qt

from ui.styles.style_manager import StyleManager
from utils.logging.logger import get_logger

logger = get_logger(__name__)


class ModeTab(QWidget):
    """모드별 설정 탭"""
    
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
        
        # 탭 위젯 생성
        self.tab_widget = QTabWidget()
        
        # 클릭 모드 탭
        self.click_tab = self._create_click_tab()
        self.tab_widget.addTab(self.click_tab, "클릭")
        
        # 스크롤 모드 탭
        self.scroll_tab = self._create_scroll_tab()
        self.tab_widget.addTab(self.scroll_tab, "스크롤")
        
        # 스와이프 모드 탭
        self.swipe_tab = self._create_swipe_tab()
        self.tab_widget.addTab(self.swipe_tab, "스와이프")
        
        layout.addWidget(self.tab_widget)
    
    def _create_click_tab(self):
        """클릭 모드 탭 생성"""
        tab = QWidget()
        layout = QFormLayout(tab)
        
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
        layout.addRow("클릭 임계값:", click_threshold_layout)
        
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
        layout.addRow("더블클릭 시간:", double_click_layout)
        
        # 모드 안정화 시간 (슬라이더)
        stabilization_layout = QHBoxLayout()
        self.stabilization_slider = QSlider(Qt.Horizontal)
        self.stabilization_slider.setRange(10, 50)
        self.stabilization_slider.setTickPosition(QSlider.TicksBelow)
        self.stabilization_slider.setTickInterval(10)
        self.stabilization_label = QLabel("0.2s")
        self.stabilization_slider.valueChanged.connect(
            lambda v: self.stabilization_label.setText(f"{v/100:.1f}s")
        )
        stabilization_layout.addWidget(self.stabilization_slider)
        stabilization_layout.addWidget(self.stabilization_label)
        layout.addRow("모드 안정화 시간:", stabilization_layout)
        
        return tab
    
    def _create_scroll_tab(self):
        """스크롤 모드 탭 생성"""
        tab = QWidget()
        layout = QFormLayout(tab)
        
        # 스크롤 임계값 (슬라이더)
        scroll_threshold_layout = QHBoxLayout()
        self.scroll_threshold_slider = QSlider(Qt.Horizontal)
        self.scroll_threshold_slider.setRange(5, 20)
        self.scroll_threshold_slider.setTickPosition(QSlider.TicksBelow)
        self.scroll_threshold_slider.setTickInterval(5)
        self.scroll_threshold_label = QLabel("0.1")
        self.scroll_threshold_slider.valueChanged.connect(
            lambda v: self.scroll_threshold_label.setText(f"{v/100:.1f}")
        )
        scroll_threshold_layout.addWidget(self.scroll_threshold_slider)
        scroll_threshold_layout.addWidget(self.scroll_threshold_label)
        layout.addRow("스크롤 임계값:", scroll_threshold_layout)
        
        # X축 반전
        self.invert_scroll_x = QCheckBox("X축 반전")
        self.invert_scroll_x.setToolTip("스크롤 시 X축 방향을 반전")
        layout.addRow("", self.invert_scroll_x)
        
        # Y축 반전
        self.invert_scroll_y = QCheckBox("Y축 반전")
        self.invert_scroll_y.setToolTip("스크롤 시 Y축 방향을 반전")
        layout.addRow("", self.invert_scroll_y)
        
        return tab
    
    def _create_swipe_tab(self):
        """스와이프 모드 탭 생성"""
        tab = QWidget()
        layout = QFormLayout(tab)
        
        # 스와이프 임계값 (슬라이더)
        swipe_threshold_layout = QHBoxLayout()
        self.swipe_threshold_slider = QSlider(Qt.Horizontal)
        self.swipe_threshold_slider.setRange(10, 50)
        self.swipe_threshold_slider.setTickPosition(QSlider.TicksBelow)
        self.swipe_threshold_slider.setTickInterval(10)
        self.swipe_threshold_label = QLabel("0.03")
        self.swipe_threshold_slider.valueChanged.connect(
            lambda v: self.swipe_threshold_label.setText(f"{v/1000:.2f}")
        )
        swipe_threshold_layout.addWidget(self.swipe_threshold_slider)
        swipe_threshold_layout.addWidget(self.swipe_threshold_label)
        layout.addRow("스와이프 임계값:", swipe_threshold_layout)
        
        # 스와이프 시간 제한 (슬라이더)
        swipe_time_layout = QHBoxLayout()
        self.swipe_time_slider = QSlider(Qt.Horizontal)
        self.swipe_time_slider.setRange(50, 200)
        self.swipe_time_slider.setTickPosition(QSlider.TicksBelow)
        self.swipe_time_slider.setTickInterval(50)
        self.swipe_time_label = QLabel("1.0s")
        self.swipe_time_slider.valueChanged.connect(
            lambda v: self.swipe_time_label.setText(f"{v/100:.1f}s")
        )
        swipe_time_layout.addWidget(self.swipe_time_slider)
        swipe_time_layout.addWidget(self.swipe_time_label)
        layout.addRow("스와이프 시간 제한:", swipe_time_layout)
        
        # X축 반전
        self.invert_swipe_x = QCheckBox("X축 반전")
        self.invert_swipe_x.setToolTip("스와이프 시 X축 방향을 반전")
        layout.addRow("", self.invert_swipe_x)
        
        # Y축 반전
        self.invert_swipe_y = QCheckBox("Y축 반전")
        self.invert_swipe_y.setToolTip("스와이프 시 Y축 방향을 반전")
        layout.addRow("", self.invert_swipe_y)
        
        return tab
    
    def _load_settings(self):
        """설정 로드"""
        try:
            config = self.config_manager.get_gesture_config()
            
            # 클릭 모드 설정
            click_threshold = int(config.get('click_threshold', 0.12) * 100)
            self.click_threshold_slider.setValue(click_threshold)
            
            double_click_time = int(config.get('double_click_time', 0.5) * 100)
            self.double_click_slider.setValue(double_click_time)
            
            stabilization_time = int(config.get('mode_stabilization_time', 0.2) * 100)
            self.stabilization_slider.setValue(stabilization_time)
            
            # 스크롤 모드 설정
            scroll_threshold = int(config.get('scroll_threshold', 0.1) * 100)
            self.scroll_threshold_slider.setValue(scroll_threshold)
            
            self.invert_scroll_x.setChecked(config.get('invert_scroll_x', True))
            self.invert_scroll_y.setChecked(config.get('invert_scroll_y', False))
            
            # 스와이프 모드 설정
            swipe_threshold = int(config.get('swipe_threshold', 0.03) * 1000)
            self.swipe_threshold_slider.setValue(swipe_threshold)
            
            swipe_time_limit = int(config.get('swipe_time_limit', 1.0) * 100)
            self.swipe_time_slider.setValue(swipe_time_limit)
            
            self.invert_swipe_x.setChecked(config.get('invert_swipe_x', True))
            self.invert_swipe_y.setChecked(config.get('invert_swipe_y', False))
            
            logger.info("모드별 설정이 로드되었습니다.")
            
        except Exception as e:
            logger.error(f"모드별 설정 로드 실패: {e}")
    
    def get_settings(self):
        """설정 값 반환"""
        try:
            return {
                'click_threshold': self.click_threshold_slider.value() / 100.0,
                'double_click_time': self.double_click_slider.value() / 100.0,
                'mode_stabilization_time': self.stabilization_slider.value() / 100.0,
                'scroll_threshold': self.scroll_threshold_slider.value() / 100.0,
                'invert_scroll_x': self.invert_scroll_x.isChecked(),
                'invert_scroll_y': self.invert_scroll_y.isChecked(),
                'swipe_threshold': self.swipe_threshold_slider.value() / 1000.0,
                'swipe_time_limit': self.swipe_time_slider.value() / 100.0,
                'invert_swipe_x': self.invert_swipe_x.isChecked(),
                'invert_swipe_y': self.invert_swipe_y.isChecked()
            }
            
        except Exception as e:
            logger.error(f"모드별 설정 값 반환 실패: {e}")
            return {} 