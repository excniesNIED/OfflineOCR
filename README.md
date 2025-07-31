# 离线PDF-OCR工具

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)]()
[![License](https://img.shields.io/badge/license-MIT-blue.svg)]()

一个完全离线的PDF OCR工具，使用PaddleOCR进行文本识别，支持中英文，具有现代化的GUI界面，并可打包为独立的exe文件。

## 功能特点

- 🖥️ **完全离线工作** - 无需网络连接，所有模型本地运行
- 📄 **PDF支持** - 直接处理PDF文件，自动转换为图像进行OCR
- 🧠 **高精度OCR** - 基于PaddleOCR PP-Structure，支持复杂版面分析
- 🌐 **多语言支持** - 支持中英文等多种语言识别
- 🎨 **现代化界面** - 基于CustomTkinter的美观GUI界面
- 📦 **独立打包** - 可打包为单个exe文件，便于分发
- ⚡ **多线程处理** - 后台处理OCR任务，界面不卡顿
- 📊 **进度显示** - 实时显示处理进度

## 界面预览

![界面截图](screenshot.png) *(需要添加实际截图)*

## 环境准备

### 方法一：使用Conda（推荐）

```bash
# 创建虚拟环境
conda create -n ocr python=3.9
conda activate ocr

# 安装依赖
pip install -r requirements.txt
```

### 方法二：使用原生Python

```bash
# 创建虚拟环境
python -m venv ocr_env
# Windows
ocr_env\Scripts\activate
# macOS/Linux
source ocr_env/bin/activate

# 升级pip并安装依赖
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 模型准备

### 自动下载并设置模型（推荐）

```bash
python setup_models.py
```

该脚本会自动完成以下操作：
1. 下载所需的PaddleOCR模型
2. 将模型文件复制到项目目录的`models`文件夹中
3. 验证模型文件是否正确复制

### 手动下载模型

```bash
python pre_download_models.py
```

脚本会自动下载所需模型文件到用户目录的`.paddleocr`文件夹中。

### 手动设置模型

1. 创建项目中的`models`文件夹
2. 将下载的模型文件从用户目录下的`.paddleocr/whl`文件夹复制到项目中的`models`文件夹
3. 确保最终项目结构如下：

```
project/
├── main.py
├── models/
│   ├── cls/
│   │   └── ch_ppocr_mobile_v2.0_cls_infer/
│   ├── det/
│   │   └── ch/ch_PP-OCRv4_det_infer/
│   └── rec/
│       └── ch/ch_PP-OCRv4_rec_infer/
├── requirements.txt
└── ...
```

## 使用方法

### 开发模式运行

```bash
python main.py
```

### 程序功能说明

1. **选择PDF文件** - 点击"选择PDF文件"按钮选择要处理的PDF文件
2. **设置参数** - 可调整图像缩放比例和识别语言
3. **开始识别** - 点击"开始识别"按钮开始OCR处理
4. **查看结果** - 识别结果会实时显示在文本框中
5. **导出结果** - 可通过菜单栏复制结果到剪贴板

### 界面操作

- **文件菜单**：
  - 打开PDF：选择要处理的PDF文件
  - 退出：关闭程序

- **编辑菜单**：
  - 清空结果：清空当前识别结果
  - 复制全部：将所有结果复制到剪贴板

- **帮助菜单**：
  - 关于：显示程序信息

## 打包为exe

### 自动打包

```bash
python build.py
```

### 手动打包

```bash
pyinstaller --noconsole --onefile --name OfflinePDF-OCR --add-data "models;models" main.py
```

打包完成后，exe文件将位于`dist`文件夹中。

### 打包选项

- `--noconsole` 或 `--windowed`：不显示控制台窗口
- `--onefile`：打包为单个exe文件
- `--name`：指定生成的exe文件名
- `--add-data`：添加数据文件（模型文件）
- `--icon`：指定程序图标（需要ico文件）

## 项目结构

```
ocr-project/
├── main.py                 # 主程序文件
├── setup_models.py         # 自动设置模型脚本（推荐）
├── pre_download_models.py  # 手动模型下载脚本
├── build.py                # 打包脚本
├── requirements.txt        # 依赖列表
├── README.md              # 说明文档
├── models/                # OCR模型文件夹（需手动创建）
│   ├── det/               # 检测模型
│   ├── rec/               # 识别模型
│   └── cls/               # 方向分类模型
└── dist/                  # 打包生成的exe文件（打包后自动生成）
```

## 系统要求

- **操作系统**：Windows 7 SP1及以上 / macOS 10.13及以上 / Ubuntu 16.04 LTS及以上
- **Python版本**：3.8及以上
- **内存**：建议4GB以上
- **磁盘空间**：至少2GB可用空间（包括模型文件）

## 常见问题

### 1. 启动时报错"无法加载本地OCR模型"

确保models文件夹已正确放置且包含所需的模型文件。

### 2. 识别准确率不高

可以尝试调整图像缩放比例，通常2.0-3.0的效果较好。

### 3. 打包后的exe文件很大

这是正常的，因为包含了模型文件和Python运行时。

### 4. 打包时报错找不到模型文件

确保打包时使用了`--add-data "models;models"`参数。

## 技术栈

- **GUI框架**：[CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- **OCR引擎**：[PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)
- **PDF处理**：[PyMuPDF](https://github.com/pymupdf/PyMuPDF)
- **打包工具**：[PyInstaller](https://github.com/pyinstaller/pyinstaller)

## 许可证

本项目采用MIT许可证，详情请见[LICENSE](LICENSE)文件。

## 贡献

欢迎提交Issue和Pull Request来改进本项目。