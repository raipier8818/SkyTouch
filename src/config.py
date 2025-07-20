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
    frame_delay: float = 0.03  # 프레임 간 딜레이 (초) - 약 30 FPS


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
    # 클릭 모드 설정
    click_threshold: float = 0.12  # 클릭 감지 임계값 (더 큰 값으로 조정)
    
    # 스크롤 모드 설정
    scroll_distance_threshold: float = 0.003  # 스크롤 감지 최소 거리
    scroll_required_frames: int = 1  # 스크롤 감지에 필요한 연속 프레임 수
    
    # 스와이프 모드 설정
    swipe_distance_threshold: float = 0.008  # 스와이프 감지 최소 거리
    swipe_required_frames: int = 3  # 스와이프 감지에 필요한 연속 프레임 수
    swipe_cooldown: float = 2.0  # 스와이프 쿨타임 (초) - 연속 실행 방지를 위해 증가
    
    # 손가락 감지 설정
    finger_threshold: float = 0.02  # 손가락 펴짐/접힘 감지 임계값
    
    # 기존 설정 (호환성 유지)
    swipe_threshold: float = 0.05  # 스와이프 임계값 (더 낮춤)
    swipe_time_limit: float = 1.0  # 스와이프 시간 제한 (초)
    mode_stabilization_time: float = 0.2  # 모드 안정화 시간 (초) - 더 빠른 모드 변경을 위해 단축
    scroll_threshold: float = 0.1  # 스크롤 임계값
    smoothing_factor: float = 0.5
    sensitivity: float = 1.5

    # 마우스 반전 설정
    invert_x: bool = False  # X축 좌우 반전
    invert_y: bool = False  # Y축 상하 반전
    invert_scroll_x: bool = False  # 스크롤 X축 반전
    invert_scroll_y: bool = False  # 스크롤 Y축 반전
    invert_swipe_x: bool = False  # 스와이프 X축 반전
    invert_swipe_y: bool = False  # 스와이프 Y축 반전


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