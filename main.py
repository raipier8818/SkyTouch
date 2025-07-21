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
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app import HandTrackpadApp
from utils.logging.logger import get_logger
from exceptions.base import HandTrackpadError

logger = get_logger(__name__)


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