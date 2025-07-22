#!/bin/bash

# SkyTouch 배포 패키지 생성 스크립트

echo "📦 SkyTouch 배포 패키지를 생성합니다..."

# 버전 정보
VERSION="1.0.0"
APP_NAME="SkyTouch"
DIST_DIR="dist"
PACKAGE_NAME="${APP_NAME}-${VERSION}-macOS"

# 애플리케이션이 존재하는지 확인
if [ ! -d "${DIST_DIR}/${APP_NAME}.app" ]; then
    echo "❌ ${APP_NAME}.app을 찾을 수 없습니다. 먼저 빌드를 실행해주세요."
    echo "   ./build_macos.sh"
    exit 1
fi

# 기존 패키지 정리
echo "🧹 기존 패키지를 정리합니다..."
rm -rf "${PACKAGE_NAME}.zip"
rm -rf "${PACKAGE_NAME}"

# 배포 폴더 생성
echo "📁 배포 폴더를 생성합니다..."
mkdir -p "${PACKAGE_NAME}"

# 애플리케이션 복사
echo "📱 애플리케이션을 복사합니다..."
cp -R "${DIST_DIR}/${APP_NAME}.app" "${PACKAGE_NAME}/"

# README 파일 생성
echo "📝 README 파일을 생성합니다..."
cat > "${PACKAGE_NAME}/README.txt" << 'EOF'
SkyTouch v1.0.0 - macOS

🎯 개요
SkyTouch는 MediaPipe를 사용한 손 추적 기술로 마우스 커서를 제어하고 제스처를 인식하는 데스크톱 애플리케이션입니다.

🚀 설치 및 실행
1. SkyTouch.app을 Applications 폴더로 드래그하거나
2. 더블클릭하여 직접 실행

⚠️  주의사항
- macOS 10.13 이상이 필요합니다
- 카메라 접근 권한이 필요합니다
- 처음 실행 시 보안 경고가 나타날 수 있습니다

🔧 시스템 요구사항
- macOS 10.13+
- 카메라
- 최소 4GB RAM

📞 지원
문제가 발생하면 개발팀에 문의해주세요.

© 2024 SkyTouch Team
EOF

# 라이선스 파일
echo "📄 라이선스 정보를 추가합니다..."
cat > "${PACKAGE_NAME}/LICENSE.txt" << 'EOF'
MIT License

Copyright (c) 2024 SkyTouch Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF

# ZIP 파일 생성
echo "🗜️  ZIP 파일을 생성합니다..."
zip -r "${PACKAGE_NAME}.zip" "${PACKAGE_NAME}"

# 정리
echo "🧹 임시 파일을 정리합니다..."
rm -rf "${PACKAGE_NAME}"

echo "✅ 배포 패키지가 성공적으로 생성되었습니다!"
echo "📦 패키지 파일: ${PACKAGE_NAME}.zip"
echo ""
echo "🎯 배포 준비 완료!"
echo "   - 파일 크기: $(du -h "${PACKAGE_NAME}.zip" | cut -f1)"
echo "   - 생성 위치: $(pwd)/${PACKAGE_NAME}.zip" 