"""
Mode-specific settings tab for SkyTouch application.
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QFormLayout, QLineEdit, QCheckBox

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
    
    def _setup_ui(self):
        """UI 설정"""
        layout = QVBoxLayout(self)
        mode_tabs = QTabWidget()
        gesture_cfg = self.config_manager.get_gesture_config()
        
        # 클릭 모드 탭
        click_tab = self._create_click_tab(gesture_cfg)
        mode_tabs.addTab(click_tab, "클릭")
        
        # 스크롤 모드 탭
        scroll_tab = self._create_scroll_tab(gesture_cfg)
        mode_tabs.addTab(scroll_tab, "스크롤")
        
        # 스와이프 모드 탭
        swipe_tab = self._create_swipe_tab(gesture_cfg)
        mode_tabs.addTab(swipe_tab, "스와이프")
        
        layout.addWidget(mode_tabs)
    
    def _create_click_tab(self, gesture_cfg):
        """클릭 모드 탭 생성"""
        tab = QWidget()
        layout = QFormLayout(tab)
        
        self.click_threshold_mode = QLineEdit(str(gesture_cfg.get('click_threshold', '')))
        self.double_click_time = QLineEdit(str(gesture_cfg.get('double_click_time', '')))
        self.click_stabilization_time = QLineEdit(str(gesture_cfg.get('mode_stabilization_time', '')))
        
        layout.addRow("[클릭] 임계값", self.click_threshold_mode)
        layout.addRow("[클릭] 더블클릭 시간", self.double_click_time)
        layout.addRow("[클릭] 모드 안정화 시간", self.click_stabilization_time)
        
        return tab
    
    def _create_scroll_tab(self, gesture_cfg):
        """스크롤 모드 탭 생성"""
        tab = QWidget()
        layout = QFormLayout(tab)
        
        self.scroll_distance_threshold = QLineEdit(str(gesture_cfg.get('scroll_distance_threshold', '')))
        self.scroll_required_frames = QLineEdit(str(gesture_cfg.get('scroll_required_frames', '')))
        self.invert_scroll_x = QCheckBox()
        self.invert_scroll_x.setChecked(gesture_cfg.get('invert_scroll_x', False))
        self.invert_scroll_y = QCheckBox()
        self.invert_scroll_y.setChecked(gesture_cfg.get('invert_scroll_y', False))
        
        layout.addRow("[스크롤] 거리 임계값", self.scroll_distance_threshold)
        layout.addRow("[스크롤] 필요 프레임", self.scroll_required_frames)
        layout.addRow("[스크롤] X축 반전", self.invert_scroll_x)
        layout.addRow("[스크롤] Y축 반전", self.invert_scroll_y)
        
        return tab
    
    def _create_swipe_tab(self, gesture_cfg):
        """스와이프 모드 탭 생성"""
        tab = QWidget()
        layout = QFormLayout(tab)
        
        self.swipe_distance_threshold = QLineEdit(str(gesture_cfg.get('swipe_distance_threshold', '')))
        self.swipe_required_frames = QLineEdit(str(gesture_cfg.get('swipe_required_frames', '')))
        self.swipe_cooldown = QLineEdit(str(gesture_cfg.get('swipe_cooldown', '')))
        self.invert_swipe_x = QCheckBox()
        self.invert_swipe_x.setChecked(gesture_cfg.get('invert_swipe_x', False))
        self.invert_swipe_y = QCheckBox()
        self.invert_swipe_y.setChecked(gesture_cfg.get('invert_swipe_y', False))
        
        layout.addRow("[스와이프] 거리 임계값", self.swipe_distance_threshold)
        layout.addRow("[스와이프] 필요 프레임", self.swipe_required_frames)
        layout.addRow("[스와이프] 쿨다운", self.swipe_cooldown)
        layout.addRow("[스와이프] X축 반전", self.invert_swipe_x)
        layout.addRow("[스와이프] Y축 반전", self.invert_swipe_y)
        
        return tab
    
    def get_settings(self):
        """설정 값 반환"""
        return {
            'double_click_time': float(self.double_click_time.text()),
            'mode_stabilization_time': float(self.click_stabilization_time.text()),
            'scroll_distance_threshold': float(self.scroll_distance_threshold.text()),
            'scroll_required_frames': int(self.scroll_required_frames.text()),
            'invert_scroll_x': self.invert_scroll_x.isChecked(),
            'invert_scroll_y': self.invert_scroll_y.isChecked(),
            'swipe_distance_threshold': float(self.swipe_distance_threshold.text()),
            'swipe_required_frames': int(self.swipe_required_frames.text()),
            'swipe_cooldown': float(self.swipe_cooldown.text()),
            'invert_swipe_x': self.invert_swipe_x.isChecked(),
            'invert_swipe_y': self.invert_swipe_y.isChecked()
        } 