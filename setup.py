from setuptools import setup
import sys
import os

# 检查py2exe是否安装
if sys.platform.startswith('win'):
    try:
        import py2exe
    except ImportError:
        print("错误：未安装 py2exe。请运行 'pip install py2exe'")
        sys.exit(1)

# --- 数据文件收集函数 ---
def find_data_files(source, target, patterns=None):
    """一个健壮的函数，用于查找并复制数据文件，保持目录结构。"""
    if not os.path.isdir(source):
        print(f"警告: 源目录 '{source}' 不存在，跳过。")
        return []
    
    if patterns is None:
        patterns = ['*']
        
    data_files_list = []
    for root, dirs, files in os.walk(source):
        for pattern in patterns:
            for filename in files:
                if pattern == '*' or filename.endswith(pattern) or os.path.splitext(filename)[1] in pattern:
                    filepath = os.path.join(root, filename)
                    rel_dir = os.path.relpath(root, source)
                    dest_dir = os.path.join(target, rel_dir)
                    data_files_list.append((dest_dir.replace('\\', '/'), [filepath]))
    return data_files_list

# --- 数据文件配置 ---
data_files = []

# 1. 添加模型文件
print("正在收集PaddleOCR模型文件...")
data_files.extend(find_data_files('models', 'models'))

# 2. 添加图标文件
if os.path.exists('app_icon.ico'):
    data_files.append(('.', ['app_icon.ico']))
    print("已添加图标文件。")

# 3. 关键：将整个 customtkinter 库作为数据文件复制
print("正在收集CustomTkinter库文件...")
try:
    import customtkinter
    ctk_path = os.path.dirname(customtkinter.__file__)
    # 复制所有文件，确保库的完整性
    data_files.extend(find_data_files(ctk_path, 'customtkinter', patterns=['*']))
    print(f"将完整的CustomTkinter库作为数据文件复制，源路径: {ctk_path}")
except ImportError:
    print("警告: customtkinter 未找到，相关资源文件将不会被打包。")

# 4. 添加 PyMuPDF (pypdfium2) 相关的库文件
print("正在收集PyMuPDF (pypdfium2)相关文件...")
try:
    import pypdfium2
    pypdfium2_path = os.path.dirname(pypdfium2.__file__)
    data_files.extend(find_data_files(pypdfium2_path, 'pypdfium2', patterns=['.dll', '.so', '.dylib', 'version.json']))

    import pypdfium2_raw
    pypdfium2_raw_path = os.path.dirname(pypdfium2_raw.__file__)
    pdfium_dll_path = os.path.join(pypdfium2_raw_path, 'pdfium.dll')
    if os.path.exists(pdfium_dll_path):
        data_files.append(('.', [pdfium_dll_path]))
        print(f"已将 '{pdfium_dll_path}' 添加到根目录。")
    else:
        print("警告: 未在pypdfium2_raw中找到pdfium.dll。")
except ImportError as e:
    print(f"警告: pypdfium2 或 pypdfium2_raw 未找到，PDF功能可能无法工作: {e}")


# --- py2exe 配置 ---
setup(
    name='OfflinePDF-OCR',
    version='1.0',
    description='Offline PDF OCR Tool',
    author='EPIBoly',
    
    options={
        'py2exe': {
            'bundle_files': 3,
            'compressed': True,
            'optimize': 2,
            'dist_dir': 'dist',
            'packages': [
                'tkinter',
                'paddleocr',
                'pypdfium2',
                'fitz',
            ],
            'includes': [
                'pypdfium2_raw',
            ],
            'excludes': [
                'customtkinter',  # 关键：禁止py2exe捆绑它
                'PyQt5',
                'matplotlib',
            ],
        }
    },
    windows=[{
        'script': 'main.py',
        'icon_resources': [(1, 'app_icon.ico')] if os.path.exists('app_icon.ico') else []
    }],
    data_files=data_files,
    zipfile=None,  # 关键：禁止生成 library.zip
)