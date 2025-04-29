from abc import ABC, abstractmethod
from typing import Optional
from loggermodule import logger

# 필요한 타입들은 외부에 정의되어야 합니다
# 예시로 Vector3, Transformation은 별도로 만들어야 합니다
# class Vector3: ...
# class Transformation: ...

class UnifiedObject(ABC):
    """
    A unified object is the abstract class encompassing all object types within the sim.
    """
    def CreateObject1(self, Position: 'Vector3', StartingDistance: float, EndingDistance: float, TrackPosition: float):
        self.CreateObject(Position, 'Transformation.NullTransformation', 'Transformation.NullTransformation', -1, StartingDistance, EndingDistance, TrackPosition, 1.0)

    def CreateObject2(self, Position: 'Vector3', WorldTransformation: 'Transformation', StartingDistance: float, EndingDistance: float, TrackPosition: float):
        self.CreateObject(Position, WorldTransformation, 'Transformation.NullTransformation', -1, StartingDistance, EndingDistance, TrackPosition, 1.0)

    @abstractmethod
    def CreateObject(self, Position: 'Vector3', WorldTransformation: 'Transformation', LocalTransformation: 'Transformation', SectionIndex: int, StartingDistance: float, EndingDistance: float, TrackPosition: float, Brightness: float, DuplicateMaterials: bool = False):
        """
        Creates the object within the world.
        """
        pass

    @abstractmethod
    def OptimizeObject(self, PreserveVertices: bool, Threshold: int, VertexCulling: bool):
        """
        Call this method to optimize the object.
        """
        pass

    @abstractmethod
    def Clone(self) -> 'UnifiedObject':
        """
        Creates a clone of this object.
        """
        pass

    @abstractmethod
    def Mirror(self) -> 'UnifiedObject':
        """
        Creates a mirrored clone of this object.
        """
        pass

    @abstractmethod
    def Transform(self, NearDistance: float, FarDistance: float) -> 'UnifiedObject':
        """
        Creates a transformed clone of this object.
        """
        pass

    @abstractmethod
    def TransformLeft(self, NearDistance: float, FarDistance: float) -> 'UnifiedObject':
        """
        Creates a left-handed transformed clone of this object.
        """
        pass

    @abstractmethod
    def TransformRight(self, NearDistance: float, FarDistance: float) -> 'UnifiedObject':
        """
        Creates a right-handed transformed clone of this object.
        """
        pass
