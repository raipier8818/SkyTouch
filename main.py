#!/usr/bin/env python3
"""
SkyTouch Application

A desktop application that uses MediaPipe for hand tracking
to control mouse cursor and perform gestures.

Author: SkyTouch Team
Version: 1.0.0
"""

import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app import SkyTouchApp
from utils.logging.logger import get_logger
from exceptions.base import HandTrackpadError

logger = get_logger(__name__)


def main():
    """메인 함수"""
    try:
        # QApplication 생성 (PyQt5 앱 아이콘 설정을 위해)
        qt_app = QApplication(sys.argv)
        
        # 앱 아이콘 설정
        icon_path = project_root / "SkyTouch.icns"
        if icon_path.exists():
            qt_app.setWindowIcon(QIcon(str(icon_path)))
            logger.info("앱 아이콘이 설정되었습니다.")
        else:
            # .icns 파일이 없으면 PNG 파일 시도
            png_icon_path = project_root / "asset" / "icons" / "1024.png"
            if png_icon_path.exists():
                qt_app.setWindowIcon(QIcon(str(png_icon_path)))
                logger.info("PNG 아이콘이 설정되었습니다.")
            else:
                logger.warning("아이콘 파일을 찾을 수 없습니다.")
        
        # 애플리케이션 생성 및 실행
        app = SkyTouchApp()
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