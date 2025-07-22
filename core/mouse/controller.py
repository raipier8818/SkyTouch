"""
Mouse controller for Hand Tracking Trackpad application.
"""
import pyautogui
import time
import sys
import subprocess
from typing import Tuple
from dataclasses import dataclass

from utils.logging.logger import get_logger
from exceptions.base import MouseError
from core.camera.capture import CameraCapture
from core.gesture.types import GestureType

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
    
    def __init__(self, camera_capture: CameraCapture, config_manager):
        """
        마우스 컨트롤러 초기화
        
        Args:
            camera_capture: 카메라 캡처 객체 (실제 웹캠 해상도 가져오기용)
            config_manager: 설정 관리자
        """
        try:
            # macOS 접근성 권한 확인
            self._check_accessibility_permissions()
            
            # 화면 크기 가져오기
            self.screen_width, self.screen_height = pyautogui.size()
            
            # 카메라 캡처 참조 저장
            self.camera_capture = camera_capture
            
            # 설정 관리자 저장
            self.config_manager = config_manager
            
            # 마우스 설정
            pyautogui.FAILSAFE = True  # 마우스를 화면 모서리로 이동하면 중단
            pyautogui.PAUSE = 0.001    # 각 동작 사이의 지연 시간
            
            # macOS에서 키보드 입력 안정성을 위한 설정
            pyautogui.MINIMUM_DURATION = 0.1  # 최소 키 입력 지속 시간
            pyautogui.MINIMUM_SLEEP = 0.1     # 최소 대기 시간
            
            # 이전 손바닥 위치 저장 (상대적 이동을 위해)
            self.prev_palm_x = None
            self.prev_palm_y = None
            
            # 초기화 플래그
            self.is_initialized = False
            
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
            raise MouseError(f"마우스 컨트롤러 초기화 실패: {e}")
    
    def _check_accessibility_permissions(self) -> None:
        """macOS 접근성 권한 확인 및 안내"""
        if sys.platform == "darwin":  # macOS
            try:
                # 접근성 권한 확인
                result = subprocess.run([
                    'osascript', '-e', 
                    'tell application "System Events" to keystroke "a"'
                ], capture_output=True, timeout=5)
                
                if result.returncode != 0:
                    logger.warning("⚠️  접근성 권한이 필요합니다!")
                    logger.warning("시스템 환경설정 > 보안 및 개인정보 보호 > 개인정보 보호 > 접근성에서 SkyTouch를 추가해주세요.")
                    logger.warning("권한 없이는 마우스 제어가 작동하지 않습니다.")
                    
                    # 사용자에게 권한 설정 안내
                    self._show_permission_guide()
                    
            except subprocess.TimeoutExpired:
                logger.warning("접근성 권한 확인 중 시간 초과")
            except Exception as e:
                logger.warning(f"접근성 권한 확인 실패: {e}")
    
    def _show_permission_guide(self) -> None:
        """권한 설정 안내 메시지"""
        try:
            # 시스템 환경설정 열기
            subprocess.run(['open', 'x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility'])
            logger.info("시스템 환경설정이 열렸습니다. SkyTouch를 접근성 목록에 추가해주세요.")
        except Exception as e:
            logger.error(f"시스템 환경설정 열기 실패: {e}")
            logger.info("수동으로 시스템 환경설정 > 보안 및 개인정보 보호 > 개인정보 보호 > 접근성에서 SkyTouch를 추가해주세요.")
    
    def update_mouse_position(self, palm_center: list, gesture_mode: GestureType = GestureType.CLICK, 
                            smoothing: float = 0.5, sensitivity: float = 1.5,
                            invert_x: bool = False, invert_y: bool = False) -> None:
        """
        손바닥 위치에 따라 마우스 커서 위치 업데이트
        
        Args:
            palm_center: 손바닥 중심점 [x, y, z]
            gesture_mode: 제스처 모드 ("click", "scroll", "swipe", "move")
            smoothing: 스무딩 팩터 (0.0 ~ 1.0)
            sensitivity: 감도
            invert_x: X축 좌우 반전
            invert_y: Y축 상하 반전
        """
        try:
            # 현재 손바닥 위치 (0~1 범위)
            current_palm_x = palm_center[0]
            current_palm_y = palm_center[1]
            
            # 좌우/상하 반전 적용
            if invert_x:
                current_palm_x = 1.0 - current_palm_x
            if invert_y:
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
            if gesture_mode != GestureType.MOVE:
                logger.debug(f"{gesture_mode.value} 모드 - 마우스 이동 중단")
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
            if self.camera_capture:
                camera_width, camera_height = self.camera_capture.get_actual_resolution()
            else:
                camera_width = 480
                camera_height = 360
            
            # 웹캠에서 1cm 이동할 때 화면에서도 같은 비율로 이동하도록 감도 계산
            auto_sensitivity_x = self.screen_width / camera_width
            auto_sensitivity_y = self.screen_height / camera_height
            
            # 사용자 설정 감도와 자동 계산 감도를 곱함
            final_sensitivity_x = auto_sensitivity_x * sensitivity
            final_sensitivity_y = auto_sensitivity_y * sensitivity
            
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
                # 권한 확인
                if not self._check_mouse_permission():
                    logger.warning("마우스 제어 권한이 없어 클릭을 건너뜁니다.")
                    return
                    
                pyautogui.click()
                self.current_state.is_clicking = True
                logger.info(f"마우스 클릭 실행 - 위치: ({self.current_state.x}, {self.current_state.y})")
            elif not is_clicking and self.current_state.is_clicking:
                self.current_state.is_clicking = False
                logger.debug("클릭 상태 해제")
                
        except Exception as e:
            logger.error(f"클릭 처리 중 오류: {e}")
    
    def _check_mouse_permission(self) -> bool:
        """마우스 제어 권한 확인"""
        if sys.platform == "darwin":  # macOS
            try:
                # 간단한 마우스 위치 조회로 권한 확인
                pyautogui.position()
                return True
            except Exception:
                logger.warning("마우스 제어 권한이 없습니다.")
                return False
        return True
    
    def handle_right_click(self, is_right_clicking: bool) -> None:
        """
        우클릭 제스처 처리
        
        Args:
            is_right_clicking: 우클릭 상태
        """
        try:
            if is_right_clicking and not self.current_state.is_right_clicking:
                # 권한 확인
                if not self._check_mouse_permission():
                    logger.warning("마우스 제어 권한이 없어 우클릭을 건너뜁니다.")
                    return
                    
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
        스크롤 제스처 처리 (PyAutoGUI 사용)
        
        Args:
            is_scrolling: 스크롤 상태
            scroll_direction: 스크롤 방향 ("up", "down", "left", "right")
        """
        try:
            if is_scrolling:
                # 설정에서 스크롤 정도 가져오기
                gesture_config = self.config_manager.get_gesture_config()
                scroll_amount = gesture_config.get('scroll_amount', 5)
                logger.info(f"스크롤 시도: {scroll_direction}, 양: {scroll_amount}")
                
                if scroll_direction == "up":
                    pyautogui.scroll(scroll_amount)
                    logger.info(f"위로 스크롤: {scroll_amount}")
                    
                elif scroll_direction == "down":
                    pyautogui.scroll(-scroll_amount)
                    logger.info(f"아래로 스크롤: -{scroll_amount}")
                    
                elif scroll_direction == "left":
                    pyautogui.hscroll(-scroll_amount)
                    logger.info(f"왼쪽으로 스크롤: -{scroll_amount}")
                    
                elif scroll_direction == "right":
                    pyautogui.hscroll(scroll_amount)
                    logger.info(f"오른쪽으로 스크롤: {scroll_amount}")
                
                self.current_state.is_scrolling = True
                self.current_state.scroll_direction = scroll_direction
            elif not is_scrolling and self.current_state.is_scrolling:
                self.current_state.is_scrolling = False
                self.current_state.scroll_direction = ""
                logger.debug("스크롤 상태 해제")
                
        except Exception as e:
            logger.error(f"스크롤 처리 중 오류: {e}")
    
    def _fallback_scroll(self, scroll_direction: str) -> None:
        """fallback 스크롤 (더 이상 사용하지 않음)"""
        logger.warning("fallback 스크롤이 호출되었지만 더 이상 사용되지 않습니다.")
        pass
    
    def handle_swipe(self, is_swiping: bool, swipe_direction: str) -> None:
        """
        스와이프 제스처 처리 (맥북 데스크탑 전환 + 미션 컨트롤)
        
        Args:
            is_swiping: 스와이프 상태
            swipe_direction: 스와이프 방향 ("left", "right", "up", "down")
        """
        try:
            if is_swiping and not self.current_state.is_swiping:
                # 맥북 제스처 단축키
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
    
    def cleanup(self) -> None:
        """리소스 정리"""
        try:
            # 마우스 상태 초기화
            self.reset_state()
            logger.info("마우스 컨트롤러 리소스가 정리되었습니다.")
            
        except Exception as e:
            logger.error(f"마우스 컨트롤러 리소스 정리 중 오류: {e}") 