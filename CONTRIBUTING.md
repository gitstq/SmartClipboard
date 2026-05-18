# 🤝 Contributing to SmartClipboard

感谢您对 SmartClipboard 项目的关注！我们欢迎并感谢所有形式的贡献。

## 🚀 如何贡献

### 报告问题

如果您发现了bug或有功能建议，请通过 [GitHub Issues](https://github.com/gitstq/SmartClipboard/issues) 提交：

1. 使用清晰的标题描述问题
2. 提供详细的问题描述，包括：
   - 操作系统和版本
   - Python版本
   - 复现步骤
   - 期望行为和实际行为
   - 错误日志或截图

### 提交代码

1. **Fork 仓库**
   ```bash
   git clone https://github.com/your-username/SmartClipboard.git
   cd SmartClipboard
   ```

2. **创建特性分支**
   ```bash
   git checkout -b feature/your-feature-name
   # 或
   git checkout -b fix/your-bug-fix
   ```

3. **提交更改**
   ```bash
   git add .
   git commit -m "feat: 添加新功能描述"
   ```

4. **推送到您的Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **创建 Pull Request**
   - 描述您的更改
   - 关联相关的Issue
   - 确保CI检查通过

### 代码规范

#### Python代码风格

- 遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 规范
- 使用 4 个空格缩进
- 最大行长度 100 字符
- 使用有意义的变量名

#### 提交信息规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

```
<type>(<scope>): <subject>

<body>

<footer>
```

类型说明：
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整（不影响功能）
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

示例：
```
feat(ocr): 添加对多语言OCR的支持

- 集成Tesseract OCR引擎
- 支持英文、中文、日文识别
- 添加语言自动检测功能

Closes #123
```

### 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/gitstq/SmartClipboard.git
cd SmartClipboard

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 安装开发依赖
pip install -r requirements.txt
pip install pytest black flake8

# 运行测试
pytest

# 代码格式化
black .

# 代码检查
flake8 .
```

### 测试

- 为新功能编写测试用例
- 确保所有测试通过
- 保持代码覆盖率

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_database.py

# 生成覆盖率报告
pytest --cov=smartclipboard --cov-report=html
```

## 📋 贡献检查清单

- [ ] 代码符合项目风格规范
- [ ] 添加了必要的测试
- [ ] 所有测试通过
- [ ] 更新了相关文档
- [ ] 添加了CHANGELOG条目
- [ ] 提交信息符合规范

## 🎯 开发路线图

查看 [Projects](https://github.com/gitstq/SmartClipboard/projects) 了解当前开发重点。

## 💬 社区交流

- GitHub Discussions: 一般性讨论
- GitHub Issues: Bug报告和功能请求

## 🙏 感谢

再次感谢您的贡献！每一份努力都让 SmartClipboard 变得更好。
