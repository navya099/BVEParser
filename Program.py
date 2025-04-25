import tkinter as tk
from tkinter import ttk
from loggermodule import logger
from LoadingR import Loading

class Program(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BVE Parser for Python")
        self.geometry("500x200")

        self.new_task_button = tk.Button(self, text="파일 열기", command=self.file_open)
        self.new_task_button.pack(pady=10)

        self.exit_button = tk.Button(self, text="종료", command=self.close_application)
        self.exit_button.pack(pady=10)

        # 프로그레스바와 상태 라벨
        self.progress = ttk.Progressbar(self, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=5)

        self.status = tk.Label(self, text="대기 중...")
        self.status.pack()

        logger.info('MainWindow 초기화 완료')

    def file_open(self):
        """새 작업 마법사 창 시작"""
        loading = Loading(self.progress, self.status)
        loading.run()
    def close_application(self):
        """프로그램 종료"""
        self.quit()
        self.destroy()

