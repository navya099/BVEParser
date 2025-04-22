from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Rail:
    Accuracy: float
    AdhesionMultiplier: float
    RailStarted: bool = False
    RailStartRefreshed: bool = False
    RailStart: Optional['Vector2'] = None
    RailEnded: bool = False
    RailEnd: Optional['Vector2'] = None
    CurveCant: float = 0.0
    IsDriveable: bool = False

    @property
    def MidPoint(self) -> Optional['Vector2']:
        if self.RailStart and self.RailEnd:
            return self.RailEnd - self.RailStart
        return None
