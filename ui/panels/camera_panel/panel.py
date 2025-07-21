"""
Camera panel for SkyTouch application.
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
import cv2
import threading
import time
import numpy as np

from utils.logging.logger import get_logger

logger = get_logger(__name__)


class CameraPanel(QWidget):
    """카메라 패널 클래스"""
    
    def __init__(self, app_logic, parent=None):
        super().__init__(parent)
        self.app_logic = app_logic
        self.layout = QVBoxLayout(self)
        self.camera_label = QLabel("카메라 화면")
        self.camera_label.setObjectName("CameraLabel")
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.camera_label)
        self.setLayout(self.layout)
        
        # 카메라 관련 변수
        self.is_displaying = False
        self.display_thread = None
        
        # 컴포넌트 참조
        self.hand_detector = app_logic.hand_detector
        self.gesture_detector = app_logic.gesture_detector
        self.mouse_controller = app_logic.mouse_controller

    def start_display(self):
        """카메라 표시 시작"""
        if not self.is_displaying:
            self.is_displaying = True
            self.display_thread = threading.Thread(target=self.display_loop, daemon=True)
            self.display_thread.start()
            logger.info("카메라 표시가 시작되었습니다.")

    def stop_display(self):
        """카메라 표시 정지"""
        self.is_displaying = False
        # 스레드가 완전히 종료될 때까지 기다림
        if self.display_thread and self.display_thread.is_alive():
            self.display_thread.join(timeout=1.0)  # 최대 1초 대기
        # 초기 화면으로 복원
        self.camera_label.setText("카메라 화면")
        self.camera_label.setPixmap(QPixmap())  # 픽스맵 초기화
        logger.info("카메라 표시가 정지되었습니다.")

    def display_loop(self):
        """카메라 표시 루프"""
        while self.is_displaying:
            frame = self.app_logic.get_camera_frame()
            if frame is not None:
                # 1. 손 인식 (원본 프레임)
                hand_landmarks_list = self.hand_detector.detect_hands(frame)
                if hand_landmarks_list:
                    for hand_landmarks in hand_landmarks_list:
                        # 2. 랜드마크 그리기 (원본 프레임)
                        frame = self.hand_detector.draw_landmarks(frame, hand_landmarks)
                        # 3. 제스처 인식
                        gesture_data = self.gesture_detector.detect_gestures(hand_landmarks)
                        # 4. 마우스 제어
                        self.mouse_controller.update_mouse_position(
                            gesture_data.palm_center,
                            gesture_mode=gesture_data.gesture_mode,
                            smoothing=0.5,
                            sensitivity=1.5,
                            invert_x=False,
                            invert_y=False
                        )
                        self.mouse_controller.handle_click(gesture_data.is_clicking)
                        self.mouse_controller.handle_right_click(gesture_data.is_right_clicking)
                        self.mouse_controller.handle_double_click(gesture_data.is_double_clicking)
                        self.mouse_controller.handle_scroll(gesture_data.is_scrolling, gesture_data.scroll_direction)
                        self.mouse_controller.handle_swipe(gesture_data.is_swiping, gesture_data.swipe_direction)
                
                # 3. 마지막에만 좌우반전
                frame = np.fliplr(frame)
                # 5. 화면 표시
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_frame.shape
                bytes_per_line = ch * w
                qt_img = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qt_img)
                self.camera_label.setPixmap(
                    pixmap.scaled(
                        self.camera_label.width(),
                        self.camera_label.height(),
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                )
            time.sleep(1/30)
        
        # 루프 종료 시 초기 화면으로 복원 및 카메라 리소스 해제
        self.camera_label.setText("카메라 화면")
        self.camera_label.setPixmap(QPixmap())
        # 카메라 리소스 해제 (스레드 종료 시)
        if hasattr(self.app_logic, 'camera_capture') and self.app_logic.camera_capture:
            self.app_logic.camera_capture.release()
            logger.info("카메라 리소스가 해제되었습니다.") 