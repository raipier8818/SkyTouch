"""
Main application class for SkyTouch.
"""
import threading
import time
from typing import Optional

from core.hand_tracking.detector import HandDetector
from core.gesture.detector import GestureDetector
from core.mouse.controller import MouseController
from core.camera.capture import CameraCapture
from config.manager import ConfigManager
from utils.logging.logger import get_logger
from exceptions.base import HandTrackpadError
import sys
from PyQt5.QtWidgets import QApplication
import qtmodern.styles
import qtmodern.windows
from ui.main_window.pyqt_main_window import IOSMainWindow

logger = get_logger(__name__)


class SkyTouchApp:
    """SkyTouch 메인 애플리케이션 클래스"""
    
    def __init__(self):
        """애플리케이션 초기화"""
        try:
            logger.info("SkyTouch 애플리케이션을 시작합니다.")
            
            # 설정 관리자 초기화
            self.config_manager = ConfigManager()
            
            # 핵심 컴포넌트 초기화
            self.camera_capture = None
            self.hand_detector = None
            self.gesture_detector = None
            self.mouse_controller = None
            self.main_window = None
            
            # 트래킹 상태
            self.tracking_active = False
            
            # 컴포넌트 초기화
            self.initialize_components()
            
            logger.info("애플리케이션이 성공적으로 초기화되었습니다.")
            
        except Exception as e:
            logger.error(f"애플리케이션 초기화 실패: {e}")
            raise HandTrackpadError(f"애플리케이션 초기화 실패: {e}")
    
    def initialize_components(self) -> None:
        """컴포넌트 초기화"""
        try:
            # 카메라 캡처 초기화
            camera_config = self.config_manager.get_camera_config()
            self.camera_capture = CameraCapture(camera_config)
            self.hand_detector = HandDetector(self.config_manager.get_hand_tracking_config())
            self.gesture_detector = GestureDetector(self.config_manager.get_gesture_config())
            self.mouse_controller = MouseController(self.camera_capture)
            self.qt_app = QApplication(sys.argv)
            self.main_window = IOSMainWindow(self)
            
            logger.info("모든 컴포넌트가 초기화되었습니다.")
            
        except Exception as e:
            logger.error(f"컴포넌트 초기화 실패: {e}")
            raise
    
    def tracking_loop(self) -> None:
        """손 트래킹 메인 루프"""
        try:
            logger.info("손 트래킹 루프를 시작합니다.")
            
            while self.tracking_active:
                # CPU 사용량 조절
                time.sleep(0.01)
                
                # 트래킹 상태 확인
                if not self.tracking_active:
                    break
                
            logger.info("손 트래킹 루프가 종료되었습니다.")
                
        except Exception as e:
            logger.error(f"손 트래킹 루프 중 오류: {e}")
            if self.main_window:
                self.main_window.set_error_status(str(e))
        finally:
            # 리소스 정리
            if self.hand_detector:
                self.hand_detector = None
    
    def start_tracking(self) -> None:
        """트래킹 시작"""
        try:
            if not self.tracking_active:
                self.tracking_active = True
                # 카메라 패널 시작
                if self.main_window and self.main_window.camera_panel:
                    self.main_window.camera_panel.start_display()
                logger.info("트래킹이 시작되었습니다.")
            
        except Exception as e:
            logger.error(f"트래킹 시작 실패: {e}")
            raise
    
    def stop_tracking(self) -> None:
        """트래킹 정지"""
        try:
            if self.tracking_active:
                self.tracking_active = False
                # 카메라 패널 정지
                if self.main_window and self.main_window.camera_panel:
                    self.main_window.camera_panel.stop_display()
                # 카메라 재초기화 (리소스 해제 후 다시 준비)
                if self.camera_capture:
                    self.camera_capture.release()
                    # 카메라 재초기화
                    camera_config = self.config_manager.get_camera_config()
                    self.camera_capture = CameraCapture(camera_config)
                logger.info("트래킹이 정지되었습니다.")
            
        except Exception as e:
            logger.error(f"트래킹 정지 실패: {e}")
            raise
    
    def run(self) -> None:
        """애플리케이션 실행"""
        try:
            logger.info("애플리케이션을 실행합니다.")
            # 카메라 자동 시작 제거 - 사용자가 버튼을 눌러야 시작됨
            self.main_window.show()
            sys.exit(self.qt_app.exec_())
            
        except Exception as e:
            logger.error(f"애플리케이션 실행 중 오류: {e}")
            raise HandTrackpadError(f"애플리케이션 실행 실패: {e}")
        finally:
            # 리소스 정리
            self.cleanup()
            logger.info("애플리케이션이 종료되었습니다.")
    
    def cleanup(self) -> None:
        """리소스 정리"""
        try:
            if self.camera_capture:
                self.camera_capture.release()
            if self.hand_detector:
                self.hand_detector.release()
            if self.mouse_controller:
                self.mouse_controller.cleanup()
            logger.info("애플리케이션 리소스가 정리되었습니다.")
            
        except Exception as e:
            logger.error(f"리소스 정리 중 오류: {e}") 

    def get_camera_frame(self):
        if self.camera_capture:
            ret, frame = self.camera_capture.read()
            if ret:
                return frame
        return None 