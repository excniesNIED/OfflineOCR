import tkinter
import customtkinter as ctk
from tkinter import filedialog, messagebox, Menu
import fitz  # PyMuPDF
from paddleocr import PaddleOCR
import threading
import os
import sys
import logging

# --- 全局设置 ---
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

def resource_path(relative_path):
    """获取资源文件的绝对路径"""
    try:
        # PyInstaller创建临时文件夹，将路径存储在_MEIPASS中
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

# 禁用PaddleOCR的日志输出
logging.getLogger('ppocr').setLevel(logging.WARNING)

# --- OCR引擎初始化 (离线模式) ---
# 使用旧模型结构路径
def init_ocr_engine():
    """初始化OCR引擎"""
    try:
        # 检查模型文件是否存在
        det_model_path = resource_path('models/det/ch/ch_PP-OCRv4_det_infer')
        rec_model_path = resource_path('models/rec/ch/ch_PP-OCRv4_rec_infer')
        cls_model_path = resource_path('models/cls/ch_ppocr_mobile_v2.0_cls_infer')
        
        print(f"检测模型路径: {det_model_path}")
        print(f"识别模型路径: {rec_model_path}")
        print(f"方向分类模型路径: {cls_model_path}")
        
        # 检查模型目录是否存在
        if not os.path.exists(det_model_path):
            raise FileNotFoundError(f"检测模型目录不存在: {det_model_path}")
        if not os.path.exists(rec_model_path):
            raise FileNotFoundError(f"识别模型目录不存在: {rec_model_path}")
        if not os.path.exists(cls_model_path):
            raise FileNotFoundError(f"方向分类模型目录不存在: {cls_model_path}")
        
        # 检查关键模型文件是否存在
        det_model_file = os.path.join(det_model_path, 'inference.pdiparams')
        rec_model_file = os.path.join(rec_model_path, 'inference.pdiparams')
        cls_model_file = os.path.join(cls_model_path, 'inference.pdiparams')
        
        print(f"检测模型文件存在: {os.path.exists(det_model_file)}")
        print(f"识别模型文件存在: {os.path.exists(rec_model_file)}")
        print(f"方向分类模型文件存在: {os.path.exists(cls_model_file)}")
        
        if not os.path.exists(det_model_file):
            raise FileNotFoundError(f"检测模型文件不存在: {det_model_file}")
        if not os.path.exists(rec_model_file):
            raise FileNotFoundError(f"识别模型文件不存在: {rec_model_file}")
        if not os.path.exists(cls_model_file):
            raise FileNotFoundError(f"方向分类模型文件不存在: {cls_model_file}")
        
        # 打印环境信息
        print(f"当前工作目录: {os.getcwd()}")
        print(f"sys.argv[0]: {sys.argv[0] if len(sys.argv) > 0 else 'N/A'}")
        print(f"sys._MEIPASS: {getattr(sys, '_MEIPASS', 'N/A')}")
        
        # 使用resource_path函数确保打包后能找到模型文件
        ocr_engine = PaddleOCR(
            use_textline_orientation=True, 
            lang='ch',
            text_detection_model_dir=det_model_path,
            text_recognition_model_dir=rec_model_path,
            textline_orientation_model_dir=cls_model_path
        )
        print("OCR引擎初始化成功")
        return ocr_engine
    except Exception as e:
        # 捕获初始化异常，通常是模型路径问题
        print(f"OCR引擎初始化失败: {e}")
        import traceback
        traceback.print_exc()
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
            lang = self.lang_var.get()
            
            full_text = ""
            for i, page in enumerate(doc):
                if not self.is_processing:  # 用户可能取消了操作
                    break
                    
                # 1. PDF页面转图片
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat)
                img_bytes = pix.tobytes("png") # 转为字节流

                # 2. OCR识别图片
                result = OCR_ENGINE.ocr(img_bytes, cls=True)
                
                # 3. 提取并整理文字
                page_text = ""
                if result and result[0]:
                    txts = [line[1][0] for line in result[0]]
                    page_text = "\n".join(txts)

                full_text += f"--- 第 {i+1} 页 ---\n{page_text}\n\n"
                
                # 4. 在UI线程中更新内容
                self.after(0, self.update_ui, f"--- 第 {i+1} 页 ---\n{page_text}\n\n", (i + 1) / total_pages, f"已完成 {i+1}/{total_pages} 页")

            doc.close()
            
            if self.is_processing:
                self.after(0, lambda: messagebox.showinfo("完成", f"所有 {total_pages} 页均已识别完毕！"))
            else:
                self.after(0, lambda: self.status_label.configure(text="操作已取消"))

        except Exception as e:
            self.after(0, lambda: messagebox.showerror("OCR处理失败", f"处理过程中发生错误:\n{str(e)}"))
        finally:
            # 无论成功失败，都恢复按钮状态
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
    # 检查OCR引擎是否初始化成功
    if not OCR_ENGINE:
        print("OCR引擎初始化失败，程序无法启动")
        root = ctk.CTk()
        root.withdraw()  # 隐藏主窗口
        messagebox.showerror("OCR引擎错误", "无法初始化OCR引擎，请检查模型文件路径是否正确。")
        root.destroy()
        sys.exit(1)
    
    app = App()
    app.mainloop()