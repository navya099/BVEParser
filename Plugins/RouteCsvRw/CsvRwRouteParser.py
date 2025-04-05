from RouteManager2.CurrentRoute import CurrentRoute
from .RouteData import RouteData

class Parser:
    def __init__(self):
        self.ObjectPath = ''
        self.SoundPath = ''
        self.TrainPath = ''
        self.CompatibilityFolder = ''
        self.IsRW = None
        self.IsHmmsim = None
        self.CurrentRoute = CurrentRoute()
        self.Plugin = None  # 여긴 직접 생성 X
        self.AllowTrackPositionArguments = False
        self.SplitLineHack = True
        
    def ParseRoute(self, FileName, isRW, Encoding, trainPath, objectPath, soundPath, PreviewOnly, hostPlugin):
        self.Plugin = hostPlugin
        currentRoute = self.Plugin.CurrentRoute
        self.ObjectPath = objectPath
        self.SoundPath = soundPath
        self.TrainPath = trainPath
        self.IsRW = isRW

        freeObjCount = 0
        railtypeCount = 0
        Data = RouteData(PreviewOnly)

        Data = self.ParseRouteForData(FileName, Encoding, Data, PreviewOnly)

        if self.Plugin.Cancel:
            self.Plugin.IsLoading = False
            return
        Data = self.ApplyRouteData(FileName, Data, PreviewOnly)
		
    @staticmethod
    def ParseRouteForData(FileName, Encoding,Data,PreviewOnly):
        pass

    @staticmethod
    def ApplyRouteData(FileName, Data, PreviewOnly):
        pass
