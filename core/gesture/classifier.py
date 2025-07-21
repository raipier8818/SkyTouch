"""
Gesture classifier for Hand Tracking Trackpad application.
"""
import time
from typing import Dict, Any

from .types import GestureType, FingerState, ThumbDistance
from utils.logging.logger import get_logger

logger = get_logger(__name__)


class GestureClassifier:
    """제스처 분류기 클래스"""
    
    def __init__(self, config: dict):
        """
        제스처 분류기 초기화
        
        Args:
            config: 제스처 설정
        """
        self.config = config
        self.finger_threshold = config.get('finger_threshold', 0.02)
        self.click_threshold = config.get('click_threshold', 0.12)
        
        # 제스처 히스토리
        self.gesture_history = []
        self.max_history_size = 3
        
        # 모드 안정화 변수들
        self.current_gesture_mode = GestureType.CLICK.value
        self.mode_start_time = 0.0
        self.is_mode_stable = False
        
        # 클릭 상태 추적 변수들
        self.thumb_index_touching = False
        self.thumb_middle_touching = False
        self.last_click_time = 0.0
        self.click_count = 0
        
        logger.info("제스처 분류기가 초기화되었습니다.")
    
    def classify_gesture(self, finger_state: FingerState, thumb_distance: ThumbDistance) -> GestureType:
        """
        손가락 상태와 엄지 거리를 기반으로 제스처 분류
        
        Args:
            finger_state: 손가락 상태
            thumb_distance: 엄지 거리
            
        Returns:
            제스처 타입
        """
        # 클릭 모드: 새끼손가락이 펴진 상태 (다른 손가락은 상관없음)
        if (finger_state.pinky_extended):
            return GestureType.CLICK
        
        # 스와이프 모드: 주먹 (모든 손가락을 접은 상태)
        elif not any([finger_state.index_extended, finger_state.middle_extended, 
                     finger_state.ring_extended, finger_state.pinky_extended]):
            return GestureType.SWIPE
        
        # 스크롤 모드: 검지와 중지를 펴진 상태 (엄격한 조건)
        elif (finger_state.index_extended and finger_state.middle_extended and 
              not finger_state.ring_extended and not finger_state.pinky_extended):
            # 중지가 손바닥에 닿지 않았는지 추가 확인
            if thumb_distance.thumb_middle_distance > self.click_threshold:
                logger.debug("스크롤 모드 감지: 검지+중지 펴짐, 중지 터치 없음")
                return GestureType.SCROLL
            else:
                logger.debug("중지가 손바닥에 닿아서 스크롤 모드 무효화")
                # 중지가 닿으면 클릭 모드로 처리
                return GestureType.CLICK
        
        # 이동 모드: 검지만 편 상태
        elif (finger_state.index_extended and not finger_state.middle_extended and 
              not finger_state.ring_extended and not finger_state.pinky_extended):
            return GestureType.MOVE
        
        return GestureType.CLICK  # 기본값
    
    def get_stable_gesture_mode(self, current_mode: GestureType) -> GestureType:
        """히스토리를 바탕으로 안정적인 제스처 모드 결정"""
        # 스크롤 모드는 히스토리 사용 안함 (즉시 반응)
        if current_mode == GestureType.SCROLL:
            return current_mode
        
        if len(self.gesture_history) < 3:
            return current_mode
        
        # 최근 3프레임의 모드 확인
        recent_modes = [gesture['mode'] for gesture in self.gesture_history[-3:]]
        
        # 3프레임 동안 들어온 모드가 히스토리와 다 다르면 모드 변경
        if current_mode.value not in recent_modes:
            logger.debug(f"제스처 모드 변경: 3프레임 연속 {current_mode.value} 감지")
            return current_mode
        else:
            # 히스토리와 일치하면 현재 모드 유지
            return current_mode
    
    def add_to_gesture_history(self, gesture_info: dict) -> None:
        """제스처 히스토리에 현재 프레임 정보 추가"""
        self.gesture_history.append(gesture_info)
        
        # 히스토리 크기 제한
        if len(self.gesture_history) > self.max_history_size:
            self.gesture_history.pop(0)
    
    def handle_mode_change(self, gesture_mode: GestureType) -> None:
        """모드 변경 처리"""
        if gesture_mode.value != self.current_gesture_mode:
            # 클릭 모드로 진입할 때 로그
            if gesture_mode == GestureType.CLICK:
                logger.debug("클릭 모드 진입")
            
            self.gesture_history.clear()
            self.current_gesture_mode = gesture_mode.value
            self.is_mode_stable = True
            logger.debug(f"모드 변경: {gesture_mode.value} (히스토리 초기화, 즉시 안정화)")
    
    def detect_click_actions(self, thumb_distance: ThumbDistance, current_time: float) -> Dict[str, bool]:
        """클릭 감지 (클릭 모드에서만 실행)"""
        actions = {
            'is_clicking': False,
            'is_right_clicking': False,
            'is_double_clicking': False
        }
        
        # 엄지-검지 클릭 감지 (클릭 모드에서만)
        if thumb_distance.thumb_index_distance < self.click_threshold:
            # 손가락이 닿음
            if not self.thumb_index_touching:
                logger.debug(f"엄지-검지 터치 시작 (거리: {thumb_distance.thumb_index_distance:.3f})")
            self.thumb_index_touching = True
        else:
            # 손가락이 떨어짐
            if self.thumb_index_touching:
                # 터치가 끝났으므로 클릭 실행
                actions['is_clicking'] = True
                logger.debug(f"좌클릭 실행: 엄지-검지 떼어짐 (거리: {thumb_distance.thumb_index_distance:.3f})")
                
                # 더블클릭 감지
                if current_time - self.last_click_time < 0.5:
                    self.click_count += 1
                    if self.click_count >= 2:
                        actions['is_double_clicking'] = True
                        self.click_count = 0
                        logger.debug("더블클릭 감지!")
                else:
                    self.click_count = 1
                
                self.last_click_time = current_time
            
            self.thumb_index_touching = False
        
        # 엄지-중지 우클릭 감지 (클릭 모드에서만)
        if thumb_distance.thumb_middle_distance < self.click_threshold:
            # 손가락이 닿음
            if not self.thumb_middle_touching:
                logger.debug(f"엄지-중지 터치 시작 (거리: {thumb_distance.thumb_middle_distance:.3f})")
            self.thumb_middle_touching = True
        else:
            # 손가락이 떨어짐
            if self.thumb_middle_touching:
                # 터치가 끝났으므로 우클릭 실행
                actions['is_right_clicking'] = True
                logger.debug(f"우클릭 실행: 엄지-중지 떼어짐 (거리: {thumb_distance.thumb_middle_distance:.3f})")
            
            self.thumb_middle_touching = False
        
        return actions
    
    def reset_click_states(self) -> None:
        """클릭 상태 리셋"""
        self.thumb_index_touching = False
        self.thumb_middle_touching = False
    
    def update_config(self, config: dict) -> None:
        """설정 업데이트"""
        self.config = config
        self.finger_threshold = config.get('finger_threshold', 0.02)
        self.click_threshold = config.get('click_threshold', 0.12)
        logger.info("제스처 분류기 설정이 업데이트되었습니다.") 