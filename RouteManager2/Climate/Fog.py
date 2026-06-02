from dataclasses import dataclass
from OpenBveApi.Colors import Color24  # Color24는 직접 포팅 필요할 수 있음


@dataclass
class Fog:
    start: float
    end: float
    color: Color24
    track_position: float
    is_linear: bool = True
    density: float = 0.0
