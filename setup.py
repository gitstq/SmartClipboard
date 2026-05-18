#!/usr/bin/env python3
"""
SmartClipboard 安装脚本
"""

from setuptools import setup, find_packages
import os

# 读取README
here = os.path.abspath(os.path.dirname(__file__))
readme_path = os.path.join(here, 'README.md')
long_description = ""
if os.path.exists(readme_path):
    with open(readme_path, 'r', encoding='utf-8') as f:
        long_description = f.read()

# 读取requirements
requirements_path = os.path.join(here, 'requirements.txt')
requirements = []
if os.path.exists(requirements_path):
    with open(requirements_path, 'r', encoding='utf-8') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='SmartClipboard',
    version='1.0.0',
    description='智能剪贴板管理工具 - 集成OCR、AI处理和智能分类功能',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='SmartClipboard Team',
    author_email='smartclipboard@example.com',
    url='https://github.com/gitstq/SmartClipboard',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'smartclipboard=main:main',
            'scb=main:main',
        ],
        'gui_scripts': [
            'smartclipboard-gui=main:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Utilities',
        'Topic :: Office/Business',
        'Topic :: Text Processing',
    ],
    python_requires='>=3.9',
    keywords='clipboard ocr ai productivity tool',
    project_urls={
        'Bug Reports': 'https://github.com/gitstq/SmartClipboard/issues',
        'Source': 'https://github.com/gitstq/SmartClipboard',
    },
)
