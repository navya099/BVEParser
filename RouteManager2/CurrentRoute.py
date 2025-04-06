from RouteManager2.Climate.Atmosphere import Atmosphere
from RouteManager2.RouteInformation import RouteInformation
from OpenBveApi.Routes.Track import Track

class CurrentRoute:
    def __init__(self):
        self.currentHost = None
        self.renderer = None
        self.Information = RouteInformation()
        self.Comment = ''
        self.Image = ''
        self.Tracks = {0:Track()}
        self.Sections = None
        self.Stations = None
        self.BogusPreTrainInstructions = None
        self.PointsOfInterest = None
        self.CurrentBackground = None
        self.TargetBackground = None
        self.NoFogStart = f'800.:0f'
        self.NoFogEnd = f'1600.:0f'
        self.PreviousFog = None
        self.CurrentFog = None
        self.NextFog = None
        self.Atmosphere = Atmosphere()

    
