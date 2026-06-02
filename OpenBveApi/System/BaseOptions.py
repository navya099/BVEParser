from abc import ABC, abstractmethod
from OpenBveApi.Routes.ObjectDisposalMode import ObjectDisposalMode


class BaseOptions(ABC):
    def __init__(self):
        self.TrainDownloadLocation: str = ''
        self.EnableBveTsHacks = False
        self.UnitOfSpeed: str = "km/h"
        self.ObjectDisposalMode = ObjectDisposalMode
        self.SpeedConversionFactor = 0.0
