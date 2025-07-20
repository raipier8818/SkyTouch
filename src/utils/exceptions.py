"""
Custom exceptions for the Hand Tracking Trackpad application.
"""


class HandTrackpadError(Exception):
    """기본 애플리케이션 예외 클래스"""
    pass


class CameraError(HandTrackpadError):
    """카메라 관련 예외"""
    pass


class HandTrackingError(HandTrackpadError):
    """손 트래킹 관련 예외"""
    pass


class GestureError(HandTrackpadError):
    """제스처 인식 관련 예외"""
    pass


class ConfigError(HandTrackpadError):
    """설정 관련 예외"""
    pass


class UIError(HandTrackpadError):
    """UI 관련 예외"""
    pass 