"""
Hand landmarks processing for Hand Tracking Trackpad application.
"""
from dataclasses import dataclass
from typing import List, Tuple, Optional
import numpy as np

from utils.logging.logger import get_logger

logger = get_logger(__name__)


@dataclass
class HandLandmarks:
    """손 랜드마크 데이터 클래스"""
    landmarks: List[List[float]]
    handedness: str
    confidence: float


class LandmarkProcessor:
    """손 랜드마크 처리 클래스"""
    
    def __init__(self):
        """랜드마크 프로세서 초기화"""
        self.logger = get_logger(__name__)
    
    def extract_landmarks(self, hand_landmarks) -> List[List[float]]:
        """랜드마크 좌표 추출"""
        return [[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark]
    
    def get_handedness(self, results, index: int) -> str:
        """손 방향 확인"""
        if results.multi_handedness:
            return results.multi_handedness[index].classification[0].label
        return "Unknown"
    
    def get_confidence(self, results, index: int) -> float:
        """신뢰도 계산"""
        if results.multi_handedness:
            return results.multi_handedness[index].classification[0].score
        return 0.0
    
    def get_palm_center(self, landmarks: List[List[float]]) -> List[float]:
        """손바닥 중심점 계산"""
        # 중지 MCP 관절 (랜드마크 9번)을 손바닥 중심으로 사용
        return landmarks[9]
    
    def get_finger_states(self, landmarks: List[List[float]], threshold: float = 0.02) -> dict:
        """손가락 상태 확인"""
        # 각 손가락의 팁과 MCP 관절
        finger_tips = [8, 12, 16, 20]  # 검지, 중지, 약지, 새끼
        finger_mcps = [5, 9, 13, 17]   # 각 손가락의 MCP 관절
        
        finger_states = {}
        
        for i, (tip, mcp) in enumerate(zip(finger_tips, finger_mcps)):
            tip_y = landmarks[tip][1]
            mcp_y = landmarks[mcp][1]
            
            # 손가락이 펴져있으면 팁이 MCP보다 위에 있음 (y값이 작음)
            finger_states[f'finger_{i+1}_extended'] = tip_y < (mcp_y - threshold)
        
        return finger_states
    
    def get_thumb_distances(self, landmarks: List[List[float]]) -> dict:
        """엄지-검지, 엄지-중지 거리 계산"""
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        middle_tip = landmarks[12]
        
        return {
            'thumb_index_distance': self.calculate_distance(thumb_tip, index_tip),
            'thumb_middle_distance': self.calculate_distance(thumb_tip, middle_tip)
        }
    
    def calculate_distance(self, point1: List[float], point2: List[float]) -> float:
        """두 점 사이의 유클리드 거리 계산"""
        return np.sqrt(
            (point1[0] - point2[0])**2 + 
            (point1[1] - point2[1])**2 + 
            (point1[2] - point2[2])**2
        )
    
    def process_results(self, results) -> Optional[List[HandLandmarks]]:
        """MediaPipe 결과를 HandLandmarks 객체로 변환"""
        if not results.multi_hand_landmarks:
            return None
        
        hand_landmarks_list = []
        
        for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
            landmarks = self.extract_landmarks(hand_landmarks)
            handedness = self.get_handedness(results, i)
            confidence = self.get_confidence(results, i)
            
            hand_landmarks_list.append(HandLandmarks(
                landmarks=landmarks,
                handedness=handedness,
                confidence=confidence
            ))
        
        return hand_landmarks_list 