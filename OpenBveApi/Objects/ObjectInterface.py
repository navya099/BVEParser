from abc import ABC, abstractmethod
from typing import List

from OpenBveApi.Objects.ObjectTypes.UnifiedObject import UnifiedObject


class CompatabilityHacks:
    """Controls various hacks used with older content."""
    def __init__(self):
        self.BveTsHacks = None
        self.CylinderHack = None
        self.BlackTransparency = None
        self.DisableSemiTransparentFaces = None
        self.AggressiveRwBrackets = None


class ObjectInterface(ABC):
    """Represents the interface for loading objects. Plugins must implement this interface if they wish to expose objects."""

    @property
    @abstractmethod
    def SupportedAnimatedObjectExtensions(self) -> List[str]:
        """Array of supported animated object extensions."""
        pass

    @property
    @abstractmethod
    def SupportedStaticObjectExtensions(self) -> List[str]:
        """Array of supported static object extensions."""
        pass

    @abstractmethod
    def CanLoadObject(self, path: str) -> bool:
        """Checks whether the plugin can load the specified object."""
        pass

    @abstractmethod
    def LoadObject(self, path: str, encoding: str) -> tuple[bool, UnifiedObject]:
        """Loads the specified object."""
        pass

    def Load(self, host, file_system):
        """Called when the plugin is loaded."""
        pass

    def Unload(self):
        """Called when the plugin is unloaded."""
        pass

    def SetCompatibilityHacks(self, enabled_hacks: CompatabilityHacks):
        """Sets various hacks to workaround buggy objects."""
        pass

    def SetObjectParser(self, parser_type):
        """Sets the parser type to use."""
        pass
