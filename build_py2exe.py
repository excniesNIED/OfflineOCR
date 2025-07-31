import sys
import os
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
    """使用py2exe构建可执行文件"""
    print("开始使用py2exe构建可执行文件...")
    
    # 检查必要文件是否存在
    required_files = ['main.py', 'setup.py']
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
    
    try:
        # 先清理旧的构建文件
        print("\n清理旧的构建文件...")
        clean_build()
        
        print("\n正在构建，请稍候...")
        # 使用py2exe构建
        import subprocess
        result = subprocess.run([sys.executable, 'setup.py', 'py2exe'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("\n✓ py2exe构建完成！")
            
                        # 后处理：确保CustomTkinter资源文件正确复制
            print("正在进行后处理...")
            dist_dir = os.path.join(os.getcwd(), 'dist')
            try:
                import customtkinter
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
            
            print("\n检查构建结果...")
            # 检查exe文件是否存在（使用上面定义的dist_dir）
            exe_path = os.path.join(dist_dir, 'main.exe')
            
            if os.path.exists(exe_path):
                print(f"可执行文件位置: {exe_path}")
                
                # 检查重要文件是否存在
                ctk_assets = os.path.join(dist_dir, 'customtkinter', 'assets', 'themes')
                python_dll = os.path.join(dist_dir, 'python39.dll')  # 根据python版本调整
                
                # 检查Python DLL（bundle_files=3时会有独立的DLL文件）
                python_dlls = [f for f in os.listdir(dist_dir) if f.startswith('python') and f.endswith('.dll')]
                if python_dlls:
                    print(f"✓ Python库文件: {', '.join(python_dlls)}")
                else:
                    print("⚠ 警告: Python DLL文件未找到")
                    
                if os.path.exists(ctk_assets):
                    print(f"✓ CustomTkinter主题文件: {ctk_assets}")
                    theme_files = [f for f in os.listdir(ctk_assets) if f.endswith('.json')]
                    print(f"  包含主题: {', '.join(theme_files)}")
                else:
                    print("⚠ 警告: CustomTkinter主题文件未找到")
                    
                print(f"\n你可以运行以下命令测试应用:")
                print(f"cd dist && .\\main.exe")
                
            else:
                # 查找可能的exe文件
                if os.path.exists(dist_dir):
                    exe_files = [f for f in os.listdir(dist_dir) if f.endswith('.exe')]
                    if exe_files:
                        print(f"可执行文件位置: {os.path.join(dist_dir, exe_files[0])}")
                    else:
                        print("未找到可执行文件，请检查dist目录")
                        print("dist目录内容:")
                        for item in os.listdir(dist_dir):
                            print(f"  - {item}")
                else:
                    print("未找到dist目录")
            return True
        else:
            print(f"\n✗ 构建失败:")
            print(result.stdout)
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"\n✗ 构建失败: {e}")
        return False

def clean_build():
    """清理构建文件"""
    print("清理构建文件...")
    dirs_to_remove = ['build', 'dist', '__pycache__']
    
    # 删除目录
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"  已删除: {dir_name}/")
            except Exception as e:
                print(f"  删除 {dir_name}/ 失败: {e}")
    
    print("清理完成！")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--clean':
        clean_build()
    else:
        print("OfflinePDF-OCR py2exe 打包工具")
        print("=" * 35)
        print("选项:")
        print("  无参数    - 构建可执行文件")
        print("  --clean   - 清理构建文件")
        print("=" * 35)
        
        action = input("\n请选择操作 (build/clean): ") if len(sys.argv) == 1 else sys.argv[1]
        
        if action == 'clean':
            clean_build()
        else:
            build_executable()

