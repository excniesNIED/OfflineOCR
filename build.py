import PyInstaller.__main__
import os
import sys
import shutil
from pathlib import Path

def check_models():
    """检查模型文件是否存在"""
    print("检查模型文件...")
    model_dirs = [
        'models/det/ch/ch_PP-OCRv4_det_infer',
        'models/rec/ch/ch_PP-OCRv4_rec_infer', 
        'models/cls/ch_ppocr_mobile_v2.0_cls_infer'
    ]
    
    missing_models = []
    for model_dir in model_dirs:
        if not os.path.exists(model_dir):
            missing_models.append(model_dir)
        else:
            print(f"✓ 找到模型目录: {model_dir}")
    
    if missing_models:
        print("✗ 以下模型文件缺失:")
        for model in missing_models:
            print(f"  - {model}")
        return False
    else:
        print("✓ 所有模型文件都已找到")
        return True

def build_executable():
    """构建可执行文件"""
    print("开始构建可执行文件...")
    
    # 检查是否在conda环境中
    conda_prefix = os.environ.get('CONDA_PREFIX')
    if conda_prefix:
        print(f"检测到Conda环境: {conda_prefix}")
    else:
        print("警告：未检测到Conda环境，请确保在正确的环境中运行此脚本")
    
    # 检查必要文件是否存在
    required_files = ['main.py']
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"错误：以下文件缺失: {', '.join(missing_files)}")
        return False
    
    # 检查模型文件
    if not check_models():
        response = input("\n是否继续构建？(y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("构建已取消")
            return False
    
    # 检查图标文件
    icon_path = 'app_icon.ico'
    if not os.path.exists(icon_path):
        print("未找到图标文件 app_icon.ico，将使用默认图标")
        create_default_icon(icon_path)
    
    # 使用spec文件进行构建
    spec_file = 'OfflinePDF-OCR.spec'
    if not os.path.exists(spec_file):
        print(f"错误：未找到spec文件 {spec_file}")
        return False
    
    build_args = [
        spec_file,
        '--clean',
        # 禁用确认
        '--noconfirm'
    ]
    
    print(f"使用spec文件进行构建: {spec_file}")
    print("\n构建参数:")
    for i, arg in enumerate(build_args):
        print(f"  {i+1:2d}. {arg}")
    
    try:
        print("\n正在构建，请稍候...")
        PyInstaller.__main__.run(build_args)
        
        print("\n✓ 构建完成！")
        print(f"可执行文件位置: {os.path.join(os.getcwd(), 'dist', 'OfflinePDF-OCR.exe')}")
        return True
        
    except Exception as e:
        print(f"\n✗ 构建失败: {e}")
        return False

def create_default_icon(icon_path):
    """创建默认图标文件"""
    # 创建一个最小的ICO文件
    with open(icon_path, 'wb') as f:
        # 创建一个最小的有效的ICO文件头
        f.write(b'\x00\x00')  # Reserved
        f.write(b'\x01\x00')  # ICO type
        f.write(b'\x01\x00')  # Number of images
        f.write(b'\x10\x10')  # Width and height
        f.write(b'\x00')      # Number of colors
        f.write(b'\x00')      # Reserved
        f.write(b'\x01\x00')  # Color planes
        f.write(b'\x20\x00')  # Bits per pixel
        f.write(b'\x6c\x00\x00\x00')  # Image size
        f.write(b'\x16\x00\x00\x00')  # Image offset

def clean_build():
    """清理构建文件"""
    print("清理构建文件...")
    dirs_to_remove = ['build', 'dist', '__pycache__']
    files_to_remove = []
    
    # 查找 .spec 文件
    for file in os.listdir('.'):
        if file.endswith('.spec'):
            files_to_remove.append(file)
    
    # 删除目录
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"  已删除: {dir_name}/")
            except Exception as e:
                print(f"  删除 {dir_name}/ 失败: {e}")
    
    # 删除文件
    for file_name in files_to_remove:
        try:
            os.remove(file_name)
            print(f"  已删除: {file_name}")
        except Exception as e:
            print(f"  删除 {file_name} 失败: {e}")
    
    # 删除图标文件（如果是我们创建的）
    icon_path = 'app_icon.ico'
    if os.path.exists(icon_path) and os.path.getsize(icon_path) < 100:
        try:
            os.remove(icon_path)
            print(f"  已删除临时图标文件: {icon_path}")
        except Exception as e:
            print(f"  删除 {icon_path} 失败: {e}")
    
    print("清理完成！")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--clean':
        clean_build()
    else:
        print("OfflinePDF-OCR 打包工具")
        print("=" * 30)
        print("选项:")
        print("  无参数    - 构建可执行文件")
        print("  --clean   - 清理构建文件")
        print("=" * 30)
        
        action = input("\n请选择操作 (build/clean): ") if len(sys.argv) == 1 else sys.argv[1]
        
        if action == 'clean':
            clean_build()
        else:
            build_executable()

