from abc import ABC, abstractmethod
from OpenBveApi.Routes.ObjectDisposalMode import ObjectDisposalMode

class BaseOptions(ABC):
    def __init__(self):
        self.EnableBveTsHacks = False

        self.ObjectDisposalMode = ObjectDisposalMode()
