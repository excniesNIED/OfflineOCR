import os
import sys
import logging
# 关键改动：提前导入tkinter和messagebox，以确保任何后续的导入失败都能被正确报告
import tkinter
from tkinter import messagebox

# --- 启动时的路径和环境设置 ---
IS_FROZEN = hasattr(sys, 'frozen')
if IS_FROZEN:
    base_path = os.path.dirname(os.path.abspath(sys.executable))
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

log_file = os.path.join(base_path, 'debug.log')
try:
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - [%(funcName)s] %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8', mode='w'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logging.info(f"应用程序启动，运行模式: {'打包' if IS_FROZEN else '开发'}")
    logging.info(f"基准路径 (base_path): {base_path}")
    os.chdir(base_path)
    logging.info(f"已切换当前工作目录至: {os.getcwd()}")
except Exception as e:
    print(f"设置日志系统或切换目录失败: {e}")
    messagebox.showerror("初始化错误", f"设置日志系统失败: {e}")


# --- 正常导入模块 ---
try:
    logging.info("开始导入核心模块...")
    import customtkinter as ctk
    from tkinter import filedialog, Menu
    import fitz
    from paddleocr import PaddleOCR
    import threading
    logging.info("所有核心模块导入成功。")
except ImportError as e:
    logging.error(f"模块导入失败: {e}", exc_info=True)
    messagebox.showerror("致命错误", f"无法加载核心模块，程序无法启动。\n\n错误: {e}\n\n请检查 'debug.log' 获取详细信息。")
    sys.exit(1)


# --- 全局设置 ---
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# 禁用PaddleOCR的日志输出
logging.getLogger('ppocr').setLevel(logging.WARNING)


# --- OCR引擎初始化 ---
def init_ocr_engine():
    """初始化OCR引擎"""
    try:
        logging.info("开始初始化OCR引擎...")
        det_model_path = os.path.join(base_path, 'models/det/ch/ch_PP-OCRv4_det_infer')
        rec_model_path = os.path.join(base_path, 'models/rec/ch/ch_PP-OCRv4_rec_infer')
        cls_model_path = os.path.join(base_path, 'models/cls/ch_ppocr_mobile_v2.0_cls_infer')
        
        logging.info(f"检测模型路径: {det_model_path}")
        logging.info(f"识别模型路径: {rec_model_path}")
        logging.info(f"分类模型路径: {cls_model_path}")
        
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
            show_log=False
        )
        logging.info("OCR引擎初始化成功。")
        return ocr_engine
    except Exception as e:
        logging.error(f"OCR引擎初始化失败: {e}", exc_info=True)
        messagebox.showerror("OCR引擎错误", f"OCR引擎初始化失败，程序无法继续。\n\n错误: {e}\n\n请确保 'models' 文件夹完整并位于程序根目录，然后重启程序。")
        return None

# 立即调用函数以创建全局变量
OCR_ENGINE = init_ocr_engine()

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("离线PDF-OCR工具")
        self.geometry("900x700")
        self.minsize(600, 400)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.create_menu()

        self.top_frame = ctk.CTkFrame(self, height=50)
        self.top_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.top_frame.grid_columnconfigure(1, weight=1)

        self.select_button = ctk.CTkButton(self.top_frame, text="选择PDF文件", command=self.select_pdf)
        self.select_button.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.file_label = ctk.CTkLabel(self.top_frame, text="尚未选择文件", anchor="w")
        self.file_label.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        self.start_button = ctk.CTkButton(self.top_frame, text="开始识别", command=self.start_ocr_thread, state="disabled")
        self.start_button.grid(row=0, column=2, padx=10, pady=10, sticky="e")

        self.middle_frame = ctk.CTkFrame(self)
        self.middle_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.middle_frame.grid_columnconfigure(0, weight=1)
        self.middle_frame.grid_rowconfigure(1, weight=1)

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

        self.result_textbox = ctk.CTkTextbox(self.middle_frame, wrap="word", font=("Microsoft YaHei", 12))
        self.result_textbox.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

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
        menubar = Menu(self)
        self.config(menu=menubar)
        
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="打开PDF", command=self.select_pdf)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.quit)
        
        edit_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="编辑", menu=edit_menu)
        edit_menu.add_command(label="清空结果", command=self.clear_results)
        edit_menu.add_command(label="复制全部", command=self.copy_all)
        
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
        self.result_textbox.delete("1.0", "end")
        self.status_label.configure(text="结果已清空")

    def copy_all(self):
        content = self.result_textbox.get("1.0", "end")
        self.clipboard_clear()
        self.clipboard_append(content)
        self.status_label.configure(text="已复制到剪贴板")

    def show_about(self):
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
        
        ocr_thread = threading.Thread(target=self.run_ocr_process)
        ocr_thread.daemon = True
        ocr_thread.start()

    def run_ocr_process(self):
        try:
            doc = fitz.open(self.pdf_path)
            total_pages = len(doc)
            self.status_label.configure(text=f"共 {total_pages} 页, 处理中...")
            self.progress_bar.set(0)
            
            zoom = float(self.zoom_var.get())
            
            full_text = ""
            for i, page in enumerate(doc):
                if not self.is_processing:
                    break
                    
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat)
                img_bytes = pix.tobytes("png")

                result = OCR_ENGINE.ocr(img_bytes, cls=True)
                
                page_text = ""
                if result and result[0]:
                    txts = [line[1][0] for line in result[0]]
                    page_text = "\n".join(txts)

                full_text += f"--- 第 {i+1} 页 --- \n{page_text}\n\n"
                
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
        self.result_textbox.insert("end", text)
        self.progress_bar.set(progress)
        self.status_label.configure(text=status)

    def reset_ui(self):
        self.start_button.configure(state="normal" if self.pdf_path else "disabled")
        self.select_button.configure(state="normal")
        self.status_label.configure(text="准备就绪")

if __name__ == "__main__":
    try:
        logging.info("开始主程序")
        
        if not OCR_ENGINE:
            logging.error("OCR引擎初始化失败，主程序退出。")
            # 错误信息已在 init_ocr_engine 中通过 messagebox 显示，这里直接退出即可
            sys.exit(1)
        
        logging.info("创建应用程序")
        app = App()
        
        logging.info("启动主循环")
        app.mainloop()
        
    except Exception as e:
        error_msg = f"应用程序发生致命错误: {e}"
        logging.error(error_msg, exc_info=True)
        messagebox.showerror("致命错误", error_msg)
        sys.exit(1)