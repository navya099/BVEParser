from OpenBveApi.Objects.ObjectTypes.UnifiedObject import UnifiedObject
from OpenBveApi.System.Hosts.HostInterface import HostInterface
from OpenBveApi.System.TextEncoding import TextEncoding
from RouteViewer.ProgramR import Program
import os


class Host(HostInterface):
    def __init__(self):
        super().__init__()

    def LoadObject(self, path: str, encoding: str) -> tuple[bool, UnifiedObject]:
        Object = UnifiedObject()
        if super().LoadObject(path, encoding):
            return True, Object
        else:
            return False, Object

    def register_sound(self, path: str, handle: 'SoundHandle') -> bool:
        """Register a sound to the host platform."""
        handle = None  # handle is initialized to None
        return False  # Returns False by defaul
