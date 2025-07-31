import PyInstaller.__main__
import os
import sys
import shutil
from pathlib import Path

def build_executable():
    """构建可执行文件"""
    print("开始构建可执行文件...")
    
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
    model_dirs = [
        'models/det/ch/ch_PP-OCRv4_det_infer',
        'models/rec/ch/ch_PP-OCRv4_rec_infer', 
        'models/cls/ch_ppocr_mobile_v2.0_cls_infer'
    ]
    
    missing_models = []
    for model_dir in model_dirs:
        if not os.path.exists(model_dir):
            missing_models.append(model_dir)
    
    if missing_models:
        print("警告：以下模型文件缺失:")
        for model in missing_models:
            print(f"  - {model}")
        response = input("\n是否继续构建？(y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("构建已取消")
            return False
    
    # 构建参数
    build_args = [
        'main.py',                    # 主程序
        '--name', 'OfflinePDF-OCR',   # 可执行文件名
        '--windowed',                 # 无控制台窗口模式
        '--onefile',                  # 打包为单个文件
        '--clean',                    # 清理临时文件
    ]
    
    # 添加图标（如果存在）
    if os.path.exists('icon.ico'):
        build_args.extend(['--icon', 'icon.ico'])
        print("使用自定义图标: icon.ico")
    else:
        print("未找到图标文件 icon.ico，将使用默认图标")
    
    # 添加模型文件
    if os.path.exists('models'):
        build_args.extend(['--add-data', 'models' + os.pathsep + 'models'])
        print("添加模型文件夹到打包文件")
    else:
        print("警告：未找到 models 文件夹，打包的程序可能无法正常工作")
    
    print("\n构建参数:")
    for i, arg in enumerate(build_args):
        print(f"  {i+1:2d}. {arg}")
    
    response = input("\n是否开始构建？(Y/n): ")
    if response.lower() in ['n', 'no']:
        print("构建已取消")
        return False
    
    try:
        print("\n正在构建，请稍候...")
        PyInstaller.__main__.run(build_args)
        
        print("\n✓ 构建完成！")
        print(f"可执行文件位置: {os.path.join(os.getcwd(), 'dist', 'OfflinePDF-OCR.exe')}")
        return True
        
    except Exception as e:
        print(f"\n✗ 构建失败: {e}")
        return False

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

