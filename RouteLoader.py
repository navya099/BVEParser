import threading
import time
import os

from RouteViewer.System.Host import Host
from OpenBveApi.System.BaseOptions import BaseOptions
from Plugins.RouteCsvRw.Plugin import Plugin
from RouteManager2.CurrentRoute import CurrentRoute
from OpenBveApi.System.TextEncoding import TextEncoding

class RouteLoader:
    """GUI/CUI 공용 루트 로더"""
    def __init__(self, path: str, is_revese_mode: bool):
        self.path = path
        self.plugin = Plugin()
        self.plugin.CurrentProgress = 0.0
        self.current_route = CurrentRoute()
        self.host = Host()
        self.options = BaseOptions()
        self.is_revese_mode = is_revese_mode

    def load(self, progress_callback=None):
        """
        루트 로드
        :param progress_callback: 진행률(0~100) 콜백 함수
        :return: 성공여부(bool), 에러메시지(str or None)
        """
        try:
            self.options.is_reverse_mode = self.is_revese_mode
            self.plugin.load(self.host, None, self.options, None)

            if not self.plugin.CanLoadRoute(self.path):
                self.plugin.Unload()
                return False, "유효하지 않은 루트 파일입니다."

            encoding = TextEncoding.get_system_encoding_from_file(self.path)
            object_path = os.path.join(RouteLoader.get_railway_folder(self.path), "Object")

            # 진행률 갱신 스레드
            def progress_thread():
                while self.plugin.CurrentProgress < 1.0:
                    if progress_callback:
                        progress_callback(int(self.plugin.CurrentProgress * 100))
                    time.sleep(0.1)
                if progress_callback:
                    progress_callback(100)

            threading.Thread(target=progress_thread, daemon=True).start()
            preview_only = False if self.is_revese_mode else True
            result = self.plugin.LoadRoute(self.path, encoding, '', object_path, '', preview_only, self.current_route)
            return result, None if result else "루트 로딩 실패"

        except Exception as ex:
            return False, str(ex)

    @staticmethod
    def get_railway_folder(route_file: str) -> str:
        folder = os.path.dirname(route_file)
        while folder:
            railway = os.path.join(folder, "Railway")
            if os.path.isdir(railway) and any(os.scandir(railway)):
                return railway
            parent = os.path.dirname(folder)
            if parent == folder:
                break
            folder = parent
        # fallback
        return os.path.dirname(route_file)
