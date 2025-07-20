"""
Camera panel UI component for displaying webcam feed.
"""
import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import threading
import time
from typing import Optional, Callable

from ..utils.logger import get_logger
from ..config import config

logger = get_logger(__name__)


class CameraPanel(ttk.LabelFrame):
    """카메라 패널 위젯"""
    
    def __init__(self, parent, camera_callback: Optional[Callable] = None, mouse_controller=None, control_panel=None):
        """
        카메라 패널 초기화
        
        Args:
            parent: 부모 위젯
            camera_callback: 카메라 프레임 처리 콜백
            mouse_controller: 마우스 컨트롤러
            control_panel: 제어 패널 (로딩 상태 관리용)
        """
        super().__init__(parent, text="카메라 화면", padding="10")
        
        self.camera_callback = camera_callback
        self.mouse_controller = mouse_controller
        self.control_panel = control_panel
        
        # 카메라 관련 변수
        self.cap = None
        self.is_displaying = False
        self.display_thread = None
        
        # 손 트래커
        self.hand_tracker = None
        
        self.create_widgets()
    
    def create_widgets(self) -> None:
        """위젯 생성"""
        # 카메라 화면을 표시할 라벨 (고정 크기)
        self.camera_label = ttk.Label(self, text="카메라가 시작되지 않았습니다")
        self.camera_label.grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 상태 표시
        self.status_label = ttk.Label(self, text="상태: 대기 중", foreground="gray")
        self.status_label.grid(row=1, column=0, padx=5, pady=(0, 5))
        
        # 그리드 가중치 설정
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        # 카메라 패널 크기를 고정 (480x360 이미지 + 여백)
        self.configure(width=500, height=420)
    
    def start_display(self) -> None:
        """카메라 화면 표시 시작"""
        if not self.is_displaying:
            self.is_displaying = True
            self.status_label.config(text="상태: 표시 중", foreground="green")
            self.camera_label.config(text="카메라 초기화 중...")
            
            # 로딩 상태 설정
            if self.control_panel:
                self.control_panel.set_loading_state(True)
            
            # 별도 스레드에서 카메라 화면 표시
            self.display_thread = threading.Thread(target=self._display_loop, daemon=True)
            self.display_thread.start()
            
            logger.info("카메라 화면 표시가 시작되었습니다.")
    
    def stop_display(self) -> None:
        """카메라 화면 표시 정지"""
        if self.is_displaying:
            logger.info("카메라 정지 요청...")
            self.is_displaying = False
            
            # UI 즉시 업데이트 (GUI 스레드에서 안전하게)
            self.camera_label.after(0, self._reset_ui)
            
            # 스레드가 종료될 때까지 대기 (타임아웃 단축)
            if self.display_thread and self.display_thread.is_alive():
                logger.info("디스플레이 스레드 종료 대기 중...")
                self.display_thread.join(timeout=1.0)  # 타임아웃 단축
                if self.display_thread.is_alive():
                    logger.warning("디스플레이 스레드가 강제 종료되었습니다.")
            
            # 웹캠이 완전히 꺼진 후 콜백 호출
            self.camera_label.after(100, self._on_stop_complete)
            
            logger.info("카메라 화면 표시가 정지되었습니다.")
    
    def _on_stop_complete(self) -> None:
        """카메라 정지 완료 후 호출"""
        try:
            # 컨트롤 패널에 정지 완료 알림
            if self.control_panel:
                self.control_panel.set_loading_state(False)
            logger.info("카메라 정지 완료")
            
        except Exception as e:
            logger.error(f"카메라 정지 완료 처리 중 오류: {e}")
    
    def _reset_ui(self) -> None:
        """UI 초기화 (GUI 스레드에서 호출)"""
        self.status_label.config(text="상태: 대기 중", foreground="gray")
        
        # 이미지 완전히 제거
        self.camera_label.config(image="", text="카메라가 시작되지 않았습니다")
        self.camera_label.image = None  # 이미지 참조 해제
        
        # 레이블 강제 업데이트
        self.camera_label.update_idletasks()
        self.camera_label.update()
        
        # 추가로 레이블을 다시 설정하여 확실히 초기화
        self.camera_label.config(text="카메라가 시작되지 않았습니다")
        self.camera_label.update()
    
    def _display_loop(self) -> None:
        """카메라 화면 표시 루프"""
        try:
            logger.info("카메라 디스플레이 루프 시작")
            
            # 카메라 초기화
            self.cap = cv2.VideoCapture(0)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.camera.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.camera.height)
            
            if not self.cap.isOpened():
                logger.error("카메라를 열 수 없습니다")
                self.camera_label.config(text="카메라를 열 수 없습니다")
                # 로딩 상태 해제
                if self.control_panel:
                    self.control_panel.set_loading_state(False)
                return
            
            logger.info("카메라 초기화 완료, 루프 시작")
            
            # 로딩 완료 - 버튼 활성화
            if self.control_panel:
                self.control_panel.set_loading_state(False)
            
            while self.is_displaying:
                ret, frame = self.cap.read()
                if not ret:
                    continue
                
                # 프레임 처리 (콜백이 있으면 호출)
                if self.camera_callback:
                    frame = self.camera_callback(frame)
                
                # 손 트래킹 및 제스처 처리
                if hasattr(self, 'hand_tracker') and self.hand_tracker and self.mouse_controller:
                    try:
                        # 손 랜드마크 감지
                        hand_landmarks_list = self.hand_tracker.process_frame(frame)
                        
                        if hand_landmarks_list:
                            logger.debug(f"손 감지됨: {len(hand_landmarks_list)}개")
                            for hand_landmarks in hand_landmarks_list:
                                # 랜드마크 그리기
                                frame = self.hand_tracker.draw_landmarks(frame, hand_landmarks)
                                logger.debug(f"랜드마크 그리기 완료: {hand_landmarks.handedness}")
                                
                                # 제스처 감지
                                gesture_data = self.hand_tracker.detect_gestures(hand_landmarks)
                                
                                # 제스처 상태 로깅
                                gesture_status = []
                                if gesture_data.gesture_mode != "stop":
                                    gesture_status.append(f"모드: {gesture_data.gesture_mode}")
                                if gesture_data.is_clicking:
                                    gesture_status.append("클릭")
                                if gesture_data.is_right_clicking:
                                    gesture_status.append("우클릭")
                                if gesture_data.is_double_clicking:
                                    gesture_status.append("더블클릭")
                                if gesture_data.is_scrolling:
                                    gesture_status.append(f"스크롤({gesture_data.scroll_direction})")
                                if gesture_data.is_swiping:
                                    gesture_status.append(f"스와이프({gesture_data.swipe_direction})")
                                
                                if gesture_status:
                                    logger.info(f"제스처 감지: {', '.join(gesture_status)} - {hand_landmarks.handedness}손")
                                else:
                                    logger.debug(f"정지 모드 - {hand_landmarks.handedness}손")
                                
                                # 마우스 제어
                                self.mouse_controller.update_mouse_position(
                                    gesture_data.palm_center,
                                    gesture_mode=gesture_data.gesture_mode,
                                    smoothing=config.gesture.smoothing_factor
                                )
                                
                                # 제스처 처리
                                self.mouse_controller.handle_click(gesture_data.is_clicking)
                                self.mouse_controller.handle_right_click(gesture_data.is_right_clicking)
                                self.mouse_controller.handle_double_click(gesture_data.is_double_clicking)
                                self.mouse_controller.handle_scroll(gesture_data.is_scrolling, gesture_data.scroll_direction)
                                self.mouse_controller.handle_swipe(gesture_data.is_swiping, gesture_data.swipe_direction)
                        else:
                            logger.debug("손이 감지되지 않음")
                    except Exception as e:
                        logger.error(f"손 트래킹 처리 중 오류: {e}")
                else:
                    logger.debug("손 트래커 또는 마우스 컨트롤러가 설정되지 않음")
                
                # OpenCV BGR을 RGB로 변환
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # PIL Image로 변환
                pil_image = Image.fromarray(frame_rgb)
                
                # GUI 스레드에서 안전하게 업데이트 (PIL Image 전달)
                self.camera_label.after(0, self._update_image, pil_image)
                
                time.sleep(0.03)  # 약 30 FPS
            
            logger.info("카메라 디스플레이 루프 종료")
            
        except Exception as e:
            logger.error(f"카메라 화면 표시 중 오류: {e}")
            # 로딩 상태 해제
            if self.control_panel:
                self.control_panel.set_loading_state(False)
        finally:
            # 카메라 리소스 안전하게 해제
            try:
                if hasattr(self, 'cap') and self.cap and self.cap.isOpened():
                    self.cap.release()
                    self.cap = None
                    logger.info("카메라 리소스 해제됨")
            except Exception as e:
                logger.error(f"카메라 리소스 해제 중 오류: {e}")
            
            # 모든 OpenCV 창 닫기
            try:
                cv2.destroyAllWindows()
            except Exception as e:
                logger.error(f"OpenCV 창 닫기 중 오류: {e}")
            
            logger.info("카메라 디스플레이 루프 완전 종료")
    
    def _update_image(self, pil_image) -> None:
        """이미지 업데이트 (GUI 스레드에서 호출)"""
        try:
            # 디스플레이가 정지된 상태면 이미지 업데이트하지 않음
            if not self.is_displaying:
                return
                
            # 카메라 패널 크기에 맞게 이미지 조정
            resized_image = self._resize_to_fit(pil_image)
            self.camera_label.config(image=resized_image, text="")
            self.camera_label.image = resized_image  # 참조 유지
        except Exception as e:
            logger.error(f"이미지 업데이트 중 오류: {e}")
    
    def _resize_to_fit(self, pil_image) -> ImageTk.PhotoImage:
        """이미지를 카메라 패널에 딱 맞게 조정"""
        try:
            # 카메라 패널의 사용 가능한 크기 (패딩 제외)
            panel_width = 480  # 고정 크기
            panel_height = 360  # 고정 크기
            
            # 원본 이미지 크기
            original_width, original_height = pil_image.size
            
            # 비율 계산 (가로세로 비율 유지)
            width_ratio = panel_width / original_width
            height_ratio = panel_height / original_height
            scale_ratio = min(width_ratio, height_ratio)
            
            # 새로운 크기 계산
            new_width = int(original_width * scale_ratio)
            new_height = int(original_height * scale_ratio)
            
            # 이미지 리사이즈
            resized_pil = pil_image.resize((new_width, new_height), Image.Resampling.NEAREST)
            
            # PhotoImage로 변환
            return ImageTk.PhotoImage(resized_pil)
            
        except Exception as e:
            logger.error(f"이미지 리사이즈 중 오류: {e}")
            return ImageTk.PhotoImage(pil_image)
    
    def set_hand_tracker(self, hand_tracker) -> None:
        """
        손 트래커 설정
        
        Args:
            hand_tracker: 손 트래커 객체
        """
        self.hand_tracker = hand_tracker
        logger.info("카메라 패널에 손 트래커가 설정되었습니다.")
    
    def update_status(self, status: str, color: str = "black") -> None:
        """
        상태 업데이트
        
        Args:
            status: 상태 메시지
            color: 텍스트 색상
        """
        self.status_label.config(text=f"상태: {status}", foreground=color)
    
    def update_config(self) -> None:
        """설정 업데이트"""
        try:
            # 설정값은 항상 업데이트 (카메라 상태와 관계없이)
            logger.info("카메라 패널 설정이 업데이트되었습니다.")
            
            # 카메라가 열려있을 때만 카메라 하드웨어 설정 업데이트
            if (hasattr(self, 'cap') and 
                self.cap is not None and 
                hasattr(self.cap, 'isOpened') and 
                self.cap.isOpened()):
                
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.camera.width)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.camera.height)
                self.cap.set(cv2.CAP_PROP_FPS, config.camera.fps)
                logger.debug("카메라 하드웨어 설정이 업데이트되었습니다.")
            
        except Exception as e:
            logger.error(f"카메라 패널 설정 업데이트 실패: {e}") 