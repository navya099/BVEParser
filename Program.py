import tkinter as tk
from tkinter import filedialog, messagebox
from loggermodule import logger
import traceback
from LoadingR import Loading

class Program(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BVE Parser for Python")
        self.geometry("500x200")

        # "새 작업" 버튼
        self.new_task_button = tk.Button(self, text="파일 열기", command=self.file_open)
        self.new_task_button.pack(pady=20)

        # "종료" 버튼
        self.exit_button = tk.Button(self, text="종료", command=self.close_application)
        self.exit_button.pack(pady=20)

        logger.info(f'MainWindow 초기화 완료')

    def file_open(self):
        """새 작업 마법사 창 시작"""
        loading = Loading()
        loading.run()
    def close_application(self):
        """프로그램 종료"""
        self.quit()
        self.destroy()
