from abc import ABC, abstractmethod
import random


class TrainManagerBase(ABC):
    # 클래스 속성 (static 속성)
    currentHost: 'HostInterface' = None
    Renderer: 'BaseRenderer' = None
    CurrentRoute: 'CurrentRoute' = None
    FileSystem: 'FileSystem' = None
    Toppling: bool = None
    Derailments: bool = None
    RandomNumberGenerator: random.Random = random.Random()
    PlayerTrain: 'TrainBase' = None
    CurrentOptions: 'BaseOptions' = None
    PluginError: str = None

    def __init__(self, host: 'HostInterface', renderer: 'BaseRenderer',
                 Options: 'BaseOptions', fileSystem: 'FileSystem'):
        self.Trains: list['TrainBase'] = []
        self.TFOs: list['AbstractTrain'] = []
        TrainManagerBase.currentHost = host
        TrainManagerBase.Renderer = renderer
        TrainManagerBase.CurrentOptions = Options
        TrainManagerBase.FileSystem = fileSystem  # 클래스 변수에 설정




