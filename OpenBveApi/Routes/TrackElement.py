from OpenBveApi.Math.Vectors.Vector3 import Vector3
from dataclasses import dataclass, field
from typing import List


@dataclass
class TrackElement:
    InvalidElement: bool = False
    StartingTrackPosition: float = 0.0
    CurveRadius: float = 0.0
    CurveCant: float = 0.0
    CurveCantTangent: float = 0.0
    AdhesionMultiplier: float = 1.0
    RainIntensity: int = 0
    SnowIntensity: int = 0
    CsvRwAccuracyLevel: float = 2.0
    Pitch: float = 0.0
    WorldPosition: Vector3 = field(default_factory=lambda: Vector3.Zero())
    WorldDirection: Vector3 = field(default_factory=lambda: Vector3.Forward())
    WorldUp: Vector3 = field(default_factory=lambda: Vector3.Down())
    WorldSide: Vector3 = field(default_factory=lambda: Vector3.Right())
    Events: List['GeneralEvent'] = field(default_factory=list)
    IsDriveable: bool = False
    ContainsSwitch: bool = False
