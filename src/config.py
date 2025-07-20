"""
Configuration settings for the Hand Tracking Trackpad application.
"""
from dataclasses import dataclass
from typing import Tuple
import json
import os
from pathlib import Path


@dataclass
class CameraConfig:
    """카메라 설정"""
    width: int = 480
    height: int = 360
    fps: int = 30
    device_id: int = 0


@dataclass
class HandTrackingConfig:
    """손 트래킹 설정"""
    max_num_hands: int = 1
    min_detection_confidence: float = 0.7
    min_tracking_confidence: float = 0.5
    static_image_mode: bool = False


@dataclass
class GestureConfig:
    """제스처 설정"""
    click_threshold: float = 0.08

    swipe_threshold: float = 0.03  # 스와이프 임계값 (더 낮춤)
    swipe_time_limit: float = 1.0  # 스와이프 시간 제한 (초)
    swipe_cooldown: float = 1.5  # 스와이프 쿨타임 (초)
    mode_stabilization_time: float = 0.8  # 모드 안정화 시간 (초)
    scroll_threshold: float = 0.1  # 스크롤 임계값
    smoothing_factor: float = 0.5
    sensitivity: float = 1.0

    invert_x: bool = False  # X축 좌우 반전
    invert_y: bool = False  # Y축 상하 반전


@dataclass
class UIConfig:
    """UI 설정"""
    window_width: int = 520
    window_height: int = 800
    theme: str = "clam"
    font_family: str = "Arial"
    title: str = "Hand Tracking Trackpad"
    debug_mode: bool = False


class ConfigManager:
    """설정 관리자"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.camera = CameraConfig()
        self.hand_tracking = HandTrackingConfig()
        self.gesture = GestureConfig()
        self.ui = UIConfig()
        
        self.load_config()
    
    def load_config(self) -> None:
        """설정 파일에서 설정 로드"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # 각 설정 섹션 업데이트
                if 'camera' in data:
                    self._update_dataclass(self.camera, data['camera'])
                if 'hand_tracking' in data:
                    self._update_dataclass(self.hand_tracking, data['hand_tracking'])
                if 'gesture' in data:
                    self._update_dataclass(self.gesture, data['gesture'])
                if 'ui' in data:
                    self._update_dataclass(self.ui, data['ui'])
                    
            except (json.JSONDecodeError, KeyError) as e:
                print(f"설정 파일 로드 중 오류: {e}")
    
    def save_config(self) -> None:
        """현재 설정을 파일에 저장"""
        try:
            config_data = {
                'camera': self._dataclass_to_dict(self.camera),
                'hand_tracking': self._dataclass_to_dict(self.hand_tracking),
                'gesture': self._dataclass_to_dict(self.gesture),
                'ui': self._dataclass_to_dict(self.ui)
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"설정 파일 저장 중 오류: {e}")
    
    def _update_dataclass(self, dataclass_obj, data: dict) -> None:
        """딕셔너리 데이터로 dataclass 업데이트"""
        for key, value in data.items():
            if hasattr(dataclass_obj, key):
                setattr(dataclass_obj, key, value)
    
    def _dataclass_to_dict(self, dataclass_obj) -> dict:
        """dataclass를 딕셔너리로 변환"""
        return {field: getattr(dataclass_obj, field) 
                for field in dataclass_obj.__dataclass_fields__}


# 전역 설정 인스턴스
config = ConfigManager() 