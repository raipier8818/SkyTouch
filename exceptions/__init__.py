"""
Exception module for Hand Tracking Trackpad application.
"""

from .base import (
    HandTrackpadError,
    CameraError,
    HandTrackingError,
    GestureError,
    ConfigError,
    UIError,
    MouseError
)

__all__ = [
    'HandTrackpadError',
    'CameraError',
    'HandTrackingError',
    'GestureError',
    'ConfigError',
    'UIError',
    'MouseError'
] 