from dataclasses import dataclass, field
from typing import Optional

from OpenBveApi.Math.Vectors.Vector2 import Vector2


@dataclass
class Rail:
    Accuracy: float
    AdhesionMultiplier: float
    RailStarted: bool = False
    RailStartRefreshed: bool = False
    RailStart: Vector2 = field(default_factory=Vector2)
    RailEnded: bool = False
    RailEnd: Vector2 = field(default_factory=Vector2)
    CurveCant: float = 0.0
    IsDriveable: bool = False
    raaaaa: bool = False
    @property
    def MidPoint(self) -> Optional['Vector2']:
        if self.RailStart and self.RailEnd:
            return self.RailEnd - self.RailStart
        return None
