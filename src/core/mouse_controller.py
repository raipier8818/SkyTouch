"""
Mouse control functionality for hand gestures.
"""
import pyautogui
import numpy as np
import time
from typing import Tuple, Optional
from dataclasses import dataclass

from ..config import config
from ..utils.logger import get_logger
from ..utils.exceptions import HandTrackpadError

logger = get_logger(__name__)


@dataclass
class MouseState:
    """마우스 상태 데이터 클래스"""
    x: int
    y: int
    is_clicking: bool
    is_right_clicking: bool
    is_double_clicking: bool
    is_scrolling: bool
    is_swiping: bool
    swipe_direction: str
    scroll_direction: str


class MouseController:
    """마우스 제어 클래스"""
    
    def __init__(self, hand_tracker=None):
        """
        마우스 컨트롤러 초기화
        
        Args:
            hand_tracker: HandTracker 인스턴스 (실제 웹캠 해상도 가져오기용)
        """
        try:
            # 화면 크기 가져오기
            self.screen_width, self.screen_height = pyautogui.size()
            
            # HandTracker 참조 저장 (실제 웹캠 해상도 가져오기용)
            self.hand_tracker = hand_tracker
            
            # 마우스 설정
            pyautogui.FAILSAFE = True  # 마우스를 화면 모서리로 이동하면 중단
            pyautogui.PAUSE = 0.001    # 각 동작 사이의 지연 시간 (더 빠르게)
            
            # macOS에서 키보드 입력 안정성을 위한 설정
            pyautogui.MINIMUM_DURATION = 0.1  # 최소 키 입력 지속 시간
            pyautogui.MINIMUM_SLEEP = 0.1     # 최소 대기 시간
            
            # 이전 손바닥 위치 저장 (상대적 이동을 위해)
            self.prev_palm_x = None
            self.prev_palm_y = None
            
            # 초기화 플래그
            self.is_initialized = False
            
            # 제스처 모드 관련 속성들
            self.gesture_history = []
            self.current_gesture_mode = "click"
            self.mode_start_time = time.time()
            self.is_mode_stable = False
            
            # 부드러운 이동을 위한 변수들
            self.smoothed_x = 0.0
            self.smoothed_y = 0.0
            self.last_move_time = time.time()
            
            # 마우스 상태
            self.current_state = MouseState(
                x=0, y=0, 
                is_clicking=False, 
                is_right_clicking=False,
                is_double_clicking=False,
                is_scrolling=False, 
                is_swiping=False,
                swipe_direction="",
                scroll_direction=""
            )
            
            logger.info("마우스 컨트롤러가 초기화되었습니다.")
            
        except Exception as e:
            logger.error(f"마우스 컨트롤러 초기화 실패: {e}")
            raise HandTrackpadError(f"마우스 컨트롤러 초기화 실패: {e}")
    
    def update_mouse_position(self, palm_center: list, gesture_mode: str = "click", smoothing: float = 0.5) -> None:
        """
        손바닥 위치에 따라 마우스 커서 위치 업데이트
        
        Args:
            palm_center: 손바닥 중심점 [x, y, z]
            gesture_mode: 제스처 모드 ("click", "scroll", "swipe", "move")
            smoothing: 스무딩 팩터 (0.0 ~ 1.0)
        """
        try:
            # 현재 손바닥 위치 (0~1 범위)
            current_palm_x = palm_center[0]
            current_palm_y = palm_center[1]
            
            # 좌우/상하 반전 적용
            if config.gesture.invert_x:
                current_palm_x = 1.0 - current_palm_x
            if config.gesture.invert_y:
                current_palm_y = 1.0 - current_palm_y
            
            # 첫 번째 호출이면 초기화
            if not self.is_initialized:
                self.prev_palm_x = current_palm_x
                self.prev_palm_y = current_palm_y
                self.is_initialized = True
                logger.debug("마우스 컨트롤러 초기화 완료")
                return
            
            # 손바닥 위치 변화량 계산
            delta_x = current_palm_x - self.prev_palm_x
            delta_y = current_palm_y - self.prev_palm_y
            
            # 현재 시간 가져오기
            current_time = time.time()
            
            # 이동 모드가 아니면 마우스 이동 안함
            if gesture_mode != "move":
                logger.debug(f"{gesture_mode} 모드 - 마우스 이동 중단")
                # 이전 손바닥 위치 업데이트 (중요!)
                self.prev_palm_x = current_palm_x
                self.prev_palm_y = current_palm_y
                return
            
            # 부드러운 스무딩 적용 (지수 이동 평균)
            smoothing_factor = smoothing * 0.8  # 더 부드럽게
            self.smoothed_x = self.smoothed_x * (1 - smoothing_factor) + delta_x * smoothing_factor
            self.smoothed_y = self.smoothed_y * (1 - smoothing_factor) + delta_y * smoothing_factor
            
            # 최소 이동량 임계값 (너무 작은 움직임 무시)
            min_movement_threshold = 0.001
            if abs(self.smoothed_x) < min_movement_threshold and abs(self.smoothed_y) < min_movement_threshold:
                # 이전 손바닥 위치 업데이트
                self.prev_palm_x = current_palm_x
                self.prev_palm_y = current_palm_y
                return
            
            # 실제 웹캠 해상도 기반 1:1 비례 감도 계산
            if self.hand_tracker:
                camera_width, camera_height = self.hand_tracker.get_actual_camera_resolution()
            else:
                camera_width = config.camera.width
                camera_height = config.camera.height
            
            # 웹캠에서 1cm 이동할 때 화면에서도 같은 비율로 이동하도록 감도 계산
            # 웹캠 좌표 (0~1)를 화면 좌표로 매핑할 때 비율 유지
            auto_sensitivity_x = self.screen_width / camera_width
            auto_sensitivity_y = self.screen_height / camera_height
            
            # 사용자 설정 감도와 자동 계산 감도를 곱함
            final_sensitivity_x = auto_sensitivity_x * config.gesture.sensitivity
            final_sensitivity_y = auto_sensitivity_y * config.gesture.sensitivity
            
            # 화면 크기에 비례한 이동량 계산 (부드러운 값 사용)
            move_x = int(self.smoothed_x * self.screen_width * final_sensitivity_x)
            move_y = int(self.smoothed_y * self.screen_height * final_sensitivity_y)
            
            # 감도 디버그 로그 (주기적으로 출력)
            if abs(move_x) > 0 or abs(move_y) > 0:
                logger.debug(f"부드러운 이동: smoothed=({self.smoothed_x:.3f}, {self.smoothed_y:.3f}), sensitivity=({final_sensitivity_x:.2f}, {final_sensitivity_y:.2f}), move=({move_x}, {move_y})")
            
            # 현재 마우스 위치 가져오기
            current_mouse_x, current_mouse_y = pyautogui.position()
            
            # 새로운 마우스 위치 계산
            new_x = current_mouse_x + move_x
            new_y = current_mouse_y + move_y
            
            # 화면 범위 내로 제한 (PyAutoGUI fail-safe 방지)
            margin = 1  # 화면 가장자리에서 1픽셀 여유 (fail-safe 방지)
            new_x = max(margin, min(new_x, self.screen_width - margin - 1))
            new_y = max(margin, min(new_y, self.screen_height - margin - 1))
            
            # 마우스 이동 (더 부드럽게)
            pyautogui.moveTo(new_x, new_y, duration=0.001)
            
            # 이전 손바닥 위치 업데이트
            self.prev_palm_x = current_palm_x
            self.prev_palm_y = current_palm_y
            
            # 현재 상태 업데이트
            self.current_state.x = new_x
            self.current_state.y = new_y
            
        except Exception as e:
            logger.error(f"마우스 위치 업데이트 중 오류: {e}")
    
    def handle_click(self, is_clicking: bool) -> None:
        """
        클릭 제스처 처리
        
        Args:
            is_clicking: 클릭 상태
        """
        try:
            if is_clicking and not self.current_state.is_clicking:
                pyautogui.click()
                self.current_state.is_clicking = True
                logger.info(f"마우스 클릭 실행 - 위치: ({self.current_state.x}, {self.current_state.y})")
            elif not is_clicking and self.current_state.is_clicking:
                self.current_state.is_clicking = False
                logger.debug("클릭 상태 해제")
                
        except Exception as e:
            logger.error(f"클릭 처리 중 오류: {e}")
    
    def handle_right_click(self, is_right_clicking: bool) -> None:
        """
        우클릭 제스처 처리
        
        Args:
            is_right_clicking: 우클릭 상태
        """
        try:
            if is_right_clicking and not self.current_state.is_right_clicking:
                pyautogui.rightClick()
                self.current_state.is_right_clicking = True
                logger.info(f"마우스 우클릭 실행 - 위치: ({self.current_state.x}, {self.current_state.y})")
            elif not is_right_clicking and self.current_state.is_right_clicking:
                self.current_state.is_right_clicking = False
                logger.debug("우클릭 상태 해제")
                
        except Exception as e:
            logger.error(f"우클릭 처리 중 오류: {e}")
    
    def handle_double_click(self, is_double_clicking: bool) -> None:
        """
        더블클릭 제스처 처리
        
        Args:
            is_double_clicking: 더블클릭 상태
        """
        try:
            if is_double_clicking and not self.current_state.is_double_clicking:
                pyautogui.doubleClick()
                self.current_state.is_double_clicking = True
                logger.info(f"마우스 더블클릭 실행 - 위치: ({self.current_state.x}, {self.current_state.y})")
            elif not is_double_clicking and self.current_state.is_double_clicking:
                self.current_state.is_double_clicking = False
                logger.debug("더블클릭 상태 해제")
                
        except Exception as e:
            logger.error(f"더블클릭 처리 중 오류: {e}")
    
    def handle_scroll(self, is_scrolling: bool, scroll_direction: str) -> None:
        """
        스크롤 제스처 처리 (더 매끄럽게)
        
        Args:
            is_scrolling: 스크롤 상태
            scroll_direction: 스크롤 방향 ("up", "down", "left", "right")
        """
        try:
            if is_scrolling:
                # 스크롤 방향에 따라 스크롤 실행 (더 부드럽게)
                scroll_amount = 2  # 더 작은 스크롤 양
                
                if scroll_direction == "up":
                    pyautogui.scroll(scroll_amount)  # 위로 스크롤
                    logger.debug("위로 스크롤")
                elif scroll_direction == "down":
                    pyautogui.scroll(-scroll_amount)  # 아래로 스크롤
                    logger.debug("아래로 스크롤")
                elif scroll_direction == "left":
                    pyautogui.hscroll(-scroll_amount)  # 왼쪽으로 스크롤
                    logger.debug("왼쪽으로 스크롤")
                elif scroll_direction == "right":
                    pyautogui.hscroll(scroll_amount)  # 오른쪽으로 스크롤
                    logger.debug("오른쪽으로 스크롤")
                
                self.current_state.is_scrolling = True
                self.current_state.scroll_direction = scroll_direction
            elif not is_scrolling and self.current_state.is_scrolling:
                self.current_state.is_scrolling = False
                self.current_state.scroll_direction = ""
                logger.debug("스크롤 상태 해제")
                
        except Exception as e:
            logger.error(f"스크롤 처리 중 오류: {e}")
    
    def handle_swipe(self, is_swiping: bool, swipe_direction: str) -> None:
        """
        스와이프 제스처 처리 (맥북 데스크탑 전환 + 미션 컨트롤)
        
        Args:
            is_swiping: 스와이프 상태
            swipe_direction: 스와이프 방향 ("left", "right", "up", "down")
        """
        try:
            if is_swiping and not self.current_state.is_swiping:
                # 맥북 제스처 단축키 (time.sleep 제거하여 카메라 끊김 방지)
                if swipe_direction == "left":
                    # 왼쪽으로 스와이프: 다음 데스크탑
                    try:
                        pyautogui.hotkey('ctrl', 'right')
                        logger.info(f"스와이프 왼쪽 - 다음 데스크탑으로 이동 (성공)")
                    except Exception as e:
                        logger.error(f"스와이프 왼쪽 실패: {e}")
                elif swipe_direction == "right":
                    # 오른쪽으로 스와이프: 이전 데스크탑
                    try:
                        pyautogui.hotkey('ctrl', 'left')
                        logger.info(f"스와이프 오른쪽 - 이전 데스크탑으로 이동 (성공)")
                    except Exception as e:
                        logger.error(f"스와이프 오른쪽 실패: {e}")
                elif swipe_direction == "up":
                    # 위로 스와이프: 미션 컨트롤 시작
                    try:
                        pyautogui.hotkey('ctrl', 'up')
                        logger.info(f"스와이프 위 - 미션 컨트롤 시작 (성공)")
                    except Exception as e:
                        logger.error(f"스와이프 위 실패: {e}")
                elif swipe_direction == "down":
                    # 아래로 스와이프: 미션 컨트롤 종료
                    try:
                        pyautogui.hotkey('ctrl', 'down')
                        logger.info(f"스와이프 아래 - 미션 컨트롤 종료 (성공)")
                    except Exception as e:
                        logger.error(f"스와이프 아래 실패: {e}")
                
                self.current_state.is_swiping = True
                self.current_state.swipe_direction = swipe_direction
            elif not is_swiping and self.current_state.is_swiping:
                self.current_state.is_swiping = False
                self.current_state.swipe_direction = ""
                logger.debug("스와이프 상태 해제")
                
        except Exception as e:
            logger.error(f"스와이프 처리 중 오류: {e}")
    
    def get_current_position(self) -> Tuple[int, int]:
        """
        현재 마우스 위치 반환
        
        Returns:
            현재 마우스 x, y 좌표
        """
        return pyautogui.position()
    
    def get_screen_size(self) -> Tuple[int, int]:
        """
        화면 크기 반환
        
        Returns:
            화면 너비, 높이
        """
        return self.screen_width, self.screen_height
    
    def reset_state(self) -> None:
        """마우스 상태 초기화"""
        try:
            self.current_state = MouseState(
                x=0, y=0,
                is_clicking=False,
                is_right_clicking=False,
                is_double_clicking=False,
                is_scrolling=False,
                is_swiping=False,
                swipe_direction="",
                scroll_direction=""
            )
            
            # 상대적 이동 초기화
            self.prev_palm_x = None
            self.prev_palm_y = None
            self.is_initialized = False
            
            # 부드러운 이동 변수 초기화
            self.smoothed_x = 0.0
            self.smoothed_y = 0.0
            self.last_move_time = time.time()
            
            logger.debug("마우스 상태가 초기화되었습니다.")
            
        except Exception as e:
            logger.error(f"마우스 상태 초기화 중 오류: {e}")
    
    def update_config(self) -> None:
        """설정 업데이트"""
        try:
            # 화면 크기 다시 가져오기 (화면 해상도 변경 시)
            self.screen_width, self.screen_height = pyautogui.size()
            
            # 마우스 상태 초기화
            self.reset_state()
            
            logger.info("마우스 컨트롤러 설정이 업데이트되었습니다.")
            
        except Exception as e:
            logger.error(f"마우스 컨트롤러 설정 업데이트 실패: {e}") 