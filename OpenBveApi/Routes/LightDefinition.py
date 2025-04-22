from dataclasses import dataclass
from typing import Optional

from OpenBveApi.Math.Vectors.Vector3 import Vector3


@dataclass
class LightDefinition:
    ambientColor: Optional['Color24'] = None
    diffuseColor: Optional['Color24'] = None
    lightPosition: Optional['Vector3'] = None
    time: int = 0
    cabBrightness: float = 0.0