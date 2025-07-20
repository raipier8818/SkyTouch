"""
Core hand tracking functionality using MediaPipe.
"""
import cv2
import mediapipe as mp
import numpy as np
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
    gesture_mode: str  # "click", "scroll", "swipe", "stop"
    is_clicking: bool  # 클릭 모드에서 클릭
    is_right_clicking: bool  # 클릭 모드에서 우클릭
    is_double_clicking: bool  # 더블클릭
    is_scrolling: bool  # 스크롤 모드에서 스크롤
    is_swiping: bool  # 스와이프 모드에서 스와이프
    swipe_direction: str  # "left", "right", "none"
    scroll_direction: str  # "up", "down", "left", "right", "none"


class HandTracker:
    """MediaPipe를 사용한 손 트래킹 클래스"""
    
    def __init__(self):
        """손 트래커 초기화"""
        try:
            self.mp_hands = mp.solutions.hands
            self.hands = self.mp_hands.Hands(
                static_image_mode=config.hand_tracking.static_image_mode,
                max_num_hands=config.hand_tracking.max_num_hands,
                min_detection_confidence=config.hand_tracking.min_detection_confidence,
                min_tracking_confidence=config.hand_tracking.min_tracking_confidence
            )
            self.mp_draw = mp.solutions.drawing_utils
            
            # 카메라 초기화
            self.cap = cv2.VideoCapture(config.camera.device_id)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.camera.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.camera.height)
            self.cap.set(cv2.CAP_PROP_FPS, config.camera.fps)
            
            if not self.cap.isOpened():
                raise CameraError("카메라를 열 수 없습니다.")
            
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
            
            # 더블클릭 추적 변수들
            self.last_click_time = 0.0
            self.click_count = 0
            
            logger.info("손 트래커가 성공적으로 초기화되었습니다.")
            
        except Exception as e:
            logger.error(f"손 트래커 초기화 실패: {e}")
            raise HandTrackingError(f"손 트래커 초기화 실패: {e}")
    
    def process_frame(self, frame: np.ndarray) -> Optional[List[HandLandmarks]]:
        """
        프레임에서 손 랜드마크 감지
        
        Args:
            frame: 입력 프레임
            
        Returns:
            감지된 손 랜드마크 리스트 또는 None
        """
        try:
            # BGR을 RGB로 변환
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)
            
            if not results.multi_hand_landmarks:
                return None
            
            hand_landmarks_list = []
            
            for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # 랜드마크 좌표 추출
                landmarks = []
                for lm in hand_landmarks.landmark:
                    landmarks.append([lm.x, lm.y, lm.z])
                
                # 손 방향 확인
                handedness = "Unknown"
                if results.multi_handedness:
                    handedness = results.multi_handedness[i].classification[0].label
                
                # 신뢰도 계산
                confidence = results.multi_handedness[i].classification[0].score if results.multi_handedness else 0.0
                
                hand_landmarks_list.append(HandLandmarks(
                    landmarks=landmarks,
                    handedness=handedness,
                    confidence=confidence
                ))
            
            return hand_landmarks_list
            
        except Exception as e:
            logger.error(f"프레임 처리 중 오류: {e}")
            return None
    
    def draw_landmarks(self, frame: np.ndarray, hand_landmarks: HandLandmarks) -> np.ndarray:
        """
        손 랜드마크를 프레임에 그리기
        
        Args:
            frame: 원본 프레임
            hand_landmarks: 손 랜드마크 데이터
            
        Returns:
            랜드마크가 그려진 프레임
        """
        try:
            height, width = frame.shape[:2]
            landmarks = hand_landmarks.landmarks
            
            # 손 방향에 따른 색상 설정
            if hand_landmarks.handedness == "Right":
                color = (0, 255, 0)  # 초록색 (오른손)
            else:
                color = (255, 0, 0)  # 빨간색 (왼손)
            
            # 각 랜드마크 포인트를 원으로 그리기
            for i, landmark in enumerate(landmarks):
                x = int(landmark[0] * width)
                y = int(landmark[1] * height)
                
                # 랜드마크 포인트 크기 설정 (중요한 포인트는 더 크게)
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
            
            # 손가락 연결선 그리기
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
            
            for connection in connections:
                start_idx = connection[0]
                end_idx = connection[1]
                
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
            
            # 손바닥 중심점 강조
            palm_center = landmarks[9]  # 중지 MCP
            palm_x = int(palm_center[0] * width)
            palm_y = int(palm_center[1] * height)
            cv2.circle(frame, (palm_x, palm_y), 12, (0, 255, 255), -1)  # 노란색
            cv2.circle(frame, (palm_x, palm_y), 12, (255, 255, 255), 2)  # 흰색 테두리
            
            return frame
            
        except Exception as e:
            logger.error(f"랜드마크 그리기 중 오류: {e}")
            return frame
    
    def calculate_distance(self, point1: List[float], point2: List[float]) -> float:
        """
        두 점 사이의 유클리드 거리 계산
        
        Args:
            point1: 첫 번째 점 [x, y, z]
            point2: 두 번째 점 [x, y, z]
            
        Returns:
            두 점 사이의 거리
        """
        return np.sqrt(
            (point1[0] - point2[0])**2 + 
            (point1[1] - point2[1])**2 + 
            (point1[2] - point2[2])**2
        )
    
    def detect_gestures(self, hand_landmarks: HandLandmarks) -> GestureData:
        """
        손 랜드마크에서 제스처 감지
        
        Args:
            hand_landmarks: 손 랜드마크 데이터
            
        Returns:
            제스처 데이터
        """
        try:
            import time
            current_time = time.time()
            landmarks = hand_landmarks.landmarks
            
            # 손바닥 중심점
            palm_center = landmarks[9]
            
            # 각 손가락의 팁과 MCP 관절
            thumb_tip = landmarks[4]
            index_tip = landmarks[8]
            middle_tip = landmarks[12]
            ring_tip = landmarks[16]
            pinky_tip = landmarks[20]
            
            index_mcp = landmarks[5]
            middle_mcp = landmarks[9]
            ring_mcp = landmarks[13]
            pinky_mcp = landmarks[17]
            
            # 손가락 상태 확인 (펴져 있는지 구부러져 있는지)
            # 약간의 여유를 두어 안정성 향상
            finger_threshold = 0.02  # 2% 여유
            
            index_extended = index_tip[1] < (index_mcp[1] - finger_threshold)
            middle_extended = middle_tip[1] < (middle_mcp[1] - finger_threshold)
            ring_extended = ring_tip[1] < (ring_mcp[1] - finger_threshold)
            pinky_extended = pinky_tip[1] < (pinky_mcp[1] - finger_threshold)
            
            # 제스처 모드 감지
            gesture_mode = "stop"  # 기본값: 정지 모드
            
            # 디버그: 손가락 상태 로깅
            logger.debug(f"손가락 상태: 검지={index_extended}, 중지={middle_extended}, 약지={ring_extended}, 새끼={pinky_extended}")
            
            # 스와이프 모드: 검지, 중지, 약지가 펴진 상태 (가장 구체적인 조건)
            if index_extended and middle_extended and ring_extended and not pinky_extended:
                gesture_mode = "swipe"
            # 스크롤 모드: 검지와 중지를 펴진 상태
            elif index_extended and middle_extended and not ring_extended and not pinky_extended:
                gesture_mode = "scroll"
            # 이동 모드: 검지만 펴진 상태
            elif index_extended and not middle_extended and not ring_extended and not pinky_extended:
                gesture_mode = "move"
            
            # 모드 안정화 확인
            if gesture_mode != self.current_gesture_mode:
                # 모드가 변경되었으면 안정화 시간 시작
                self.current_gesture_mode = gesture_mode
                self.mode_start_time = current_time
                self.is_mode_stable = False
                logger.debug(f"모드 변경: {gesture_mode} (안정화 시작)")
            elif not self.is_mode_stable:
                # 현재 모드가 안정화 시간을 충족했는지 확인
                mode_duration = current_time - self.mode_start_time
                if mode_duration >= config.gesture.mode_stabilization_time:
                    self.is_mode_stable = True
                    logger.debug(f"모드 안정화 완료: {gesture_mode} ({mode_duration:.1f}초)")
                else:
                    logger.debug(f"모드 안정화 중: {gesture_mode} ({mode_duration:.1f}초)")
            
            logger.debug(f"제스처 모드: {gesture_mode} (안정화: {self.is_mode_stable})")
            
            # 각 모드별 세부 제스처 감지
            is_clicking = False
            is_right_clicking = False
            is_double_clicking = False
            is_scrolling = False
            is_swiping = False
            swipe_direction = "none"
            scroll_direction = "none"
            
            # 클릭과 우클릭은 모든 모드에서 감지 (손 모양과 상관없이)
            # 클릭: 엄지와 검지가 붙었을 때
            thumb_index_distance = self.calculate_distance(thumb_tip, index_tip)
            if thumb_index_distance < config.gesture.click_threshold:
                is_clicking = True
                logger.debug(f"클릭 감지: 엄지-검지 거리={thumb_index_distance:.3f}, 임계값={config.gesture.click_threshold:.3f}")
                
                # 더블클릭 감지
                if current_time - self.last_click_time < 0.5:  # 0.5초 이내에 연속 클릭
                    self.click_count += 1
                    if self.click_count >= 2:
                        is_double_clicking = True
                        self.click_count = 0  # 리셋
                        logger.debug("더블클릭 감지!")
                else:
                    self.click_count = 1
                
                self.last_click_time = current_time
            
            # 우클릭: 엄지와 중지가 붙었을 때
            thumb_middle_distance = self.calculate_distance(thumb_tip, middle_tip)
            if thumb_middle_distance < config.gesture.click_threshold:
                is_right_clicking = True
                logger.debug(f"우클릭 감지: 엄지-중지 거리={thumb_middle_distance:.3f}, 임계값={config.gesture.click_threshold:.3f}")
            
            if gesture_mode == "scroll" and self.is_mode_stable:
                # 스크롤: 손 움직임에 따라 스크롤 방향 결정
                if self.last_palm_position is None:
                    self.last_palm_position = palm_center
                    self.scroll_start_time = current_time
                else:
                    # 스크롤 거리와 시간 계산
                    scroll_distance_x = abs(palm_center[0] - self.last_palm_position[0])
                    scroll_distance_y = abs(palm_center[1] - self.last_palm_position[1])
                    scroll_time = current_time - self.scroll_start_time
                    
                    # 스크롤 임계값 확인
                    if scroll_time > 0.1:  # 0.1초 이상 움직임
                        if scroll_distance_x > scroll_distance_y:
                            # 좌우 스크롤
                            if palm_center[0] > self.last_palm_position[0]:
                                scroll_direction = "right"
                            else:
                                scroll_direction = "left"
                        else:
                            # 상하 스크롤
                            if palm_center[1] > self.last_palm_position[1]:
                                scroll_direction = "down"
                            else:
                                scroll_direction = "up"
                        
                        is_scrolling = True
                        self.last_palm_position = palm_center
                        self.scroll_start_time = current_time
            else:
                self.last_palm_position = None
                self.scroll_start_time = 0.0
            
            if gesture_mode == "swipe" and self.is_mode_stable:
                # 스와이프 쿨타임 확인
                if self.is_swipe_cooldown:
                    cooldown_remaining = config.gesture.swipe_cooldown - (current_time - self.last_swipe_time)
                    if cooldown_remaining > 0:
                        logger.debug(f"스와이프 쿨타임 중: {cooldown_remaining:.1f}초 남음")
                        return GestureData(
                            palm_center=palm_center,
                            gesture_mode=gesture_mode,
                            is_clicking=is_clicking,
                            is_right_clicking=is_right_clicking,
                            is_double_clicking=is_double_clicking,
                            is_scrolling=is_scrolling,
                            is_swiping=False,  # 쿨타임 중에는 스와이프 비활성화
                            swipe_direction="none",
                            scroll_direction=scroll_direction
                        )
                    else:
                        self.is_swipe_cooldown = False
                        logger.debug("스와이프 쿨타임 종료")
                
                # 스와이프: 손 움직임에 따라 스와이프 방향 결정
                if self.last_swipe_position is None:
                    self.last_swipe_position = palm_center[0]
                    self.swipe_start_time = current_time
                    logger.debug(f"스와이프 시작: 위치={palm_center[0]:.3f}")
                else:
                    # 스와이프 거리와 시간 계산
                    swipe_distance = abs(palm_center[0] - self.last_swipe_position)
                    swipe_time = current_time - self.swipe_start_time
                    
                    logger.debug(f"스와이프 추적: 현재={palm_center[0]:.3f}, 시작={self.last_swipe_position:.3f}, 거리={swipe_distance:.3f}, 시간={swipe_time:.2f}, 임계값={config.gesture.swipe_threshold:.3f}")
                    
                    # 스와이프 임계값 확인
                    if (swipe_distance > config.gesture.swipe_threshold and 
                        swipe_time < config.gesture.swipe_time_limit):  # 설정된 시간 이내에 스와이프
                        
                        if palm_center[0] > self.last_swipe_position:
                            swipe_direction = "right"
                        else:
                            swipe_direction = "left"
                        
                        is_swiping = True
                        logger.debug(f"스와이프 감지: 방향={swipe_direction}, 거리={swipe_distance:.3f}, 시간={swipe_time:.2f}")
                        
                        # 스와이프 쿨타임 시작
                        self.last_swipe_time = current_time
                        self.is_swipe_cooldown = True
                        logger.debug(f"스와이프 쿨타임 시작: {config.gesture.swipe_cooldown}초")
                        
                        # 스와이프 감지 후 리셋 (쿨타임 동안 새로운 스와이프 방지)
                        self.last_swipe_position = None
                        self.swipe_start_time = 0.0
            else:
                if self.last_swipe_position is not None:
                    logger.debug("스와이프 모드 종료, 위치 리셋")
                self.last_swipe_position = None
                self.swipe_start_time = 0.0
            
            return GestureData(
                palm_center=palm_center,
                gesture_mode=gesture_mode,
                is_clicking=is_clicking,
                is_right_clicking=is_right_clicking,
                is_double_clicking=is_double_clicking,
                is_scrolling=is_scrolling,
                is_swiping=is_swiping,
                swipe_direction=swipe_direction,
                scroll_direction=scroll_direction
            )
            
        except Exception as e:
            logger.error(f"제스처 감지 중 오류: {e}")
            raise GestureError(f"제스처 감지 실패: {e}")
    
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
            # MediaPipe Hands 설정 업데이트
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