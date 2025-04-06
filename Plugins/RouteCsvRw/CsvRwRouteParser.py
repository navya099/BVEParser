from RouteManager2.CurrentRoute import CurrentRoute
from .RouteData import RouteData
from .Preprocess import PreprocessMixin
from OpenBveApi.Objects.ObjectInterface import ObjectInterface, CompatabilityHacks

class Parser(PreprocessMixin):
    EnabledHacks = CompatabilityHacks()
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
		
    def ParseRouteForData(self, FileName, Encoding,Data,PreviewOnly):
        with open(FileName, 'r', encoding=Encoding) as f:
            lines: List[str] = f.readlines()

        Expressions = self.PreprocessSplitIntoExpressions(FileName, lines, True)
        Expressions = self.PreprocessChrRndSub(FileName, Encoding, Expressions)
        test(Expressions)

    @staticmethod
    def ApplyRouteData(FileName, Data, PreviewOnly):
        pass

def test(Expressions):
    with open("C:/TEMP/expressions_all.txt", "w", encoding="utf-8") as f:
        for i in range(len(Expressions)):
            f.write(
                f"{i} , {Expressions[i].Line} , {Expressions[i].Text}, {Expressions[i].TrackPositionOffset}, {Expressions[i].File}\n")
    pass