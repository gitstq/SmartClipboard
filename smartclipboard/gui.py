"""
GUI界面模块 - PyQt6实现的现代化界面
"""

import sys
import os
from typing import Optional, List, Callable
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QListWidget, QListWidgetItem, QLabel,
    QTextEdit, QSplitter, QMenu, QSystemTrayIcon, QStyle, QMessageBox,
    QDialog, QDialogButtonBox, QComboBox, QCheckBox, QSpinBox,
    QTabWidget, QFrame, QScrollArea, QGridLayout, QProgressBar,
    QStatusBar, QToolBar, QFileDialog, QInputDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QIcon, QKeySequence, QShortcut, QAction, QFont, QPalette, QColor

from .clipboard_manager import ClipboardManager, ClipboardContent
from .database import ClipboardItem
from .ocr_engine import OCREngine, create_ocr_engine
from .ai_processor import AIProcessor, AIFeature, create_ai_processor


class ClipboardListItem(QWidget):
    """自定义剪贴板列表项"""
    
    def __init__(self, item: ClipboardItem, parent=None):
        super().__init__(parent)
        self.item_data = item
        self.setup_ui()
    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)
        
        # 类型图标
        self.icon_label = QLabel()
        icon_map = {
            "text": "📝",
            "image": "🖼️",
            "file": "📁",
            "rich_text": "📄"
        }
        self.icon_label.setText(icon_map.get(self.item_data.content_type, "📋"))
        self.icon_label.setStyleSheet("font-size: 20px;")
        layout.addWidget(self.icon_label)
        
        # 内容区域
        content_layout = QVBoxLayout()
        content_layout.setSpacing(2)
        
        # 内容预览
        preview_text = self.item_data.content[:100] + "..." if len(self.item_data.content) > 100 else self.item_data.content
        self.content_label = QLabel(preview_text)
        self.content_label.setWordWrap(True)
        self.content_label.setStyleSheet("font-size: 13px; color: #333;")
        content_layout.addWidget(self.content_label)
        
        # 元信息
        meta_layout = QHBoxLayout()
        
        # 时间
        time_str = self.item_data.updated_at.strftime("%m-%d %H:%M") if self.item_data.updated_at else ""
        self.time_label = QLabel(time_str)
        self.time_label.setStyleSheet("font-size: 11px; color: #999;")
        meta_layout.addWidget(self.time_label)
        
        # 来源应用
        if self.item_data.source_app:
            self.source_label = QLabel(f"📱 {self.item_data.source_app}")
            self.source_label.setStyleSheet("font-size: 11px; color: #666;")
            meta_layout.addWidget(self.source_label)
        
        # 状态标记
        if self.item_data.is_pinned:
            self.pin_label = QLabel("📌")
            meta_layout.addWidget(self.pin_label)
        
        if self.item_data.is_favorite:
            self.fav_label = QLabel("⭐")
            meta_layout.addWidget(self.fav_label)
        
        meta_layout.addStretch()
        content_layout.addLayout(meta_layout)
        
        layout.addLayout(content_layout, stretch=1)
        
        # 设置样式
        self.update_style()
    
    def update_style(self):
        """更新样式"""
        if self.item_data.is_pinned:
            self.setStyleSheet("""
                ClipboardListItem {
                    background-color: #fff8e1;
                    border-left: 4px solid #ffc107;
                    border-radius: 4px;
                }
            """)
        elif self.item_data.is_favorite:
            self.setStyleSheet("""
                ClipboardListItem {
                    background-color: #e3f2fd;
                    border-left: 4px solid #2196f3;
                    border-radius: 4px;
                }
            """)
        else:
            self.setStyleSheet("""
                ClipboardListItem {
                    background-color: white;
                    border-left: 4px solid transparent;
                    border-radius: 4px;
                }
                ClipboardListItem:hover {
                    background-color: #f5f5f5;
                    border-left: 4px solid #4caf50;
                }
            """)


class SmartClipboardWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SmartClipboard - 智能剪贴板管理器")
        self.setMinimumSize(900, 600)
        
        # 初始化管理器
        self.clipboard_manager = ClipboardManager()
        self.ocr_engine = create_ocr_engine(fallback_to_mock=True)
        self.ai_processor = create_ai_processor(use_local_fallback=True)
        
        # 设置UI
        self.setup_ui()
        self.setup_menu()
        self.setup_toolbar()
        self.setup_statusbar()
        self.setup_shortcuts()
        self.setup_tray()
        
        # 加载数据
        self.load_history()
        
        # 启动监听
        self.clipboard_manager.start_monitoring()
        self.clipboard_manager.add_listener(self.on_clipboard_change)
        
        # 定时刷新
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.load_history)
        self.refresh_timer.start(3000)  # 每3秒刷新
    
    def setup_ui(self):
        """设置UI"""
        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # 分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # 左侧：列表区域
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # 搜索框
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 搜索剪贴板历史...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #e0e0e0;
                border-radius: 20px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #4caf50;
            }
        """)
        self.search_input.textChanged.connect(self.on_search)
        search_layout.addWidget(self.search_input)
        
        # 清除搜索按钮
        clear_btn = QPushButton("✕")
        clear_btn.setFixedSize(30, 30)
        clear_btn.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
                font-size: 16px;
                color: #999;
            }
            QPushButton:hover {
                color: #f44336;
            }
        """)
        clear_btn.clicked.connect(self.clear_search)
        search_layout.addWidget(clear_btn)
        
        left_layout.addLayout(search_layout)
        
        # 列表
        self.history_list = QListWidget()
        self.history_list.setStyleSheet("""
            QListWidget {
                border: none;
                background-color: #f5f5f5;
            }
            QListWidget::item {
                background-color: transparent;
                margin: 5px;
            }
        """)
        self.history_list.setSpacing(5)
        self.history_list.itemClicked.connect(self.on_item_selected)
        self.history_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.history_list.customContextMenuRequested.connect(self.show_context_menu)
        left_layout.addWidget(self.history_list)
        
        # 统计信息
        self.stats_label = QLabel("📊 加载中...")
        self.stats_label.setStyleSheet("color: #666; font-size: 12px; padding: 5px;")
        left_layout.addWidget(self.stats_label)
        
        splitter.addWidget(left_widget)
        
        # 右侧：详情区域
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # 标签页
        self.tab_widget = QTabWidget()
        
        # 内容标签
        self.content_tab = QWidget()
        content_layout = QVBoxLayout(self.content_tab)
        
        self.content_text = QTextEdit()
        self.content_text.setReadOnly(True)
        self.content_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                line-height: 1.6;
            }
        """)
        content_layout.addWidget(self.content_text)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        
        self.copy_btn = QPushButton("📋 复制到剪贴板")
        self.copy_btn.setStyleSheet(self._get_button_style("#4caf50"))
        self.copy_btn.clicked.connect(self.copy_selected)
        btn_layout.addWidget(self.copy_btn)
        
        self.fav_btn = QPushButton("⭐ 收藏")
        self.fav_btn.setStyleSheet(self._get_button_style("#ff9800"))
        self.fav_btn.clicked.connect(self.toggle_favorite)
        btn_layout.addWidget(self.fav_btn)
        
        self.pin_btn = QPushButton("📌 置顶")
        self.pin_btn.setStyleSheet(self._get_button_style("#2196f3"))
        self.pin_btn.clicked.connect(self.toggle_pin)
        btn_layout.addWidget(self.pin_btn)
        
        self.delete_btn = QPushButton("🗑️ 删除")
        self.delete_btn.setStyleSheet(self._get_button_style("#f44336"))
        self.delete_btn.clicked.connect(self.delete_selected)
        btn_layout.addWidget(self.delete_btn)
        
        content_layout.addLayout(btn_layout)
        
        self.tab_widget.addTab(self.content_tab, "📝 内容")
        
        # AI处理标签
        self.ai_tab = QWidget()
        ai_layout = QVBoxLayout(self.ai_tab)
        
        # AI功能选择
        ai_btn_layout = QGridLayout()
        
        ai_features = [
            ("📝 摘要", self.ai_summarize),
            ("🌐 翻译", self.ai_translate),
            ("✨ 格式化", self.ai_format),
            ("🔍 提取", self.ai_extract),
            ("💻 代码审查", self.ai_code_review),
            ("😊 情感分析", self.ai_sentiment),
            ("🏷️ 分类", self.ai_classify),
        ]
        
        for i, (text, callback) in enumerate(ai_features):
            btn = QPushButton(text)
            btn.setStyleSheet(self._get_button_style("#9c27b0"))
            btn.clicked.connect(callback)
            ai_btn_layout.addWidget(btn, i // 3, i % 3)
        
        ai_layout.addLayout(ai_btn_layout)
        
        # AI结果显示
        self.ai_result_text = QTextEdit()
        self.ai_result_text.setReadOnly(True)
        self.ai_result_text.setPlaceholderText("AI处理结果将显示在这里...")
        self.ai_result_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                background-color: #f3e5f5;
            }
        """)
        ai_layout.addWidget(self.ai_result_text)
        
        # 复制AI结果按钮
        self.copy_ai_btn = QPushButton("📋 复制AI结果")
        self.copy_ai_btn.setStyleSheet(self._get_button_style("#9c27b0"))
        self.copy_ai_btn.clicked.connect(self.copy_ai_result)
        ai_layout.addWidget(self.copy_ai_btn)
        
        self.tab_widget.addTab(self.ai_tab, "🤖 AI处理")
        
        # OCR标签
        self.ocr_tab = QWidget()
        ocr_layout = QVBoxLayout(self.ocr_tab)
        
        self.ocr_btn = QPushButton("🖼️ 识别剪贴板图片")
        self.ocr_btn.setStyleSheet(self._get_button_style("#00bcd4", large=True))
        self.ocr_btn.clicked.connect(self.perform_ocr)
        ocr_layout.addWidget(self.ocr_btn)
        
        self.ocr_result_text = QTextEdit()
        self.ocr_result_text.setReadOnly(True)
        self.ocr_result_text.setPlaceholderText("OCR识别结果将显示在这里...")
        self.ocr_result_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                background-color: #e0f7fa;
            }
        """)
        ocr_layout.addWidget(self.ocr_result_text)
        
        self.copy_ocr_btn = QPushButton("📋 复制OCR结果")
        self.copy_ocr_btn.setStyleSheet(self._get_button_style("#00bcd4"))
        self.copy_ocr_btn.clicked.connect(self.copy_ocr_result)
        ocr_layout.addWidget(self.copy_ocr_btn)
        
        self.tab_widget.addTab(self.ocr_tab, "🖼️ OCR识别")
        
        right_layout.addWidget(self.tab_widget)
        
        splitter.addWidget(right_widget)
        
        # 设置分割比例
        splitter.setSizes([400, 500])
        
        # 当前选中的条目
        self.current_item: Optional[ClipboardItem] = None
    
    def _get_button_style(self, color: str, large: bool = False) -> str:
        """生成按钮样式"""
        padding = "15px 30px" if large else "10px 20px"
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 6px;
                padding: {padding};
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {color}dd;
            }}
            QPushButton:pressed {{
                background-color: {color}aa;
            }}
        """
    
    def setup_menu(self):
        """设置菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件")
        
        exit_action = QAction("退出", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 编辑菜单
        edit_menu = menubar.addMenu("编辑")
        
        clear_action = QAction("清空历史", self)
        clear_action.triggered.connect(self.clear_history)
        edit_menu.addAction(clear_action)
        
        # 视图菜单
        view_menu = menubar.addMenu("视图")
        
        refresh_action = QAction("刷新", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.load_history)
        view_menu.addAction(refresh_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助")
        
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_toolbar(self):
        """设置工具栏"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # 显示收藏
        fav_action = QAction("⭐ 收藏", self)
        fav_action.triggered.connect(self.show_favorites)
        toolbar.addAction(fav_action)
        
        # 显示置顶
        pin_action = QAction("📌 置顶", self)
        pin_action.triggered.connect(self.show_pinned)
        toolbar.addAction(pin_action)
        
        toolbar.addSeparator()
        
        # 设置
        settings_action = QAction("⚙️ 设置", self)
        settings_action.triggered.connect(self.show_settings)
        toolbar.addAction(settings_action)
    
    def setup_statusbar(self):
        """设置状态栏"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("就绪")
    
    def setup_shortcuts(self):
        """设置快捷键"""
        # Ctrl+F 聚焦搜索
        search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        search_shortcut.activated.connect(self.search_input.setFocus)
        
        # Delete 删除选中
        delete_shortcut = QShortcut(QKeySequence("Delete"), self)
        delete_shortcut.activated.connect(self.delete_selected)
        
        # Ctrl+C 复制选中
        copy_shortcut = QShortcut(QKeySequence("Ctrl+C"), self)
        copy_shortcut.activated.connect(self.copy_selected)
    
    def setup_tray(self):
        """设置系统托盘"""
        self.tray_icon = QSystemTrayIcon(self)
        # 使用系统图标
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        
        # 托盘菜单
        tray_menu = QMenu()
        
        show_action = QAction("显示", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction("退出", self)
        quit_action.triggered.connect(self.quit_app)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()
    
    def load_history(self):
        """加载历史记录"""
        self.history_list.clear()
        
        items = self.clipboard_manager.get_history(100)
        
        for item in items:
            list_item = QListWidgetItem()
            widget = ClipboardListItem(item)
            
            list_item.setSizeHint(widget.sizeHint())
            list_item.setData(Qt.ItemDataRole.UserRole, item.id)
            
            self.history_list.addItem(list_item)
            self.history_list.setItemWidget(list_item, widget)
        
        # 更新统计
        stats = self.clipboard_manager.get_statistics()
        self.stats_label.setText(
            f"📊 总计: {stats.get('total_items', 0)} | "
            f"⭐ 收藏: {stats.get('favorite_count', 0)} | "
            f"📌 置顶: {stats.get('pinned_count', 0)} | "
            f"📅 今日: {stats.get('today_count', 0)}"
        )
    
    def on_search(self, text: str):
        """搜索处理"""
        if not text:
            self.load_history()
            return
        
        self.history_list.clear()
        items = self.clipboard_manager.search_history(text, 50)
        
        for item in items:
            list_item = QListWidgetItem()
            widget = ClipboardListItem(item)
            
            list_item.setSizeHint(widget.sizeHint())
            list_item.setData(Qt.ItemDataRole.UserRole, item.id)
            
            self.history_list.addItem(list_item)
            self.history_list.setItemWidget(list_item, widget)
    
    def clear_search(self):
        """清除搜索"""
        self.search_input.clear()
        self.load_history()
    
    def on_item_selected(self, item: QListWidgetItem):
        """条目选中处理"""
        item_id = item.data(Qt.ItemDataRole.UserRole)
        self.current_item = self.clipboard_manager.db.get_item_by_id(item_id)
        
        if self.current_item:
            self.content_text.setText(self.current_item.content)
            self.statusbar.showMessage(f"选中: ID {item_id}")
    
    def on_clipboard_change(self, content: ClipboardContent):
        """剪贴板变化处理"""
        self.statusbar.showMessage("检测到新剪贴板内容", 2000)
        # 延迟刷新以显示新内容
        QTimer.singleShot(500, self.load_history)
    
    def show_context_menu(self, position):
        """显示右键菜单"""
        item = self.history_list.itemAt(position)
        if not item:
            return
        
        menu = QMenu()
        
        copy_action = QAction("📋 复制", self)
        copy_action.triggered.connect(self.copy_selected)
        menu.addAction(copy_action)
        
        fav_action = QAction("⭐ 收藏/取消", self)
        fav_action.triggered.connect(self.toggle_favorite)
        menu.addAction(fav_action)
        
        pin_action = QAction("📌 置顶/取消", self)
        pin_action.triggered.connect(self.toggle_pin)
        menu.addAction(pin_action)
        
        menu.addSeparator()
        
        delete_action = QAction("🗑️ 删除", self)
        delete_action.triggered.connect(self.delete_selected)
        menu.addAction(delete_action)
        
        menu.exec(self.history_list.mapToGlobal(position))
    
    def copy_selected(self):
        """复制选中内容"""
        if self.current_item:
            self.clipboard_manager.copy_to_clipboard(self.current_item.content)
            self.statusbar.showMessage("已复制到剪贴板", 2000)
    
    def toggle_favorite(self):
        """切换收藏状态"""
        if self.current_item:
            self.clipboard_manager.toggle_favorite(self.current_item.id)
            self.load_history()
            self.statusbar.showMessage("收藏状态已切换", 2000)
    
    def toggle_pin(self):
        """切换置顶状态"""
        if self.current_item:
            self.clipboard_manager.toggle_pin(self.current_item.id)
            self.load_history()
            self.statusbar.showMessage("置顶状态已切换", 2000)
    
    def delete_selected(self):
        """删除选中条目"""
        if self.current_item:
            reply = QMessageBox.question(
                self, "确认删除",
                "确定要删除这条记录吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.clipboard_manager.delete_item(self.current_item.id)
                self.current_item = None
                self.content_text.clear()
                self.load_history()
                self.statusbar.showMessage("已删除", 2000)
    
    def clear_history(self):
        """清空历史"""
        reply = QMessageBox.question(
            self, "确认清空",
            "确定要清空历史记录吗？\n收藏的条目将被保留。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            count = self.clipboard_manager.clear_history(keep_favorites=True)
            self.load_history()
            self.statusbar.showMessage(f"已清空 {count} 条记录", 2000)
    
    def show_favorites(self):
        """显示收藏"""
        self.history_list.clear()
        items = self.clipboard_manager.db.get_favorites()
        
        for item in items:
            list_item = QListWidgetItem()
            widget = ClipboardListItem(item)
            
            list_item.setSizeHint(widget.sizeHint())
            list_item.setData(Qt.ItemDataRole.UserRole, item.id)
            
            self.history_list.addItem(list_item)
            self.history_list.setItemWidget(list_item, widget)
        
        self.statusbar.showMessage(f"显示 {len(items)} 条收藏", 2000)
    
    def show_pinned(self):
        """显示置顶"""
        self.load_history()
        self.statusbar.showMessage("已按置顶排序", 2000)
    
    # AI功能
    def ai_summarize(self):
        """AI摘要"""
        if not self.current_item:
            return
        
        self.statusbar.showMessage("正在生成摘要...")
        result = self.ai_processor.summarize(self.current_item.content)
        
        if result.success:
            self.ai_result_text.setText(f"【摘要】\n\n{result.content}")
        else:
            self.ai_result_text.setText(f"处理失败: {result.error}")
        
        self.tab_widget.setCurrentIndex(1)
    
    def ai_translate(self):
        """AI翻译"""
        if not self.current_item:
            return
        
        # 简单判断语言
        target_lang = "中文" if any('\u4e00' <= c <= '\u9fff' for c in self.current_item.content[:50]) else "English"
        
        self.statusbar.showMessage(f"正在翻译为{target_lang}...")
        result = self.ai_processor.translate(self.current_item.content, target_lang)
        
        if result.success:
            self.ai_result_text.setText(f"【翻译为{target_lang}】\n\n{result.content}")
        else:
            self.ai_result_text.setText(f"处理失败: {result.error}")
        
        self.tab_widget.setCurrentIndex(1)
    
    def ai_format(self):
        """AI格式化"""
        if not self.current_item:
            return
        
        self.statusbar.showMessage("正在格式化...")
        result = self.ai_processor.format_text(self.current_item.content)
        
        if result.success:
            self.ai_result_text.setText(f"【格式化结果】\n\n{result.content}")
        else:
            self.ai_result_text.setText(f"处理失败: {result.error}")
        
        self.tab_widget.setCurrentIndex(1)
    
    def ai_extract(self):
        """AI提取"""
        if not self.current_item:
            return
        
        self.statusbar.showMessage("正在提取信息...")
        result = self.ai_processor.extract_info(self.current_item.content)
        
        if result.success:
            self.ai_result_text.setText(f"【提取结果】\n\n{result.content}")
        else:
            self.ai_result_text.setText(f"处理失败: {result.error}")
        
        self.tab_widget.setCurrentIndex(1)
    
    def ai_code_review(self):
        """AI代码审查"""
        if not self.current_item:
            return
        
        self.statusbar.showMessage("正在审查代码...")
        result = self.ai_processor.review_code(self.current_item.content)
        
        if result.success:
            self.ai_result_text.setText(f"【代码审查】\n\n{result.content}")
        else:
            self.ai_result_text.setText(f"处理失败: {result.error}")
        
        self.tab_widget.setCurrentIndex(1)
    
    def ai_sentiment(self):
        """AI情感分析"""
        if not self.current_item:
            return
        
        self.statusbar.showMessage("正在分析情感...")
        result = self.ai_processor.analyze_sentiment(self.current_item.content)
        
        if result.success:
            self.ai_result_text.setText(f"【情感分析】\n\n{result.content}")
        else:
            self.ai_result_text.setText(f"处理失败: {result.error}")
        
        self.tab_widget.setCurrentIndex(1)
    
    def ai_classify(self):
        """AI分类"""
        if not self.current_item:
            return
        
        self.statusbar.showMessage("正在分类...")
        result = self.ai_processor.classify(self.current_item.content)
        
        if result.success:
            self.ai_result_text.setText(f"【分类结果】\n\n类别: {result.content}")
        else:
            self.ai_result_text.setText(f"处理失败: {result.error}")
        
        self.tab_widget.setCurrentIndex(1)
    
    def copy_ai_result(self):
        """复制AI结果"""
        text = self.ai_result_text.toPlainText()
        if text:
            self.clipboard_manager.copy_to_clipboard(text)
            self.statusbar.showMessage("AI结果已复制", 2000)
    
    # OCR功能
    def perform_ocr(self):
        """执行OCR"""
        self.statusbar.showMessage("正在识别图片...")
        results = self.ocr_engine.recognize_clipboard_image()
        
        if results:
            text = self.ocr_engine.get_full_text(results)
            self.ocr_result_text.setText(text)
            self.statusbar.showMessage(f"识别完成，共 {len(results)} 行", 2000)
        else:
            self.ocr_result_text.setText("未能识别剪贴板中的图片，请确保剪贴板包含图片内容。")
            self.statusbar.showMessage("识别失败", 2000)
        
        self.tab_widget.setCurrentIndex(2)
    
    def copy_ocr_result(self):
        """复制OCR结果"""
        text = self.ocr_result_text.toPlainText()
        if text:
            self.clipboard_manager.copy_to_clipboard(text)
            self.statusbar.showMessage("OCR结果已复制", 2000)
    
    def show_settings(self):
        """显示设置对话框"""
        QMessageBox.information(self, "设置", "设置功能开发中...")
    
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于 SmartClipboard",
            "<h2>SmartClipboard v1.0.0</h2>"
            "<p>智能剪贴板管理工具</p>"
            "<p>功能特性：</p>"
            "<ul>"
            "<li>📝 剪贴板历史管理</li>"
            "<li>🤖 AI智能处理</li>"
            "<li>🖼️ OCR图片识别</li>"
            "<li>⭐ 收藏与置顶</li>"
            "<li>🔍 全文搜索</li>"
            "</ul>"
            "<p>License: MIT</p>"
        )
    
    def on_tray_activated(self, reason):
        """托盘图标激活处理"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show()
            self.raise_()
            self.activateWindow()
    
    def closeEvent(self, event):
        """关闭事件处理"""
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "SmartClipboard",
            "程序已最小化到系统托盘",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )
    
    def quit_app(self):
        """退出应用"""
        self.clipboard_manager.close()
        self.tray_icon.hide()
        QApplication.quit()


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用样式
    app.setStyle('Fusion')
    
    # 设置调色板
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(250, 250, 250))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(33, 33, 33))
    app.setPalette(palette)
    
    # 设置字体
    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)
    
    window = SmartClipboardWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
