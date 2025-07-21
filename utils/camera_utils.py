"""
Camera utilities for SkyTouch application.
"""
import cv2
import platform
from typing import List, Tuple, Optional
from utils.logging.logger import get_logger

logger = get_logger(__name__)


def get_available_cameras(max_check: int = 10) -> List[Tuple[int, str]]:
    """
    시스템에서 사용 가능한 카메라 목록을 가져옵니다.
    
    Args:
        max_check: 확인할 최대 카메라 개수
        
    Returns:
        [(device_id, camera_name), ...] 형태의 리스트
    """
    available_cameras = []
    
    try:
        # macOS에서는 카메라 이름을 가져오는 방법이 제한적이므로
        # 실제로 카메라를 열어서 확인하는 방식 사용
        for device_id in range(max_check):
            cap = cv2.VideoCapture(device_id)
            if cap.isOpened():
                # 카메라 이름 생성 (플랫폼별)
                camera_name = _generate_camera_name(device_id, cap)
                available_cameras.append((device_id, camera_name))
                cap.release()
                logger.debug(f"카메라 {device_id} 발견: {camera_name}")
            else:
                # 더 이상 카메라가 없으면 중단
                if device_id > 0:  # 첫 번째 카메라가 없으면 계속 시도
                    break
        
        if not available_cameras:
            logger.warning("사용 가능한 카메라가 없습니다.")
            # 기본 카메라 0번 추가
            available_cameras.append((0, "기본 카메라"))
        
        logger.info(f"총 {len(available_cameras)}개의 카메라를 발견했습니다.")
        return available_cameras
        
    except Exception as e:
        logger.error(f"카메라 목록 가져오기 실패: {e}")
        # 오류 시 기본 카메라만 반환
        return [(0, "기본 카메라")]


def _generate_camera_name(device_id: int, cap: cv2.VideoCapture) -> str:
    """
    카메라 이름을 생성합니다.
    
    Args:
        device_id: 카메라 디바이스 ID
        cap: VideoCapture 객체
        
    Returns:
        카메라 이름
    """
    system = platform.system()
    
    if system == "Darwin":  # macOS
        # macOS에서는 카메라 정보를 직접 가져오기 어려우므로
        # 해상도 정보를 이용해 카메라 종류 추정
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        if width >= 1920 or height >= 1080:
            return f"HD 카메라 {device_id}"
        elif width >= 1280 or height >= 720:
            return f"웹캠 {device_id}"
        else:
            return f"카메라 {device_id}"
    
    elif system == "Windows":
        # Windows에서는 카메라 이름을 가져올 수 있음
        try:
            # 카메라 이름 가져오기 시도
            camera_name = cap.getBackendName()
            if camera_name and camera_name != "Unknown":
                return f"{camera_name} {device_id}"
            else:
                return f"카메라 {device_id}"
        except:
            return f"카메라 {device_id}"
    
    elif system == "Linux":
        # Linux에서는 /dev/video* 경로 확인
        try:
            import subprocess
            result = subprocess.run(['v4l2-ctl', '--list-devices'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                # v4l2-ctl이 있으면 카메라 이름 파싱
                lines = result.stdout.split('\n')
                for line in lines:
                    if f'/dev/video{device_id}' in line:
                        # 이전 줄에서 카메라 이름 찾기
                        for i in range(len(lines)):
                            if f'/dev/video{device_id}' in lines[i]:
                                if i > 0 and lines[i-1].strip():
                                    return f"{lines[i-1].strip()} {device_id}"
                                break
        except:
            pass
        
        return f"카메라 {device_id}"
    
    else:
        return f"카메라 {device_id}"


def test_camera(device_id: int) -> bool:
    """
    특정 카메라가 사용 가능한지 테스트합니다.
    
    Args:
        device_id: 카메라 디바이스 ID
        
    Returns:
        사용 가능 여부
    """
    try:
        cap = cv2.VideoCapture(device_id)
        if cap.isOpened():
            # 실제로 프레임을 읽어서 테스트
            ret, frame = cap.read()
            cap.release()
            return ret
        return False
    except Exception as e:
        logger.error(f"카메라 {device_id} 테스트 실패: {e}")
        return False


def get_camera_info(device_id: int) -> Optional[dict]:
    """
    카메라 정보를 가져옵니다.
    
    Args:
        device_id: 카메라 디바이스 ID
        
    Returns:
        카메라 정보 딕셔너리 또는 None
    """
    try:
        cap = cv2.VideoCapture(device_id)
        if not cap.isOpened():
            return None
        
        info = {
            'device_id': device_id,
            'name': _generate_camera_name(device_id, cap),
            'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'fps': cap.get(cv2.CAP_PROP_FPS),
            'backend': cap.getBackendName()
        }
        
        cap.release()
        return info
        
    except Exception as e:
        logger.error(f"카메라 {device_id} 정보 가져오기 실패: {e}")
        return None 