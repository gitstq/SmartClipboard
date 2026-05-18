"""
剪贴板管理核心模块 - 负责监听和管理剪贴板内容
"""

import os
import sys
import time
import threading
from typing import Callable, Optional, List
from dataclasses import dataclass
from datetime import datetime
import hashlib
import json

# 跨平台剪贴板支持
try:
    import pyperclip
except ImportError:
    pyperclip = None

# 平台特定导入
if sys.platform == 'darwin':
    try:
        from AppKit import NSPasteboard, NSString, NSData, NSImage
        from Foundation import NSObject
        MACOS_AVAILABLE = True
    except ImportError:
        MACOS_AVAILABLE = False
elif sys.platform == 'win32':
    try:
        import win32clipboard
        import win32con
        WINDOWS_AVAILABLE = True
    except ImportError:
        WINDOWS_AVAILABLE = False
else:
    # Linux
    try:
        import subprocess
        LINUX_AVAILABLE = True
    except ImportError:
        LINUX_AVAILABLE = False

from .database import DatabaseManager, ClipboardItem


@dataclass
class ClipboardContent:
    """剪贴板内容数据类"""
    text: str = ""
    html: str = ""
    image_data: bytes = None
    files: List[str] = None
    content_type: str = "text"
    timestamp: datetime = None
    source_app: str = ""
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.files is None:
            self.files = []
    
    def get_hash(self) -> str:
        """生成内容哈希"""
        content = self.text or self.html or str(self.image_data) or str(self.files)
        return hashlib.md5(content.encode()).hexdigest()


class ClipboardManager:
    """剪贴板管理器 - 跨平台剪贴板监听和管理"""
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        """初始化剪贴板管理器
        
        Args:
            db_manager: 数据库管理器实例
        """
        self.db = db_manager or DatabaseManager()
        self._last_content_hash = ""
        self._listeners: List[Callable] = []
        self._running = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        
        # 配置
        self.max_history = 1000
        self.ignore_duplicates_duration = 2  # 秒内重复的忽略
        self._last_copy_time = 0
        
        # 初始化平台支持
        self._init_platform()
    
    def _init_platform(self):
        """初始化平台特定功能"""
        self.platform = sys.platform
        
        if self.platform == 'darwin' and MACOS_AVAILABLE:
            self._pb = NSPasteboard.generalPasteboard()
            self._platform_available = True
        elif self.platform == 'win32' and WINDOWS_AVAILABLE:
            self._platform_available = True
        elif self.platform.startswith('linux') and LINUX_AVAILABLE:
            self._platform_available = True
        else:
            self._platform_available = pyperclip is not None
    
    def start_monitoring(self, interval: float = 0.5):
        """启动剪贴板监听
        
        Args:
            interval: 检查间隔（秒）
        """
        if self._running:
            return
        
        self._running = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, args=(interval,))
        self._monitor_thread.daemon = True
        self._monitor_thread.start()
    
    def stop_monitoring(self):
        """停止剪贴板监听"""
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2)
    
    def _monitor_loop(self, interval: float):
        """监听循环"""
        while self._running:
            try:
                self._check_clipboard()
            except Exception as e:
                print(f"Clipboard check error: {e}")
            
            time.sleep(interval)
    
    def _check_clipboard(self):
        """检查剪贴板变化"""
        content = self._get_clipboard_content()
        
        if not content or not content.text:
            return
        
        content_hash = content.get_hash()
        
        with self._lock:
            # 检查是否与上次相同
            if content_hash == self._last_content_hash:
                return
            
            # 检查时间间隔（防止重复）
            current_time = time.time()
            if current_time - self._last_copy_time < self.ignore_duplicates_duration:
                return
            
            self._last_content_hash = content_hash
            self._last_copy_time = current_time
        
        # 保存到数据库
        self._save_content(content)
        
        # 通知监听器
        self._notify_listeners(content)
    
    def _get_clipboard_content(self) -> Optional[ClipboardContent]:
        """获取剪贴板内容（跨平台）"""
        content = ClipboardContent()
        
        try:
            if self.platform == 'darwin' and MACOS_AVAILABLE:
                content = self._get_macos_clipboard()
            elif self.platform == 'win32' and WINDOWS_AVAILABLE:
                content = self._get_windows_clipboard()
            elif self.platform.startswith('linux'):
                content = self._get_linux_clipboard()
            else:
                # 使用pyperclip作为后备
                text = pyperclip.paste()
                if text:
                    content.text = text
                    content.content_type = "text"
        except Exception as e:
            print(f"Get clipboard error: {e}")
        
        return content if content.text or content.image_data else None
    
    def _get_macos_clipboard(self) -> ClipboardContent:
        """获取macOS剪贴板内容"""
        content = ClipboardContent()
        
        # 获取文本
        text = self._pb.stringForType_("public.utf8-plain-text")
        if text:
            content.text = str(text)
            content.content_type = "text"
        
        # 获取HTML
        html = self._pb.stringForType_("public.html")
        if html:
            content.html = str(html)
            content.content_type = "rich_text"
        
        # 获取图片
        image_data = self._pb.dataForType_("public.png")
        if not image_data:
            image_data = self._pb.dataForType_("public.tiff")
        if image_data:
            content.image_data = bytes(image_data)
            content.content_type = "image"
        
        # 获取文件列表
        files = self._pb.propertyListForType_("NSFilenamesPboardType")
        if files:
            content.files = list(files)
            content.content_type = "file"
        
        return content
    
    def _get_windows_clipboard(self) -> ClipboardContent:
        """获取Windows剪贴板内容"""
        content = ClipboardContent()
        
        try:
            win32clipboard.OpenClipboard()
            
            # 检查可用的格式
            available_formats = []
            current_format = 0
            while True:
                current_format = win32clipboard.EnumClipboardFormats(current_format)
                if current_format == 0:
                    break
                available_formats.append(current_format)
            
            # 获取文本
            if win32con.CF_UNICODETEXT in available_formats:
                text = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
                if text:
                    content.text = text
                    content.content_type = "text"
            
            # 获取HTML
            if win32con.CF_HTML in available_formats:
                html = win32clipboard.GetClipboardData(win32con.CF_HTML)
                if html:
                    content.html = html
                    content.content_type = "rich_text"
            
            # 获取图片
            if win32con.CF_BITMAP in available_formats or win32con.CF_DIB in available_formats:
                try:
                    image_data = win32clipboard.GetClipboardData(win32con.CF_DIB)
                    if image_data:
                        content.image_data = image_data
                        content.content_type = "image"
                except:
                    pass
            
            # 获取文件列表
            if win32con.CF_HDROP in available_formats:
                try:
                    files = win32clipboard.GetClipboardData(win32con.CF_HDROP)
                    content.files = list(files)
                    content.content_type = "file"
                except:
                    pass
            
            win32clipboard.CloseClipboard()
        except Exception as e:
            try:
                win32clipboard.CloseClipboard()
            except:
                pass
            raise e
        
        return content
    
    def _get_linux_clipboard(self) -> ClipboardContent:
        """获取Linux剪贴板内容"""
        content = ClipboardContent()
        
        # 尝试使用xclip或xsel
        try:
            # 获取文本
            result = subprocess.run(
                ['xclip', '-selection', 'clipboard', '-o'],
                capture_output=True,
                text=True,
                timeout=1
            )
            if result.returncode == 0:
                content.text = result.stdout
                content.content_type = "text"
        except:
            try:
                result = subprocess.run(
                    ['xsel', '--clipboard', '--output'],
                    capture_output=True,
                    text=True,
                    timeout=1
                )
                if result.returncode == 0:
                    content.text = result.stdout
                    content.content_type = "text"
            except:
                pass
        
        return content
    
    def _save_content(self, content: ClipboardContent):
        """保存内容到数据库"""
        # 检测内容类型
        if content.image_data:
            content_type = "image"
        elif content.files:
            content_type = "file"
        elif content.html:
            content_type = "rich_text"
        else:
            content_type = "text"
        
        # 准备元数据
        metadata = {
            'has_html': bool(content.html),
            'file_count': len(content.files) if content.files else 0,
            'image_size': len(content.image_data) if content.image_data else 0,
        }
        
        item = ClipboardItem(
            content=content.text or content.html or json.dumps(content.files) or "[Image]",
            content_type=content_type,
            source_app=content.source_app,
            metadata=json.dumps(metadata)
        )
        
        self.db.add_item(item)
    
    def _notify_listeners(self, content: ClipboardContent):
        """通知所有监听器"""
        for listener in self._listeners:
            try:
                listener(content)
            except Exception as e:
                print(f"Listener error: {e}")
    
    def add_listener(self, callback: Callable):
        """添加剪贴板变化监听器"""
        self._listeners.append(callback)
    
    def remove_listener(self, callback: Callable):
        """移除监听器"""
        if callback in self._listeners:
            self._listeners.remove(callback)
    
    def copy_to_clipboard(self, text: str) -> bool:
        """复制文本到剪贴板
        
        Args:
            text: 要复制的文本
            
        Returns:
            是否成功
        """
        try:
            if pyperclip:
                pyperclip.copy(text)
                return True
            return False
        except Exception as e:
            print(f"Copy error: {e}")
            return False
    
    def get_history(self, limit: int = 50) -> List[ClipboardItem]:
        """获取剪贴板历史"""
        return self.db.get_recent_items(limit)
    
    def search_history(self, query: str, limit: int = 50) -> List[ClipboardItem]:
        """搜索历史记录"""
        return self.db.search_items(query, limit)
    
    def delete_item(self, item_id: int) -> bool:
        """删除历史条目"""
        return self.db.delete_item(item_id)
    
    def clear_history(self, keep_favorites: bool = True) -> int:
        """清空历史"""
        return self.db.clear_history(keep_favorites)
    
    def toggle_favorite(self, item_id: int) -> bool:
        """切换收藏状态"""
        return self.db.toggle_favorite(item_id)
    
    def toggle_pin(self, item_id: int) -> bool:
        """切换置顶状态"""
        return self.db.toggle_pin(item_id)
    
    def get_statistics(self) -> dict:
        """获取统计信息"""
        return self.db.get_statistics()
    
    def close(self):
        """关闭管理器"""
        self.stop_monitoring()
        self.db.close()
