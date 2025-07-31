# pre_download_models.py
# 该脚本用于预下载PaddleOCR模型文件并自动复制到项目目录

from paddleocr import PaddleOCR
import sys
import logging
import os
import shutil
import platform

# 禁用PaddleOCR的日志输出
logging.getLogger('ppocr').setLevel(logging.WARNING)

def get_paddleocr_model_dir():
    """
    获取PaddleOCR模型默认下载目录
    """
    system = platform.system()
    if system == "Windows":
        # Windows: C:\Users\{username}\.paddleocr\
        home_dir = os.path.expanduser("~")
        return os.path.join(home_dir, ".paddleocr")
    elif system in ("Linux", "Darwin"):  # Darwin is macOS
        # Linux/macOS: ~/.paddleocr/
        home_dir = os.path.expanduser("~")
        return os.path.join(home_dir, ".paddleocr")
    else:
        raise OSError(f"Unsupported operating system: {system}")

def get_paddlex_model_dir():
    """
    获取PaddleX模型默认下载目录（新版本PaddleOCR可能使用此目录）
    """
    system = platform.system()
    if system == "Windows":
        # Windows: C:\Users\{username}\.paddlex\
        home_dir = os.path.expanduser("~")
        return os.path.join(home_dir, ".paddlex")
    elif system in ("Linux", "Darwin"):  # Darwin is macOS
        # Linux/macOS: ~/.paddlex/
        home_dir = os.path.expanduser("~")
        return os.path.join(home_dir, ".paddlex")
    else:
        raise OSError(f"Unsupported operating system: {system}")

def download_models():
    """下载各种语言的OCR模型"""
    print("开始下载OCR模型...")
    print("=" * 50)
    
    # 下载中英文模型
    print("1. 正在下载中英文OCR模型...")
    try:
        _ = PaddleOCR(use_textline_orientation=True, lang='ch')
        print("   ✓ 中英文模型下载完成")
    except Exception as e:
        print(f"   ✗ 中英文模型下载失败: {e}")
        return False
    
    # 下载英文模型
    print("2. 正在下载英文OCR模型...")
    try:
        _ = PaddleOCR(use_textline_orientation=True, lang='en')
        print("   ✓ 英文模型下载完成")
    except Exception as e:
        print(f"   ✗ 英文模型下载失败: {e}")
    
    # 下载多语言模型（如果支持）
    print("3. 正在下载多语言OCR模型...")
    try:
        _ = PaddleOCR(use_textline_orientation=True, lang='ml')
        print("   ✓ 多语言模型下载完成")
    except Exception as e:
        print(f"   ! 多语言模型下载失败: {e}")
        print("     这可能是因为当前版本不支持多语言模型，不影响主要功能")
    
    print("=" * 50)
    print("模型下载完成！")
    return True

def copy_models_to_project():
    """
    将下载的模型从默认位置复制到项目目录的models文件夹中（适配旧模型结构）
    """
    try:
        # 首先尝试查找 .paddleocr 目录
        source_model_dir = os.path.join(get_paddleocr_model_dir(), "whl")
        if not os.path.exists(source_model_dir):
            # 如果 .paddleocr 目录不存在，尝试查找 .paddlex 目录
            paddlex_dir = get_paddlex_model_dir()
            official_models_dir = os.path.join(paddlex_dir, "official_models")
            if os.path.exists(official_models_dir):
                source_model_dir = official_models_dir
                print(f"使用PaddleX模型目录: {source_model_dir}")
            else:
                print(f"✗ 未找到源模型目录: {source_model_dir}")
                print(f"  也未找到PaddleX模型目录: {official_models_dir}")
                return False
        else:
            print(f"使用PaddleOCR模型目录: {source_model_dir}")
        
        print(f"源模型目录: {source_model_dir}")
        
        # 创建目标目录
        target_model_dir = os.path.join(os.getcwd(), "models")
        os.makedirs(target_model_dir, exist_ok=True)
        print(f"目标模型目录: {target_model_dir}")
        
        # 需要复制的模型子目录（适配两种目录结构）
        if "official_models" in source_model_dir:
            # PaddleX 结构 - 需要重新组织为旧结构
            model_mapping = {
                "PP-OCRv5_server_det": ("det", "ch", "ch_PP-OCRv4_det_infer"),
                "PP-OCRv5_server_rec": ("rec", "ch", "ch_PP-OCRv4_rec_infer"),
                "PP-LCNet_x1_0_textline_ori": ("cls", "", "ch_ppocr_mobile_v2.0_cls_infer")
            }
        else:
            # 传统 PaddleOCR 结构 - 保持原有结构
            model_mapping = {
                "det": ("det", "", ""),
                "rec": ("rec", "", ""),
                "cls": ("cls", "", "")
            }
        
        # 复制模型文件
        if "official_models" in source_model_dir:
            # 处理 PaddleX 结构并重新组织为旧结构
            for model_name, (target_subdir, sub_subdir, final_subdir) in model_mapping.items():
                # 在 official_models 中查找匹配的模型目录
                for item in os.listdir(source_model_dir):
                    item_path = os.path.join(source_model_dir, item)
                    if os.path.isdir(item_path) and model_name in item:
                        # 创建目标目录结构
                        target_subdir_path = os.path.join(target_model_dir, target_subdir)
                        os.makedirs(target_subdir_path, exist_ok=True)
                        
                        if sub_subdir:
                            sub_subdir_path = os.path.join(target_subdir_path, sub_subdir)
                            os.makedirs(sub_subdir_path, exist_ok=True)
                            final_target_path = os.path.join(sub_subdir_path, final_subdir)
                        else:
                            final_target_path = os.path.join(target_subdir_path, final_subdir)
                        
                        print(f"正在复制 {model_name} 模型到 {final_target_path}...")
                        if os.path.exists(final_target_path):
                            shutil.rmtree(final_target_path)
                        shutil.copytree(item_path, final_target_path)
                        print(f"✓ {model_name} 模型复制完成")
                        break
                else:
                    print(f"! 未找到 {model_name} 模型")
        else:
            # 处理传统 PaddleOCR 结构
            for subdir, (target_subdir, sub_subdir, final_subdir) in model_mapping.items():
                source_subdir = os.path.join(source_model_dir, subdir)
                target_subdir_path = os.path.join(target_model_dir, target_subdir)
                
                if os.path.exists(source_subdir):
                    print(f"正在复制 {subdir} 模型...")
                    if os.path.exists(target_subdir_path):
                        shutil.rmtree(target_subdir_path)
                    shutil.copytree(source_subdir, target_subdir_path)
                    print(f"✓ {subdir} 模型复制完成")
                else:
                    print(f"! 未找到 {subdir} 模型: {source_subdir}")
        
        print("\n✓ 所有模型已成功复制到项目目录的models文件夹中，适配旧结构!")
        return True
        
    except Exception as e:
        print(f"✗ 模型复制失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_models():
    """
    验证模型文件是否正确复制（检查旧结构）
    """
    try:
        model_dir = os.path.join(os.getcwd(), "models")
        if not os.path.exists(model_dir):
            print("✗ 未找到models目录")
            return False
            
        # 检查旧结构
        required_paths = [
            "det/ch/ch_PP-OCRv4_det_infer",
            "rec/ch/ch_PP-OCRv4_rec_infer", 
            "cls/ch_ppocr_mobile_v2.0_cls_infer"
        ]
        
        for path in required_paths:
            full_path = os.path.join(model_dir, path)
            if not os.path.exists(full_path):
                print(f"✗ 缺少必需的模型目录: {full_path}")
                return False
            print(f"✓ 找到模型目录: {full_path}")
            
        print("\n✓ 模型文件验证通过，符合旧结构!")
        return True
    except Exception as e:
        print(f"✗ 模型验证失败: {e}")
        return False

def main():
    print("PaddleOCR 模型下载和设置工具")
    print("注意：此过程需要网络连接，并可能需要较长时间")
    print("此工具将模型组织为旧结构以确保兼容性")
    response = input("\n是否继续下载并设置模型？(y/N): ")
    
    if response.lower() not in ['y', 'yes']:
        print("操作已取消")
        sys.exit(0)
    
    # 下载模型
    if not download_models():
        print("模型下载失败，无法继续")
        return
    
    # 自动复制模型到项目目录（适配旧结构）
    print("\n正在将模型复制到项目目录（适配旧结构）...")
    if not copy_models_to_project():
        print("模型复制失败")
        return
    
    # 验证模型
    print("\n正在验证模型文件...")
    if not verify_models():
        print("模型验证失败")
        return
    
    print("\n" + "=" * 60)
    print("🎉 模型下载和设置完成（适配旧结构）!")
    print("现在可以运行程序了:")
    print("  python main.py")
    print("=" * 60)

if __name__ == "__main__":
    main()