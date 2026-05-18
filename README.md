<div align="center">

# 🚀 SmartClipboard

**智能剪贴板管理工具 - 让复制粘贴更智能**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.4+-green.svg)](https://www.riverbankcomputing.com/software/pyqt/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()

[简体中文](#简体中文) | [繁體中文](#繁體中文) | [English](#english)

</div>

---

## 简体中文

### 🎉 项目介绍

**SmartClipboard** 是一款功能强大的智能剪贴板管理工具，专为提升工作效率而设计。它不仅能记录剪贴板历史，还集成了 **OCR图片文字识别** 和 **AI智能处理** 功能，让复制粘贴变得更加智能高效。

#### 💡 灵感来源

在日常工作中，我们经常需要：
- 反复查找之前复制过的内容
- 从图片中提取文字信息
- 对复制的文本进行快速处理（翻译、摘要、格式化）

SmartClipboard 正是为解决这些痛点而生，它将剪贴板管理、OCR识别和AI处理完美融合，打造一站式生产力工具。

### ✨ 核心特性

| 功能 | 描述 | 状态 |
|------|------|------|
| 📝 **剪贴板历史** | 自动记录所有复制内容，支持文本、图片、文件 | ✅ |
| 🔍 **全文搜索** | 基于SQLite FTS5的快速搜索，毫秒级响应 | ✅ |
| ⭐ **收藏置顶** | 重要内容可收藏或置顶，方便快速访问 | ✅ |
| 🖼️ **OCR识别** | 集成PaddleOCR，支持图片文字识别 | ✅ |
| 🤖 **AI处理** | 摘要、翻译、格式化、代码审查、情感分析 | ✅ |
| 🎨 **现代UI** | PyQt6打造的现代化界面，支持系统托盘 | ✅ |
| ⌨️ **快捷键** | 丰富的快捷键支持，操作更便捷 | ✅ |
| 🌐 **跨平台** | 支持Windows、macOS、Linux | ✅ |

### 🚀 快速开始

#### 环境要求

- **Python**: 3.9 或更高版本
- **操作系统**: Windows 10+/macOS 10.15+/Linux
- **内存**: 建议 4GB+

#### 安装步骤

**方式一：从源码安装**

```bash
# 克隆仓库
git clone https://github.com/gitstq/SmartClipboard.git
cd SmartClipboard

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 运行程序
python main.py
```

**方式二：使用pip安装**

```bash
pip install -e .
smartclipboard
```

#### 启动方式

```bash
# GUI模式（默认）
python main.py

# 命令行模式
python main.py --cli

# 守护模式（后台运行）
python main.py --daemon
```

### 📖 详细使用指南

#### GUI界面操作

1. **查看历史**: 主界面左侧显示所有剪贴板历史记录
2. **搜索内容**: 顶部搜索框支持实时全文搜索
3. **复制内容**: 点击列表项，然后点击"复制到剪贴板"按钮
4. **收藏/置顶**: 选中条目后点击⭐或📌按钮
5. **AI处理**: 切换到"AI处理"标签，选择需要的功能
6. **OCR识别**: 切换到"OCR识别"标签，点击识别按钮

#### CLI命令行

```bash
# 显示历史记录
SmartClipboard> history

# 搜索内容
SmartClipboard> search 关键词

# 复制指定ID
SmartClipboard> copy 123

# 收藏/置顶
SmartClipboard> fav 123
SmartClipboard> pin 123

# AI处理
SmartClipboard> ai 123 summarize

# OCR识别
SmartClipboard> ocr
```

#### 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+F` | 聚焦搜索框 |
| `Delete` | 删除选中条目 |
| `Ctrl+C` | 复制选中内容 |
| `F5` | 刷新列表 |

### 💡 设计思路与迭代规划

#### 技术选型原因

- **PyQt6**: 跨平台原生体验，丰富的组件库
- **SQLite + FTS5**: 轻量级本地存储，支持全文搜索
- **PaddleOCR**: 中文识别效果优秀，支持离线使用
- **模块化架构**: 易于扩展和维护

#### 后续迭代计划

- [ ] 云同步功能（支持WebDAV、iCloud）
- [ ] 插件系统，支持自定义扩展
- [ ] 更多AI提供商支持（本地LLM）
- [ ] 剪贴板内容加密存储
- [ ] 团队协作功能

### 📦 打包与部署

#### 构建可执行文件

```bash
# 安装构建依赖
pip install pyinstaller

# 运行构建脚本
python build.py

# 或使用PyInstaller直接构建
pyinstaller --onefile --windowed main.py
```

#### 各平台打包

```bash
# Windows
python build.py

# macOS
python build.py

# Linux
python build.py
```

### 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 📄 开源协议

本项目采用 [MIT](LICENSE) 协议开源。

---

## 繁體中文

### 🎉 專案介紹

**SmartClipboard** 是一款功能強大的智慧剪貼簿管理工具，專為提升工作效率而設計。它不僅能記錄剪貼簿歷史，還整合了 **OCR圖片文字識別** 和 **AI智慧處理** 功能，讓複製貼上變得更加智慧高效。

#### 💡 靈感來源

在日常工作中，我們經常需要：
- 反覆查找之前複製過的內容
- 從圖片中提取文字資訊
- 對複製的文字進行快速處理（翻譯、摘要、格式化）

SmartClipboard 正是為解決這些痛點而生，它將剪貼簿管理、OCR識別和AI處理完美融合，打造一站式生產力工具。

### ✨ 核心特性

| 功能 | 描述 | 狀態 |
|------|------|------|
| 📝 **剪貼簿歷史** | 自動記錄所有複製內容，支援文字、圖片、檔案 | ✅ |
| 🔍 **全文搜尋** | 基於SQLite FTS5的快速搜尋，毫秒級響應 | ✅ |
| ⭐ **收藏置頂** | 重要內容可收藏或置頂，方便快速訪問 | ✅ |
| 🖼️ **OCR識別** | 整合PaddleOCR，支援圖片文字識別 | ✅ |
| 🤖 **AI處理** | 摘要、翻譯、格式化、程式碼審查、情感分析 | ✅ |
| 🎨 **現代UI** | PyQt6打造的現代化介面，支援系統托盤 | ✅ |
| ⌨️ **快捷鍵** | 豐富的快捷鍵支援，操作更便捷 | ✅ |
| 🌐 **跨平台** | 支援Windows、macOS、Linux | ✅ |

### 🚀 快速開始

#### 環境要求

- **Python**: 3.9 或更高版本
- **作業系統**: Windows 10+/macOS 10.15+/Linux
- **記憶體**: 建議 4GB+

#### 安裝步驟

```bash
# 克隆倉庫
git clone https://github.com/gitstq/SmartClipboard.git
cd SmartClipboard

# 建立虛擬環境
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 或 venv\Scripts\activate  # Windows

# 安裝依賴
pip install -r requirements.txt

# 執行程式
python main.py
```

### 📖 詳細使用指南

請參考簡體中文部分的詳細說明。

### 📄 開源協議

本專案採用 [MIT](LICENSE) 協議開源。

---

## English

### 🎉 Project Introduction

**SmartClipboard** is a powerful intelligent clipboard management tool designed to boost productivity. It not only records clipboard history but also integrates **OCR image text recognition** and **AI intelligent processing** features, making copy-paste smarter and more efficient.

#### 💡 Inspiration

In daily work, we often need to:
- Repeatedly search for previously copied content
- Extract text information from images
- Quickly process copied text (translation, summarization, formatting)

SmartClipboard was born to solve these pain points, perfectly integrating clipboard management, OCR recognition, and AI processing into a one-stop productivity tool.

### ✨ Core Features

| Feature | Description | Status |
|---------|-------------|--------|
| 📝 **Clipboard History** | Auto-record all copied content: text, images, files | ✅ |
| 🔍 **Full-text Search** | SQLite FTS5-based fast search, millisecond response | ✅ |
| ⭐ **Favorite & Pin** | Mark important content for quick access | ✅ |
| 🖼️ **OCR Recognition** | Integrated PaddleOCR for image text recognition | ✅ |
| 🤖 **AI Processing** | Summarize, translate, format, code review, sentiment analysis | ✅ |
| 🎨 **Modern UI** | PyQt6 modern interface with system tray support | ✅ |
| ⌨️ **Shortcuts** | Rich keyboard shortcuts for easier operation | ✅ |
| 🌐 **Cross-platform** | Support Windows, macOS, Linux | ✅ |

### 🚀 Quick Start

#### Requirements

- **Python**: 3.9 or higher
- **OS**: Windows 10+/macOS 10.15+/Linux
- **RAM**: 4GB+ recommended

#### Installation

```bash
# Clone repository
git clone https://github.com/gitstq/SmartClipboard.git
cd SmartClipboard

# Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# or venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

#### Launch Modes

```bash
# GUI mode (default)
python main.py

# CLI mode
python main.py --cli

# Daemon mode (background)
python main.py --daemon
```

### 📖 Detailed Usage Guide

#### GUI Operations

1. **View History**: Left panel shows all clipboard history
2. **Search**: Top search box supports real-time full-text search
3. **Copy**: Select item and click "Copy to Clipboard" button
4. **Favorite/Pin**: Click ⭐ or 📌 button after selecting item
5. **AI Processing**: Switch to "AI Processing" tab and select function
6. **OCR**: Switch to "OCR" tab and click recognize button

#### CLI Commands

```bash
# Show history
SmartClipboard> history

# Search content
SmartClipboard> search keyword

# Copy by ID
SmartClipboard> copy 123

# Favorite/Pin
SmartClipboard> fav 123
SmartClipboard> pin 123

# AI processing
SmartClipboard> ai 123 summarize

# OCR recognition
SmartClipboard> ocr
```

#### Keyboard Shortcuts

| Shortcut | Function |
|----------|----------|
| `Ctrl+F` | Focus search box |
| `Delete` | Delete selected item |
| `Ctrl+C` | Copy selected content |
| `F5` | Refresh list |

### 💡 Design Philosophy & Roadmap

#### Technical Choices

- **PyQt6**: Cross-platform native experience, rich component library
- **SQLite + FTS5**: Lightweight local storage with full-text search
- **PaddleOCR**: Excellent Chinese recognition, supports offline use
- **Modular Architecture**: Easy to extend and maintain

#### Roadmap

- [ ] Cloud sync (WebDAV, iCloud support)
- [ ] Plugin system for custom extensions
- [ ] More AI providers (local LLM support)
- [ ] Encrypted clipboard storage
- [ ] Team collaboration features

### 📦 Packaging & Deployment

#### Build Executable

```bash
# Install build dependencies
pip install pyinstaller

# Run build script
python build.py

# Or use PyInstaller directly
pyinstaller --onefile --windowed main.py
```

### 🤝 Contributing

Contributions are welcome! Please feel free to submit Issues and Pull Requests.

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Create Pull Request

### 📄 License

This project is licensed under the [MIT](LICENSE) License.

---

<div align="center">

**Made with ❤️ by SmartClipboard Team**

⭐ Star us on GitHub — it motivates us a lot!

</div>
