from RouteManager2.Climate.Atmosphere import Atmosphere
from RouteManager2.RouteInformation import RouteInformation
from OpenBveApi.Routes.Track import Track
from RouteManager2.Stations.RouteStation import RouteStation


class CurrentRoute:
    def __init__(self, host: 'HostInterface' = None, renderer: 'BaseRenderer' = None):
        self.currentHost: 'HostInterface' = None
        self.renderer: 'BaseRenderer' = None
        self.Information: RouteInformation = RouteInformation()
        self.Comment: str = ''
        self.Image: str = ''
        self.Tracks: dict[int, Track] = {0: Track()}
        self.Sections: list['Section'] = []
        self.Stations: list[RouteStation] = []
        self.InitialStationName: str = ''
        self.InitialStationTime: int = -1
        self.BogusPreTrainInstructions: list['BogusPreTrainInstruction'] = []
        self.PointsOfInterest: list['PointOfInterest'] = []
        self.CurrentBackground: 'BackgroundHandle' = None
        self.TargetBackground: 'BackgroundHandle' = None
        self.NoFogStart: float = 800.0
        self.NoFogEnd: float = 1600.0
        self.PreviousFog: 'Fog' = None
        self.CurrentFog: 'Fog' = None
        self.NextFog: 'Fog' = None
        self.Atmosphere: Atmosphere = Atmosphere()
        self.BufferTrackPositions: list['BufferStop'] = []
        self.SecondsSinceMidnight: float = 0.0
        self.UnitOfLength: list[float] = [1.0]
        self.BlockLength: float = 25.0
        self.AccurateObjectDisposal: 'ObjectDisposalMode' = None
        self.Switches: dict['Guid', 'Switch'] = {}

