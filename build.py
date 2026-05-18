#!/usr/bin/env python3
"""
SmartClipboard 构建脚本
支持多平台打包
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path


def clean_build():
    """清理构建目录"""
    dirs_to_remove = ['build', 'dist', '__pycache__', '.pytest_cache']
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            print(f"Removing {dir_name}/")
            shutil.rmtree(dir_name)
    
    # 清理.pyc文件
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                os.remove(os.path.join(root, file))
        for dir in dirs:
            if dir == '__pycache__':
                shutil.rmtree(os.path.join(root, dir))


def build_windows():
    """构建Windows可执行文件"""
    print("Building for Windows...")
    
    # PyInstaller spec文件内容
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['PyQt6.sip', 'paddle', 'paddleocr'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SmartClipboard',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/icon.ico' if os.path.exists('resources/icon.ico') else None,
)
'''
    
    with open('SmartClipboard.spec', 'w') as f:
        f.write(spec_content)
    
    # 运行PyInstaller
    subprocess.run([sys.executable, '-m', 'PyInstaller', 
                    'SmartClipboard.spec', '--clean', '--noconfirm'], check=True)
    
    print("Windows build completed!")
    print("Output: dist/SmartClipboard.exe")


def build_macos():
    """构建macOS应用"""
    print("Building for macOS...")
    
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['PyQt6.sip', 'paddle', 'paddleocr'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SmartClipboard',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/icon.icns' if os.path.exists('resources/icon.icns') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SmartClipboard'
)

app = BUNDLE(
    coll,
    name='SmartClipboard.app',
    icon='resources/icon.icns' if os.path.exists('resources/icon.icns') else None,
    bundle_identifier='com.smartclipboard.app',
    info_plist={
        'NSHighResolutionCapable': 'True',
        'LSBackgroundOnly': 'False',
    },
)
'''
    
    with open('SmartClipboard.spec', 'w') as f:
        f.write(spec_content)
    
    subprocess.run([sys.executable, '-m', 'PyInstaller', 
                    'SmartClipboard.spec', '--clean', '--noconfirm'], check=True)
    
    print("macOS build completed!")
    print("Output: dist/SmartClipboard.app")


def build_linux():
    """构建Linux可执行文件"""
    print("Building for Linux...")
    
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['PyQt6.sip', 'paddle', 'paddleocr'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SmartClipboard',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    with open('SmartClipboard.spec', 'w') as f:
        f.write(spec_content)
    
    subprocess.run([sys.executable, '-m', 'PyInstaller', 
                    'SmartClipboard.spec', '--clean', '--noconfirm'], check=True)
    
    print("Linux build completed!")
    print("Output: dist/SmartClipboard")


def create_installer():
    """创建安装程序"""
    system = platform.system()
    
    if system == 'Windows':
        # 使用NSIS创建Windows安装程序
        print("Creating Windows installer...")
        # 这里可以集成NSIS
        print("Please use NSIS to create installer from dist/SmartClipboard.exe")
    
    elif system == 'Darwin':
        # 创建DMG
        print("Creating macOS DMG...")
        subprocess.run([
            'hdiutil', 'create', '-volname', 'SmartClipboard',
            '-srcfolder', 'dist/SmartClipboard.app',
            '-ov', '-format', 'UDZO',
            'dist/SmartClipboard.dmg'
        ], check=True)
        print("Output: dist/SmartClipboard.dmg")
    
    elif system == 'Linux':
        # 创建AppImage或deb包
        print("Creating Linux package...")
        print("Please manually package dist/SmartClipboard")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='SmartClipboard Build Script')
    parser.add_argument('--clean', action='store_true', help='Clean build directories')
    parser.add_argument('--installer', action='store_true', help='Create installer')
    parser.add_argument('--all', action='store_true', help='Build for all platforms')
    
    args = parser.parse_args()
    
    if args.clean:
        clean_build()
        return
    
    # 安装依赖
    print("Installing dependencies...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], check=True)
    
    # 清理旧构建
    clean_build()
    
    # 检测平台并构建
    system = platform.system()
    
    if args.all:
        print("Building for all platforms...")
        # 注意：实际跨平台构建需要相应的环境
        build_windows()
        build_macos()
        build_linux()
    else:
        if system == 'Windows':
            build_windows()
        elif system == 'Darwin':
            build_macos()
        elif system == 'Linux':
            build_linux()
        else:
            print(f"Unsupported platform: {system}")
            sys.exit(1)
    
    if args.installer:
        create_installer()
    
    print("\nBuild completed!")


if __name__ == '__main__':
    main()
