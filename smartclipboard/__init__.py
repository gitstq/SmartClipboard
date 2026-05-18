"""
SmartClipboard - 智能剪贴板管理工具

一个功能强大的跨平台剪贴板管理器，集成OCR、AI处理和智能分类功能。

Author: SmartClipboard Team
Version: 1.0.0
License: MIT
"""

__version__ = "1.0.0"
__author__ = "SmartClipboard Team"
__license__ = "MIT"

from .clipboard_manager import ClipboardManager
from .database import DatabaseManager
from .ai_processor import AIProcessor
from .ocr_engine import OCREngine

__all__ = [
    "ClipboardManager",
    "DatabaseManager", 
    "AIProcessor",
    "OCREngine",
]
