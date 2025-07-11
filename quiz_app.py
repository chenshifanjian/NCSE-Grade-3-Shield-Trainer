import tkinter as tk
from tkinter import ttk, messagebox
import random
import re
import os
from docx import Document

class QuizApp:
    def __init__(self, root, questions_file):
        self.root = root
        self.root.title("三级御盾锻打中")
        self.root.geometry("900x700")
        self.root.resizable(True, True)

        # 设置中文字体
        self.font_config = ('SimHei', 10)
        self.title_font = ('SimHei', 12, 'bold')

        # 配置样式
        self.style = ttk.Style()
        self.style.configure('TLabel', font=self.font_config)
        self.style.configure('Title.TLabel', font=self.title_font)
        self.style.configure('Option.TButton', font=self.font_config, padding=5)
        self.style.configure('Correct.TButton', background='lightgreen', font=self.font_config, padding=5)
        self.style.configure('Incorrect.TButton', background='lightcoral', font=self.font_config, padding=5)

        self.questions_file = questions_file
        self.current_question = None
        self.score = 0
        self.total_questions = 0
        self.time_remaining = 30
        self.timer_id = None
        self.current_notes = ""
        self.encouraging_words = self.load_encouraging_words()
        self.need_to_record_mistake = False

        self.create_widgets()
        self.load_random_question()

    def load_encouraging_words(self):
        """加载鼓励话语"""
        words_file = os.path.join(os.path.dirname(__file__), "Encouraging words.txt")
        words = []
        try:
            if os.path.exists(words_file):
                with open(words_file, 'r', encoding='utf-8') as f:
                    words = [line.strip() for line in f if line.strip()]
        except Exception as e:
            messagebox.showwarning("警告", f"加载鼓励话语失败: {str(e)}")
        return words

    def load_questions(self, file_path):
        """从Word文件加载题目数据"""
        questions = []
        try:
            # 读取Word文档
            doc = Document(file_path)
            content = '\n'.join([para.text for para in doc.paragraphs if para.text.strip()])
            
            # 使用正则表达式分割题目块
            # 匹配题目内容（非答案行）和答案解析行
            pattern = re.compile(r'(.+?)(答案：.*?)((?=\n[^答案]|$))', re.DOTALL)
            matches = pattern.findall(content)
                
            for match in matches:
                question_block = match[0].strip()
                answer_line = match[1].strip()
                
                # 分割题目和选项
                lines = [line.strip() for line in question_block.split('\n') if line.strip()]
                if not lines:
                    continue
                
                question_text = lines[0]
                options = []
                
                # 提取选项（A.xxx, B.xxx等格式）
                for line in lines[1:]:
                    if re.match(r'^[A-D]\.', line):
                        options.append(line)
                
                # 提取答案
                answer_match = re.search(r'答案：([A-D])', answer_line)
                if not answer_match:
                    continue
                answer = answer_match.group(1).strip()
                
                # 提取解析
                explanation_match = re.search(r'解析：(.+)', answer_line)
                explanation = explanation_match.group(1).strip() if explanation_match else "无解析"
                
                # 验证题目数据完整性
                if question_text and options and answer:
                    questions.append({
                        'question': question_text,
                        'options': options,
                        'answer': answer,
                        'explanation': explanation
                    })
                else:
                    messagebox.showwarning("警告", f"题目解析不完整: {question_text[:30]}...")
            return questions
        except Exception as e:
            messagebox.showerror("错误", f"加载题库失败: {str(e)}")
            return []

    def create_widgets(self):
        """创建GUI组件"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 顶部框架（标题和错题本按钮）
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 错题本按钮
        self.mistake_book_btn = ttk.Button(
            top_frame,
            text="错题本",
            command=self.open_mistake_book,
            style='Option.TButton'
        )
        self.mistake_book_btn.pack(side=tk.LEFT)
        
        # 标题标签
        title_label = ttk.Label(top_frame, text="三级御盾锻打中", style='Title.TLabel')
        title_label.pack(side=tk.LEFT, padx=10)

        # 倒计时标签
        self.timer_label = ttk.Label(main_frame, text="剩余时间: 30秒", style='TLabel')
        self.timer_label.pack(pady=(0, 10))

        # 题目区域
        self.question_frame = ttk.LabelFrame(main_frame, text="题目", padding="10")
        self.question_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.question_text = ttk.Label(self.question_frame, text="", style='TLabel', wraplength=700, justify=tk.LEFT)
        self.question_text.pack(fill=tk.BOTH, expand=True, pady=10)

        # 选项区域
        self.options_frame = ttk.Frame(main_frame)
        self.options_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.option_buttons = []
        for i in range(4):  # 最多4个选项
            btn = ttk.Button(
                    self.options_frame,
                    text="",
                    command=lambda idx=i: self.select_option(idx),
                    width=60,
                    style='Option.TButton'
                )
            btn.pack(fill=tk.X, pady=5)
            self.option_buttons.append(btn)

        # 结果显示区域
        self.result_frame = ttk.LabelFrame(main_frame, text="结果", padding="10")
        self.result_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.result_text = ttk.Label(self.result_frame, text="", style='TLabel', wraplength=700, justify=tk.LEFT)
        self.result_text.pack(fill=tk.BOTH, expand=True, pady=10)

        # 用户笔记区域
        self.notes_frame = ttk.Frame(self.result_frame)
        self.notes_label = ttk.Label(self.notes_frame, text="长长记性:", style='TLabel')
        self.notes_label.pack(anchor=tk.W)
        self.notes_text = tk.Text(self.notes_frame, height=3, width=60, font=self.font_config)
        self.notes_text.pack(fill=tk.X, pady=5)
        self.submit_notes_btn = ttk.Button(
            self.notes_frame, 
            text="提交笔记", 
            command=self.submit_notes, 
            style='Option.TButton'
        )
        self.submit_notes_btn.pack(pady=5)
        self.notes_frame.pack(fill=tk.X, pady=10)
        self.notes_frame.pack_forget()  # 默认隐藏

        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        self.next_button = ttk.Button(
            button_frame,
            text="下一题",
            command=self.confirm_next_question,
            state=tk.DISABLED
        )
        self.next_button.pack(side=tk.RIGHT, padx=5)

        self.quit_button = ttk.Button(
            button_frame,
            text="退出",
            command=self.root.quit
        )
        self.quit_button.pack(side=tk.RIGHT, padx=5)

        # 分数显示
        self.score_label = ttk.Label(button_frame, text="得分: 0/0", style='TLabel')
        self.score_label.pack(side=tk.LEFT)

    def update_timer(self):
        """更新倒计时显示"""
        self.time_remaining -= 1
        self.timer_label.config(text=f"剩余时间: {self.time_remaining}秒")
        if self.time_remaining <= 0:
            self.handle_timeout()
            return
        self.timer_id = self.root.after(1000, self.update_timer)

    def handle_timeout(self):
        """处理超时未作答情况"""
        if not self.current_question:
            return

        # 禁用所有选项按钮
        for btn in self.option_buttons:
            btn.config(state=tk.DISABLED)

        # 显示正确答案
        correct_answer = self.current_question['answer']
        for i, btn in enumerate(self.option_buttons):
            if btn.cget("text").startswith(correct_answer):
                btn.config(style='Correct.TButton')
                break

        result_text = f"时间到！未作答。正确答案是：{correct_answer}\n\n解析：{self.current_question['explanation']}"
        self.result_text.config(text=result_text)
        self.score_label.config(text=f"得分: {self.score}/{self.total_questions}")

        # 显示笔记区域
        self.notes_frame.pack(fill=tk.X, pady=10)
        self.current_notes = ""
        self.need_to_record_mistake = True

        # 启用下一题按钮
        self.next_button.config(state=tk.NORMAL)

    def confirm_next_question(self):
        """确认是否继续下一题，未提交笔记时自动记录错题"""
        # 检查是否需要记录错题
        if self.need_to_record_mistake:
            self.record_mistake()
            self.need_to_record_mistake = False
        
        # 加载下一题
        self.load_random_question()

    def load_random_question(self):
        """加载随机题目"""
        # 取消当前计时器
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

            # 每次重新加载题目
        current_questions = self.load_questions(self.questions_file)
        if not current_questions:
            messagebox.showinfo("提示", "题库中没有题目，请检查题库文件是否正确")
            self.next_button.config(state=tk.DISABLED)
            return

        # 重置界面状态
        self.time_remaining = 30
        self.timer_label.config(text=f"剩余时间: {self.time_remaining}秒")
        self.timer_id = self.root.after(1000, self.update_timer)
        self.current_question = random.choice(current_questions)
        self.result_text.config(text="")
        self.notes_frame.pack_forget()  # 隐藏笔记区域
        self.next_button.config(state=tk.DISABLED)
        self.need_to_record_mistake = False  # 重置错题记录标志

        # 启用所有选项按钮
        for btn in self.option_buttons:
            btn.config(state=tk.NORMAL, style='TButton')

        # 显示题目
        self.question_text.config(text=self.current_question['question'])

        # 打乱选项顺序
        shuffled_options = self.current_question['options'].copy()
        random.shuffle(shuffled_options)
        
        # 显示选项
        for i, btn in enumerate(self.option_buttons):
            if i < len(shuffled_options):
                btn.config(text=shuffled_options[i])
                btn.pack(fill=tk.X, pady=5)
            else:
                btn.pack_forget()

    def select_option(self, option_index):
        """处理选项选择"""
        if not self.current_question:
            return

        # 获取选中的选项文本
        selected_btn = self.option_buttons[option_index]
        selected_text = selected_btn.cget("text")
        selected_option = selected_text[0]  # 获取选项字母(A, B, C, D)

        # 停止倒计时
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

        # 禁用所有选项按钮
        for btn in self.option_buttons:
            btn.config(state=tk.DISABLED)

        # 检查答案
        correct_answer = self.current_question['answer']
        is_correct = selected_option == correct_answer

        # 更新分数
        self.total_questions += 1
        if is_correct:
            self.score += 1
            selected_btn.config(style='Correct.TButton')
            result_text = f"正确！\n\n解析：{self.current_question['explanation']}"
        else:
            selected_btn.config(style='Incorrect.TButton')
            # 高亮正确答案
            for i, btn in enumerate(self.option_buttons):
                if btn.cget("text").startswith(correct_answer):
                    btn.config(style='Correct.TButton')
                    break
            # 获取随机鼓励语
            encouraging_text = ""
            if self.encouraging_words:
                encouraging_text = f"\n\n鼓励：{random.choice(self.encouraging_words)}"
            result_text = f"错误！正确答案是：{correct_answer}\n\n解析：{self.current_question['explanation']}{encouraging_text}"
            # 显示笔记区域
            self.notes_frame.pack(fill=tk.X, pady=10)
            self.current_notes = ""
            self.need_to_record_mistake = True

        # 显示结果
        self.result_text.config(text=result_text)
        self.score_label.config(text=f"得分: {self.score}/{self.total_questions}")

        # 启用下一题按钮
        self.next_button.config(state=tk.NORMAL)

    def submit_notes(self):
        """提交用户笔记并更新错题本和题库"""
        self.current_notes = self.notes_text.get("1.0", tk.END).strip()
        self.notes_frame.pack_forget()
        self.notes_text.delete("1.0", tk.END)
        
        # 记录错题（包含笔记）
        self.record_mistake()
        self.need_to_record_mistake = False
        
        # 启用下一题按钮
        self.next_button.config(state=tk.NORMAL)

    def record_mistake(self):
        """记录错题到文件（包含用户笔记）"""
        if not self.current_question:
            return
        mistake_file = os.path.join(os.path.dirname(__file__), "mistakes.txt")
        try:
            # 确保目录存在
            mistake_dir = os.path.dirname(mistake_file)
            if not os.path.exists(mistake_dir):
                os.makedirs(mistake_dir)
                
            with open(mistake_file, 'a', encoding='utf-8') as f:
                f.write(f"题目: {self.current_question['question']}\n")
                f.write(f"选项: {', '.join(self.current_question['options'])}\n")
                f.write(f"正确答案: {self.current_question['answer']}\n")
                f.write(f"解析: {self.current_question['explanation']}\n")
                if self.current_notes:
                    f.write(f"用户笔记: {self.current_notes}\n")
                f.write("-" * 50 + "\n")  # 分隔线
        except PermissionError:
            messagebox.showerror("权限错误", f"无法写入错题本文件: {mistake_file}\n请检查文件权限")
        except IOError as e:
            messagebox.showerror("IO错误", f"写入错题本失败: {str(e)}")
        except Exception as e:
            messagebox.showerror("错误", f"记录错题失败: {str(e)}")

    def open_mistake_book(self):
        """打开错题本窗口查看错题"""
        mistake_window = tk.Toplevel(self.root)
        mistake_window.title("错题本")
        mistake_window.geometry("800x600")
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(mistake_window)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_widget = tk.Text(mistake_window, yscrollcommand=scrollbar.set, font=self.font_config)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.config(command=text_widget.yview)
        
        # 读取错题本内容
        mistake_file = os.path.join(os.path.dirname(__file__), "mistakes.txt")
        try:
            if not os.path.exists(mistake_file):
                text_widget.insert(tk.END, "错题本为空，继续努力！")
                return
                
            with open(mistake_file, 'r', encoding='utf-8') as f:
                content = f.read()
                text_widget.insert(tk.END, content)
        except Exception as e:
            messagebox.showerror("错误", f"读取错题本失败: {str(e)}")
        
        # 设置文本框为只读
        text_widget.config(state=tk.DISABLED)

    def __del__(self):
        """清理资源"""
        if self.timer_id:
            self.root.after_cancel(self.timer_id)

if __name__ == "__main__":
    # 检查依赖
    try:
        from docx import Document
    except ImportError:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        messagebox.showerror("依赖缺失", "请安装python-docx库：pip install python-docx")
        root.destroy()
        exit(1)
    
    # 题库文件路径
    QUESTIONS_FILE = os.path.join(os.path.dirname(__file__), "combined_questions_without_numbers.docx")
    
    # 创建主窗口
    root = tk.Tk()
    
    # 配置样式
    style = ttk.Style()
    
    # 创建并运行应用
    app = QuizApp(root, QUESTIONS_FILE)
    root.mainloop()

    def __del__(self):
        """清理资源"""
        if self.timer_id:
            self.root.after_cancel(self.timer_id)