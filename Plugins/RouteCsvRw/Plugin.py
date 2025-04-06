import os
import chardet
from RouteManager2.CurrentRoute import CurrentRoute
from .CsvRwRouteParser import Parser
from OpenBveApi.Routes.RouteInterface import RouteInterface
from OpenBveApi.System.BaseOptions import BaseOptions 
from OpenBveApi.System.Path import Path
import traceback
import threading
import time

def detect_encoding(path):
    # 파일을 열어 일부를 읽어서 인코딩을 감지합니다
    with open(path, 'rb') as file:
        raw_data = file.read(10000)  # 처음 10000 바이트를 읽어봄
        result = chardet.detect(raw_data)  # 인코딩 탐지
        return result['encoding']
    
class Plugin(RouteInterface):
    CurrentRoute = CurrentRoute()
    CurrentOptions = BaseOptions()
    CurrentHost = None
    Random = None
    FileSystem = None
    TrainManager = None
    
    def __init__(self):
        super().__init__()
        
    def load(self, host, file_system, options, train_manager_reference):
        CurrentHost = host
        FileSystem = file_system
        CurrentOptions = options
        
        # Check if train_manager_reference is of type TrainManagerBase
        if isinstance(train_manager_reference, TrainManagerBase):
            self.TrainManager = train_manager_reference
        
        # Set TrainDownloadLocation to an empty string
        CurrentOptions.TrainDownloadLocation = ""
        
    def CanLoadRoute(self, path: str) -> bool:
        if not path or not os.path.exists(path):
            return False
        if path.lower().endswith(".rw"):
            return True
        if path.lower().endswith(".csv"):
            encoding = detect_encoding(path)  # 파일 인코딩 탐지
            with open(path, 'r',encoding=encoding) as file:
                for i in range(30):
                    try:
                        line = file.readline()
                        print('s')
                        if not line:
                            break  # 파일 끝에 도달하면 종료
                        if "meshbuilder" in line.lower():
                            # 첫 30줄 내에 'meshbuilder'가 포함되어 있으면 False 반환
                            return False
                    except Exception as ex:
                        print(ex)
                        return False

            return True

        return False
    
    def LoadRoute(self, path: str, encoding: str, trainPath: str,
                  objectPath: str, soundPath: str,
                  previewOnly: bool, route: object) -> bool:
        if encoding is None:

            encoding = 'utf-8'

        self.LastException = None
        self.Cancel = False
        self.CurrentProgress = 0.0
        self.IsLoading = True
        if isinstance(route, CurrentRoute):
            self.CurrentRoute = route
        else:
            raise TypeError("route must be a CurrentRoute instance.")
        print(f"Loading route file: {path}")
        print(f"INFO: Route file hash {Path.get_checksum(path)}");

        #First, check the format of the route file
        #RW routes were written for BVE1 / 2, and have a different command syntax
        isrw = path.lower().endswith(".rw")
        print(f"Route file format is: {'RW' if isrw else 'CSV'}\n")
        try:
            parser = Parser()
            parser.ParseRoute(path, isrw, encoding,
                              trainPath, objectPath,soundPath,
                              previewOnly ,self)
            self.IsLoading = False
            return True

        except Exception as ex:
            route = None
            print("An unexpected error occured whilst attempting to load the following routefile: " + path)
            self.IsLoading = False
            self.LastException = ex
            print("Error loading route:", ex)
            traceback.print_exc()
            return False
    def Unload(self):
        self.Cancel = True
        while self.IsLoading:
            time.sleep(0.1)
