"""
Core hand tracking functionality using MediaPipe.
"""
import cv2
import mediapipe as mp
import numpy as np
import time
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass

from ..config import config
from ..utils.logger import get_logger
from ..utils.exceptions import HandTrackingError, CameraError, GestureError

logger = get_logger(__name__)


@dataclass
class HandLandmarks:
    """손 랜드마크 데이터 클래스"""
    landmarks: List[List[float]]
    handedness: str
    confidence: float


@dataclass
class GestureData:
    """제스처 데이터 클래스"""
    palm_center: List[float]
    gesture_mode: str  # "click", "stop", "scroll", "swipe", "move"
    is_clicking: bool  # 클릭 모드에서 클릭
    is_right_clicking: bool  # 클릭 모드에서 우클릭
    is_double_clicking: bool  # 더블클릭
    is_scrolling: bool  # 스크롤 모드에서 스크롤
    is_swiping: bool  # 스와이프 모드에서 스와이프
    swipe_direction: str  # "left", "right", "up", "down", "none"
    scroll_direction: str  # "up", "down", "left", "right", "none"


class HandTracker:
    """MediaPipe를 사용한 손 트래킹 클래스"""
    
    def __init__(self):
        """손 트래커 초기화"""
        try:
            self._init_mediapipe()
            self._init_camera()
            self._init_gesture_variables()
            logger.info("손 트래커가 성공적으로 초기화되었습니다.")
            
        except Exception as e:
            logger.error(f"손 트래커 초기화 실패: {e}")
            raise HandTrackingError(f"손 트래커 초기화 실패: {e}")
    
    def _init_mediapipe(self) -> None:
        """MediaPipe 초기화"""
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=config.hand_tracking.static_image_mode,
            max_num_hands=config.hand_tracking.max_num_hands,
            min_detection_confidence=config.hand_tracking.min_detection_confidence,
            min_tracking_confidence=config.hand_tracking.min_tracking_confidence
        )
        self.mp_draw = mp.solutions.drawing_utils
            
    def _init_camera(self) -> None:
        """카메라 초기화"""
        self.cap = cv2.VideoCapture(config.camera.device_id)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.camera.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.camera.height)
        self.cap.set(cv2.CAP_PROP_FPS, config.camera.fps)
        
        if not self.cap.isOpened():
            raise CameraError("카메라를 열 수 없습니다.")
            
    def _init_gesture_variables(self) -> None:
        """제스처 관련 변수 초기화"""
        # 제스처 시간 추적 변수들
        self.last_swipe_position = None
        self.swipe_start_time = 0.0
        self.last_palm_position = None
        self.scroll_start_time = 0.0
        
        # 스와이프 쿨타임 변수
        self.last_swipe_time = 0.0
        self.is_swipe_cooldown = False
        
        # 모드 안정화 변수들
        self.current_gesture_mode = "stop"
        self.mode_start_time = 0.0
        self.is_mode_stable = False
        
        # 제스처 히스토리 시스템
        self.gesture_history = []
        self.max_history_size = 3  # 최근 3프레임 저장
            
        # 더블클릭 추적 변수들
        self.last_click_time = 0.0
        self.click_count = 0
        
        # 클릭 상태 추적 변수들 (새로 작성)
        self.thumb_index_touching = False  # 엄지-검지 터치 상태
        self.thumb_middle_touching = False  # 엄지-중지 터치 상태
    
    def get_actual_camera_resolution(self) -> tuple[int, int]:
        """실제 웹캠 해상도를 가져옴"""
        try:
            if self.cap and self.cap.isOpened():
                actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                logger.debug(f"실제 웹캠 해상도: {actual_width}x{actual_height}")
                return (actual_width, actual_height)
            else:
                logger.warning("카메라가 열려있지 않아 설정된 해상도를 반환합니다.")
                return (config.camera.width, config.camera.height)
        except Exception as e:
            logger.error(f"실제 웹캠 해상도 가져오기 실패: {e}")
            return (config.camera.width, config.camera.height)
    
    def process_frame(self, frame: np.ndarray) -> Optional[List[HandLandmarks]]:
        """프레임에서 손 랜드마크 감지"""
        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)
            
            if not results.multi_hand_landmarks:
                return None
            
            hand_landmarks_list = []
            
            for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
                landmarks = self._extract_landmarks(hand_landmarks)
                handedness = self._get_handedness(results, i)
                confidence = self._get_confidence(results, i)
                
                hand_landmarks_list.append(HandLandmarks(
                    landmarks=landmarks,
                    handedness=handedness,
                    confidence=confidence
                ))
            
            return hand_landmarks_list
            
        except Exception as e:
            logger.error(f"프레임 처리 중 오류: {e}")
            return None
    
    def _extract_landmarks(self, hand_landmarks) -> List[List[float]]:
        """랜드마크 좌표 추출"""
        return [[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark]
    
    def _get_handedness(self, results, index: int) -> str:
        """손 방향 확인"""
        if results.multi_handedness:
            return results.multi_handedness[index].classification[0].label
        return "Unknown"
    
    def _get_confidence(self, results, index: int) -> float:
        """신뢰도 계산"""
        if results.multi_handedness:
            return results.multi_handedness[index].classification[0].score
        return 0.0
    
    def draw_landmarks(self, frame: np.ndarray, hand_landmarks: HandLandmarks) -> np.ndarray:
        """손 랜드마크를 프레임에 그리기"""
        try:
            height, width = frame.shape[:2]
            landmarks = hand_landmarks.landmarks
            
            # 손 방향에 따른 색상 설정
            color = (0, 255, 0) if hand_landmarks.handedness == "Right" else (255, 0, 0)
            
            # 랜드마크 포인트 그리기
            self._draw_landmark_points(frame, landmarks, color, width, height)
            
            # 손가락 연결선 그리기
            self._draw_connections(frame, landmarks, color, width, height)
            
            # 손바닥 중심점 강조
            self._draw_palm_center(frame, landmarks, width, height)
            
            return frame
            
        except Exception as e:
            logger.error(f"랜드마크 그리기 중 오류: {e}")
            return frame
    
    def _draw_landmark_points(self, frame: np.ndarray, landmarks: List[List[float]], 
                            color: Tuple[int, int, int], width: int, height: int) -> None:
        """랜드마크 포인트 그리기"""
        for i, landmark in enumerate(landmarks):
            x = int(landmark[0] * width)
            y = int(landmark[1] * height)
            
        # 랜드마크 포인트 크기 설정
            if i in [4, 8, 12, 16, 20]:  # 손가락 팁
                radius = 8
            elif i in [3, 7, 11, 15, 19]:  # 손가락 PIP
                radius = 6
            elif i in [2, 6, 10, 14, 18]:  # 손가락 DIP
                radius = 5
            else:  # 기타 포인트
                radius = 4
            
            cv2.circle(frame, (x, y), radius, color, -1)
            cv2.circle(frame, (x, y), radius, (255, 255, 255), 1)  # 흰색 테두리
            
    def _draw_connections(self, frame: np.ndarray, landmarks: List[List[float]], 
                         color: Tuple[int, int, int], width: int, height: int) -> None:
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
                if start_idx < len(landmarks) and end_idx < len(landmarks):
                    start_point = (
                        int(landmarks[start_idx][0] * width),
                        int(landmarks[start_idx][1] * height)
                    )
                    end_point = (
                        int(landmarks[end_idx][0] * width),
                        int(landmarks[end_idx][1] * height)
                    )
                    
                    cv2.line(frame, start_point, end_point, color, 2)
            
    def _draw_palm_center(self, frame: np.ndarray, landmarks: List[List[float]], 
                         width: int, height: int) -> None:
        """손바닥 중심점 강조"""
        palm_center = landmarks[9]  # 중지 MCP
        palm_x = int(palm_center[0] * width)
        palm_y = int(palm_center[1] * height)
        cv2.circle(frame, (palm_x, palm_y), 12, (0, 255, 255), -1)  # 노란색
        cv2.circle(frame, (palm_x, palm_y), 12, (255, 255, 255), 2)  # 흰색 테두리
    
    def calculate_distance(self, point1: List[float], point2: List[float]) -> float:
        """두 점 사이의 유클리드 거리 계산"""
        return np.sqrt(
            (point1[0] - point2[0])**2 + 
            (point1[1] - point2[1])**2 + 
            (point1[2] - point2[2])**2
        )
    
    def add_to_gesture_history(self, gesture_info: dict) -> None:
        """제스처 히스토리에 현재 프레임 정보 추가"""
        self.gesture_history.append(gesture_info)
        
        # 히스토리 크기 제한
        if len(self.gesture_history) > self.max_history_size:
            self.gesture_history.pop(0)
    
    def get_stable_gesture_mode(self, current_mode: str) -> str:
        """히스토리를 바탕으로 안정적인 제스처 모드 결정"""
        # 스크롤 모드는 히스토리 사용 안함 (즉시 반응)
        if current_mode == "scroll":
            return current_mode
        
        if len(self.gesture_history) < 3:
            return current_mode
        
        # 최근 3프레임의 모드 확인
        recent_modes = [gesture['mode'] for gesture in self.gesture_history[-3:]]
        
        # 3프레임 동안 들어온 모드가 히스토리와 다 다르면 모드 변경
        if current_mode not in recent_modes:
            logger.debug(f"제스처 모드 변경: 3프레임 연속 {current_mode} 감지")
            return current_mode
        else:
            # 히스토리와 일치하면 현재 모드 유지
            return current_mode
    
    def detect_gestures(self, hand_landmarks: HandLandmarks) -> GestureData:
        """손 랜드마크에서 제스처 감지"""
        try:
            current_time = time.time()
            landmarks = hand_landmarks.landmarks
            
            # 현재 랜드마크 저장 (스크롤/스와이프 모드에서 사용)
            self.current_landmarks = landmarks
            
            # 기본 정보 추출
            palm_center = landmarks[9]
            finger_states = self._get_finger_states(landmarks)
            thumb_distances = self._get_thumb_distances(landmarks)
            
            # 제스처 모드 감지
            gesture_mode = self._detect_gesture_mode(finger_states, thumb_distances)
            
            # 모드 변경 처리
            self._handle_mode_change(gesture_mode)
            
            # 히스토리 기반 안정화된 제스처 모드 결정
            stable_gesture_mode = self.get_stable_gesture_mode(gesture_mode)
            
            # 히스토리에 추가
            self._add_to_history(stable_gesture_mode, current_time, finger_states)
            
            logger.debug(f"제스처 모드: {gesture_mode} → {stable_gesture_mode} (안정화: {self.is_mode_stable})")
            
            # 각 모드별 세부 제스처 감지
            gesture_actions = self._detect_gesture_actions(
                stable_gesture_mode, thumb_distances, current_time, finger_states
            )
            
            return GestureData(
                palm_center=palm_center,
                gesture_mode=stable_gesture_mode,
                **gesture_actions
            )
            
        except Exception as e:
            logger.error(f"제스처 감지 중 오류: {e}")
            raise GestureError(f"제스처 감지 실패: {e}")
    
    def _get_finger_states(self, landmarks: List[List[float]]) -> Dict[str, bool]:
        """손가락 상태 확인"""
        finger_threshold = config.gesture.finger_threshold
        
        # 각 손가락의 팁과 MCP 관절
        index_tip, index_mcp = landmarks[8], landmarks[5]
        middle_tip, middle_mcp = landmarks[12], landmarks[9]
        ring_tip, ring_mcp = landmarks[16], landmarks[13]
        pinky_tip, pinky_mcp = landmarks[20], landmarks[17]
        
        return {
            'index_extended': index_tip[1] < (index_mcp[1] - finger_threshold),
            'middle_extended': middle_tip[1] < (middle_mcp[1] - finger_threshold),
            'ring_extended': ring_tip[1] < (ring_mcp[1] - finger_threshold),
            'pinky_extended': pinky_tip[1] < (pinky_mcp[1] - finger_threshold)
        }
    
    def _get_thumb_distances(self, landmarks: List[List[float]]) -> Dict[str, float]:
        """엄지-검지, 엄지-중지 거리 계산"""
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        middle_tip = landmarks[12]
        
        return {
            'thumb_index_distance': self.calculate_distance(thumb_tip, index_tip),
            'thumb_middle_distance': self.calculate_distance(thumb_tip, middle_tip)
        }
    
    def _detect_gesture_mode(self, finger_states: Dict[str, bool], 
                           thumb_distances: Dict[str, float]) -> str:
        """제스처 모드 감지"""
        # 클릭 모드: 엄지와 검지 또는 엄지와 중지가 닿은 상태 + 약지와 새끼손가락이 펴져 있어야 함
        ring_pinky_extended = finger_states['ring_extended'] and finger_states['pinky_extended']
        if ((thumb_distances['thumb_index_distance'] < config.gesture.click_threshold or 
             thumb_distances['thumb_middle_distance'] < config.gesture.click_threshold) and 
            ring_pinky_extended):
            logger.debug(f"클릭 모드 감지: 엄지-검지={thumb_distances['thumb_index_distance']:.3f}, 엄지-중지={thumb_distances['thumb_middle_distance']:.3f}, 약지/새끼 펴짐: {ring_pinky_extended}")
            return "click"
        
        # 정지 모드: 모든 손가락을 편 상태
        elif all(finger_states.values()):
            return "stop"
        
        # 스와이프 모드: 주먹 (모든 손가락을 접은 상태)
        elif not any(finger_states.values()):
            return "swipe"
        
        # 스크롤 모드: 검지와 중지를 펴진 상태
        elif (finger_states['index_extended'] and finger_states['middle_extended'] and 
              not finger_states['ring_extended'] and not finger_states['pinky_extended']):
            return "scroll"
        
        # 이동 모드: 검지만 편 상태
        elif (finger_states['index_extended'] and not finger_states['middle_extended'] and 
              not finger_states['ring_extended'] and not finger_states['pinky_extended']):
            return "move"
        
        return "stop"  # 기본값
    
    def _handle_mode_change(self, gesture_mode: str) -> None:
        """모드 변경 처리"""
        if gesture_mode != self.current_gesture_mode:
            # 클릭 모드로 진입할 때 로그
            if gesture_mode == "click":
                logger.debug("클릭 모드 진입")
            
            self.gesture_history.clear()
            self.current_gesture_mode = gesture_mode
            self.is_mode_stable = True
            logger.debug(f"모드 변경: {gesture_mode} (히스토리 초기화, 즉시 안정화)")
    
    def _add_to_history(self, stable_gesture_mode: str, current_time: float, 
                       finger_states: Dict[str, bool]) -> None:
        """히스토리에 현재 프레임 정보 추가"""
        current_gesture_info = {
            'mode': stable_gesture_mode,
            'timestamp': current_time,
            'finger_states': finger_states
        }
        self.add_to_gesture_history(current_gesture_info)
    
    def _detect_gesture_actions(self, stable_gesture_mode: str, 
                              thumb_distances: Dict[str, float], 
                              current_time: float, finger_states: Dict[str, bool] = None) -> Dict[str, Any]:
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
        
        # 클릭 모드에서만 클릭 감지 실행
        if stable_gesture_mode == "click":
            click_actions = self._handle_click_detection(thumb_distances, current_time, finger_states)
            actions.update(click_actions)
            logger.debug(f"클릭 모드 처리 시작 (안정화: {self.is_mode_stable})")
            logger.debug(f"클릭 모드 - 엄지-검지 거리: {thumb_distances['thumb_index_distance']:.3f}, 임계값: {config.gesture.click_threshold:.3f}")
            logger.debug(f"클릭 모드 - 엄지-중지 거리: {thumb_distances['thumb_middle_distance']:.3f}, 임계값: {config.gesture.click_threshold:.3f}")
            logger.debug(f"클릭 모드 처리 완료: {actions}")
        else:
            logger.debug(f"클릭 모드 처리 건너뜀: 모드={stable_gesture_mode}")
            # 클릭 모드가 아니면 클릭 상태 리셋
            self._reset_click_states()
        
        # 스크롤 모드 처리
        if stable_gesture_mode == "scroll" and self.is_mode_stable:
            actions.update(self._handle_scroll_mode())
        else:
            # 스크롤 모드가 아니면 스크롤 관련 변수 리셋
            self._reset_scroll_variables()
        
        # 스와이프 모드 처리
        if stable_gesture_mode == "swipe" and self.is_mode_stable:
            swipe_actions = self._handle_swipe_mode(current_time)
            actions.update(swipe_actions)
            
            # 스와이프가 실행되었으면 로그만 출력 (상태는 유지)
            if swipe_actions['is_swiping']:
                logger.debug("스와이프 실행됨 - 다음 스와이프 준비")
        else:
            # 스와이프 모드가 아니면 스와이프 관련 변수 리셋
            self._reset_swipe_variables()
        
        return actions
    
    def _handle_click_detection(self, thumb_distances: Dict[str, float], 
                              current_time: float, finger_states: Dict[str, bool] = None) -> Dict[str, Any]:
        """클릭 감지 (모드와 관계없이 실행)"""
        actions = {
            'is_clicking': False,
            'is_right_clicking': False,
            'is_double_clicking': False
        }
        
        # 손가락 상태가 제공되지 않으면 기본값 설정
        if finger_states is None:
            finger_states = {
                'index_extended': True,
                'middle_extended': True,
                'ring_extended': True,
                'pinky_extended': True
            }
        
        # 약지와 새끼손가락이 펴져 있는지 확인
        ring_pinky_extended = finger_states['ring_extended'] and finger_states['pinky_extended']
        
        # 엄지-검지 클릭 감지 (약지, 새끼손가락이 펴져 있어야 함)
        if thumb_distances['thumb_index_distance'] < config.gesture.click_threshold:
            # 손가락이 닿음
            if not self.thumb_index_touching:
                logger.debug(f"엄지-검지 터치 시작 (거리: {thumb_distances['thumb_index_distance']:.3f})")
            self.thumb_index_touching = True
        else:
            # 손가락이 떨어짐
            if self.thumb_index_touching:
                # 약지와 새끼손가락이 펴져 있는지 확인
                if ring_pinky_extended:
                    # 터치가 끝났으므로 클릭 실행
                    actions['is_clicking'] = True
                    logger.debug(f"좌클릭 실행: 엄지-검지 떼어짐 (거리: {thumb_distances['thumb_index_distance']:.3f}, 약지/새끼 펴짐: {ring_pinky_extended})")
                    
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
                else:
                    logger.debug(f"좌클릭 무시: 약지/새끼손가락이 접혀있음 (약지: {finger_states['ring_extended']}, 새끼: {finger_states['pinky_extended']})")
            
            self.thumb_index_touching = False
        
        # 엄지-중지 우클릭 감지 (약지, 새끼손가락이 펴져 있어야 함)
        if thumb_distances['thumb_middle_distance'] < config.gesture.click_threshold:
            # 손가락이 닿음
            if not self.thumb_middle_touching:
                logger.debug(f"엄지-중지 터치 시작 (거리: {thumb_distances['thumb_middle_distance']:.3f})")
            self.thumb_middle_touching = True
        else:
            # 손가락이 떨어짐
            if self.thumb_middle_touching:
                # 약지와 새끼손가락이 펴져 있는지 확인
                if ring_pinky_extended:
                    # 터치가 끝났으므로 우클릭 실행
                    actions['is_right_clicking'] = True
                    logger.debug(f"우클릭 실행: 엄지-중지 떼어짐 (거리: {thumb_distances['thumb_middle_distance']:.3f}, 약지/새끼 펴짐: {ring_pinky_extended})")
                else:
                    logger.debug(f"우클릭 무시: 약지/새끼손가락이 접혀있음 (약지: {finger_states['ring_extended']}, 새끼: {finger_states['pinky_extended']})")
            
            self.thumb_middle_touching = False
        
        return actions
    
    def _reset_click_states(self) -> None:
        """클릭 상태 리셋"""
        self.thumb_index_touching = False
        self.thumb_middle_touching = False
    
    def _reset_scroll_variables(self) -> None:
        """스크롤 관련 변수 리셋"""
        if hasattr(self, 'scroll_palm_position') and self.scroll_palm_position is not None:
            logger.debug("스크롤 모드 종료, 위치 리셋")
        self.scroll_palm_position = None
        if hasattr(self, 'scroll_direction_history'):
            self.scroll_direction_history = []
        if hasattr(self, 'scroll_frame_count'):
            self.scroll_frame_count = 0
    
    def _reset_swipe_variables(self) -> None:
        """스와이프 관련 변수 리셋"""
        if hasattr(self, 'swipe_palm_position') and self.swipe_palm_position is not None:
            logger.debug("스와이프 모드 종료, 위치 리셋")
        self.swipe_palm_position = None
        if hasattr(self, 'swipe_direction_history'):
            self.swipe_direction_history = []
        if hasattr(self, 'swipe_frame_count'):
            self.swipe_frame_count = 0
    
    def _handle_scroll_mode(self) -> Dict[str, Any]:
        """스크롤 모드 처리"""
        landmarks = self.current_landmarks
        palm_center = landmarks[9]
        
        if not hasattr(self, 'scroll_palm_position') or self.scroll_palm_position is None:
            # 첫 번째 프레임이면 현재 위치 저장
            self.scroll_palm_position = palm_center
            self.scroll_direction_history = []
            self.scroll_frame_count = 0
            return {'is_scrolling': False, 'scroll_direction': "none"}
        
        # 이전 프레임과 현재 프레임 비교
        delta_x = palm_center[0] - self.scroll_palm_position[0]
        delta_y = palm_center[1] - self.scroll_palm_position[1]
        
        # 스크롤 반전 적용
        if config.gesture.invert_scroll_x:
            delta_x = -delta_x
        if config.gesture.invert_scroll_y:
            delta_y = -delta_y
        
        # 스크롤 임계값
        min_scroll_distance = config.gesture.scroll_distance_threshold
        required_frames = config.gesture.scroll_required_frames
        
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
                logger.debug(f"스크롤 감지: 방향={scroll_direction}, 연속프레임={self.scroll_frame_count}, 변화=({delta_x:.3f}, {delta_y:.3f})")
                
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
    
    def _handle_swipe_mode(self, current_time: float) -> Dict[str, Any]:
        """스와이프 모드 처리"""
        # 스와이프 쿨타임 확인
        if self.is_swipe_cooldown:
            cooldown_remaining = config.gesture.swipe_cooldown - (current_time - self.last_swipe_time)
            if cooldown_remaining > 0:
                logger.debug(f"스와이프 쿨타임 중: {cooldown_remaining:.1f}초 남음")
                return {'is_swiping': False, 'swipe_direction': "none"}
            else:
                self.is_swipe_cooldown = False
                logger.debug("스와이프 쿨타임 종료")
        
        landmarks = self.current_landmarks
        palm_center = landmarks[9]
        
        if not hasattr(self, 'swipe_palm_position') or self.swipe_palm_position is None:
            # 첫 번째 프레임이면 현재 위치 저장
            self.swipe_palm_position = palm_center
            self.swipe_direction_history = []
            self.swipe_frame_count = 0
            return {'is_swiping': False, 'swipe_direction': "none"}
        
        # 이전 프레임과 현재 프레임 비교
        delta_x = palm_center[0] - self.swipe_palm_position[0]
        delta_y = palm_center[1] - self.swipe_palm_position[1]
        
        # 스와이프 반전 적용
        if config.gesture.invert_swipe_x:
            delta_x = -delta_x
        if config.gesture.invert_swipe_y:
            delta_y = -delta_y
        
        # 스와이프 임계값
        min_swipe_distance = config.gesture.swipe_distance_threshold
        required_frames = config.gesture.swipe_required_frames
        
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
                logger.debug(f"스와이프 감지: 방향={swipe_direction}, 연속프레임={self.swipe_frame_count}, 변화=({delta_x:.3f}, {delta_y:.3f})")
                
                # 스와이프 쿨타임 시작
                self.last_swipe_time = current_time
                self.is_swipe_cooldown = True
                logger.debug(f"스와이프 쿨타임 시작: {config.gesture.swipe_cooldown}초")
                
                # 스와이프 감지 후 방향 히스토리만 초기화 (위치는 유지)
                self.swipe_direction_history = []
                self.swipe_frame_count = 0
                
                # 스와이프 상태를 즉시 False로 설정하여 연속 실행 방지
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
    
    def get_frame(self) -> Optional[np.ndarray]:
        """카메라에서 프레임 가져오기"""
        try:
            ret, frame = self.cap.read()
            if not ret:
                logger.warning("카메라에서 프레임을 읽을 수 없습니다.")
                return None
            return frame
            
        except Exception as e:
            logger.error(f"프레임 가져오기 중 오류: {e}")
            return None
    
    def release(self) -> None:
        """리소스 해제"""
        try:
            # 카메라 리소스 해제
            if hasattr(self, 'cap') and self.cap and self.cap.isOpened():
                self.cap.release()
                self.cap = None
                logger.info("손 트래커 카메라 리소스 해제됨")
            
            # MediaPipe 리소스 해제
            if hasattr(self, 'hands'):
                try:
                    self.hands.close()
                    logger.info("MediaPipe Hands 리소스 해제됨")
                except Exception as e:
                    logger.error(f"MediaPipe 리소스 해제 중 오류: {e}")
            
            # 모든 OpenCV 창 닫기
            try:
                cv2.destroyAllWindows()
            except Exception as e:
                logger.error(f"OpenCV 창 닫기 중 오류: {e}")
            
            logger.info("손 트래커 리소스가 해제되었습니다.")
            
        except Exception as e:
            logger.error(f"리소스 해제 중 오류: {e}")
    
    def update_config(self) -> None:
        """설정 업데이트"""
        try:
            self.hands = mp.solutions.hands.Hands(
                static_image_mode=False,
                max_num_hands=config.hand_tracking.max_num_hands,
                min_detection_confidence=config.hand_tracking.min_detection_confidence,
                min_tracking_confidence=config.hand_tracking.min_tracking_confidence
            )
            logger.info("손 트래커 설정이 업데이트되었습니다.")
            
        except Exception as e:
            logger.error(f"손 트래커 설정 업데이트 실패: {e}")
    
    def __enter__(self):
        """컨텍스트 매니저 진입"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 매니저 종료"""
        self.release() 