"""
Main window for SkyTouch application.
"""
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt

from ui.styles.style_manager import StyleManager
from ui.panels.camera_panel.panel import CameraPanel
from ui.panels.debug_panel.panel import DebugPanel
from ui.dialogs.settings.dialog import SettingsDialog

from utils.logging.logger import get_logger

logger = get_logger(__name__)


class IOSMainWindow(QMainWindow):
    """SkyTouch 메인 윈도우 클래스"""
    
    def __init__(self, app_logic):
        super().__init__()
        self.app_logic = app_logic
        self.setWindowTitle("SkyTouch")
        self.setFixedSize(400, 300)  # 크기 고정
        
        # 윈도우 투명도 설정
        self.setWindowOpacity(0.80)  # 80% 투명도
        # self.setAttribute(Qt.WA_TranslucentBackground, True)  # 배경 투명화 비활성화
        
        # 스타일 관리자 초기화 및 테마 적용
        self.style_manager = StyleManager()
        self.style_manager.apply_theme_to_widget(self, "dark_theme")
        
        # 디버그 패널 참조
        self.debug_panel = None
        
        self._setup_ui()
        
        # 트래킹 상태
        self.is_tracking = False
    
    def _setup_ui(self):
        """UI 설정"""
        main_widget = QWidget()
        # 중앙 위젯에도 다크 테마 적용
        self.style_manager.apply_theme_to_widget(main_widget, "dark_theme")
        
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(4)  # 간격 줄임
        main_layout.setContentsMargins(8, 8, 8, 8)  # 여백 줄임

        # 카메라 패널
        self.camera_panel = CameraPanel(self.app_logic)
        main_layout.addWidget(self.camera_panel, 1)  # stretch=1

        # 트래킹 제어 버튼
        self.tracking_btn = QPushButton("트래킹 시작")
        self.tracking_btn.setObjectName("SettingsButton")
        self.tracking_btn.clicked.connect(self.toggle_tracking)
        main_layout.addWidget(self.tracking_btn, 0)  # stretch=0

        # 설정 버튼
        self.settings_btn = QPushButton("설정")
        self.settings_btn.setObjectName("SettingsButton")
        self.settings_btn.clicked.connect(self.open_settings)
        main_layout.addWidget(self.settings_btn, 0)  # stretch=0
        
        self.setCentralWidget(main_widget)
    
    def toggle_tracking(self):
        """트래킹 시작/중지 토글"""
        # 버튼 비활성화 (중복 클릭 방지)
        self.tracking_btn.setEnabled(False)
        
        if not self.is_tracking:
            # 트래킹 시작
            try:
                self.app_logic.start_tracking()
                self.tracking_btn.setText("트래킹 중지")
                self.is_tracking = True
                logger.info("트래킹이 성공적으로 시작되었습니다.")
                
                # 디버그 모드가 활성화되어 있으면 디버그 패널 표시
                self._show_debug_panel_if_enabled()
                
            except Exception as e:
                logger.error(f"트래킹 시작 실패: {e}")
                # 실패 시 버튼 다시 활성화
                self.tracking_btn.setEnabled(True)
                return
        else:
            # 트래킹 중지
            try:
                self.app_logic.stop_tracking()
                self.tracking_btn.setText("트래킹 시작")
                self.is_tracking = False
                logger.info("트래킹이 성공적으로 중지되었습니다.")
                
                # 디버그 패널 숨기기
                self._hide_debug_panel()
                
            except Exception as e:
                logger.error(f"트래킹 중지 실패: {e}")
                # 실패 시 버튼 다시 활성화
                self.tracking_btn.setEnabled(True)
                return
        
        # 성공 시 버튼 다시 활성화 (약간의 지연 후)
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(500, lambda: self.tracking_btn.setEnabled(True))
    
    def _show_debug_panel_if_enabled(self):
        """디버그 모드가 활성화되어 있으면 디버그 패널 표시"""
        try:
            # 설정에서 디버그 모드 확인
            ui_config = self.app_logic.config_manager.config.get('ui', {})
            debug_mode = ui_config.get('debug_mode', False)
            
            if debug_mode:
                if not self.debug_panel:
                    self.debug_panel = DebugPanel()
                
                # 메인 윈도우 옆에 위치시키기
                main_geometry = self.geometry()
                debug_x = main_geometry.x() + main_geometry.width() + 10
                debug_y = main_geometry.y()
                
                self.debug_panel.move(debug_x, debug_y)
                self.debug_panel.show()
                self.debug_panel.raise_()
                
                logger.info("디버그 패널이 표시되었습니다.")
            else:
                logger.debug("디버그 모드가 비활성화되어 있어 디버그 패널을 표시하지 않습니다.")
                
        except Exception as e:
            logger.error(f"디버그 패널 표시 실패: {e}")
    
    def _hide_debug_panel(self):
        """디버그 패널 숨기기"""
        try:
            if self.debug_panel and self.debug_panel.isVisible():
                self.debug_panel.hide()
                logger.info("디버그 패널이 숨겨졌습니다.")
        except Exception as e:
            logger.error(f"디버그 패널 숨기기 실패: {e}")
    
    def open_settings(self):
        """설정 창 열기"""
        try:
            dlg = SettingsDialog(self.app_logic, self)
            dlg.exec_()
        except Exception as e:
            logger.error(f"설정 창 열기 실패: {e}")
    
    def closeEvent(self, event):
        """창 닫기 이벤트"""
        # 디버그 패널도 함께 닫기
        if self.debug_panel:
            self.debug_panel.close()
        event.accept() 