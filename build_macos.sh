#!/bin/bash

echo "Building SkyTouch application..."

# 의존성 설치
pip install -r requirements.txt

# 기존 빌드 제거
rm -rf build/
rm -rf dist/

# PyInstaller로 빌드
pyinstaller SkyTouch.spec

# 코드 서명 (자체 서명)
echo "Signing application..."
codesign --force --deep --sign - dist/SkyTouch.app

# 권한 설정 안내
echo ""
echo "Build completed!"
echo "Application is ready at: dist/SkyTouch.app"
echo ""
echo "⚠️  권한 설정이 필요합니다:"
echo "1. 시스템 환경설정 > 보안 및 개인정보 보호 > 개인정보 보호"
echo "2. 다음 항목들에서 'SkyTouch' 추가:"
echo "   - 접근성"
echo "   - 입력 모니터링"
echo "   - 완전한 디스크 접근"
echo ""
echo "앱을 실행한 후 권한을 설정해주세요!" 