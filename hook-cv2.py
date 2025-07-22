# PyInstaller hook for OpenCV to fix recursion issues
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect all OpenCV data files
datas = collect_data_files('cv2')

# Collect all OpenCV submodules
hiddenimports = collect_submodules('cv2')

# Add specific OpenCV modules that might be missed
hiddenimports += [
    'cv2.cv2',
    'cv2.data',
    'cv2.misc',
    'cv2.utils',
    'cv2.gapi',
    'cv2.mat_wrapper',
    'cv2.typing',
]

# Fix for OpenCV recursion issue
import sys
import os

# Add OpenCV path to sys.path to prevent recursion
cv2_path = None
for path in sys.path:
    if 'cv2' in path and 'site-packages' in path:
        cv2_path = path
        break

if cv2_path:
    # Ensure cv2 is loaded from the correct path
    if cv2_path not in sys.path:
        sys.path.insert(0, cv2_path) 