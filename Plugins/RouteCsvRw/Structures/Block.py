from typing import List, Dict

from OpenBveApi.Routes.LightDefinition import LightDefinition
from Plugins.RouteCsvRw.Structures.Route.Rail import Rail
from Plugins.RouteCsvRw.Structures.Route.RailCycle import RailCycle
from OpenBveApi.Routes.TrackElement import TrackElement


class Block:
    def __init__(self, preview_only):
        self.Background: int = 0
        self.BrightnessChanges: List['Brightness'] = []
        self.Fog: 'Fog' = None
        self.FogDefined: bool = False
        self.Cycle: List[int] = []
        self.RailCycles: List[RailCycle] = []
        self.Height: float = 0.0
        self.Rails: Dict[int, 'Rail'] = {}
        self.Switches: List['Switch'] = []
        self.RailType: List[int] = []
        self.RailWall: Dict[int, 'WallDike'] = {}
        self.RailDike: Dict[int, 'WallDike'] = {}
        self.RailPole: List['Pole'] = []
        self.RailFreeObj: Dict[int, List['FreeObj']] = {}
        self.GroundFreeObj: List['FreeObj'] = []
        self.Forms: List['Form'] = []
        self.Cracks: List['Crack'] = []
        self.Signals: List['Signal'] = []
        self.Sections: List['Section'] = []
        self.Limits: List['Limit'] = []
        self.StopPositions: List['Stop'] = []
        self.SoundEvents: List['Sound'] = []
        self.Transponders: List['Transponder'] = []
        self.DestinationChanges: List['DestinationEvent'] = []
        self.PointsOfInterest: List['PointOfInterest'] = []
        self.HornBlows: List['HornBlowEvent'] = []
        self.CurrentTrackState: TrackElement = TrackElement()
        self.Pitch: float = 0.0
        self.Turn: float = 0.0
        self.Station: int = -1
        self.StationPassAlarm: bool = False
        self.SnowIntensity: int = 0
        self.RainIntensity: int = 0
        self.WeatherObject: int = 0
        self.LightDefinition: LightDefinition = None if preview_only else LightDefinition()
        self.DynamicLightDefinition: int = -1
        self.LightingChanges: List['LightingChange'] = []
        self.PatternObjs: Dict[int, 'PatternObj'] = {}