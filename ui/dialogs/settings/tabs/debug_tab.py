"""
Debug settings tab for the settings dialog.
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QGroupBox

from ui.styles.style_manager import StyleManager


class DebugTab(QWidget):
    """디버그 설정 탭"""
    
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
        
        # 디버그 모드 그룹
        debug_group = QGroupBox("디버그 설정")
        debug_layout = QVBoxLayout(debug_group)
        
        # 디버그 모드 활성화
        self.debug_mode_checkbox = QCheckBox("디버그 모드 활성화")
        self.debug_mode_checkbox.setToolTip("트래킹 시작 시 디버그 패널을 표시합니다.")
        debug_layout.addWidget(self.debug_mode_checkbox)
        
        # 로그 레벨 설정
        self.verbose_logging_checkbox = QCheckBox("상세 로깅")
        self.verbose_logging_checkbox.setToolTip("더 자세한 로그 메시지를 출력합니다.")
        debug_layout.addWidget(self.verbose_logging_checkbox)
        
        # 실시간 로그 표시
        self.realtime_log_checkbox = QCheckBox("실시간 로그 표시")
        self.realtime_log_checkbox.setToolTip("로그 메시지를 실시간으로 디버그 패널에 표시합니다.")
        debug_layout.addWidget(self.realtime_log_checkbox)
        
        layout.addWidget(debug_group)
        layout.addStretch()
    
    def _load_settings(self):
        """설정 로드"""
        try:
            ui_config = self.config_manager.config.get('ui', {})
            
            # 디버그 모드 설정
            debug_mode = ui_config.get('debug_mode', False)
            self.debug_mode_checkbox.setChecked(debug_mode)
            
            # 상세 로깅 설정
            verbose_logging = ui_config.get('verbose_logging', False)
            self.verbose_logging_checkbox.setChecked(verbose_logging)
            
            # 실시간 로그 설정
            realtime_log = ui_config.get('realtime_log', True)
            self.realtime_log_checkbox.setChecked(realtime_log)
            
        except Exception as e:
            print(f"디버그 설정 로드 실패: {e}")
    
    def get_settings(self):
        """설정 값 반환"""
        return {
            'debug_mode': self.debug_mode_checkbox.isChecked(),
            'verbose_logging': self.verbose_logging_checkbox.isChecked(),
            'realtime_log': self.realtime_log_checkbox.isChecked()
        } 