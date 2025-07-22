#!/bin/bash

# SkyTouch macOS 애플리케이션 빌드 스크립트

echo "🚀 SkyTouch macOS 애플리케이션 빌드를 시작합니다..."

# 가상환경 활성화 확인
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "❌ 가상환경이 활성화되지 않았습니다. 가상환경을 활성화해주세요."
    echo "   source venv/bin/activate"
    exit 1
fi

# 기존 빌드 폴더 정리
echo "🧹 기존 빌드 폴더를 정리합니다..."
rm -rf build/
rm -rf dist/

# PyInstaller로 빌드
echo "🔨 PyInstaller로 애플리케이션을 빌드합니다..."
pyinstaller SkyTouch.spec --clean

# 빌드 결과 확인
if [ -d "dist/SkyTouch.app" ]; then
    echo "✅ 빌드가 성공적으로 완료되었습니다!"
    echo "📱 애플리케이션 위치: dist/SkyTouch.app"
    echo ""
    echo "🎯 다음 명령어로 애플리케이션을 실행할 수 있습니다:"
    echo "   open dist/SkyTouch.app"
    echo ""
    echo "📦 배포를 위해 dist/SkyTouch.app 폴더를 압축하세요."
else
    echo "❌ 빌드에 실패했습니다. 오류를 확인해주세요."
    exit 1
fi 