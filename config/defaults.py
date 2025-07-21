"""
Default configuration values for Hand Tracking Trackpad application.
"""

DEFAULT_CONFIG = {
    "camera": {
        "width": 480,
        "height": 360,
        "fps": 30,
        "device_id": 0,
        "frame_delay": 0.03
    },
    "hand_tracking": {
        "max_num_hands": 1,
        "min_detection_confidence": 0.7,
        "min_tracking_confidence": 0.5,
        "static_image_mode": False
    },
    "gesture": {
        "click_threshold": 0.12,
        "scroll_distance_threshold": 0.003,
        "scroll_required_frames": 1,
        "swipe_distance_threshold": 0.008,
        "swipe_required_frames": 3,
        "swipe_cooldown": 0.5,
        "finger_threshold": 0.02,
        "swipe_threshold": 0.03,
        "swipe_time_limit": 1.0,
        "mode_stabilization_time": 0.2,
        "scroll_threshold": 0.1,
        "smoothing_factor": 0.5,
        "sensitivity": 1.5,
        "invert_x": True,
        "invert_y": False,
        "invert_scroll_x": True,
        "invert_scroll_y": False,
        "invert_swipe_x": True,
        "invert_swipe_y": False,
        "double_click_time": 0.5,
        "min_movement_threshold": 0.001
    },
    "ui": {
        "window_width": 520,
        "window_height": 800,
        "theme": "clam",
        "font_family": "Arial",
        "title": "Hand Tracking Trackpad",
        "debug_mode": True
    }
} 