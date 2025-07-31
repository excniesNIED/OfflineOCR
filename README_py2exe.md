# 使用py2exe打包OfflinePDF-OCR

这是一个使用py2exe替代PyInstaller的打包方案，专门针对OCR工具和Conda虚拟环境进行了优化。

## 为什么选择py2exe？

1. **专为Windows设计**：py2exe是专门为Windows平台设计的打包工具，与Windows系统集成更好
2. **Conda环境兼容性**：在Conda虚拟环境中通常比PyInstaller更稳定
3. **依赖处理**：对Python标准库和第三方库的处理更直接
4. **减少错误**：避免了PyInstaller的一些常见错误，如隐藏导入错误等

## 安装py2exe

确保在您的OCR Conda环境中安装py2exe：

```bash
# 激活OCR环境
conda activate ocr

# 安装py2exe
pip install py2exe
```

## 使用方法

### 1. 使用构建脚本（推荐）

```bash
python build_py2exe.py
```

### 2. 直接使用setup.py

```bash
python setup.py py2exe
```

## 项目结构

打包后的文件将位于`dist`文件夹中：

```
dist/
├── main.exe              # 主程序exe文件
├── models/               # OCR模型文件夹
│   ├── det/              # 检测模型
│   ├── rec/              # 识别模型
│   └── cls/              # 方向分类模型
├── app_icon.ico          # 图标文件（如果存在）
└── 其他依赖文件...
```

## 配置说明

### setup.py配置详解

1. **基本配置**：
   ```python
   name='OfflinePDF-OCR'     # 应用名称
   version='1.0'             # 版本号
   ```

2. **py2exe选项**：
   ```python
   'bundle_files': 1         # 打包成单个exe文件
   'compressed': True        # 压缩文件
   'optimize': 2             # 优化级别
   ```

3. **依赖管理**：
   ```python
   'excludes': [...]         # 排除不需要的模块
   'includes': [...]         # 包含必需的模块
   'packages': [...]         # 包含的包
   ```

4. **数据文件**：
   - 自动包含models文件夹中的所有模型文件
   - 包含图标文件（如果存在）

## 常见问题解决

### 1. 模块未找到错误

如果运行时出现模块未找到错误，请在setup.py的`includes`列表中添加相应模块。

### 2. 模型文件未包含

确保models文件夹结构正确，脚本会自动包含所有模型文件。

### 3. 图标未生效

确保app_icon.ico文件存在于项目根目录，并且是有效的ICO格式。

## 与PyInstaller的对比

| 特性 | PyInstaller | py2exe |
|------|-------------|--------|
| Windows兼容性 | 良好 | 优秀 |
| Conda环境支持 | 一般 | 优秀 |
| 构建速度 | 较慢 | 较快 |
| 文件大小 | 较大 | 适中 |
| 隐藏导入错误 | 常见 | 较少 |
| 配置复杂度 | 复杂(spec文件) | 简单(setup.py) |

## 注意事项

1. **仅限Windows**：py2exe只能在Windows平台上使用
2. **Python版本**：确保使用与py2exe兼容的Python版本
3. **依赖检查**：构建前确保所有依赖已正确安装
4. **模型文件**：确保models文件夹包含所有必需的模型文件
5. **测试运行**：构建完成后在不同环境中测试exe文件