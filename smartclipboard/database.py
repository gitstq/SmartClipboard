"""
数据库管理模块 - 负责剪贴板历史数据的持久化存储
"""

import os
import json
import sqlite3
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from contextlib import contextmanager
import threading


@dataclass
class ClipboardItem:
    """剪贴板条目数据类"""
    id: Optional[int] = None
    content: str = ""
    content_type: str = "text"  # text, image, file, rich_text
    content_hash: str = ""
    source_app: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    access_count: int = 0
    is_favorite: bool = False
    is_pinned: bool = False
    tags: str = ""  # JSON string
    metadata: str = ""  # JSON string for extra data
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if not self.content_hash and self.content:
            self.content_hash = hashlib.md5(self.content.encode()).hexdigest()


class DatabaseManager:
    """SQLite数据库管理器"""
    
    def __init__(self, db_path: Optional[str] = None):
        """初始化数据库管理器
        
        Args:
            db_path: 数据库文件路径，默认为用户目录下的 .smartclipboard/history.db
        """
        if db_path is None:
            home_dir = os.path.expanduser("~")
            app_dir = os.path.join(home_dir, ".smartclipboard")
            os.makedirs(app_dir, exist_ok=True)
            db_path = os.path.join(app_dir, "history.db")
        
        self.db_path = db_path
        self._local = threading.local()
        self._init_database()
    
    def _get_connection(self) -> sqlite3.Connection:
        """获取线程本地数据库连接"""
        if not hasattr(self._local, 'connection') or self._local.connection is None:
            self._local.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self._local.connection.row_factory = sqlite3.Row
        return self._local.connection
    
    def _init_database(self):
        """初始化数据库表结构"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # 创建剪贴板历史表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clipboard_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                content_type TEXT DEFAULT 'text',
                content_hash TEXT UNIQUE NOT NULL,
                source_app TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                access_count INTEGER DEFAULT 0,
                is_favorite INTEGER DEFAULT 0,
                is_pinned INTEGER DEFAULT 0,
                tags TEXT DEFAULT '',
                metadata TEXT DEFAULT ''
            )
        """)
        
        # 创建索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_content_hash ON clipboard_history(content_hash)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_created_at ON clipboard_history(created_at)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_is_favorite ON clipboard_history(is_favorite)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_is_pinned ON clipboard_history(is_pinned)
        """)
        
        # 创建搜索索引表 (FTS5)
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS clipboard_fts USING fts5(
                content,
                content_type,
                tags,
                content='clipboard_history',
                content_rowid='id'
            )
        """)
        
        # 创建触发器保持FTS索引同步
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS clipboard_ai AFTER INSERT ON clipboard_history BEGIN
                INSERT INTO clipboard_fts(rowid, content, content_type, tags)
                VALUES (new.id, new.content, new.content_type, new.tags);
            END
        """)
        
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS clipboard_ad AFTER DELETE ON clipboard_history BEGIN
                INSERT INTO clipboard_fts(clipboard_fts, rowid, content, content_type, tags)
                VALUES ('delete', old.id, old.content, old.content_type, old.tags);
            END
        """)
        
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS clipboard_au AFTER UPDATE ON clipboard_history BEGIN
                INSERT INTO clipboard_fts(clipboard_fts, rowid, content, content_type, tags)
                VALUES ('delete', old.id, old.content, old.content_type, old.tags);
                INSERT INTO clipboard_fts(rowid, content, content_type, tags)
                VALUES (new.id, new.content, new.content_type, new.tags);
            END
        """)
        
        # 创建设置表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
    
    def add_item(self, item: ClipboardItem) -> Optional[int]:
        """添加剪贴板条目
        
        Args:
            item: 剪贴板条目对象
            
        Returns:
            新条目的ID，如果已存在则返回None
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO clipboard_history 
                (content, content_type, content_hash, source_app, is_favorite, is_pinned, tags, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item.content,
                item.content_type,
                item.content_hash,
                item.source_app,
                1 if item.is_favorite else 0,
                1 if item.is_pinned else 0,
                item.tags,
                item.metadata
            ))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            # 内容已存在，更新访问时间和计数
            cursor.execute("""
                UPDATE clipboard_history 
                SET access_count = access_count + 1, updated_at = CURRENT_TIMESTAMP
                WHERE content_hash = ?
            """, (item.content_hash,))
            conn.commit()
            return None
    
    def get_item_by_id(self, item_id: int) -> Optional[ClipboardItem]:
        """根据ID获取条目"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM clipboard_history WHERE id = ?
        """, (item_id,))
        
        row = cursor.fetchone()
        if row:
            return self._row_to_item(row)
        return None
    
    def get_recent_items(self, limit: int = 50, offset: int = 0) -> List[ClipboardItem]:
        """获取最近的剪贴板条目
        
        Args:
            limit: 返回条目数量
            offset: 偏移量
            
        Returns:
            剪贴板条目列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM clipboard_history 
            ORDER BY is_pinned DESC, updated_at DESC
            LIMIT ? OFFSET ?
        """, (limit, offset))
        
        return [self._row_to_item(row) for row in cursor.fetchall()]
    
    def search_items(self, query: str, limit: int = 50) -> List[ClipboardItem]:
        """搜索剪贴板条目
        
        Args:
            query: 搜索关键词
            limit: 返回条目数量
            
        Returns:
            匹配的剪贴板条目列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # 使用FTS5进行全文搜索
        cursor.execute("""
            SELECT h.* FROM clipboard_history h
            JOIN clipboard_fts f ON h.id = f.rowid
            WHERE clipboard_fts MATCH ?
            ORDER BY h.is_pinned DESC, h.updated_at DESC
            LIMIT ?
        """, (query, limit))
        
        return [self._row_to_item(row) for row in cursor.fetchall()]
    
    def get_favorites(self) -> List[ClipboardItem]:
        """获取收藏的条目"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM clipboard_history 
            WHERE is_favorite = 1
            ORDER BY updated_at DESC
        """)
        
        return [self._row_to_item(row) for row in cursor.fetchall()]
    
    def toggle_favorite(self, item_id: int) -> bool:
        """切换收藏状态"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE clipboard_history 
            SET is_favorite = NOT is_favorite, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (item_id,))
        
        conn.commit()
        return cursor.rowcount > 0
    
    def toggle_pin(self, item_id: int) -> bool:
        """切换置顶状态"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE clipboard_history 
            SET is_pinned = NOT is_pinned, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (item_id,))
        
        conn.commit()
        return cursor.rowcount > 0
    
    def delete_item(self, item_id: int) -> bool:
        """删除条目"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM clipboard_history WHERE id = ?", (item_id,))
        conn.commit()
        return cursor.rowcount > 0
    
    def clear_history(self, keep_favorites: bool = True) -> int:
        """清空历史记录
        
        Args:
            keep_favorites: 是否保留收藏的条目
            
        Returns:
            删除的条目数量
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if keep_favorites:
            cursor.execute("DELETE FROM clipboard_history WHERE is_favorite = 0")
        else:
            cursor.execute("DELETE FROM clipboard_history")
        
        conn.commit()
        return cursor.rowcount
    
    def cleanup_old_items(self, days: int = 30) -> int:
        """清理旧条目
        
        Args:
            days: 保留天数
            
        Returns:
            删除的条目数量
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        cursor.execute("""
            DELETE FROM clipboard_history 
            WHERE updated_at < ? AND is_favorite = 0 AND is_pinned = 0
        """, (cutoff_date.isoformat(),))
        
        conn.commit()
        return cursor.rowcount
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # 总条目数
        cursor.execute("SELECT COUNT(*) FROM clipboard_history")
        stats['total_items'] = cursor.fetchone()[0]
        
        # 收藏数
        cursor.execute("SELECT COUNT(*) FROM clipboard_history WHERE is_favorite = 1")
        stats['favorite_count'] = cursor.fetchone()[0]
        
        # 置顶数
        cursor.execute("SELECT COUNT(*) FROM clipboard_history WHERE is_pinned = 1")
        stats['pinned_count'] = cursor.fetchone()[0]
        
        # 今日新增
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute("""
            SELECT COUNT(*) FROM clipboard_history 
            WHERE DATE(created_at) = ?
        """, (today,))
        stats['today_count'] = cursor.fetchone()[0]
        
        # 类型分布
        cursor.execute("""
            SELECT content_type, COUNT(*) as count 
            FROM clipboard_history 
            GROUP BY content_type
        """)
        stats['type_distribution'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        return stats
    
    def set_setting(self, key: str, value: str):
        """保存设置"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO settings (key, value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (key, value))
        
        conn.commit()
    
    def get_setting(self, key: str, default: str = "") -> str:
        """获取设置"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        
        return row[0] if row else default
    
    def _row_to_item(self, row: sqlite3.Row) -> ClipboardItem:
        """将数据库行转换为ClipboardItem对象"""
        return ClipboardItem(
            id=row['id'],
            content=row['content'],
            content_type=row['content_type'],
            content_hash=row['content_hash'],
            source_app=row['source_app'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None,
            access_count=row['access_count'],
            is_favorite=bool(row['is_favorite']),
            is_pinned=bool(row['is_pinned']),
            tags=row['tags'],
            metadata=row['metadata']
        )
    
    def close(self):
        """关闭数据库连接"""
        if hasattr(self._local, 'connection') and self._local.connection:
            self._local.connection.close()
            self._local.connection = None
