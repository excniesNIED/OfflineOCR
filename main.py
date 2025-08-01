import os
import sys
import logging

# 设置日志输出到文件和控制台
try:
    if hasattr(sys, 'frozen'):
        log_file = os.path.join(os.path.dirname(os.path.abspath(sys.executable)), 'debug.log')
    else:
        log_file = 'debug.log'
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    print(f"日志文件: {log_file}")
    logging.info("=" * 50)
    logging.info("应用程序启动")
    
except Exception as e:
    print(f"设置日志失败: {e}")

# 立即切换工作目录并设置pypdfium2环境（必须在所有导入之前）
try:
    if hasattr(sys, 'frozen'):
        exe_dir = os.path.dirname(os.path.abspath(sys.executable))
        os.chdir(exe_dir)
        print(f"已切换到打包目录: {exe_dir}")
        logging.info(f"已切换到打包目录: {exe_dir}")
        
        # 立即设置pypdfium2相关的所有路径（在任何可能触发pypdfium2导入的库之前）
        pdfium_dll_path = os.path.join(exe_dir, 'pdfium.dll')
        pypdfium2_raw_path = os.path.join(exe_dir, 'pypdfium2_raw')
        
        if os.path.exists(pdfium_dll_path):
            print(f"找到pdfium库文件: {pdfium_dll_path}")
            logging.info(f"找到pdfium库文件: {pdfium_dll_path}")
            
            # 添加所有可能的DLL搜索路径
            if hasattr(os, 'add_dll_directory'):
                os.add_dll_directory(exe_dir)  # 根目录
                logging.info(f"添加DLL搜索路径: {exe_dir}")
                if os.path.exists(pypdfium2_raw_path):
                    os.add_dll_directory(pypdfium2_raw_path)  # pypdfium2_raw目录
                    logging.info(f"添加DLL搜索路径: {pypdfium2_raw_path}")
            
            # 设置PATH环境变量，包含所有可能的路径
            current_path = os.environ.get('PATH', '')
            new_paths = [exe_dir]
            if os.path.exists(pypdfium2_raw_path):
                new_paths.append(pypdfium2_raw_path)
            
            os.environ['PATH'] = os.pathsep.join(new_paths) + os.pathsep + current_path
            print(f"已设置pypdfium2环境路径: {new_paths}")
            logging.info(f"已设置pypdfium2环境路径: {new_paths}")
        
            # 额外设置环境变量，确保pypdfium2能找到库文件
            os.environ['PYPDFIUM2_LIBRARY_PATH'] = exe_dir
            os.environ['PDFIUM_BINARY_PATH'] = pdfium_dll_path
            logging.info(f"设置PYPDFIUM2_LIBRARY_PATH: {exe_dir}")
            logging.info(f"设置PDFIUM_BINARY_PATH: {pdfium_dll_path}")
            
            # 强制设置当前工作目录包含pdfium.dll
            try:
                # 确认pdfium.dll在当前工作目录中存在
                current_pdfium = os.path.join('.', 'pdfium.dll')
                if not os.path.exists(current_pdfium):
                    import shutil
                    shutil.copy2(pdfium_dll_path, current_pdfium)
                    logging.info(f"复制pdfium.dll到当前目录: {current_pdfium}")
                    print(f"复制pdfium.dll到当前目录: {current_pdfium}")
            except Exception as copy_e:
                logging.warning(f"复制pdfium.dll失败: {copy_e}")
                
        else:
            logging.warning(f"未找到pdfium库文件: {pdfium_dll_path}")
            
except Exception as e:
    print(f"初始化失败: {e}")
    logging.error(f"初始化失败: {e}", exc_info=True)

# 在导入CustomTkinter和pypdfium2之前修补文件系统访问
def setup_path_interception():
    """在导入前拦截并重定向模块的文件访问"""
    if hasattr(sys, 'frozen'):
        # 获取可执行文件所在目录
        exe_dir = os.path.dirname(os.path.abspath(sys.executable))
        external_assets_dir = os.path.join(exe_dir, 'customtkinter', 'assets')
        
        if os.path.exists(external_assets_dir):
            print(f"检测到打包环境，外部资源目录: {external_assets_dir}")

            # 备份原始的os.path.exists和open函数
            original_exists = os.path.exists
            original_open = open
            
            def patched_exists(path):
                """拦截CustomTkinter的路径检查，重定向到外部资源"""
                if isinstance(path, str) and 'customtkinter' in path and 'assets' in path:
                    if 'main.exe' in path and 'customtkinter' in path:
                        corrected_path = os.path.join(exe_dir, path.split('main.exe\\')[-1])
                        print(f"路径重定向: {path} -> {corrected_path}")
                        return original_exists(corrected_path)
                return original_exists(path)
            
            def patched_open(file, mode='r', **kwargs):
                """拦截CustomTkinter的文件打开，重定向到外部资源"""
                if isinstance(file, str) and 'customtkinter' in file and 'assets' in file:
                    if 'main.exe' in file and 'customtkinter' in file:
                        corrected_file = os.path.join(exe_dir, file.split('main.exe\\')[-1])
                        print(f"文件打开重定向: {file} -> {corrected_file}")
                        return original_open(corrected_file, mode, **kwargs)
                return original_open(file, mode, **kwargs)
            
            # 应用修补
            os.path.exists = patched_exists
            
            # 修补内置open函数，使用更兼容的方法
            try:
                import builtins
                builtins.open = patched_open
            except (AttributeError, TypeError):
                # 备用方法
                try:
                    if isinstance(__builtins__, dict):
                        __builtins__['open'] = patched_open
                    else:
                        setattr(__builtins__, 'open', patched_open)
                except:
                    print("警告: 无法修补内置open函数，可能影响主题加载")
            
            print("✓ 已安装CustomTkinter路径拦截器")
            
            # 现在安全导入CustomTkinter
            import customtkinter as ctk_module
            
            return ctk_module
    
    # 非打包环境，正常导入
    import customtkinter as ctk_module
    return ctk_module

# 设置拦截器并导入CustomTkinter
try:
    logging.info("开始导入CustomTkinter")
    print("开始导入CustomTkinter")
    ctk = setup_path_interception()
    logging.info("CustomTkinter导入成功")
    print("CustomTkinter导入成功")
except Exception as e:
    logging.error(f"CustomTkinter导入失败: {e}", exc_info=True)
    print(f"CustomTkinter导入失败: {e}")
    raise

try:
    logging.info("开始导入基础模块")
    print("开始导入基础模块")
    from tkinter import filedialog, messagebox, Menu
    logging.info("tkinter模块导入成功")
    print("tkinter模块导入成功")
except Exception as e:
    logging.error(f"tkinter模块导入失败: {e}", exc_info=True)
    print(f"tkinter模块导入失败: {e}")
    raise

try:
    logging.info("开始导入PyMuPDF")
    print("开始导入PyMuPDF")
    import fitz  # PyMuPDF
    logging.info("PyMuPDF导入成功")
    print("PyMuPDF导入成功")
except Exception as e:
    logging.error(f"PyMuPDF导入失败: {e}", exc_info=True)
    print(f"PyMuPDF导入失败: {e}")
    raise

try:
    logging.info("开始导入PaddleOCR")
    print("开始导入PaddleOCR")
    from paddleocr import PaddleOCR
    logging.info("PaddleOCR导入成功")
    print("PaddleOCR导入成功")
except Exception as e:
    logging.error(f"PaddleOCR导入失败: {e}", exc_info=True)
    print(f"PaddleOCR导入失败: {e}")
    raise

try:
    logging.info("开始导入threading")
    print("开始导入threading")
    import threading
    logging.info("threading导入成功")
    print("threading导入成功")
except Exception as e:
    logging.error(f"threading导入失败: {e}", exc_info=True)
    print(f"threading导入失败: {e}")
    raise

# --- 全局设置 ---
try:
    logging.info("设置CustomTkinter全局配置")
    print("设置CustomTkinter全局配置")
    
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    
    # 禁用特殊字体，使用系统默认字体
    try:
        # 设置默认字体为系统字体，避免加载外部字体文件
        import tkinter.font as tkFont
        default_font = tkFont.nametofont("TkDefaultFont")
        ctk.CTkFont._family = default_font.actual()['family']
        logging.info(f"使用系统默认字体: {default_font.actual()['family']}")
        print(f"使用系统默认字体: {default_font.actual()['family']}")
    except Exception as e:
        logging.warning(f"设置默认字体失败，将使用CustomTkinter默认配置: {e}")
        print(f"设置默认字体失败，将使用CustomTkinter默认配置: {e}")
    
    logging.info("CustomTkinter配置完成")
    print("CustomTkinter配置完成")
    
except Exception as e:
    logging.error(f"CustomTkinter配置失败: {e}", exc_info=True)
    print(f"CustomTkinter配置失败: {e}")

# 禁用PaddleOCR的日志输出
logging.getLogger('ppocr').setLevel(logging.WARNING)

# --- OCR引擎初始化 ---
def init_ocr_engine():
    """初始化OCR引擎"""
    try:
        # 关键：根据可执行文件路径构建模型的绝对路径
        if hasattr(sys, 'frozen'):
            base_path = os.path.dirname(os.path.abspath(sys.executable))
        else:
            base_path = os.path.abspath('.')
        
        det_model_path = os.path.join(base_path, 'models/det/ch/ch_PP-OCRv4_det_infer')
        rec_model_path = os.path.join(base_path, 'models/rec/ch/ch_PP-OCRv4_rec_infer')
        cls_model_path = os.path.join(base_path, 'models/cls/ch_ppocr_mobile_v2.0_cls_infer')
        
        # 检查关键模型文件是否存在以进行验证
        if not os.path.exists(os.path.join(det_model_path, 'inference.pdiparams')):
            raise FileNotFoundError(f"检测模型文件不存在: {det_model_path}")
        if not os.path.exists(os.path.join(rec_model_path, 'inference.pdiparams')):
            raise FileNotFoundError(f"识别模型文件不存在: {rec_model_path}")
        if not os.path.exists(os.path.join(cls_model_path, 'inference.pdiparams')):
            raise FileNotFoundError(f"方向分类模型文件不存在: {cls_model_path}")
            
        ocr_engine = PaddleOCR(
            use_angle_cls=True, 
            lang='ch',
            det_model_dir=det_model_path,
            rec_model_dir=rec_model_path,
            cls_model_dir=cls_model_path,
            show_log=False # 禁用PaddleOCR的日志
        )
        return ocr_engine
    except Exception as e:
        print(f"OCR引擎初始化失败: {e}")
        return None

OCR_ENGINE = init_ocr_engine()

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("离线PDF-OCR工具")
        self.geometry("900x700")
        self.minsize(600, 400)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- 菜单栏 ---
        self.create_menu()

        # --- 顶部框架 ---
        self.top_frame = ctk.CTkFrame(self, height=50)
        self.top_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.top_frame.grid_columnconfigure(1, weight=1)

        self.select_button = ctk.CTkButton(self.top_frame, text="选择PDF文件", command=self.select_pdf)
        self.select_button.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.file_label = ctk.CTkLabel(self.top_frame, text="尚未选择文件", anchor="w")
        self.file_label.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        self.start_button = ctk.CTkButton(self.top_frame, text="开始识别", command=self.start_ocr_thread, state="disabled")
        self.start_button.grid(row=0, column=2, padx=10, pady=10, sticky="e")

        # --- 中间框架（包含选项和结果） ---
        self.middle_frame = ctk.CTkFrame(self)
        self.middle_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.middle_frame.grid_columnconfigure(0, weight=1)
        self.middle_frame.grid_rowconfigure(1, weight=1)

        # --- 选项框架 ---
        self.options_frame = ctk.CTkFrame(self.middle_frame)
        self.options_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        self.zoom_label = ctk.CTkLabel(self.options_frame, text="图像缩放:")
        self.zoom_label.pack(side="left", padx=(10, 5), pady=10)
        
        self.zoom_var = ctk.StringVar(value="2.0")
        self.zoom_option = ctk.CTkOptionMenu(self.options_frame, values=["1.0", "1.5", "2.0", "2.5", "3.0"], 
                                             variable=self.zoom_var)
        self.zoom_option.pack(side="left", padx=5, pady=10)
        
        self.lang_label = ctk.CTkLabel(self.options_frame, text="语言:")
        self.lang_label.pack(side="left", padx=(20, 5), pady=10)
        
        self.lang_var = ctk.StringVar(value="中英文")
        self.lang_option = ctk.CTkOptionMenu(self.options_frame, values=["中英文", "英文", "中文"], 
                                             variable=self.lang_var)
        self.lang_option.pack(side="left", padx=5, pady=10)

        # --- 结果文本框 ---
        self.result_textbox = ctk.CTkTextbox(self.middle_frame, wrap="word", font=("Microsoft YaHei", 12))
        self.result_textbox.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

        # --- 底部状态栏 ---
        self.bottom_frame = ctk.CTkFrame(self, height=30)
        self.bottom_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        self.bottom_frame.grid_columnconfigure(0, weight=1)

        self.progress_bar = ctk.CTkProgressBar(self.bottom_frame)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        
        self.status_label = ctk.CTkLabel(self.bottom_frame, text="准备就绪", width=150)
        self.status_label.grid(row=0, column=1, padx=10, pady=5, sticky="e")

        self.pdf_path = None
        self.is_processing = False

    def create_menu(self):
        """创建菜单栏"""
        menubar = Menu(self)
        self.config(menu=menubar)
        
        # 文件菜单
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="打开PDF", command=self.select_pdf)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.quit)
        
        # 编辑菜单
        edit_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="编辑", menu=edit_menu)
        edit_menu.add_command(label="清空结果", command=self.clear_results)
        edit_menu.add_command(label="复制全部", command=self.copy_all)
        
        # 帮助菜单
        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self.show_about)

    def select_pdf(self):
        self.pdf_path = filedialog.askopenfilename(
            title="请选择一个PDF文件",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        if self.pdf_path:
            self.file_label.configure(text=os.path.basename(self.pdf_path))
            self.start_button.configure(state="normal")
            self.status_label.configure(text="文件已选择")
        else:
            self.file_label.configure(text="尚未选择文件")
            self.start_button.configure(state="disabled")

    def clear_results(self):
        """清空结果文本框"""
        self.result_textbox.delete("1.0", "end")
        self.status_label.configure(text="结果已清空")

    def copy_all(self):
        """复制所有结果到剪贴板"""
        content = self.result_textbox.get("1.0", "end")
        self.clipboard_clear()
        self.clipboard_append(content)
        self.status_label.configure(text="已复制到剪贴板")

    def show_about(self):
        """显示关于对话框"""
        messagebox.showinfo("关于", "离线PDF-OCR工具\n版本: 1.0\n\n一个基于PaddleOCR的离线PDF文本识别工具")

    def start_ocr_thread(self):
        if not self.pdf_path:
            messagebox.showwarning("提示", "请先选择一个PDF文件！")
            return
        if not OCR_ENGINE:
            messagebox.showerror("错误", "OCR引擎未能成功初始化，无法进行识别。\n请检查模型文件是否存在。")
            return
        if self.is_processing:
            messagebox.showwarning("提示", "正在处理中，请稍候...")
            return
            
        self.is_processing = True
        self.start_button.configure(state="disabled")
        self.select_button.configure(state="disabled")
        self.result_textbox.delete("1.0", "end")
        
        # 使用线程来运行OCR，防止UI卡死
        ocr_thread = threading.Thread(target=self.run_ocr_process)
        ocr_thread.daemon = True # 主程序退出时线程也退出
        ocr_thread.start()

    def run_ocr_process(self):
        try:
            doc = fitz.open(self.pdf_path)
            total_pages = len(doc)
            self.status_label.configure(text=f"共 {total_pages} 页, 处理中...")
            self.progress_bar.set(0)
            
            # 获取用户设置
            zoom = float(self.zoom_var.get())
            
            full_text = ""
            for i, page in enumerate(doc):
                if not self.is_processing:
                    break
                    
                # 1. PDF页面转图片
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat)
                img_bytes = pix.tobytes("png")

                # 2. OCR识别图片
                result = OCR_ENGINE.ocr(img_bytes, cls=True)
                
                # 3. 提取并整理文字
                page_text = ""
                if result and result[0]:
                    txts = [line[1][0] for line in result[0]]
                    page_text = "\n".join(txts)

                full_text += f"--- 第 {i+1} 页 --- \n{page_text}\n\n"
                
                # 4. 在UI线程中更新内容
                self.after(0, self.update_ui, f"--- 第 {i+1} 页 --- \n{page_text}\n\n", (i + 1) / total_pages, f"已完成 {i+1}/{total_pages} 页")

            doc.close()
            
            if self.is_processing:
                self.after(0, lambda: messagebox.showinfo("完成", f"所有 {total_pages} 页均已识别完毕！"))
            else:
                self.after(0, lambda: self.status_label.configure(text="操作已取消"))

        except Exception as e:
            self.after(0, lambda: messagebox.showerror("OCR处理失败", f"处理过程中发生错误:\n{str(e)}"))
        finally:
            self.is_processing = False
            self.after(0, self.reset_ui)

    def update_ui(self, text, progress, status):
        """在UI线程中更新界面"""
        self.result_textbox.insert("end", text)
        self.progress_bar.set(progress)
        self.status_label.configure(text=status)

    def reset_ui(self):
        """重置UI状态"""
        self.start_button.configure(state="normal" if self.pdf_path else "disabled")
        self.select_button.configure(state="normal")
        self.status_label.configure(text="准备就绪")

if __name__ == "__main__":
    try:
        logging.info("开始主程序")
        print("开始主程序")
        
        if not OCR_ENGINE:
            logging.error("OCR引擎初始化失败")
            root = ctk.CTk()
            root.withdraw()
            messagebox.showerror("OCR引擎错误", "无法初始化OCR引擎，请检查模型文件路径是否正确。")
            root.destroy()
            sys.exit(1)
        
        logging.info("创建应用程序")
        print("创建应用程序")
        app = App()
        
        logging.info("启动主循环")
        print("启动主循环")
        app.mainloop()
        
    except Exception as e:
        error_msg = f"应用程序发生致命错误: {e}"
        print(error_msg)
        logging.error(error_msg, exc_info=True)
        
        try:
            import tkinter.messagebox as mb
            mb.showerror("致命错误", error_msg)
        except:
            pass
        
        sys.exit(1)