from setuptools import setup
import sys
import os
import shutil

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 包含数据文件
data_files = []

# 添加模型文件
models_dir = 'models'
if os.path.exists(models_dir):
    for root, dirs, files in os.walk(models_dir):
        file_list = []
        for file in files:
            file_list.append(os.path.join(root, file))
        data_files.append((root, file_list))

# 添加图标文件（如果存在）
if os.path.exists('app_icon.ico'):
    data_files.append(('.', ['app_icon.ico']))

# 添加customtkinter资源文件
try:
    import customtkinter
    ctk_path = os.path.dirname(customtkinter.__file__)
    assets_path = os.path.join(ctk_path, 'assets')
    if os.path.exists(assets_path):
        # 递归添加所有assets文件
        for root, dirs, files in os.walk(assets_path):
            if files:  # 只有当目录中有文件时才添加
                file_list = []
                for file in files:
                    file_path = os.path.join(root, file)
                    file_list.append(file_path)
                # 计算相对路径
                rel_path = os.path.relpath(root, ctk_path)
                target_path = os.path.join('customtkinter', rel_path).replace('\\', '/')
                data_files.append((target_path, file_list))
                print(f"添加CustomTkinter资源: {target_path} ({len(file_list)} 个文件)")
except ImportError:
    print("Warning: customtkinter not found")

# 后处理函数：确保CustomTkinter资源文件正确复制
def post_process_customtkinter():
    """确保CustomTkinter资源文件被正确复制到dist目录"""
    try:
        import customtkinter
        dist_dir = 'dist'
        if not os.path.exists(dist_dir):
            return
            
        ctk_path = os.path.dirname(customtkinter.__file__)
        assets_path = os.path.join(ctk_path, 'assets')
        
        if os.path.exists(assets_path):
            target_ctk_dir = os.path.join(dist_dir, 'customtkinter')
            target_assets_dir = os.path.join(target_ctk_dir, 'assets')
            
            # 创建目标目录
            os.makedirs(target_assets_dir, exist_ok=True)
            
            # 复制assets目录
            if os.path.exists(target_assets_dir):
                shutil.rmtree(target_assets_dir)
            shutil.copytree(assets_path, target_assets_dir)
            print(f"✓ 成功复制CustomTkinter资源文件到: {target_assets_dir}")
            
            # 验证主题文件
            themes_dir = os.path.join(target_assets_dir, 'themes')
            if os.path.exists(themes_dir):
                theme_files = [f for f in os.listdir(themes_dir) if f.endswith('.json')]
                print(f"  主题文件: {', '.join(theme_files)}")
    except Exception as e:
        print(f"警告: 复制CustomTkinter资源文件时出错: {e}")

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
                'bundle_files': 3,  # 不打包库文件，所有文件都作为独立文件存在
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
                ],
                'dist_dir': 'dist',
                'dll_excludes': []  # 确保所有必要的DLL文件都被包含
            }
        },
        data_files=data_files,
        zipfile=None,  # 不使用zip文件，与bundle_files=3配合，确保资源文件可以正常访问
        windows=[{  # 改为windows应用，避免控制台窗口
            'script': 'main.py',
            'icon_resources': [(1, 'app_icon.ico')] if os.path.exists('app_icon.ico') else None
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