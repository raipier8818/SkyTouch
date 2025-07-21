"""
MediaPipe wrapper for hand tracking.
"""
import cv2
import mediapipe as mp
import numpy as np
from typing import Optional

from utils.logging.logger import get_logger
from exceptions.base import HandTrackingError

logger = get_logger(__name__)


class MediaPipeWrapper:
    """MediaPipe 래퍼 클래스"""
    
    def __init__(self, config: dict):
        """
        MediaPipe 래퍼 초기화
        
        Args:
            config: MediaPipe 설정
        """
        try:
            self.config = config
            self._init_mediapipe()
            logger.info("MediaPipe 래퍼가 초기화되었습니다.")
            
        except Exception as e:
            logger.error(f"MediaPipe 래퍼 초기화 실패: {e}")
            raise HandTrackingError(f"MediaPipe 초기화 실패: {e}")
    
    def _init_mediapipe(self) -> None:
        """MediaPipe 초기화"""
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=self.config.get('static_image_mode', False),
            max_num_hands=self.config.get('max_num_hands', 1),
            min_detection_confidence=self.config.get('min_detection_confidence', 0.7),
            min_tracking_confidence=self.config.get('min_tracking_confidence', 0.5)
        )
        self.mp_draw = mp.solutions.drawing_utils
    
    def process_frame(self, frame: np.ndarray):
        """프레임에서 손 랜드마크 감지"""
        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)
            return results
            
        except Exception as e:
            logger.error(f"프레임 처리 중 오류: {e}")
            return None
    
    def draw_landmarks(self, frame: np.ndarray, hand_landmarks, handedness: str = "Right") -> np.ndarray:
        """손 랜드마크를 프레임에 그리기"""
        try:
            height, width = frame.shape[:2]
            
            # 손 방향에 따른 색상 설정 (더 눈에 띄게)
            if handedness == "Right":
                color = (0, 255, 0)  # 초록색
            else:
                color = (0, 0, 255)  # 빨간색
            
            logger.debug(f"랜드마크 그리기 시작: {handedness}손, 색상={color}")
            
            # 랜드마크 포인트 그리기
            self._draw_landmark_points(frame, hand_landmarks, color, width, height)
            
            # 손가락 연결선 그리기
            self._draw_connections(frame, hand_landmarks, color, width, height)
            
            # 손바닥 중심점 강조
            self._draw_palm_center(frame, hand_landmarks, width, height)
            
            logger.debug(f"랜드마크 그리기 완료: {handedness}손")
            return frame
            
        except Exception as e:
            logger.error(f"랜드마크 그리기 중 오류: {e}")
            return frame
    
    def _draw_landmark_points(self, frame: np.ndarray, hand_landmarks, 
                            color: tuple, width: int, height: int) -> None:
        """랜드마크 포인트 그리기"""
        for i, landmark in enumerate(hand_landmarks.landmark):
            x = int(landmark.x * width)
            y = int(landmark.y * height)
            
            # 랜드마크 포인트 크기 설정 (더 크게)
            if i in [4, 8, 12, 16, 20]:  # 손가락 팁
                radius = 12
            elif i in [3, 7, 11, 15, 19]:  # 손가락 PIP
                radius = 10
            elif i in [2, 6, 10, 14, 18]:  # 손가락 DIP
                radius = 8
            elif i == 9:  # 손바닥 중심
                radius = 15
            else:  # 기타 포인트
                radius = 6
            
            # 더 두꺼운 선으로 그리기
            cv2.circle(frame, (x, y), radius, color, -1)
            cv2.circle(frame, (x, y), radius, (255, 255, 255), 2)  # 흰색 테두리
    
    def _draw_connections(self, frame: np.ndarray, hand_landmarks, 
                         color: tuple, width: int, height: int) -> None:
        """손가락 연결선 그리기"""
        connections = [
            # 엄지
            (0, 1), (1, 2), (2, 3), (3, 4),
            # 검지
            (0, 5), (5, 6), (6, 7), (7, 8),
            # 중지
            (0, 9), (9, 10), (10, 11), (11, 12),
            # 약지
            (0, 13), (13, 14), (14, 15), (15, 16),
            # 새끼
            (0, 17), (17, 18), (18, 19), (19, 20),
            # 손바닥 연결
            (5, 9), (9, 13), (13, 17)
        ]
        
        for start_idx, end_idx in connections:
            if start_idx < len(hand_landmarks.landmark) and end_idx < len(hand_landmarks.landmark):
                start_point = (
                    int(hand_landmarks.landmark[start_idx].x * width),
                    int(hand_landmarks.landmark[start_idx].y * height)
                )
                end_point = (
                    int(hand_landmarks.landmark[end_idx].x * width),
                    int(hand_landmarks.landmark[end_idx].y * height)
                )
                
                cv2.line(frame, start_point, end_point, color, 3)
    
    def _draw_palm_center(self, frame: np.ndarray, hand_landmarks, 
                         width: int, height: int) -> None:
        """손바닥 중심점 강조"""
        palm_center = hand_landmarks.landmark[9]  # 중지 MCP
        palm_x = int(palm_center.x * width)
        palm_y = int(palm_center.y * height)
        cv2.circle(frame, (palm_x, palm_y), 20, (0, 255, 255), -1)  # 노란색 (더 크게)
        cv2.circle(frame, (palm_x, palm_y), 20, (255, 255, 255), 3)  # 흰색 테두리 (더 두껍게)
    
    def update_config(self, config: dict) -> None:
        """설정 업데이트"""
        try:
            self.config = config
            self.hands = self.mp_hands.Hands(
                static_image_mode=config.get('static_image_mode', False),
                max_num_hands=config.get('max_num_hands', 1),
                min_detection_confidence=config.get('min_detection_confidence', 0.7),
                min_tracking_confidence=config.get('min_tracking_confidence', 0.5)
            )
            logger.info("MediaPipe 설정이 업데이트되었습니다.")
            
        except Exception as e:
            logger.error(f"MediaPipe 설정 업데이트 실패: {e}")
    
    def release(self) -> None:
        """리소스 해제"""
        try:
            if hasattr(self, 'hands'):
                self.hands.close()
                logger.info("MediaPipe Hands 리소스 해제됨")
            
        except Exception as e:
            logger.error(f"MediaPipe 리소스 해제 중 오류: {e}") 