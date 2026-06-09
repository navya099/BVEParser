from tkinter import filedialog, messagebox
from RouteLoader import RouteLoader
import threading

def askfile():
    return filedialog.askopenfilename(title="루트 파일 선택", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])

class Loading:
    """Tkinter GUI 전용 래퍼"""
    def __init__(self, progress_bar, status_label, button_to_disable, is_reverse_mode=False):
        self.progress = progress_bar
        self.status = status_label
        self.button = button_to_disable
        self.is_reverse = is_reverse_mode

    def run(self):
        path = askfile()
        if not path:
            messagebox.showerror("오류", "파일이 선택되지 않았습니다.")
            self.button.config(state="normal")
            return

        loader = RouteLoader(path, self.is_reverse)

        def progress_callback(percent):
            self.progress["value"] = percent
            self.status.config(text=f"진행률: {percent}%")

        def background_task():
            success, error = loader.load(progress_callback)
            if success:
                messagebox.showinfo("정보", "루트 로딩 성공")
            else:
                messagebox.showerror("오류", error)
            self.button.config(state="normal")

        threading.Thread(target=background_task, daemon=True).start()
