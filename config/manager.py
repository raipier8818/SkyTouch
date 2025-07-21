"""
Configuration manager for Hand Tracking Trackpad application.
"""
import json
from pathlib import Path
from typing import Dict, Any

from .defaults import DEFAULT_CONFIG
from utils.logging.logger import get_logger
from exceptions.base import ConfigError

logger = get_logger(__name__)


class ConfigManager:
    """설정 관리자"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.config = DEFAULT_CONFIG.copy()
        self.load_config()
    
    def load_config(self) -> None:
        """설정 파일에서 설정 로드"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                
                # 각 설정 섹션 업데이트
                for section in file_config:
                    if section in self.config:
                        self.config[section].update(file_config[section])
                
                logger.info(f"설정 파일을 로드했습니다: {self.config_file}")
                
            except (json.JSONDecodeError, KeyError) as e:
                logger.error(f"설정 파일 로드 중 오류: {e}")
                raise ConfigError(f"설정 파일 로드 실패: {e}")
        else:
            logger.info("설정 파일이 없어 기본 설정을 사용합니다.")
    
    def save_config(self) -> None:
        """현재 설정을 파일에 저장"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"설정을 저장했습니다: {self.config_file}")
            
        except Exception as e:
            logger.error(f"설정 파일 저장 중 오류: {e}")
            raise ConfigError(f"설정 파일 저장 실패: {e}")
    
    def get_camera_config(self) -> Dict[str, Any]:
        """카메라 설정 반환"""
        return self.config.get('camera', DEFAULT_CONFIG['camera'])
    
    def get_hand_tracking_config(self) -> Dict[str, Any]:
        """손 트래킹 설정 반환"""
        return self.config.get('hand_tracking', DEFAULT_CONFIG['hand_tracking'])
    
    def get_gesture_config(self) -> Dict[str, Any]:
        """제스처 설정 반환"""
        return self.config.get('gesture', DEFAULT_CONFIG['gesture'])
    
    def get_ui_config(self) -> Dict[str, Any]:
        """UI 설정 반환"""
        return self.config.get('ui', DEFAULT_CONFIG['ui'])
    
    def update_config(self, section: str, key: str, value: Any) -> None:
        """설정 업데이트"""
        if section in self.config:
            self.config[section][key] = value
            logger.debug(f"설정 업데이트: {section}.{key} = {value}")
        else:
            raise ConfigError(f"알 수 없는 설정 섹션: {section}")
    
    def get_config(self) -> Dict[str, Any]:
        """전체 설정 반환"""
        return self.config.copy()
    
    def reset_to_defaults(self) -> None:
        """기본 설정으로 초기화"""
        self.config = DEFAULT_CONFIG.copy()
        logger.info("설정을 기본값으로 초기화했습니다.") 