"""
Camera settings tab for SkyTouch application.
"""
from PyQt5.QtWidgets import (QWidget, QFormLayout, QLineEdit, QComboBox, 
                             QSlider, QLabel, QHBoxLayout, QSpinBox, QPushButton)
from PyQt5.QtCore import Qt

from ui.styles.style_manager import StyleManager
from utils.logging.logger import get_logger
from utils.camera_utils import get_available_cameras, test_camera

logger = get_logger(__name__)


class CameraTab(QWidget):
    """카메라 설정 탭"""
    
    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager
        
        # 스타일 적용
        self.style_manager = StyleManager()
        self.style_manager.apply_theme_to_widget(self, "dark_theme")
        
        # 카메라 목록 저장
        self.camera_list = []
        
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self):
        """UI 설정"""
        layout = QFormLayout(self)
        
        # 해상도 설정
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems([
            "640x480 (VGA)",
            "800x600 (SVGA)", 
            "1024x768 (XGA)",
            "1280x720 (HD)",
            "1920x1080 (Full HD)"
        ])
        layout.addRow("해상도:", self.resolution_combo)
        
        # FPS 설정 (슬라이더)
        fps_layout = QHBoxLayout()
        self.fps_slider = QSlider(Qt.Horizontal)
        self.fps_slider.setRange(15, 60)
        self.fps_slider.setTickPosition(QSlider.TicksBelow)
        self.fps_slider.setTickInterval(15)
        self.fps_label = QLabel("30")
        self.fps_slider.valueChanged.connect(lambda v: self.fps_label.setText(str(v)))
        fps_layout.addWidget(self.fps_slider)
        fps_layout.addWidget(self.fps_label)
        layout.addRow("FPS:", fps_layout)
        
        # 디바이스 ID 설정
        device_layout = QHBoxLayout()
        self.device_combo = QComboBox()
        self.device_combo.setToolTip("사용 가능한 카메라 목록")
        
        # 새로고침 버튼
        self.refresh_btn = QPushButton("새로고침")
        self.refresh_btn.setToolTip("카메라 목록 새로고침")
        self.refresh_btn.clicked.connect(self._refresh_cameras)
        
        device_layout.addWidget(self.device_combo)
        device_layout.addWidget(self.refresh_btn)
        layout.addRow("디바이스:", device_layout)
        
        # 카메라 목록 초기화
        self._refresh_cameras()
        
        # 프레임 지연 설정
        self.delay_combo = QComboBox()
        self.delay_combo.addItems([
            "1ms (매우 빠름)",
            "5ms (빠름)", 
            "10ms (보통)",
            "20ms (느림)",
            "30ms (매우 느림)"
        ])
        self.delay_combo.setToolTip("프레임 간 지연 시간")
        layout.addRow("프레임 지연:", self.delay_combo)
    
    def _refresh_cameras(self):
        """카메라 목록 새로고침"""
        try:
            self.device_combo.clear()
            self.camera_list = get_available_cameras()
            
            for device_id, camera_name in self.camera_list:
                self.device_combo.addItem(f"{camera_name} (ID: {device_id})")
            
            logger.info(f"카메라 목록이 새로고침되었습니다. ({len(self.camera_list)}개 발견)")
            
        except Exception as e:
            logger.error(f"카메라 목록 새로고침 실패: {e}")
            # 기본 카메라 추가
            self.device_combo.addItem("기본 카메라 (ID: 0)")
            self.camera_list = [(0, "기본 카메라")]
    
    def _select_camera_by_id(self, device_id: int):
        """디바이스 ID로 카메라 선택"""
        try:
            for i, (cam_id, _) in enumerate(self.camera_list):
                if cam_id == device_id:
                    self.device_combo.setCurrentIndex(i)
                    return
            
            # 찾지 못하면 첫 번째 카메라 선택
            if self.camera_list:
                self.device_combo.setCurrentIndex(0)
            logger.warning(f"카메라 ID {device_id}를 찾을 수 없어 첫 번째 카메라를 선택했습니다.")
            
        except Exception as e:
            logger.error(f"카메라 선택 실패: {e}")
    
    def _load_settings(self):
        """설정 로드"""
        try:
            config = self.config_manager.get_camera_config()
            
            # 해상도 설정
            width = config.get('width', 480)
            height = config.get('height', 360)
            resolution_map = {
                (640, 480): 0,
                (800, 600): 1,
                (1024, 768): 2,
                (1280, 720): 3,
                (1920, 1080): 4
            }
            self.resolution_combo.setCurrentIndex(resolution_map.get((width, height), 0))
            
            # FPS 설정
            fps = config.get('fps', 30)
            self.fps_slider.setValue(fps)
            
            # 디바이스 ID - 실제 카메라 목록에서 찾기
            device_id = config.get('device_id', 0)
            self._select_camera_by_id(device_id)
            
            # 프레임 지연
            delay = int(config.get('frame_delay', 0.03) * 1000)
            delay_map = {1: 0, 5: 1, 10: 2, 20: 3, 30: 4}
            self.delay_combo.setCurrentIndex(delay_map.get(delay, 2))  # 기본값은 10ms
            
            logger.info("카메라 설정이 로드되었습니다.")
            
        except Exception as e:
            logger.error(f"카메라 설정 로드 실패: {e}")
    
    def get_settings(self):
        """설정 값 반환"""
        try:
            # 해상도 파싱
            resolution_text = self.resolution_combo.currentText()
            resolution_map = {
                "640x480 (VGA)": (640, 480),
                "800x600 (SVGA)": (800, 600),
                "1024x768 (XGA)": (1024, 768),
                "1280x720 (HD)": (1280, 720),
                "1920x1080 (Full HD)": (1920, 1080)
            }
            width, height = resolution_map.get(resolution_text, (480, 360))
            
            # 디바이스 ID - 현재 선택된 카메라에서 추출
            device_id = 0
            if self.camera_list and self.device_combo.currentIndex() < len(self.camera_list):
                device_id = self.camera_list[self.device_combo.currentIndex()][0]
            
            return {
                'width': width,
                'height': height,
                'fps': self.fps_slider.value(),
                'device_id': device_id,
                'frame_delay': [1, 5, 10, 20, 30][self.delay_combo.currentIndex()] / 1000.0
            }
            
        except Exception as e:
            logger.error(f"카메라 설정 값 반환 실패: {e}")
            return {} 