from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QDialog, QLineEdit, QFormLayout, QTabWidget, QCheckBox, QComboBox, QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
import cv2
import threading
import time
import numpy as np

from ui.styles.style_manager import StyleManager

class SettingsDialog(QDialog):
    def __init__(self, app_logic, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SkyTouch 설정")
        self.resize(400, 200)
        self.app_logic = app_logic
        self.config_manager = app_logic.config_manager
        layout = QVBoxLayout(self)
        tabs = QTabWidget()
        tabs.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # 카메라 탭
        cam_tab = QWidget()
        cam_form = QFormLayout(cam_tab)
        cam_cfg = self.config_manager.get_camera_config()
        self.camera_width = QLineEdit(str(cam_cfg.get('width', '')))
        self.camera_height = QLineEdit(str(cam_cfg.get('height', '')))
        self.fps = QLineEdit(str(cam_cfg.get('fps', '')))
        self.device_id = QLineEdit(str(cam_cfg.get('device_id', '')))
        cam_form.addRow("해상도 (너비)", self.camera_width)
        cam_form.addRow("해상도 (높이)", self.camera_height)
        cam_form.addRow("FPS", self.fps)
        cam_form.addRow("장치 ID", self.device_id)
        tabs.addTab(cam_tab, "카메라")

        # 손 트래킹 탭
        hand_tab = QWidget()
        hand_form = QFormLayout(hand_tab)
        hand_cfg = self.config_manager.get_hand_tracking_config()
        self.max_hands = QLineEdit(str(hand_cfg.get('max_num_hands', '')))
        self.detection_conf = QLineEdit(str(hand_cfg.get('min_detection_confidence', '')))
        self.tracking_conf = QLineEdit(str(hand_cfg.get('min_tracking_confidence', '')))
        hand_form.addRow("최대 손 개수", self.max_hands)
        hand_form.addRow("감지 신뢰도", self.detection_conf)
        hand_form.addRow("추적 신뢰도", self.tracking_conf)
        tabs.addTab(hand_tab, "손 트래킹")

        # 제스처 탭
        gesture_tab = QWidget()
        gesture_form = QFormLayout(gesture_tab)
        gesture_cfg = self.config_manager.get_gesture_config()
        self.click_threshold = QLineEdit(str(gesture_cfg.get('click_threshold', '')))
        self.sensitivity = QLineEdit(str(gesture_cfg.get('sensitivity', '')))
        self.smoothing = QLineEdit(str(gesture_cfg.get('smoothing_factor', '')))
        self.invert_x = QCheckBox(); self.invert_x.setChecked(gesture_cfg.get('invert_x', False))
        self.invert_y = QCheckBox(); self.invert_y.setChecked(gesture_cfg.get('invert_y', False))
        self.finger_threshold = QLineEdit(str(gesture_cfg.get('finger_threshold', '')))
        gesture_form.addRow("클릭 임계값", self.click_threshold)
        gesture_form.addRow("감도", self.sensitivity)
        gesture_form.addRow("스무딩 팩터", self.smoothing)
        gesture_form.addRow("X축 반전", self.invert_x)
        gesture_form.addRow("Y축 반전", self.invert_y)
        gesture_form.addRow("손가락 임계값", self.finger_threshold)
        tabs.addTab(gesture_tab, "제스처")

        # 모드별 탭
        mode_tab = QWidget()
        mode_layout = QVBoxLayout(mode_tab)
        mode_tabs = QTabWidget()
        # 클릭 모드
        self.click_threshold_mode = QLineEdit(str(gesture_cfg.get('click_threshold', '')))
        self.double_click_time = QLineEdit(str(gesture_cfg.get('double_click_time', '')))
        self.click_stabilization_time = QLineEdit(str(gesture_cfg.get('mode_stabilization_time', '')))
        click_tab = QWidget()
        click_form = QFormLayout(click_tab)
        click_form.addRow("[클릭] 임계값", self.click_threshold_mode)
        click_form.addRow("[클릭] 더블클릭 시간", self.double_click_time)
        click_form.addRow("[클릭] 모드 안정화 시간", self.click_stabilization_time)
        mode_tabs.addTab(click_tab, "클릭")
        # 스크롤 모드
        self.scroll_distance_threshold = QLineEdit(str(gesture_cfg.get('scroll_distance_threshold', '')))
        self.scroll_required_frames = QLineEdit(str(gesture_cfg.get('scroll_required_frames', '')))
        self.invert_scroll_x = QCheckBox(); self.invert_scroll_x.setChecked(gesture_cfg.get('invert_scroll_x', False))
        self.invert_scroll_y = QCheckBox(); self.invert_scroll_y.setChecked(gesture_cfg.get('invert_scroll_y', False))
        scroll_tab = QWidget()
        scroll_form = QFormLayout(scroll_tab)
        scroll_form.addRow("[스크롤] 거리 임계값", self.scroll_distance_threshold)
        scroll_form.addRow("[스크롤] 필요 프레임", self.scroll_required_frames)
        scroll_form.addRow("[스크롤] X축 반전", self.invert_scroll_x)
        scroll_form.addRow("[스크롤] Y축 반전", self.invert_scroll_y)
        mode_tabs.addTab(scroll_tab, "스크롤")
        # 스와이프 모드
        self.swipe_distance_threshold = QLineEdit(str(gesture_cfg.get('swipe_distance_threshold', '')))
        self.swipe_required_frames = QLineEdit(str(gesture_cfg.get('swipe_required_frames', '')))
        self.swipe_cooldown = QLineEdit(str(gesture_cfg.get('swipe_cooldown', '')))
        self.invert_swipe_x = QCheckBox(); self.invert_swipe_x.setChecked(gesture_cfg.get('invert_swipe_x', False))
        self.invert_swipe_y = QCheckBox(); self.invert_swipe_y.setChecked(gesture_cfg.get('invert_swipe_y', False))
        swipe_tab = QWidget()
        swipe_form = QFormLayout(swipe_tab)
        swipe_form.addRow("[스와이프] 거리 임계값", self.swipe_distance_threshold)
        swipe_form.addRow("[스와이프] 필요 프레임", self.swipe_required_frames)
        swipe_form.addRow("[스와이프] 쿨타임", self.swipe_cooldown)
        swipe_form.addRow("[스와이프] X축 반전", self.invert_swipe_x)
        swipe_form.addRow("[스와이프] Y축 반전", self.invert_swipe_y)
        mode_tabs.addTab(swipe_tab, "스와이프")
        # 이동 모드
        self.move_stabilization_time = QLineEdit(str(gesture_cfg.get('mode_stabilization_time', '')))
        self.min_movement_threshold = QLineEdit(str(gesture_cfg.get('min_movement_threshold', '')))
        move_tab = QWidget()
        move_form = QFormLayout(move_tab)
        move_form.addRow("[이동] 모드 안정화 시간", self.move_stabilization_time)
        move_form.addRow("[이동] 최소 이동 임계값", self.min_movement_threshold)
        mode_tabs.addTab(move_tab, "이동")
        mode_layout.addWidget(mode_tabs)
        tabs.addTab(mode_tab, "모드별")

        # UI 탭
        ui_tab = QWidget()
        ui_form = QFormLayout(ui_tab)
        ui_cfg = self.config_manager.get_ui_config()
        self.window_width = QLineEdit(str(ui_cfg.get('window_width', '')))
        self.window_height = QLineEdit(str(ui_cfg.get('window_height', '')))
        self.theme = QComboBox(); self.theme.addItems(["clam", "alt", "default", "classic"]); self.theme.setCurrentText(ui_cfg.get('theme', 'clam'))
        self.font_family = QLineEdit(str(ui_cfg.get('font_family', '')))
        self.title = QLineEdit(str(ui_cfg.get('title', '')))
        self.debug_mode = QCheckBox(); self.debug_mode.setChecked(ui_cfg.get('debug_mode', False))
        ui_form.addRow("윈도우 너비", self.window_width)
        ui_form.addRow("윈도우 높이", self.window_height)
        ui_form.addRow("테마", self.theme)
        ui_form.addRow("폰트", self.font_family)
        ui_form.addRow("타이틀", self.title)
        ui_form.addRow("디버그 모드", self.debug_mode)
        tabs.addTab(ui_tab, "UI")

        layout.addWidget(tabs)
        save_btn = QPushButton("저장")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)
        self.setLayout(layout)
    def save_settings(self):
        cam_cfg = self.config_manager.get_camera_config()
        cam_cfg['width'] = int(self.camera_width.text())
        cam_cfg['height'] = int(self.camera_height.text())
        cam_cfg['fps'] = int(self.fps.text())
        cam_cfg['device_id'] = int(self.device_id.text())
        hand_cfg = self.config_manager.get_hand_tracking_config()
        hand_cfg['max_num_hands'] = int(self.max_hands.text())
        hand_cfg['min_detection_confidence'] = float(self.detection_conf.text())
        hand_cfg['min_tracking_confidence'] = float(self.tracking_conf.text())
        gesture_cfg = self.config_manager.get_gesture_config()
        gesture_cfg['click_threshold'] = float(self.click_threshold.text())
        gesture_cfg['sensitivity'] = float(self.sensitivity.text())
        gesture_cfg['smoothing_factor'] = float(self.smoothing.text())
        gesture_cfg['invert_x'] = self.invert_x.isChecked()
        gesture_cfg['invert_y'] = self.invert_y.isChecked()
        gesture_cfg['finger_threshold'] = float(self.finger_threshold.text())
        gesture_cfg['double_click_time'] = float(self.double_click_time.text())
        gesture_cfg['mode_stabilization_time'] = float(self.click_stabilization_time.text())
        gesture_cfg['scroll_distance_threshold'] = float(self.scroll_distance_threshold.text())
        gesture_cfg['scroll_required_frames'] = int(self.scroll_required_frames.text())
        gesture_cfg['invert_scroll_x'] = self.invert_scroll_x.isChecked()
        gesture_cfg['invert_scroll_y'] = self.invert_scroll_y.isChecked()
        gesture_cfg['swipe_distance_threshold'] = float(self.swipe_distance_threshold.text())
        gesture_cfg['swipe_required_frames'] = int(self.swipe_required_frames.text())
        gesture_cfg['swipe_cooldown'] = float(self.swipe_cooldown.text())
        gesture_cfg['invert_swipe_x'] = self.invert_swipe_x.isChecked()
        gesture_cfg['invert_swipe_y'] = self.invert_swipe_y.isChecked()
        gesture_cfg['min_movement_threshold'] = float(self.min_movement_threshold.text())
        ui_cfg = self.config_manager.get_ui_config()
        ui_cfg['window_width'] = int(self.window_width.text())
        ui_cfg['window_height'] = int(self.window_height.text())
        ui_cfg['theme'] = self.theme.currentText()
        ui_cfg['font_family'] = self.font_family.text()
        ui_cfg['title'] = self.title.text()
        ui_cfg['debug_mode'] = self.debug_mode.isChecked()
        self.config_manager.save_config()
        self.accept()

class CameraPanel(QWidget):
    def __init__(self, app_logic, parent=None):
        super().__init__(parent)
        self.app_logic = app_logic
        self.layout = QVBoxLayout(self)
        self.camera_label = QLabel("카메라 화면")
        self.camera_label.setObjectName("CameraLabel")
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.camera_label)
        self.setLayout(self.layout)
        self.is_displaying = False
        self.display_thread = None
        self.hand_detector = app_logic.hand_detector
        self.gesture_detector = app_logic.gesture_detector
        self.mouse_controller = app_logic.mouse_controller

    def start_display(self):
        if not self.is_displaying:
            self.is_displaying = True
            self.display_thread = threading.Thread(target=self.display_loop, daemon=True)
            self.display_thread.start()

    def stop_display(self):
        self.is_displaying = False
        # 카메라 리소스 완전 해제
        if hasattr(self.app_logic, 'camera_capture') and self.app_logic.camera_capture:
            self.app_logic.camera_capture.release()
        # 초기 화면으로 복원
        self.camera_label.setText("카메라 화면")
        self.camera_label.setPixmap(QPixmap())  # 픽스맵 초기화

    def display_loop(self):
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
        # 카메라 리소스 해제
        if hasattr(self.app_logic, 'camera_capture') and self.app_logic.camera_capture:
            self.app_logic.camera_capture.release()

class IOSMainWindow(QMainWindow):
    def __init__(self, app_logic):
        super().__init__()
        self.app_logic = app_logic
        # self.setWindowTitle("SkyTouch")
        self.setMinimumSize(400, 500)
        
        # 윈도우 투명도 설정
        self.setWindowOpacity(0.9)  # 90% 투명도
        self.setAttribute(Qt.WA_TranslucentBackground, True)  # 배경 투명화
        
        # 스타일 관리자 초기화 및 테마 적용
        self.style_manager = StyleManager()
        self.style_manager.apply_theme_to_widget(self, "dark_theme")
        
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(4)  # 간격 줄임
        main_layout.setContentsMargins(8, 8, 8, 8)  # 여백 줄임

        # 제목 라벨 제거

        self.camera_panel = CameraPanel(app_logic)
        main_layout.addWidget(self.camera_panel, 1)  # stretch=1

        # 트래킹 제어 버튼 추가
        self.tracking_btn = QPushButton("트래킹 시작")
        self.tracking_btn.setObjectName("SettingsButton")
        self.tracking_btn.clicked.connect(self.toggle_tracking)
        main_layout.addWidget(self.tracking_btn, 0)  # stretch=0

        self.settings_btn = QPushButton("설정")
        self.settings_btn.setObjectName("SettingsButton")
        self.settings_btn.clicked.connect(lambda: self.open_settings(app_logic))
        main_layout.addWidget(self.settings_btn, 0)  # stretch=0
        self.setCentralWidget(main_widget)
        
        # 트래킹 상태
        self.is_tracking = False
    
    def toggle_tracking(self):
        """트래킹 시작/중지 토글"""
        if not self.is_tracking:
            # 트래킹 시작
            self.app_logic.start_tracking()
            self.tracking_btn.setText("트래킹 중지")
            self.is_tracking = True
        else:
            # 트래킹 중지
            self.app_logic.stop_tracking()
            self.tracking_btn.setText("트래킹 시작")
            self.is_tracking = False
    
    def open_settings(self, app_logic):
        dlg = SettingsDialog(app_logic, self)
        dlg.exec_() 