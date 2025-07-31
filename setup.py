from setuptools import setup
import sys
import os

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 包含数据文件
data_files = []

# 添加模型文件
models_dir = 'models'
if os.path.exists(models_dir):
    for root, dirs, files in os.walk(models_dir):
        data_files.append((root, [os.path.join(root, f) for f in files]))

# 添加图标文件（如果存在）
if os.path.exists('app_icon.ico'):
    data_files.append(('.', ['app_icon.ico']))

# 添加customtkinter资源文件
try:
    import customtkinter
    ctk_path = os.path.dirname(customtkinter.__file__)
    assets_path = os.path.join(ctk_path, 'assets')
    if os.path.exists(assets_path):
        # 添加themes目录
        themes_path = os.path.join(assets_path, 'themes')
        if os.path.exists(themes_path):
            theme_files = []
            for file in os.listdir(themes_path):
                if file.endswith('.json'):
                    theme_files.append(os.path.join(themes_path, file))
            if theme_files:
                data_files.append(('customtkinter/assets/themes', theme_files))
        
        # 添加fonts目录（如果存在）
        fonts_path = os.path.join(assets_path, 'fonts')
        if os.path.exists(fonts_path):
            font_files = []
            for file in os.listdir(fonts_path):
                font_files.append(os.path.join(fonts_path, file))
            if font_files:
                data_files.append(('customtkinter/assets/fonts', font_files))
except ImportError:
    print("Warning: customtkinter not found")

# 检查是否在Windows上运行
if sys.platform.startswith('win'):
    try:
        import py2exe
    except ImportError:
        print("错误：未安装py2exe。请运行 'pip install py2exe'")
        sys.exit(1)

    setup(
        name='OfflinePDF-OCR',
        version='1.0',
        description='Offline PDF OCR Tool',
        author='Your Name',
        author_email='your.email@example.com',
        options={
            'py2exe': {
                'bundle_files': 1,  # 打包成单个exe文件
                'compressed': True,  # 压缩
                'optimize': 2,      # 优化级别
                'excludes': [
                    'sklearn',
                    'pysqlite2',
                    'MySQLdb',
                    'darkdetect',
                    'PyQt5',
                    'matplotlib'
                ],
                'includes': [
                    'paddleocr',
                    'paddle',
                    'paddlex',
                    'customtkinter',
                    'tkinter',
                    'tkinter.constants',
                    'tkinter.filedialog',
                    'tkinter.messagebox',
                    'tkinter.font'
                ],
                'packages': [
                    'paddleocr',
                    'paddle',
                    'paddlex',
                    'customtkinter',
                    'tkinter'
                ]
            }
        },
        data_files=data_files,
        zipfile=None,  # 将库文件打包进exe
        console=[{
            'script': 'main.py',
            'icon_resources': [(1, 'app_icon.ico')] if os.path.exists('app_icon.ico') else []
        }],
        # GUI应用需要的配置
        windows=[{
            'script': 'main.py',
            'icon_resources': [(1, 'app_icon.ico')] if os.path.exists('app_icon.ico') else []
        }]
    )
else:
    # 非Windows系统
    setup(
        name='OfflinePDF-OCR',
        version='1.0',
        description='Offline PDF OCR Tool',
        author='Your Name',
        author_email='your.email@example.com',
        py_modules=['main'],
        data_files=data_files
    )