from .Structures.Block import Block
from .Structures.Route.Rail import Rail
from Plugins.RouteCsvRw.Structures.StructureData import StructureData
from OpenBveApi.Routes.TrackElement import TrackElement
from .Structures.Route.RailCycle import RailCycle


class RouteData:
    def __init__(self, preview_only):
        self.TrackPosition: float = 0.0
        self.BlockInterval: float = 25.0
        self.UnitOfSpeed: float = 0.0
        self.SignedCant: bool = False
        self.FogTransitionMode: bool = False
        self.Structure: 'StructureData' = StructureData()
        self.Signals: 'SignalDictionary' = None
        self.CompatibilitySignals: list['CompatibilitySignalObject'] = []
        self.TimetableDaytime: list['Texture'] = []
        self.TimetableNighttime: list['Texture'] = []
        self.Backgrounds: 'BackgroundDictionary' = None
        self.SignalSpeeds: list[float] = []
        self.Blocks: list[Block] = []
        self.Markers: 'Marker' = None
        self.RequestStops: list['StopRequest'] = []
        self.FirstUsedBlock: int = -1
        self.ValueBasedSections: bool = False
        self.TurnUsed: bool = False
        self.line_ending_fix: bool = False
        self.ignore_pitch_roll: bool = False
        self.SwitchUsed: bool = False
        self.ScriptedTrainFiles: list[str] = []
        self.RailKeys: dict[str, int] = {}
        # Blocks[0]을 추가하고 설정하는 코드
        self.Blocks.append(Block(preview_only))
        self.Blocks[0].Rails[0] = Rail(2.0, 1.0)
        self.Blocks[0].RailType = 0
        self.Blocks[0].CurrentTrackState = TrackElement(StartingTrackPosition=0.0)
        self.Blocks[0].RailCycles = [RailCycle()]
        self.Blocks[0].RailCycles[0].RailCycleIndex = -1

