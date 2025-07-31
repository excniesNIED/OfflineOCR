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
datas = [(models_path, 'models')]

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
        'sklearn.utils._cython_blas',
        'sklearn.neighbors.typedefs',
        'sklearn.neighbors.quad_tree',
        'sklearn.tree._utils'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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