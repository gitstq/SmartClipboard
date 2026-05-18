# Changelog

所有重要的更改都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### Planned
- 云同步功能（WebDAV、iCloud）
- 插件系统
- 本地LLM支持
- 剪贴板内容加密

## [1.0.0] - 2026-05-18

### ✨ Added
- 🎉 项目首次发布
- 📝 剪贴板历史管理功能
  - 自动记录所有复制内容
  - 支持文本、图片、文件类型
  - SQLite持久化存储
  - FTS5全文搜索
- ⭐ 收藏和置顶功能
- 🔍 实时搜索功能
- 🖼️ OCR图片文字识别
  - 集成PaddleOCR
  - 支持剪贴板图片识别
  - 支持本地图片文件识别
- 🤖 AI智能处理
  - 文本摘要
  - 多语言翻译
  - 文本格式化
  - 信息提取
  - 代码审查
  - 情感分析
  - 内容分类
- 🎨 PyQt6现代化GUI
  - 系统托盘支持
  - 多标签界面
  - 响应式设计
  - 自定义列表项
- ⌨️ 丰富的快捷键支持
- 🌐 跨平台支持（Windows/macOS/Linux）
- 💻 CLI命令行模式
- 👻 守护进程模式
- 📦 PyInstaller打包脚本

### 🔧 Technical
- 模块化架构设计
- 数据库抽象层
- AI处理器抽象接口
- OCR引擎抽象接口
- 跨平台剪贴板访问

## 版本说明

### 版本号格式
- **主版本号**：不兼容的API更改
- **次版本号**：向下兼容的功能添加
- **修订号**：向下兼容的问题修复

### 标签说明
- `Added` 新添加的功能
- `Changed` 对现有功能的变更
- `Deprecated` 即将移除的功能
- `Removed` 已移除的功能
- `Fixed` 修复的bug
- `Security` 安全相关的修复
