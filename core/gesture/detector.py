"""
Gesture detector for Hand Tracking Trackpad application.
"""
import time
from typing import Optional, Dict, Any

from .types import GestureData, FingerState, ThumbDistance, GestureType
from .classifier import GestureClassifier
from core.hand_tracking.landmarks import HandLandmarks
from utils.logging.logger import get_logger
from exceptions.base import GestureError

logger = get_logger(__name__)


class GestureDetector:
    """제스처 감지기 클래스"""
    
    def __init__(self, config: dict):
        """
        제스처 감지기 초기화
        
        Args:
            config: 제스처 설정
        """
        try:
            self.config = config
            self.classifier = GestureClassifier(config)
            
            # 스크롤 관련 변수들
            self.scroll_palm_position = None
            self.scroll_direction_history = []
            self.scroll_frame_count = 0
            
            # 스와이프 관련 변수들
            self.swipe_palm_position = None
            self.swipe_direction_history = []
            self.swipe_frame_count = 0
            self.last_swipe_time = 0.0
            self.is_swipe_cooldown = False
            
            logger.info("제스처 감지기가 초기화되었습니다.")
            
        except Exception as e:
            logger.error(f"제스처 감지기 초기화 실패: {e}")
            raise GestureError(f"제스처 감지기 초기화 실패: {e}")
    
    def detect_gestures(self, hand_landmarks: HandLandmarks) -> GestureData:
        """
        손 랜드마크에서 제스처 감지
        
        Args:
            hand_landmarks: 손 랜드마크
            
        Returns:
            제스처 데이터
        """
        try:
            current_time = time.time()
            landmarks = hand_landmarks.landmarks
            
            # 기본 정보 추출
            palm_center = landmarks[9]  # 중지 MCP 관절
            
            # 손가락 상태와 엄지 거리 계산
            finger_state = self._get_finger_state(landmarks)
            thumb_distance = self._get_thumb_distance(landmarks)
            
            # 제스처 모드 감지
            gesture_mode = self.classifier.classify_gesture(finger_state, thumb_distance)
            
            # 모드 변경 처리
            self.classifier.handle_mode_change(gesture_mode, current_time)
            
            # 히스토리 기반 안정화된 제스처 모드 결정
            stable_gesture_mode = self.classifier.get_stable_gesture_mode(gesture_mode)
            
            # 히스토리에 추가
            self._add_to_history(stable_gesture_mode, current_time, finger_state)
            
            logger.debug(f"제스처 모드: {gesture_mode.value} → {stable_gesture_mode.value}")
            
            # 각 모드별 세부 제스처 감지
            gesture_actions = self._detect_gesture_actions(
                stable_gesture_mode, thumb_distance, current_time, finger_state, landmarks
            )
            
            # 기존 코드에서 gesture_mode, gesture_actions 등 생성 후
            # palm_center 좌표의 x값을 항상 좌우반전하여 반환
            gesture_data = GestureData(
                palm_center=[1.0 - palm_center[0], palm_center[1], palm_center[2]],  # x좌표 좌우반전
                gesture_mode=stable_gesture_mode,
                **gesture_actions
            )
            return gesture_data
            
        except Exception as e:
            logger.error(f"제스처 감지 중 오류: {e}")
            raise GestureError(f"제스처 감지 실패: {e}")
    
    def _get_finger_state(self, landmarks: list) -> FingerState:
        """손가락 상태 확인"""
        finger_threshold = self.config.get('finger_threshold', 0.02)
        
        # 각 손가락의 팁과 MCP 관절
        index_tip, index_mcp = landmarks[8], landmarks[5]
        middle_tip, middle_mcp = landmarks[12], landmarks[9]
        ring_tip, ring_mcp = landmarks[16], landmarks[13]
        pinky_tip, pinky_mcp = landmarks[20], landmarks[17]
        
        return FingerState(
            index_extended=index_tip[1] < (index_mcp[1] - finger_threshold),
            middle_extended=middle_tip[1] < (middle_mcp[1] - finger_threshold),
            ring_extended=ring_tip[1] < (ring_mcp[1] - finger_threshold),
            pinky_extended=pinky_tip[1] < (pinky_mcp[1] - finger_threshold)
        )
    
    def _get_thumb_distance(self, landmarks: list) -> ThumbDistance:
        """엄지-검지, 엄지-중지 거리 계산"""
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        middle_tip = landmarks[12]
        
        return ThumbDistance(
            thumb_index_distance=self._calculate_distance(thumb_tip, index_tip),
            thumb_middle_distance=self._calculate_distance(thumb_tip, middle_tip)
        )
    
    def _calculate_distance(self, point1: list, point2: list) -> float:
        """두 점 사이의 유클리드 거리 계산"""
        import numpy as np
        return np.sqrt(
            (point1[0] - point2[0])**2 + 
            (point1[1] - point2[1])**2 + 
            (point1[2] - point2[2])**2
        )
    
    def _add_to_history(self, stable_gesture_mode: GestureType, current_time: float, 
                       finger_state: FingerState) -> None:
        """히스토리에 현재 프레임 정보 추가"""
        current_gesture_info = {
            'mode': stable_gesture_mode.value,
            'timestamp': current_time,
            'finger_states': {
                'index_extended': finger_state.index_extended,
                'middle_extended': finger_state.middle_extended,
                'ring_extended': finger_state.ring_extended,
                'pinky_extended': finger_state.pinky_extended
            }
        }
        self.classifier.add_to_gesture_history(current_gesture_info)
    
    def _detect_gesture_actions(self, stable_gesture_mode: GestureType, 
                              thumb_distance: ThumbDistance, 
                              current_time: float, 
                              finger_state: FingerState,
                              landmarks: list) -> Dict[str, Any]:
        """각 모드별 세부 제스처 감지"""
        # 기본값 초기화
        actions = {
            'is_clicking': False,
            'is_right_clicking': False,
            'is_double_clicking': False,
            'is_scrolling': False,
            'is_swiping': False,
            'swipe_direction': "none",
            'scroll_direction': "none"
        }
        
        # 클릭 감지는 클릭 모드에서만 실행
        if stable_gesture_mode == GestureType.CLICK:
            click_actions = self.classifier.detect_click_actions(thumb_distance, current_time)
            actions.update(click_actions)
            logger.debug(f"클릭 감지 실행: 클릭 모드")
        else:
            logger.debug(f"클릭 감지 건너뜀: 클릭 모드가 아님 (현재 모드: {stable_gesture_mode.value})")
            # 클릭 모드가 아니면 클릭 상태 리셋
            self.classifier.reset_click_states()
        
        # 스크롤 모드 처리
        if stable_gesture_mode == GestureType.SCROLL:
            actions.update(self._handle_scroll_mode(landmarks))
        else:
            # 스크롤 모드가 아니면 스크롤 관련 변수 리셋
            self._reset_scroll_variables()
        
        # 스와이프 모드 처리
        if stable_gesture_mode == GestureType.SWIPE:
            swipe_actions = self._handle_swipe_mode(landmarks, current_time)
            actions.update(swipe_actions)
        else:
            # 스와이프 모드가 아니면 스와이프 관련 변수 리셋
            self._reset_swipe_variables()
        
        return actions
    
    def _handle_scroll_mode(self, landmarks: list) -> Dict[str, Any]:
        """스크롤 모드 처리"""
        palm_center = landmarks[9]
        
        if self.scroll_palm_position is None:
            # 첫 번째 프레임이면 현재 위치 저장
            self.scroll_palm_position = palm_center
            self.scroll_direction_history = []
            self.scroll_frame_count = 0
            return {'is_scrolling': False, 'scroll_direction': "none"}
        
        # 이전 프레임과 현재 프레임 비교
        delta_x = palm_center[0] - self.scroll_palm_position[0]
        delta_y = palm_center[1] - self.scroll_palm_position[1]
        
        # 스크롤 반전 적용
        if self.config.get('invert_scroll_x', False):
            delta_x = -delta_x
        if self.config.get('invert_scroll_y', False):
            delta_y = -delta_y
        
        # 스크롤 임계값
        min_scroll_distance = self.config.get('scroll_distance_threshold', 0.003)
        required_frames = self.config.get('scroll_required_frames', 1)
        
        # 현재 프레임의 이동 방향 결정
        current_direction = self._get_movement_direction(delta_x, delta_y, min_scroll_distance)
        
        # 방향 히스토리에 추가
        if current_direction:
            self.scroll_direction_history.append(current_direction)
            self.scroll_frame_count += 1
            
            # 최근 N프레임만 유지
            if len(self.scroll_direction_history) > required_frames:
                self.scroll_direction_history.pop(0)
            
            # 스크롤 조건 확인: 같은 방향으로 N프레임 연속 이동
            if (len(self.scroll_direction_history) == required_frames and 
                len(set(self.scroll_direction_history)) == 1):
                # 모든 프레임이 같은 방향이면 스크롤 실행
                scroll_direction = self.scroll_direction_history[0]
                logger.info(f"스크롤 감지 성공: 방향={scroll_direction}, 연속프레임={self.scroll_frame_count}, 히스토리={self.scroll_direction_history}")
                
                # 스크롤 감지 후 초기화
                self.scroll_palm_position = None
                self.scroll_direction_history = []
                self.scroll_frame_count = 0
                
                return {'is_scrolling': True, 'scroll_direction': scroll_direction}
        else:
            # 이동이 없으면 히스토리 초기화
            self.scroll_direction_history = []
            self.scroll_frame_count = 0
        
        # 다음 프레임을 위해 현재 위치 저장
        self.scroll_palm_position = palm_center
        return {'is_scrolling': False, 'scroll_direction': "none"}
    
    def _handle_swipe_mode(self, landmarks: list, current_time: float) -> Dict[str, Any]:
        """스와이프 모드 처리"""
        # 스와이프 쿨타임 확인
        swipe_cooldown = self.config.get('swipe_cooldown', 0.5)
        if self.is_swipe_cooldown:
            cooldown_remaining = swipe_cooldown - (current_time - self.last_swipe_time)
            if cooldown_remaining > 0:
                logger.debug(f"스와이프 쿨타임 중: {cooldown_remaining:.1f}초 남음")
                return {'is_swiping': False, 'swipe_direction': "none"}
            else:
                self.is_swipe_cooldown = False
                logger.debug("스와이프 쿨타임 종료")
        
        palm_center = landmarks[9]
        
        if self.swipe_palm_position is None:
            # 첫 번째 프레임이면 현재 위치 저장
            self.swipe_palm_position = palm_center
            self.swipe_direction_history = []
            self.swipe_frame_count = 0
            return {'is_swiping': False, 'swipe_direction': "none"}
        
        # 이전 프레임과 현재 프레임 비교
        delta_x = palm_center[0] - self.swipe_palm_position[0]
        delta_y = palm_center[1] - self.swipe_palm_position[1]
        
        # 스와이프 반전 적용
        if self.config.get('invert_swipe_x', False):
            delta_x = -delta_x
        if self.config.get('invert_swipe_y', False):
            delta_y = -delta_y
        
        # 스와이프 임계값
        min_swipe_distance = self.config.get('swipe_distance_threshold', 0.008)
        required_frames = self.config.get('swipe_required_frames', 3)
        
        # 현재 프레임의 이동 방향 결정
        current_direction = self._get_movement_direction(delta_x, delta_y, min_swipe_distance)
        
        # 방향 히스토리에 추가
        if current_direction:
            self.swipe_direction_history.append(current_direction)
            self.swipe_frame_count += 1
            
            # 최근 N프레임만 유지
            if len(self.swipe_direction_history) > required_frames:
                self.swipe_direction_history.pop(0)
            
            # 스와이프 조건 확인: 같은 방향으로 N프레임 연속 이동
            if (len(self.swipe_direction_history) == required_frames and 
                len(set(self.swipe_direction_history)) == 1):
                # 모든 프레임이 같은 방향이면 스와이프 실행
                swipe_direction = self.swipe_direction_history[0]
                logger.debug(f"스와이프 감지: 방향={swipe_direction}, 연속프레임={self.swipe_frame_count}")
                
                # 스와이프 쿨타임 시작
                self.last_swipe_time = current_time
                self.is_swipe_cooldown = True
                logger.debug(f"스와이프 쿨타임 시작: {swipe_cooldown}초")
                
                # 스와이프 감지 후 방향 히스토리만 초기화 (위치는 유지)
                self.swipe_direction_history = []
                self.swipe_frame_count = 0
                
                return {'is_swiping': True, 'swipe_direction': swipe_direction}
        else:
            # 이동이 없으면 히스토리 초기화
            self.swipe_direction_history = []
            self.swipe_frame_count = 0
        
        # 다음 프레임을 위해 현재 위치 저장
        self.swipe_palm_position = palm_center
        return {'is_swiping': False, 'swipe_direction': "none"}
    
    def _get_movement_direction(self, delta_x: float, delta_y: float, min_distance: float) -> Optional[str]:
        """이동 방향 결정"""
        if abs(delta_x) > abs(delta_y) and abs(delta_x) > min_distance:
            return "right" if delta_x > 0 else "left"
        elif abs(delta_y) > min_distance:
            return "up" if delta_y < 0 else "down"
        return None
    
    def _reset_scroll_variables(self) -> None:
        """스크롤 관련 변수 리셋"""
        if self.scroll_palm_position is not None:
            logger.debug("스크롤 모드 종료, 위치 리셋")
        self.scroll_palm_position = None
        self.scroll_direction_history = []
        self.scroll_frame_count = 0
    
    def _reset_swipe_variables(self) -> None:
        """스와이프 관련 변수 리셋"""
        if self.swipe_palm_position is not None:
            logger.debug("스와이프 모드 종료, 위치 리셋")
        self.swipe_palm_position = None
        self.swipe_direction_history = []
        self.swipe_frame_count = 0
    
    def update_config(self, config: dict) -> None:
        """설정 업데이트"""
        self.config = config
        self.classifier.update_config(config)
        logger.info("제스처 감지기 설정이 업데이트되었습니다.") 