from setuptools import setup
import sys
import os
import shutil

# --- 数据文件配置 ---
data_files = []

# 1. 添加模型文件
models_dir = 'models'
if os.path.exists(models_dir):
    for root, dirs, files in os.walk(models_dir):
        file_list = [os.path.join(root, file) for file in files]
        if file_list:
            data_files.append((root, file_list))

# 2. 添加图标文件
if os.path.exists('app_icon.ico'):
    data_files.append(('.', ['app_icon.ico']))

# 3. 关键：将整个 customtkinter 库作为数据文件复制
try:
    import customtkinter
    ctk_path = os.path.dirname(customtkinter.__file__)
    for root, dirs, files in os.walk(ctk_path):
        file_list = [os.path.join(root, file) for file in files]
        if file_list:
            # 计算目标路径，保持目录结构
            dest_path = os.path.join('customtkinter', os.path.relpath(root, ctk_path))
            # 替换反斜杠以确保路径正确
            data_files.append((dest_path.replace('\\', '/'), file_list))
except ImportError:
    print("警告: customtkinter 未找到，请确保已安装。")

# 4. 添加pypdfium2相关的库文件 (根据网上解决方案)
try:
    import pypdfium2_raw
    import pypdfium2
    
    # 复制pypdfium2_raw的所有文件
    pypdfium2_raw_path = os.path.dirname(pypdfium2_raw.__file__)
    print(f"找到pypdfium2_raw路径: {pypdfium2_raw_path}")
    
    # 复制整个pypdfium2_raw目录，保持完整结构
    for root, dirs, files in os.walk(pypdfium2_raw_path):
        file_list = [os.path.join(root, file) for file in files]
        if file_list:
            dest_path = os.path.join('pypdfium2_raw', os.path.relpath(root, pypdfium2_raw_path))
            data_files.append((dest_path.replace('\\', '/'), file_list))
    print(f"[OK] 添加完整的pypdfium2_raw目录结构")
    
    # 复制pypdfium2的所有文件 (特别是version.json)
    pypdfium2_path = os.path.dirname(pypdfium2.__file__)
    print(f"找到pypdfium2路径: {pypdfium2_path}")
    
    for root, dirs, files in os.walk(pypdfium2_path):
        file_list = [os.path.join(root, file) for file in files]
        if file_list:
            dest_path = os.path.join('pypdfium2', os.path.relpath(root, pypdfium2_path))
            data_files.append((dest_path.replace('\\', '/'), file_list))
    print(f"[OK] 添加完整的pypdfium2目录结构")
    
    # 额外确保关键文件在根目录也有副本（保险起见）
    pdfium_dll = os.path.join(pypdfium2_raw_path, 'pdfium.dll')
    if os.path.exists(pdfium_dll):
        data_files.append(('.', [pdfium_dll]))
        print(f"[OK] 在根目录添加pdfium.dll副本")
        
except ImportError as e:
    print(f"警告: pypdfium2相关库未找到: {e}")


# --- py2exe 配置 ---
if sys.platform.startswith('win'):
    try:
        import py2exe
    except ImportError:
        print("错误：未安装 py2exe。请运行 'pip install py2exe'")
        sys.exit(1)

    setup(
        name='OfflinePDF-OCR',
        version='1.0',
        description='Offline PDF OCR Tool',
        author='Your Name',
        
        options={
            'py2exe': {
                'bundle_files': 3,  # 3 = 不打包，所有文件保持为独立文件
                'compressed': True,
                'optimize': 2,
                'dist_dir': 'dist',
                'packages': [
                    'paddleocr',
                    'paddle',
                    'paddlex',
                    'customtkinter',  # 恢复正常打包customtkinter
                    'pypdfium2',
                    'pypdfium2_raw',
                ],
                'excludes': [
                    'sklearn',
                    'pysqlite2',
                    'MySQLdb',
                    'PyQt5',
                    'matplotlib'
                ],
            }
        },
        windows=[{
            'script': 'main.py',
            'icon_resources': [(1, 'app_icon.ico')] if os.path.exists('app_icon.ico') else []
        }],
        data_files=data_files,
        zipfile=None,  # 确保不创建zip文件
    )
else:
    # 非Windows系统的备用配置
    setup(
        name='OfflinePDF-OCR',
        version='1.0',
        description='Offline PDF OCR Tool',
        py_modules=['main'],
        data_files=data_files
    )
