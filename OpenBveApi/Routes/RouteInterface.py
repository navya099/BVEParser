from abc import ABC, abstractmethod

class RouteInterface(ABC):
    def __init__(self):
        self.IsLoading = False
        self.LastException = None
        self.Cancel = False
        self.CurrentProgress = 0.0

    @abstractmethod
    def CanLoadRoute(self, path: str) -> bool:
        """Checks whether the plugin can load the specified route."""
        pass

    @abstractmethod
    def LoadRoute(self, path: str, encoding: str, trainPath: str,
                  objectPath: str, soundPath: str,
                  previewOnly: bool, route: object) -> bool:
        """Loads the specified route and returns success."""
        pass

    def Load(self, host, fileSystem, options, trainManagerReference):
        """Optional override: Called when plugin is loaded."""
        pass

    def Unload(self):
        """Optional override: Called when plugin is unloaded."""
        pass
