import threading
import time
from tkinter import filedialog
import traceback

from OpenBveApi.System.BaseOptions import BaseOptions
from Plugins.RouteCsvRw.Plugin import Plugin
from RouteManager2.CurrentRoute import CurrentRoute
from OpenBveApi.System.TextEncoding import TextEncoding


def askfile():
    file = filedialog.askopenfile(title="루트 파일 선택", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
    return file


class Loading:
    def __init__(self, progress_bar, status_label):
        self.progress = progress_bar
        self.status = status_label

    def run(self):
        try:
            file = askfile()
            if file is None:
                print("파일이 선택되지 않았습니다.")
                return

            path = file.name

            # ✅ 프로그레스바 초기화 (즉시 적용)
            self.progress["value"] = 0
            self.status.config(text="루트 로딩 준비 중...")

            def background_task():
                try:
                    plugin = Plugin()
                    plugin.CurrentProgress = 0.0
                    current_route = CurrentRoute()
                    options = BaseOptions()
                    plugin.load(None, None, options, None)

                    if not plugin.CanLoadRoute(path):
                        print('유효한 루트 파일이 아닙니다.')
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

                    # ✅ UI 업데이트용 쓰레드
                    threading.Thread(target=update_progress, daemon=True).start()

                    # ✅ 루트 로드 (백그라운드에서 실행)
                    result = plugin.LoadRoute(path, encoding, '', '', '', True, current_route)

                    if result:
                        print('루트 로딩에 성공했습니다.')
                    else:
                        print('루트 로딩 실패.')
                except Exception as ex_inner:
                    print("내부 오류 발생:", ex_inner)
                    traceback.print_exc()
                    self.status.config(text="오류 발생!")

            # ✅ 전체 루트 로딩을 백그라운드에서 실행
            threading.Thread(target=background_task, daemon=True).start()

        except Exception as ex:
            print("오류가 발생했습니다:", ex)
            traceback.print_exc()
            self.status.config(text="오류 발생!")
