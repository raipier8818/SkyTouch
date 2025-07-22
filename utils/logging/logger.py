"""
Logging utilities for the Hand Tracking Trackpad application.
"""
import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


class AppLogger:
    """애플리케이션 로거"""
    
    def __init__(self, name: str = "HandTrackpad", log_file: Optional[str] = None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # 중복 핸들러 방지
        if not self.logger.handlers:
            self._setup_handlers(log_file)
    
    def _setup_handlers(self, log_file: Optional[str]) -> None:
        """로거 핸들러 설정"""
        # 콘솔 핸들러
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # 파일 핸들러 (선택적)
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
    
    def debug(self, message: str) -> None:
        """디버그 로그"""
        self.logger.debug(message)
    
    def info(self, message: str) -> None:
        """정보 로그"""
        self.logger.info(message)
    
    def warning(self, message: str) -> None:
        """경고 로그"""
        self.logger.warning(message)
    
    def error(self, message: str) -> None:
        """에러 로그"""
        self.logger.error(message)
    
    def critical(self, message: str) -> None:
        """치명적 에러 로그"""
        self.logger.critical(message)


# 전역 로거 인스턴스
def get_logger(name: str = "HandTrackpad") -> AppLogger:
    """로거 인스턴스 반환"""
    # PyInstaller로 빌드된 환경에서는 로그 파일 생성하지 않음
    import sys
    if getattr(sys, 'frozen', False):
        # PyInstaller로 빌드된 경우
        return AppLogger(name, None)
    else:
        # 개발 환경에서는 로그 파일 생성
        log_file = f"logs/hand_trackpad_{datetime.now().strftime('%Y%m%d')}.log"
        return AppLogger(name, log_file) 