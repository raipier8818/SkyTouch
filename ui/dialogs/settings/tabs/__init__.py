"""
Settings tabs module for SkyTouch application.
"""

from .camera_tab import CameraTab
from .hand_tracking_tab import HandTrackingTab
from .gesture_tab import GestureTab
from .mode_tab import ModeTab

__all__ = [
    'CameraTab',
    'HandTrackingTab', 
    'GestureTab',
    'ModeTab'
] 