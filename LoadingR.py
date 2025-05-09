import threading
import time
from tkinter import filedialog, messagebox
import traceback
from RouteViewer.System.Host import Host
from loggermodule import logger
import os
import sys

from OpenBveApi.System.BaseOptions import BaseOptions
from Plugins.RouteCsvRw.Plugin import Plugin
from RouteManager2.CurrentRoute import CurrentRoute
from OpenBveApi.System.TextEncoding import TextEncoding


def askfile():
    return filedialog.askopenfilename(title="루트 파일 선택", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])


class Loading:
    def __init__(self, progress_bar, status_label, button_to_disable):
        self.progress = progress_bar
        self.status = status_label
        self.button = button_to_disable  # 새로 추가

    def run(self):
        try:
            path = askfile()
            if not path:
                messagebox.showerror("오류", "파일이 선택되지 않았습니다.")
                self.button.config(state="normal")  # 선택 안 했으면 다시 활성화
                return

            railway_path = Loading.get_railway_folder(path)
            object_path = os.path.join(railway_path, 'Object')

            # ✅ 프로그레스바 초기화 (즉시 적용)
            self.progress["value"] = 0
            self.status.config(text="루트 로딩 준비 중...")

            def background_task():
                try:
                    plugin = Plugin()
                    plugin.CurrentProgress = 0.0
                    current_route = CurrentRoute()
                    host = Host()
                    options = BaseOptions()
                    plugin.load(host, None, options, None)

                    if not plugin.CanLoadRoute(path):
                        messagebox.showerror("오류", "유효하지 않은 루트 파일입니다.")
                        plugin.Unload()
                        self.status.config(text="유효하지 않은 루트 파일입니다.")
                        return

                    encoding = TextEncoding.get_system_encoding_from_file(path)

                    def update_progress():
                        while True:
                            percent = int(plugin.CurrentProgress * 100)
                            self.progress["value"] = percent
                            self.status.config(text=f"진행률: {percent}%")
                            if plugin.CurrentProgress >= 1.0:
                                break
                            time.sleep(0.1)
                        self.progress["value"] = 100
                        self.status.config(text="루트 로딩 완료!")
                        self.button.config(state="normal")  # 로딩 완료 후 다시 활성화

                    # ✅ UI 업데이트용 쓰레드
                    threading.Thread(target=update_progress, daemon=True).start()

                    # ✅ 루트 로드 (백그라운드에서 실행)
                    result = plugin.LoadRoute(path, encoding, '', object_path, '', False, current_route)

                    if result:

                        messagebox.showinfo("정보", "루트 로딩 성공.")
                    else:
                        messagebox.showerror("에러", "루트 로딩 실패.")
                        self.button.config(state="normal")  # 실패 시 다시 활성화
                except Exception as ex_inner:
                    logger.critical("내부 오류 발생:", ex_inner)
                    logger.critical(traceback.print_exc())
                    self.status.config(text="오류 발생!")
                    self.button.config(state="normal")  # 실패 시 다시 활성화

            # ✅ 전체 루트 로딩을 백그라운드에서 실행
            threading.Thread(target=background_task, daemon=True).start()

        except Exception as ex:
            logger.error("오류가 발생했습니다:", ex)
            logger.critical(traceback.format_exc())
            self.status.config(text="오류 발생!")

    @staticmethod
    def get_railway_folder(route_file: str) -> str:
        try:
            folder = os.path.dirname(route_file)

            while True:
                subfolder = os.path.join(folder, "Railway")
                if os.path.isdir(subfolder):
                    # Ignore completely empty directories
                    if any(os.scandir(subfolder)):
                        return subfolder

                if not folder:
                    continue
                parent = os.path.dirname(folder)
                if not parent or parent == folder:
                    break
                folder = parent
        except Exception:
            pass

        # If the Route, Object and Sound folders exist, but are not inside a Railway folder
        try:
            folder = os.path.dirname(route_file)
            if not folder:
                # Fallback: Return application base path
                return os.path.dirname(sys.argv[0])

            candidate = None
            while True:
                route_folder = os.path.join(folder, "Route")
                object_folder = os.path.join(folder, "Object")
                sound_folder = os.path.join(folder, "Sound")

                if os.path.isdir(route_folder) and os.path.isdir(object_folder) and os.path.isdir(sound_folder):
                    return folder

                if os.path.isdir(route_folder) and os.path.isdir(object_folder):
                    candidate = folder

                parent = os.path.dirname(folder)
                if not parent or parent == folder:
                    if candidate:
                        return candidate
                    break
                folder = parent
        except Exception:
            pass

        return os.path.dirname(sys.argv[0])
