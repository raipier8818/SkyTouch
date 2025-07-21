"""
Gesture types and data classes for Hand Tracking Trackpad application.
"""
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any


class GestureType(Enum):
    """제스처 타입 열거형"""
    MOVE = "move"
    CLICK = "click"
    SCROLL = "scroll"
    SWIPE = "swipe"


@dataclass
class GestureData:
    """제스처 데이터 클래스"""
    palm_center: List[float]
    gesture_mode: GestureType  # GestureType enum 사용
    is_clicking: bool  # 클릭 모드에서 클릭
    is_right_clicking: bool  # 클릭 모드에서 우클릭
    is_double_clicking: bool  # 더블클릭
    is_scrolling: bool  # 스크롤 모드에서 스크롤
    is_swiping: bool  # 스와이프 모드에서 스와이프
    swipe_direction: str  # "left", "right", "up", "down", "none"
    scroll_direction: str  # "up", "down", "left", "right", "none"
    metadata: Dict[str, Any] = None  # 추가 메타데이터


@dataclass
class FingerState:
    """손가락 상태 데이터 클래스"""
    index_extended: bool
    middle_extended: bool
    ring_extended: bool
    pinky_extended: bool


@dataclass
class ThumbDistance:
    """엄지 거리 데이터 클래스"""
    thumb_index_distance: float
    thumb_middle_distance: float 