# -*- mode: python ; coding: utf-8 -*-

import os
import sys

block_cipher = None

# 获取当前目录
current_dir = os.path.dirname(os.path.abspath(sys.argv[0])) if hasattr(sys, 'argv') and sys.argv else os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
print(f"Current directory: {current_dir}")

# 添加模型文件路径
models_path = os.path.join(current_dir, 'models')
print(f"Models path: {models_path}")

# 检查模型目录是否存在
if os.path.exists(models_path):
    print("Models directory found")
    # 列出模型子目录
    for root, dirs, files in os.walk(models_path):
        level = root.replace(models_path, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f'{indent}{os.path.basename(root)}/')
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            print(f'{subindent}{file}')
else:
    print("Warning: Models directory not found")

# 添加paddle和paddleocr相关路径
paddle_path = None
paddleocr_path = None
paddlex_path = None

try:
    import paddle
    paddle_path = os.path.dirname(paddle.__file__)
    print(f"Found paddle at: {paddle_path}")
except ImportError as e:
    print(f"Could not import paddle: {e}")

try:
    import paddleocr
    paddleocr_path = os.path.dirname(paddleocr.__file__)
    print(f"Found paddleocr at: {paddleocr_path}")
except ImportError as e:
    print(f"Could not import paddleocr: {e}")

try:
    import paddlex
    paddlex_path = os.path.dirname(paddlex.__file__)
    print(f"Found paddlex at: {paddlex_path}")
    
    # 特别添加.version文件
    version_file = os.path.join(paddlex_path, '.version')
    if os.path.exists(version_file):
        print(f"Found paddlex version file at: {version_file}")
except ImportError as e:
    print(f"Could not import paddlex: {e}")

# 收集数据文件
datas = []

# 添加模型文件（使用更精确的映射）
if os.path.exists(models_path):
    # 添加整个models目录
    datas.append((models_path, 'models'))
    print("添加模型文件夹到打包文件")
    
    # 显式添加模型子目录（解决可能的路径问题）
    model_subdirs = [
        ('models/det/ch/ch_PP-OCRv4_det_infer', 'models/det/ch/ch_PP-OCRv4_det_infer'),
        ('models/rec/ch/ch_PP-OCRv4_rec_infer', 'models/rec/ch/ch_PP-OCRv4_rec_infer'),
        ('models/cls/ch_ppocr_mobile_v2.0_cls_infer', 'models/cls/ch_ppocr_mobile_v2.0_cls_infer')
    ]
    
    for src, dest in model_subdirs:
        if os.path.exists(src):
            datas.append((src, dest))
            print(f"添加模型子目录: {src} -> {dest}")
        else:
            print(f"警告：模型子目录不存在: {src}")
else:
    print("警告：未找到 models 文件夹，打包的程序可能无法正常工作")

# 添加paddle相关数据文件
if paddle_path and os.path.exists(os.path.join(paddle_path, 'libs')):
    datas.append((os.path.join(paddle_path, 'libs'), 'paddle/libs'))

# 添加paddleocr相关数据文件
if paddleocr_path and os.path.exists(paddleocr_path):
    datas.append((paddleocr_path, 'paddleocr'))

# 添加paddlex相关数据文件
if paddlex_path and os.path.exists(paddlex_path):
    datas.append((paddlex_path, 'paddlex'))
    
    # 特别添加.version文件
    version_file = os.path.join(paddlex_path, '.version')
    if os.path.exists(version_file):
        datas.append((version_file, 'paddlex'))

# 检查图标文件
icon_path = os.path.join(current_dir, 'app_icon.ico')
if not os.path.exists(icon_path):
    print(f"Warning: Icon file not found at {icon_path}")
    icon_path = None

a = Analysis(
    ['main.py'],
    pathex=[current_dir],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'paddleocr',
        'paddle',
        'paddlex',
         # 添加customtkinter相关依赖
        'customtkinter',
        'customtkinter.windows',
        'customtkinter.windows.widgets',
        'customtkinter.windows.widgets.core',
        'customtkinter.windows.widgets.core_widget_classes',
        'customtkinter.windows.widgets.font',
        'customtkinter.windows.widgets.image',
        'customtkinter.windows.widgets.scaling',
        'customtkinter.windows.widgets.theme',
        'customtkinter.windows.widgets.utility',
        'customtkinter.windows.widgets.appearance_mode',
        'tkinter',
        'tkinter.constants',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.font'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 排除不需要的模块，但保留tkinter
        'sklearn',
        'pysqlite2',
        'MySQLdb',
        'darkdetect',  # 排除macOS特定模块
        'PyQt5',  # 排除可能的GUI相关模块
        'matplotlib'  # 排除绘图相关模块
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='OfflinePDF-OCR',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path
)