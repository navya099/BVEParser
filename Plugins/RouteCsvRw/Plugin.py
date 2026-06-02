import os
import random

import chardet
from loggermodule import logger
from RouteManager2.CurrentRoute import CurrentRoute
from TrainManager.TrainManager import TrainManagerBase
from OpenBveApi.Routes.RouteInterface import RouteInterface
from OpenBveApi.System.BaseOptions import BaseOptions
from OpenBveApi.System.Path import Path
import traceback
import time


def detect_encoding(path):
    # 파일을 열어 일부를 읽어서 인코딩을 감지합니다
    with open(path, 'rb') as file:
        raw_data = file.read(10000)  # 처음 10000 바이트를 읽어봄
        result = chardet.detect(raw_data)  # 인코딩 탐지
        return result['encoding']


class Plugin(RouteInterface):
    CurrentHost: 'HostInterface' = None
    CurrentRoute: CurrentRoute = None
    RandomNumberGenerator: random.Random = random.Random()
    FileSystem: 'FileSystem' = None
    CurrentOptions: BaseOptions = None
    TrainManager: TrainManagerBase = None

    def __init__(self):
        super().__init__()

    def load(self, host: 'HostInterface', file_system: 'FileSystem', options: BaseOptions,
             train_manager_reference: object):
        Plugin.CurrentHost = host
        Plugin.FileSystem = file_system
        Plugin.CurrentOptions = options

        # Check if train_manager_reference is of type TrainManagerBase
        if isinstance(train_manager_reference, TrainManagerBase):
            Plugin.TrainManager = train_manager_reference

        # Set TrainDownloadLocation to an empty string
        Plugin.CurrentOptions.TrainDownloadLocation = ""

    def CanLoadRoute(self, path: str) -> bool:
        if not path or not os.path.exists(path):
            return False
        if path.lower().endswith(".rw"):
            return True
        if path.lower().endswith(".csv"):
            encoding = detect_encoding(path)  # 파일 인코딩 탐지
            with open(path, 'r', encoding=encoding) as file:
                for i in range(30):
                    try:
                        line = file.readline()
                        if not line:
                            break  # 파일 끝에 도달하면 종료
                        if "meshbuilder" in line.lower():
                            # 첫 30줄 내에 'meshbuilder'가 포함되어 있으면 False 반환
                            return False
                    except Exception as ex:

                        logger.critical(ex)
                        return False

            return True

        return False

    def LoadRoute(self, path: str, encoding: str, train_path: str,
                  object_path: str, sound_path: str,
                  preview_only: bool, route: object) -> bool:
        Plugin.CurrentOptions.TrainDownloadLocation = ''
        if encoding is None:
            encoding = 'utf-8'

        self.LastException = None
        self.Cancel = False
        self.CurrentProgress = 0.0
        self.IsLoading = True
        Plugin.CurrentRoute = route

        logger.info(f"Loading route file: {path}")
        logger.info(f"INFO: Route file hash {Path.get_checksum(path)}")
        logger.info(f'Encoding: {encoding}')
        # First, check the format of the route file
        # RW routes were written for BVE1 / 2, and have a different command syntax
        isrw = path.lower().endswith(".rw")
        logger.info(f"Route file format is: {'RW' if isrw else 'CSV'}\n")
        try:
            from .CsvRwRouteParser import Parser
            parser = Parser()
            parser.parse_route(path, isrw, encoding,
                               train_path, object_path, sound_path,
                               preview_only, self)
            self.IsLoading = False
            return True

        except Exception as ex:
            route = None
            logger.critical("An unexpected error occured whilst attempting to load the following routefile: " + path)
            self.IsLoading = False
            self.LastException = ex
            logger.critical(ex)
            logger.critical(traceback.print_exc())
            return False

    def Unload(self):
        self.Cancel = True
        while self.IsLoading:
            time.sleep(0.1)
