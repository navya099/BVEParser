from OpenBveApi.Runtime.Route.Station import Station


from dataclasses import dataclass, field
from typing import Optional, List
from OpenBveApi.Math.Vectors import Vector3
from Plugins.RouteCsvRw.Structures.Route import StationStop


class RouteStation(Station):
    def __init__(self):
        super().__init__()
        self.PassengerRatio: float = 100.0
        self.TimetableDaytimeTexture = None
        self.TimetableNighttimeTexture = None
        self.SoundOrigin = None  # Vector3
        self.ArrivalSoundBuffer = None  # SoundHandle
        self.DepartureSoundBuffer = None  # SoundHandle
        self.SafetySystem = None
        self.Stops: list = []
        self.AccessibilityAnnounced: bool = False
        self.Dummy: bool = False
        self.Key: str = ""

