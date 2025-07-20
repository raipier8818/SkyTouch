#!/usr/bin/env python3
"""
Hand Tracking Trackpad Application

A desktop application that uses MediaPipe for hand tracking
to control mouse cursor and perform gestures.

Author: SkyTouch Team
Version: 1.0.0
"""

import sys
import os
import threading
import time
import cv2
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config import config
from src.utils.logger import get_logger
from src.utils.exceptions import HandTrackpadError
from src.core.hand_tracker import HandTracker
from src.core.mouse_controller import MouseController
from src.ui.main_window import MainWindow

logger = get_logger(__name__)


class HandTrackpadApp:
    """Hand Tracking Trackpad 메인 애플리케이션 클래스"""
    
    def __init__(self):
        """애플리케이션 초기화"""
        try:
            logger.info("Hand Tracking Trackpad 애플리케이션을 시작합니다.")
            
            # 핵심 컴포넌트 초기화
            self.hand_tracker = None
            self.mouse_controller = None
            self.main_window = None
            
            # 트래킹 상태
            self.tracking_active = False
            
            # 컴포넌트 초기화
            self.initialize_components()
            
            logger.info("애플리케이션이 성공적으로 초기화되었습니다.")
            
        except Exception as e:
            logger.error(f"애플리케이션 초기화 실패: {e}")
            raise HandTrackpadError(f"애플리케이션 초기화 실패: {e}")
    
    def initialize_components(self) -> None:
        """컴포넌트 초기화"""
        try:
            # 마우스 컨트롤러 초기화 (hand_tracker는 나중에 설정)
            self.mouse_controller = MouseController()
            
            # 메인 윈도우 초기화 (트래킹 콜백과 마우스 컨트롤러 전달)
            self.main_window = MainWindow(tracking_callback=self.tracking_loop, mouse_controller=self.mouse_controller)
            
            logger.info("모든 컴포넌트가 초기화되었습니다.")
            
        except Exception as e:
            logger.error(f"컴포넌트 초기화 실패: {e}")
            raise
    
    def tracking_loop(self) -> None:
        """손 트래킹 메인 루프"""
        try:
            logger.info("손 트래킹 루프를 시작합니다.")
            
            # 손 트래커 초기화 (카메라 없이)
            self.hand_tracker = HandTracker()
            
            # 마우스 컨트롤러에 hand_tracker 설정 (실제 웹캠 해상도 가져오기용)
            self.mouse_controller.hand_tracker = self.hand_tracker
            
            # 메인 윈도우에 손 트래커 전달
            self.main_window.hand_tracker = self.hand_tracker
            
            # 카메라 패널에 손 트래커 전달
            self.main_window.camera_panel.set_hand_tracker(self.hand_tracker)
            
            # 카메라는 GUI에서 처리하므로 여기서는 제스처 처리만
            while self.tracking_active:
                # CPU 사용량 조절
                time.sleep(0.01)
                
                # 트래킹 상태 확인
                if not self.tracking_active:
                    break
                
                logger.info("손 트래킹 루프가 종료되었습니다.")
                
        except Exception as e:
            logger.error(f"손 트래킹 루프 중 오류: {e}")
            self.main_window.status_panel.set_error_status(str(e))
        finally:
            # 리소스 정리
            if self.hand_tracker:
                self.hand_tracker = None
    
    def start_tracking(self) -> None:
        """트래킹 시작"""
        try:
            if not self.tracking_active:
                self.tracking_active = True
                logger.info("트래킹이 시작되었습니다.")
            
        except Exception as e:
            logger.error(f"트래킹 시작 실패: {e}")
            raise
    
    def stop_tracking(self) -> None:
        """트래킹 정지"""
        try:
            if self.tracking_active:
                self.tracking_active = False
                logger.info("트래킹이 정지되었습니다.")
            
        except Exception as e:
            logger.error(f"트래킹 정지 실패: {e}")
            raise
    
    def run(self) -> None:
        """애플리케이션 실행"""
        try:
            logger.info("애플리케이션을 실행합니다.")
            self.main_window.run()
            
        except Exception as e:
            logger.error(f"애플리케이션 실행 중 오류: {e}")
            raise HandTrackpadError(f"애플리케이션 실행 실패: {e}")
        finally:
            logger.info("애플리케이션이 종료되었습니다.")


def main():
    """메인 함수"""
    try:
        # 애플리케이션 생성 및 실행
        app = HandTrackpadApp()
        app.run()
        
    except KeyboardInterrupt:
        logger.info("사용자에 의해 애플리케이션이 중단되었습니다.")
        sys.exit(0)
        
    except HandTrackpadError as e:
        logger.error(f"애플리케이션 오류: {e}")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"예상치 못한 오류: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 