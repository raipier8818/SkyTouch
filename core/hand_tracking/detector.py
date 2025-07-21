"""
Hand detector for Hand Tracking Trackpad application.
"""
import numpy as np
from typing import Optional, List

from .mediapipe_wrapper import MediaPipeWrapper
from .landmarks import LandmarkProcessor, HandLandmarks
from utils.logging.logger import get_logger
from exceptions.base import HandTrackingError

logger = get_logger(__name__)


class HandDetector:
    """손 감지기 클래스"""
    
    def __init__(self, config: dict):
        """
        손 감지기 초기화
        
        Args:
            config: 손 트래킹 설정
        """
        try:
            self.config = config
            self.mediapipe_wrapper = MediaPipeWrapper(config)
            self.landmark_processor = LandmarkProcessor()
            self.last_results = None  # MediaPipe 결과 저장용
            logger.info("손 감지기가 초기화되었습니다.")
            
        except Exception as e:
            logger.error(f"손 감지기 초기화 실패: {e}")
            raise HandTrackingError(f"손 감지기 초기화 실패: {e}")
    
    def detect_hands(self, frame: np.ndarray) -> Optional[List[HandLandmarks]]:
        """
        프레임에서 손 감지
        
        Args:
            frame: 입력 프레임
            
        Returns:
            감지된 손 랜드마크 리스트
        """
        try:
            # MediaPipe로 손 감지
            results = self.mediapipe_wrapper.process_frame(frame)
            
            # 결과 저장 (랜드마크 그리기용)
            self.last_results = results
            
            if results is None:
                return None
            
            # 결과를 HandLandmarks 객체로 변환
            hand_landmarks_list = self.landmark_processor.process_results(results)
            
            return hand_landmarks_list
            
        except Exception as e:
            logger.error(f"손 감지 중 오류: {e}")
            return None
    
    def draw_landmarks(self, frame: np.ndarray, hand_landmarks: HandLandmarks) -> np.ndarray:
        """
        손 랜드마크를 프레임에 그리기
        
        Args:
            frame: 입력 프레임
            hand_landmarks: 손 랜드마크
            
        Returns:
            랜드마크가 그려진 프레임
        """
        try:
            # 저장된 MediaPipe 결과가 있으면 랜드마크 그리기
            if self.last_results and self.last_results.multi_hand_landmarks:
                # 해당 손의 랜드마크 찾기
                for i, mp_landmarks in enumerate(self.last_results.multi_hand_landmarks):
                    if i < len(self.last_results.multi_handedness):
                        handedness = self.last_results.multi_handedness[i].classification[0].label
                        # MediaPipe 래퍼를 사용하여 랜드마크 그리기
                        frame = self.mediapipe_wrapper.draw_landmarks(
                            frame, mp_landmarks, handedness
                        )
                        logger.debug(f"랜드마크 그리기 완료: {handedness}손")
                        break  # 첫 번째 손만 그리기
            
            return frame
            
        except Exception as e:
            logger.error(f"랜드마크 그리기 중 오류: {e}")
            return frame
    
    def get_actual_camera_resolution(self) -> tuple[int, int]:
        """실제 웹캠 해상도를 가져옴"""
        try:
            # 이 메서드는 카메라 캡처에서 구현되어야 함
            # 여기서는 기본값 반환
            return (self.config.get('width', 480), self.config.get('height', 360))
            
        except Exception as e:
            logger.error(f"실제 웹캠 해상도 가져오기 실패: {e}")
            return (480, 360)
    
    def update_config(self, config: dict) -> None:
        """설정 업데이트"""
        try:
            self.config = config
            self.mediapipe_wrapper.update_config(config)
            logger.info("손 감지기 설정이 업데이트되었습니다.")
            
        except Exception as e:
            logger.error(f"손 감지기 설정 업데이트 실패: {e}")
    
    def release(self) -> None:
        """리소스 해제"""
        try:
            if hasattr(self, 'mediapipe_wrapper'):
                self.mediapipe_wrapper.release()
            logger.info("손 감지기 리소스가 해제되었습니다.")
            
        except Exception as e:
            logger.error(f"손 감지기 리소스 해제 중 오류: {e}") 