"""
Camera capture for Hand Tracking Trackpad application.
"""
import cv2
import numpy as np
from typing import Optional, Tuple

from utils.logging.logger import get_logger
from exceptions.base import CameraError

logger = get_logger(__name__)


class CameraCapture:
    """카메라 캡처 클래스"""
    
    def __init__(self, config: dict):
        """
        카메라 캡처 초기화
        
        Args:
            config: 카메라 설정
        """
        try:
            self.config = config
            self.cap = None
            # 카메라 자동 초기화 제거 - 사용자가 시작할 때 열림
            logger.info("카메라 캡처가 초기화되었습니다. (카메라는 사용자가 시작할 때 열립니다)")
            
        except Exception as e:
            logger.error(f"카메라 캡처 초기화 실패: {e}")
            raise CameraError(f"카메라 캡처 초기화 실패: {e}")
    
    def _init_camera(self) -> None:
        """카메라 초기화"""
        self.cap = cv2.VideoCapture(self.config.get('device_id', 0))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.get('width', 480))
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.get('height', 360))
        self.cap.set(cv2.CAP_PROP_FPS, self.config.get('fps', 30))
        
        if not self.cap.isOpened():
            raise CameraError("카메라를 열 수 없습니다.")
    
    def reinitialize(self) -> None:
        """카메라 재초기화"""
        try:
            # 기존 카메라 해제
            if self.cap and self.cap.isOpened():
                self.cap.release()
            
            # 새로 초기화
            self._init_camera()
            logger.info("카메라가 재초기화되었습니다.")
            
        except Exception as e:
            logger.error(f"카메라 재초기화 실패: {e}")
            raise CameraError(f"카메라 재초기화 실패: {e}")
    
    def get_frame(self) -> Optional[np.ndarray]:
        """
        카메라에서 프레임 가져오기
        
        Returns:
            카메라 프레임 또는 None
        """
        try:
            ret, frame = self.cap.read()
            if not ret:
                logger.warning("카메라에서 프레임을 읽을 수 없습니다.")
                return None
            return frame
            
        except Exception as e:
            logger.error(f"프레임 가져오기 중 오류: {e}")
            return None
    
    def read(self):
        if self.cap is not None:
            return self.cap.read()
        return False, None
    
    def get_actual_resolution(self) -> Tuple[int, int]:
        """
        실제 웹캠 해상도를 가져옴
        
        Returns:
            실제 웹캠 해상도 (width, height)
        """
        try:
            if self.cap and self.cap.isOpened():
                actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                logger.debug(f"실제 웹캠 해상도: {actual_width}x{actual_height}")
                return (actual_width, actual_height)
            else:
                logger.warning("카메라가 열려있지 않아 설정된 해상도를 반환합니다.")
                return (self.config.get('width', 480), self.config.get('height', 360))
        except Exception as e:
            logger.error(f"실제 웹캠 해상도 가져오기 실패: {e}")
            return (self.config.get('width', 480), self.config.get('height', 360))
    
    def is_opened(self) -> bool:
        """
        카메라가 열려있는지 확인
        
        Returns:
            카메라 열림 상태
        """
        return self.cap is not None and self.cap.isOpened()
    
    def update_config(self, config: dict) -> None:
        """설정 업데이트"""
        try:
            self.config = config
            
            if self.cap and self.cap.isOpened():
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.get('width', 480))
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.get('height', 360))
                self.cap.set(cv2.CAP_PROP_FPS, config.get('fps', 30))
            
            logger.info("카메라 캡처 설정이 업데이트되었습니다.")
            
        except Exception as e:
            logger.error(f"카메라 캡처 설정 업데이트 실패: {e}")
    
    def release(self) -> None:
        """리소스 해제"""
        try:
            if self.cap and self.cap.isOpened():
                self.cap.release()
                self.cap = None
                logger.info("카메라 캡처 리소스가 해제되었습니다.")
            
        except Exception as e:
            logger.error(f"카메라 캡처 리소스 해제 중 오류: {e}")
    
    def __enter__(self):
        """컨텍스트 매니저 진입"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 매니저 종료"""
        self.release() 