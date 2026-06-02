from OpenBveApi.Objects.ObjectTypes.UnifiedObject import UnifiedObject
from OpenBveApi.System.Hosts.HostInterface import HostInterface
from OpenBveApi.Objects.Mesh import Mesh


class StaticObject(UnifiedObject):
    def __init__(self, Host: HostInterface):
        super().__init__()
        self.IsOptimized: bool = True
        self.Mesh: Mesh = Mesh()
        self.StartingTrackDistance: float = 0.0
        self.EndingTrackDistance: float = 0.0
        self.Dynamic: bool = True
        self.Author: str = ''
        self.Copyright: str = ''
        self.currentHost: HostInterface = Host

    def CreateObject(self, Position: 'Vector3', WorldTransformation: 'Transformation',
                     LocalTransformation: 'Transformation', SectionIndex: int, StartingDistance: float,
                     EndingDistance: float, TrackPosition: float, Brightness: float, DuplicateMaterials: bool = False):
        """
        Creates the object within the world.
        """
        pass

    def OptimizeObject(self, PreserveVertices: bool, Threshold: int, VertexCulling: bool):
        """
        Call this method to optimize the object.
        """
        pass

    def Clone(self) -> 'UnifiedObject':
        """
        Creates a clone of this object.
        """
        pass

    def Mirror(self) -> 'UnifiedObject':
        """
        Creates a mirrored clone of this object.
        """
        pass

    def Transform(self, NearDistance: float, FarDistance: float) -> 'UnifiedObject':
        """
        Creates a transformed clone of this object.
        """
        pass

    def TransformLeft(self, NearDistance: float, FarDistance: float) -> 'UnifiedObject':
        """
        Creates a left-handed transformed clone of this object.
        """
        pass

    def TransformRight(self, NearDistance: float, FarDistance: float) -> 'UnifiedObject':
        """
        Creates a right-handed transformed clone of this object.
        """
        pass


