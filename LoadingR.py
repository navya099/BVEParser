from OpenBveApi.System.BaseOptions import BaseOptions
from Plugins.RouteCsvRw.Plugin import Plugin
from RouteManager2.CurrentRoute import CurrentRoute
import tkinter as tk
from tkinter import filedialog
import traceback
from OpenBveApi.System.TextEncoding import TextEncoding


def askfile():
    # 파일 열기 대화상자에서 파일 선택
    file = filedialog.askopenfile(title="루트 파일 선택", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
    return file  # 선택된 파일을 반환


class Loading:
    def __init__(self):
        pass

    def run(self):
        try:
            file = askfile()  # 파일 선택 대화상자 호출

            if file is None:  # 사용자가 파일을 선택하지 않은 경우
                print("파일이 선택되지 않았습니다. ")

            else:
                path = file.name
                plugin = Plugin()  # 플러그인 인스턴스 생성
                current_route = CurrentRoute()
                # 권장되는 구조
                options = BaseOptions()
                plugin.load(None, None, options, None)

                # 루트 파일이 유효한지 확인
                if plugin.CanLoadRoute(path):

                    encoding = TextEncoding.get_system_encoding_from_file(path)
                    result = plugin.LoadRoute(path, encoding, '', '', '', True, current_route)
                    if result:
                        print('루트 로딩에 성공했습니다.')
                else:
                    print('유효한 루트 파일이 아닙니다.')
                    plugin.Unload()

        except Exception as ex:
            print("오류가 발생했습니다:", ex)
            traceback.print_exc()
