from .Structures.Block import Block
from .Structures.Route.Rail import Rail
from Plugins.RouteCsvRw.Structures.StructureData import StructureData
from OpenBveApi.Routes.TrackElement import TrackElement
from .Structures.Route.RailCycle import RailCycle
from OpenBveApi.Math.Vectors.Vector2 import Vector2

import copy


class RouteData:
    def __init__(self, preview_only):
        self.TrackPosition: float = 0.0
        self.BlockInterval: float = 25.0
        self.UnitOfSpeed: float = 0.0
        self.SignedCant: bool = False
        self.FogTransitionMode: bool = False
        self.Structure: StructureData = StructureData()
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
        self.Blocks[0].Rails[0] = Rail(2.0, 1.0, RailStarted=True)
        self.Blocks[0].RailType = []
        self.Blocks[0].CurrentTrackState = TrackElement(StartingTrackPosition=0.0)
        self.Blocks[0].RailCycles = [RailCycle()]
        self.Blocks[0].RailCycles[0].RailCycleIndex = -1

    def create_missing_blocks(self, toindex: int, preview_only: bool):
        if toindex >= len(self.Blocks):
            for i in range(len(self.Blocks), toindex + 1):
                self.Blocks.append(Block(preview_only))
                if not preview_only:
                    self.Blocks[i].Cycle = self.Blocks[i - 1].Cycle
                    self.Blocks[i].Height = 0.0
                self.Blocks[i].RailCycles = self.Blocks[i - 1].RailCycles
                self.Blocks[i].RailType = [0] * len(self.Blocks[i - 1].RailType)
                if not preview_only:
                    for j in range(len(self.Blocks[i].RailType)):
                        rc = -1
                        if len(self.Blocks[i].RailCycles) > j:
                            rc = self.Blocks[i].RailCycles[j].RailCycleIndex
                        if rc != -1 and len(self.Structure.RailCycles) > rc and \
                            len(self.Structure.RailCycles[rc]) > 1:
                            cc = self.Blocks[i].RailCycles[j].CurrentCycle
                            if cc == len(self.Structure.RailCycles[rc]) - 1:
                                self.Blocks[i].RailType[j] = self.Structure.RailCycles[rc][0]
                                self.Blocks[i].RailCycles[j].CurrentCycle = 0
                            else:
                                cc += 1
                                self.Blocks[i].RailType[j] = self.Structure.RailCycles[rc][cc]
                                self.Blocks[i].RailCycles[j].CurrentCycle += 1
                        else:
                            self.Blocks[i].RailType[j] = self.Blocks[i - 1].RailType[j]

                for j in range(len(self.Blocks[i - 1].Rails)):
                    key = list(self.Blocks[i - 1].Rails.keys())[j]

                    rail = Rail(self.Blocks[i - 1].Rails[key].Accuracy,
                                self.Blocks[i - 1].Rails[key].AdhesionMultiplier,
                                RailStarted=self.Blocks[i - 1].Rails[key].RailStarted,
                                RailStart=copy.deepcopy(self.Blocks[i - 1].Rails[key].RailStart),
                                RailStartRefreshed=False,
                                RailEnded=False,
                                RailEnd=copy.deepcopy(self.Blocks[i - 1].Rails[key].RailStart),
                                IsDriveable=self.Blocks[i - 1].Rails[key].IsDriveable
                                )
                    self.Blocks[i].Rails[key] = rail
                if not preview_only:
                    self.Blocks[i].RailPole = self.Blocks[i - 1].RailPole.copy()

                self.Blocks[i].Pitch = self.Blocks[i - 1].Pitch

                self.Blocks[i].CurrentTrackState = copy.deepcopy(self.Blocks[i - 1].CurrentTrackState)
                self.Blocks[i].Turn = 0.0


