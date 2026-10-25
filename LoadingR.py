from tkinter import filedialog, messagebox
from RouteLoader import RouteLoader
import threading

from expor_module.exporter import BVEExporter


def askfile():
    return filedialog.askopenfilename(title="루트 파일 선택", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])

class Loading:
    """Tkinter GUI 전용 래퍼"""
    def __init__(self, progress_bar, status_label, button_to_disable):
        self.progress = progress_bar
        self.status = status_label
        self.button = button_to_disable

    def run(self):
        path = askfile()
        if not path:
            messagebox.showerror("오류", "파일이 선택되지 않았습니다.")
            self.button.config(state="normal")
            return

        loader = RouteLoader(path)

        def progress_callback(percent):
            self.progress["value"] = percent
            self.status.config(text=f"진행률: {percent}%")

        def background_task():
            success, error = loader.load(progress_callback)
            if success:
                # 💡 loader가 품고 있는 current_route에서 data 추출
                route_data = getattr(loader.current_route, "route_data", None)
                current_route = getattr(loader, "current_route", None)
                if route_data and current_route:
                    # Vermoute 익스포터 실행
                    exporter = BVEExporter()
                    result = exporter.extract_and_save(route_data, current_route)
                    if result:
                        messagebox.showinfo("정보", "루트 로딩 및 추출 성공!")
                    else:
                        messagebox.showerror("오류", "추출 실패!")
                else:
                    messagebox.showerror("오류", "데이터(ParsedData)를 찾을 수 없습니다.")
            else:
                messagebox.showerror("오류", error)
            self.button.config(state="normal")

        threading.Thread(target=background_task, daemon=True).start()
