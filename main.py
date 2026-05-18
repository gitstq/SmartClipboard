#!/usr/bin/env python3
"""
SmartClipboard - 智能剪贴板管理工具
主入口文件

Usage:
    python main.py              # 启动GUI
    python main.py --cli        # 启动CLI模式
    python main.py --daemon     # 后台守护模式
"""

import sys
import os
import argparse
import signal

# 确保可以导入本地模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def run_gui():
    """运行GUI模式"""
    try:
        from smartclipboard.gui import main
        main()
    except ImportError as e:
        print(f"无法启动GUI: {e}")
        print("请确保已安装PyQt6: pip install PyQt6")
        sys.exit(1)


def run_cli():
    """运行CLI模式"""
    from smartclipboard.clipboard_manager import ClipboardManager
    from smartclipboard.ocr_engine import create_ocr_engine
    from smartclipboard.ai_processor import create_ai_processor
    
    import cmd
    
    class SmartClipboardCLI(cmd.Cmd):
        intro = """
╔══════════════════════════════════════════════════════════════╗
║              SmartClipboard CLI v1.0.0                       ║
║         智能剪贴板管理工具 - 命令行界面                       ║
╠══════════════════════════════════════════════════════════════╣
║  命令:                                                        ║
║    history    - 显示剪贴板历史                                ║
║    search     - 搜索历史记录                                  ║
║    copy       - 复制指定ID的内容到剪贴板                      ║
║    fav        - 收藏/取消收藏指定ID                           ║
║    pin        - 置顶/取消置顶指定ID                           ║
║    delete     - 删除指定ID的记录                              ║
║    clear      - 清空历史（保留收藏）                          ║
║    stats      - 显示统计信息                                  ║
║    ocr        - 识别剪贴板图片                                ║
║    ai         - AI处理指定ID的内容                            ║
║    help       - 显示帮助                                      ║
║    quit       - 退出程序                                      ║
╚══════════════════════════════════════════════════════════════╝
        """
        prompt = "SmartClipboard> "
        
        def __init__(self):
            super().__init__()
            self.manager = ClipboardManager()
            self.ocr = create_ocr_engine(fallback_to_mock=True)
            self.ai = create_ai_processor(use_local_fallback=True)
            self.manager.start_monitoring()
        
        def do_history(self, arg):
            """显示剪贴板历史: history [limit]"""
            try:
                limit = int(arg) if arg else 20
            except ValueError:
                limit = 20
            
            items = self.manager.get_history(limit)
            
            print(f"\n{'ID':<6} {'Type':<10} {'Content':<50} {'Time':<16}")
            print("-" * 90)
            
            for item in items:
                content = item.content[:47] + "..." if len(item.content) > 50 else item.content
                content = content.replace('\n', ' ')
                time_str = item.updated_at.strftime("%m-%d %H:%M") if item.updated_at else ""
                fav_mark = "⭐" if item.is_favorite else " "
                pin_mark = "📌" if item.is_pinned else " "
                
                print(f"{item.id:<6} {item.content_type:<10} {content:<50} {time_str:<16} {fav_mark}{pin_mark}")
            
            print(f"\n共 {len(items)} 条记录\n")
        
        def do_search(self, arg):
            """搜索历史记录: search <keyword>"""
            if not arg:
                print("请输入搜索关键词")
                return
            
            items = self.manager.search_history(arg, 50)
            
            print(f"\n搜索 '{arg}' 的结果:\n")
            print(f"{'ID':<6} {'Type':<10} {'Content':<50} {'Time':<16}")
            print("-" * 90)
            
            for item in items:
                content = item.content[:47] + "..." if len(item.content) > 50 else item.content
                content = content.replace('\n', ' ')
                time_str = item.updated_at.strftime("%m-%d %H:%M") if item.updated_at else ""
                
                print(f"{item.id:<6} {item.content_type:<10} {content:<50} {time_str:<16}")
            
            print(f"\n找到 {len(items)} 条记录\n")
        
        def do_copy(self, arg):
            """复制指定ID的内容到剪贴板: copy <id>"""
            try:
                item_id = int(arg)
            except ValueError:
                print("请输入有效的ID")
                return
            
            item = self.manager.db.get_item_by_id(item_id)
            if item:
                self.manager.copy_to_clipboard(item.content)
                print(f"已复制ID {item_id} 的内容到剪贴板")
            else:
                print(f"未找到ID {item_id}")
        
        def do_fav(self, arg):
            """收藏/取消收藏指定ID: fav <id>"""
            try:
                item_id = int(arg)
            except ValueError:
                print("请输入有效的ID")
                return
            
            if self.manager.toggle_favorite(item_id):
                item = self.manager.db.get_item_by_id(item_id)
                status = "已收藏" if item and item.is_favorite else "已取消收藏"
                print(f"ID {item_id} {status}")
            else:
                print(f"未找到ID {item_id}")
        
        def do_pin(self, arg):
            """置顶/取消置顶指定ID: pin <id>"""
            try:
                item_id = int(arg)
            except ValueError:
                print("请输入有效的ID")
                return
            
            if self.manager.toggle_pin(item_id):
                item = self.manager.db.get_item_by_id(item_id)
                status = "已置顶" if item and item.is_pinned else "已取消置顶"
                print(f"ID {item_id} {status}")
            else:
                print(f"未找到ID {item_id}")
        
        def do_delete(self, arg):
            """删除指定ID的记录: delete <id>"""
            try:
                item_id = int(arg)
            except ValueError:
                print("请输入有效的ID")
                return
            
            if self.manager.delete_item(item_id):
                print(f"已删除ID {item_id}")
            else:
                print(f"未找到ID {item_id}")
        
        def do_clear(self, arg):
            """清空历史（保留收藏）: clear"""
            count = self.manager.clear_history(keep_favorites=True)
            print(f"已清空 {count} 条记录")
        
        def do_stats(self, arg):
            """显示统计信息: stats"""
            stats = self.manager.get_statistics()
            
            print("\n📊 剪贴板统计信息")
            print("-" * 40)
            print(f"总记录数:    {stats.get('total_items', 0)}")
            print(f"收藏数量:    {stats.get('favorite_count', 0)}")
            print(f"置顶数量:    {stats.get('pinned_count', 0)}")
            print(f"今日新增:    {stats.get('today_count', 0)}")
            
            type_dist = stats.get('type_distribution', {})
            if type_dist:
                print("\n类型分布:")
                for t, count in type_dist.items():
                    print(f"  {t}: {count}")
            print()
        
        def do_ocr(self, arg):
            """识别剪贴板图片: ocr"""
            print("正在识别剪贴板图片...")
            results = self.ocr.recognize_clipboard_image()
            
            if results:
                text = self.ocr.get_full_text(results)
                print(f"\n识别结果（共 {len(results)} 行）:\n")
                print(text)
                print()
            else:
                print("未能识别剪贴板中的图片")
        
        def do_ai(self, arg):
            """AI处理指定ID的内容: ai <id> [summarize|translate|format|classify]"""
            args = arg.split()
            if len(args) < 1:
                print("用法: ai <id> [summarize|translate|format|classify]")
                return
            
            try:
                item_id = int(args[0])
            except ValueError:
                print("请输入有效的ID")
                return
            
            item = self.manager.db.get_item_by_id(item_id)
            if not item:
                print(f"未找到ID {item_id}")
                return
            
            feature = args[1] if len(args) > 1 else "summarize"
            
            print(f"正在处理...")
            
            if feature == "summarize":
                result = self.ai.summarize(item.content)
            elif feature == "translate":
                result = self.ai.translate(item.content)
            elif feature == "format":
                result = self.ai.format_text(item.content)
            elif feature == "classify":
                result = self.ai.classify(item.content)
            else:
                print(f"未知功能: {feature}")
                return
            
            if result.success:
                print(f"\n【{feature}结果】\n")
                print(result.content)
                print()
            else:
                print(f"处理失败: {result.error}")
        
        def do_quit(self, arg):
            """退出程序: quit"""
            self.manager.close()
            print("再见！")
            return True
        
        def do_exit(self, arg):
            """退出程序: exit"""
            return self.do_quit(arg)
        
        def do_EOF(self, arg):
            """处理Ctrl+D"""
            print()
            return self.do_quit(arg)
    
    cli = SmartClipboardCLI()
    try:
        cli.cmdloop()
    except KeyboardInterrupt:
        print("\n再见！")
        cli.manager.close()


def run_daemon():
    """运行守护模式"""
    from smartclipboard.clipboard_manager import ClipboardManager
    import time
    
    print("SmartClipboard 守护模式已启动")
    print("按 Ctrl+C 停止")
    
    manager = ClipboardManager()
    manager.start_monitoring()
    
    def signal_handler(sig, frame):
        print("\n正在停止...")
        manager.close()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)


def main():
    """主入口"""
    parser = argparse.ArgumentParser(
        description="SmartClipboard - 智能剪贴板管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py              # 启动GUI界面
  python main.py --cli        # 启动命令行界面
  python main.py --daemon     # 启动后台守护模式
        """
    )
    
    parser.add_argument(
        '--cli',
        action='store_true',
        help='启动命令行模式'
    )
    
    parser.add_argument(
        '--daemon',
        action='store_true',
        help='启动守护模式（后台运行）'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='SmartClipboard v1.0.0'
    )
    
    args = parser.parse_args()
    
    if args.daemon:
        run_daemon()
    elif args.cli:
        run_cli()
    else:
        run_gui()


if __name__ == "__main__":
    main()
