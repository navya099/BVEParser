class RouteInformation:
    def __init__(self):
        self.RouteBriefing: str = ''
        self.RouteFile: str = ''
        self.TrainFolder: str = ''
        self.FilesNotFound: str = ''
        self.ErrorsAndWarnings: str = ''
        self.GradientMinTrack: float = 0.0
        self.GradientMaxTrack: float = 0.0
        self.DefaultTimetableDescription: str = ''
        self.RouteMinX: float = 0.0
        self.RouteMinY: float = 0.0
        self.RouteMinZ: float = 0.0
        self.RouteMaxZ: float = 0.0

    def LoadInformation(self):
        pass


