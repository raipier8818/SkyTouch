"""
Style manager for SkyTouch application.
"""
import os
from pathlib import Path

from utils.logging.logger import get_logger

logger = get_logger(__name__)


class StyleManager:
    """스타일 관리자 클래스"""
    
    def __init__(self):
        self.styles_dir = Path(__file__).parent
        self.current_theme = "dark_theme"
    
    def load_theme(self, theme_name: str = "dark_theme") -> str:
        """
        테마 파일 로드
        
        Args:
            theme_name: 테마 이름
            
        Returns:
            QSS 스타일 문자열
        """
        try:
            theme_file = self.styles_dir / f"{theme_name}.qss"
            
            if not theme_file.exists():
                logger.warning(f"테마 파일을 찾을 수 없습니다: {theme_file}")
                return self._get_default_style()
            
            with open(theme_file, 'r', encoding='utf-8') as f:
                style = f.read()
            
            self.current_theme = theme_name
            logger.info(f"테마가 로드되었습니다: {theme_name}")
            return style
            
        except Exception as e:
            logger.error(f"테마 로드 실패: {e}")
            return self._get_default_style()
    
    def _get_default_style(self) -> str:
        """기본 스타일 반환"""
        return """
        QMainWindow {
            background-color: #101114;
        }
        QWidget {
            font-family: 'SF Pro Text', 'Helvetica Neue', 'Arial', sans-serif;
            color: #E6E6E6;
            border: none;
        }
        """
    
    def get_available_themes(self) -> list:
        """사용 가능한 테마 목록 반환"""
        themes = []
        for file in self.styles_dir.glob("*.qss"):
            themes.append(file.stem)
        return themes
    
    def apply_theme_to_widget(self, widget, theme_name: str = "dark_theme") -> None:
        """
        위젯에 테마 적용
        
        Args:
            widget: 적용할 위젯
            theme_name: 테마 이름
        """
        try:
            style = self.load_theme(theme_name)
            widget.setStyleSheet(style)
            logger.info(f"테마가 위젯에 적용되었습니다: {theme_name}")
            
        except Exception as e:
            logger.error(f"테마 적용 실패: {e}")
    
    def get_color_palette(self, theme_name: str = "dark_theme") -> dict:
        """테마별 색상 팔레트 반환"""
        palettes = {
            "dark_theme": {
                "background": "#101114",
                "surface": "#1C1D21",
                "primary": "#0A84FF",
                "secondary": "#323337",
                "text": "#E6E6E6",
                "text_secondary": "#8A8B90",
                "border": "#3A3B3F"
            }
        }
        return palettes.get(theme_name, palettes["dark_theme"]) 