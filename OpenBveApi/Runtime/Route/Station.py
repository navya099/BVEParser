from dataclasses import dataclass
from enum import Enum


class Station:
    def __init__(self):
        self.Name: str = ""
        self.ArrivalTime: float = 0.0
        self.DepartureTime: float = 0.0
        self.ForceStopSignal: bool = False
        self.OpenLeftDoors: bool = False
        self.OpenRightDoors: bool = False
        self.DefaultTrackPosition: float = 0.0
        self.StopPosition: float = 0.0
        self.StopMode = StationStopMode.AllStop
        self.Type = StationType.Normal
        self.ReopenDoor: float = 0.0
        self.ReopenStationLimit: int = 0
        self.InterferenceInDoor: float = 0.0
        self.MaxInterferingObjectRate: int = 0
        self.JumpIndex: int = -1
        self.ExpectedTimeStopped: float = 0.0

    @property
    def StopTime(self) -> float:
        if self.StopMode == StationStopMode.AllPass:
            return 0.0
        if self.ExpectedTimeStopped <= 0 or self.ExpectedTimeStopped > 3600:
            return 15.0
        return self.ExpectedTimeStopped

    @StopTime.setter
    def StopTime(self, value: float):
        self.ExpectedTimeStopped = value


class StationStopMode(Enum):
    AllStop = 0  # All trains stop at this station
    AllPass = 1  # All trains pass this station
    PlayerStop = 2  # Player train stops, AI does not
    PlayerPass = 3  # Player passes, AI stops
    AllRequestStop = 4  # Random request stop for all trains
    PlayerRequestStop = 5  # Random request stop for player train only


class StationType(Enum):
    Normal = 0  # This station is a normal station
    ChangeEnds = 1  # This station triggers the change end mechanic on departure
    Terminal = 2  # This station is the terminal station
    RequestStop = 3  # this station is a request stop
    Jump = 4  # This station triggers the jump mechanic on departure
