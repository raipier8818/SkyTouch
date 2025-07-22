"""
Debug panel for displaying log messages in real-time.
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, QHBoxLayout, 
                             QPushButton, QLabel, QComboBox)
from PyQt5.QtCore import QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QFont, QTextCursor, QTextCharFormat, QColor
import logging
import queue
import threading
from datetime import datetime

from ui.styles.style_manager import StyleManager
from utils.logging.logger import get_logger

logger = get_logger(__name__)


class LogHandler(QObject, logging.Handler):
    """로그 메시지를 UI로 전달하는 핸들러"""
    log_signal = pyqtSignal(str, str, str, str)  # message, level, module, timestamp
    
    def __init__(self):
        super().__init__()
        self.queue = queue.Queue()
        self.thread = threading.Thread(target=self._process_logs, daemon=True)
        self.thread.start()
    
    def emit(self, record):
        """로그 레코드를 큐에 추가"""
        try:
            msg = self.format(record)
            level = record.levelname
            module = record.name
            timestamp = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")
            self.queue.put((msg, level, module, timestamp))
        except Exception:
            self.handleError(record)
    
    def _process_logs(self):
        """백그라운드에서 로그 메시지 처리"""
        while True:
            try:
                msg, level, module, timestamp = self.queue.get(timeout=1)
                self.log_signal.emit(msg, level, module, timestamp)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"로그 처리 오류: {e}")


class DebugPanel(QWidget):
    """디버그 패널 클래스"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SkyTouch 디버그 패널")
        self.resize(700, 450)
        
        # 스타일 적용
        self.style_manager = StyleManager()
        self.style_manager.apply_theme_to_widget(self, "dark_theme")
        
        # 필터 설정
        self.log_level_filter = "INFO"
        self.auto_scroll_enabled = True
        
        self._setup_ui()
        self._setup_logging()
        
        # 자동 스크롤 타이머
        self.scroll_timer = QTimer()
        self.scroll_timer.timeout.connect(self._auto_scroll)
        self.scroll_timer.start(100)  # 100ms마다 체크
    
    def _setup_ui(self):
        """UI 설정"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # 헤더
        header_layout = QHBoxLayout()
        title_label = QLabel("디버그 로그")
        title_label.setObjectName("DebugTitle")
        header_layout.addWidget(title_label)
        
        # 로그 레벨 필터
        level_label = QLabel("로그 레벨:")
        header_layout.addWidget(level_label)
        
        self.level_combo = QComboBox()
        self.level_combo.addItems(["ALL", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.level_combo.setCurrentText("INFO")  # 기본값을 INFO로 설정
        self.level_combo.currentTextChanged.connect(self._on_level_changed)
        header_layout.addWidget(self.level_combo)
        
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # 컨트롤 버튼들
        control_layout = QHBoxLayout()
        
        self.clear_btn = QPushButton("로그 지우기")
        self.clear_btn.setObjectName("DebugButton")
        self.clear_btn.clicked.connect(self.clear_logs)
        control_layout.addWidget(self.clear_btn)
        
        self.auto_scroll_btn = QPushButton("자동 스크롤 ON")
        self.auto_scroll_btn.setObjectName("DebugButton")
        self.auto_scroll_btn.setCheckable(True)
        self.auto_scroll_btn.setChecked(True)
        self.auto_scroll_btn.toggled.connect(self._on_auto_scroll_toggled)
        control_layout.addWidget(self.auto_scroll_btn)
        
        self.pause_btn = QPushButton("일시정지")
        self.pause_btn.setObjectName("DebugButton")
        self.pause_btn.setCheckable(True)
        self.pause_btn.clicked.connect(self._on_pause_toggled)
        control_layout.addWidget(self.pause_btn)
        
        control_layout.addStretch()
        
        # 통계 정보
        self.stats_label = QLabel("총 로그: 0 | 표시: 0")
        self.stats_label.setObjectName("DebugStats")
        control_layout.addWidget(self.stats_label)
        
        layout.addLayout(control_layout)
        
        # 로그 텍스트 영역
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 9))
        self.log_text.setObjectName("DebugTextEdit")
        layout.addWidget(self.log_text)
        
        # 상태 표시줄
        self.status_label = QLabel("로그 대기 중...")
        self.status_label.setObjectName("DebugStatus")
        layout.addWidget(self.status_label)
        
        # 통계 변수
        self.total_logs = 0
        self.displayed_logs = 0
    
    def _setup_logging(self):
        """로깅 설정"""
        self.log_handler = LogHandler()
        self.log_handler.log_signal.connect(self._add_log_message)
        
        # 포맷터 설정
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.log_handler.setFormatter(formatter)
        self.log_handler.setLevel(logging.DEBUG)
        
        # 루트 로거에 핸들러 추가
        root_logger = logging.getLogger()
        root_logger.addHandler(self.log_handler)
        root_logger.setLevel(logging.DEBUG)
        
        # 시작 메시지
        self._add_log_message("디버그 패널이 시작되었습니다.", "INFO", "debug_panel", datetime.now().strftime("%H:%M:%S"))
    
    def _add_log_message(self, message, level, module, timestamp):
        """로그 메시지 추가"""
        self.total_logs += 1
        
        # 레벨 필터링 체크
        if not self._should_display_log(level):
            self._update_stats()
            return
        
        self.displayed_logs += 1
        
        # 로그 레벨에 따른 색상 설정
        color = self._get_level_color(level)
        
        # 텍스트 에디터에 추가
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.log_text.setTextCursor(cursor)
        
        # 색상 적용
        format = QTextCharFormat()
        format.setForeground(color)
        self.log_text.setCurrentCharFormat(format)
        
        # 간단한 형식으로 표시
        if level == "DEBUG":
            # DEBUG 로그는 더 간단하게 표시
            short_message = message.split(" - ")[-1] if " - " in message else message
            formatted_message = f"[{timestamp}] {short_message}\n"
        else:
            formatted_message = f"[{timestamp}] [{level}] {module}: {message.split(' - ')[-1]}\n"
        
        self.log_text.insertPlainText(formatted_message)
        
        # 상태 업데이트
        self.status_label.setText(f"마지막 업데이트: {timestamp}")
        self._update_stats()
    
    def _should_display_log(self, level):
        """로그 표시 여부 결정 (레벨만 체크)"""
        if self.log_level_filter == "ALL":
            return True
        
        level_priority = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3, "CRITICAL": 4}
        filter_priority = level_priority.get(self.log_level_filter, 0)
        log_priority = level_priority.get(level, 0)
        
        return log_priority >= filter_priority
    
    def _get_level_color(self, level):
        """로그 레벨에 따른 색상 반환"""
        colors = {
            "DEBUG": QColor(128, 128, 128),    # 회색
            "INFO": QColor(255, 255, 255),     # 흰색
            "WARNING": QColor(255, 255, 0),    # 노란색
            "ERROR": QColor(255, 128, 128),    # 빨간색
            "CRITICAL": QColor(255, 0, 0)      # 진한 빨간색
        }
        return colors.get(level, QColor(255, 255, 255))
    
    def _on_level_changed(self, level):
        """로그 레벨 필터 변경"""
        self.log_level_filter = level
        self._update_stats()
    
    def _on_auto_scroll_toggled(self, checked):
        """자동 스크롤 토글"""
        self.auto_scroll_enabled = checked
        # 버튼 텍스트 업데이트
        if checked:
            self.auto_scroll_btn.setText("자동 스크롤 ON")
        else:
            self.auto_scroll_btn.setText("자동 스크롤 OFF")
    
    def _on_pause_toggled(self, checked):
        """일시정지 토글"""
        if checked:
            self.pause_btn.setText("재개")
            self.log_handler.log_signal.disconnect()
        else:
            self.pause_btn.setText("일시정지")
            self.log_handler.log_signal.connect(self._add_log_message)
    
    def _update_stats(self):
        """통계 정보 업데이트"""
        self.stats_label.setText(f"총 로그: {self.total_logs} | 표시: {self.displayed_logs}")
    
    def _auto_scroll(self):
        """자동 스크롤"""
        if self.auto_scroll_enabled and self.auto_scroll_btn.isChecked():
            scrollbar = self.log_text.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
    
    def clear_logs(self):
        """로그 지우기"""
        self.log_text.clear()
        self.total_logs = 0
        self.displayed_logs = 0
        self._add_log_message("로그가 지워졌습니다.", "INFO", "debug_panel", datetime.now().strftime("%H:%M:%S"))
    
    def closeEvent(self, event):
        """창 닫기 이벤트"""
        # 로그 핸들러 제거
        root_logger = logging.getLogger()
        root_logger.removeHandler(self.log_handler)
        event.accept() 