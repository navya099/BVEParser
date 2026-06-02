from abc import ABC, abstractmethod
import datetime
import os

from OpenBveApi.Objects.ObjectTypes.UnifiedObject import UnifiedObject
from OpenBveApi.System.HostsPlugins import PluginLoader


class HostInterface(ABC):
    def __init__(self):
        self.MonoRuntime: bool = True if type("Mono.Runtime") else False
        self.cachedPlatform: 'HostPlatform' = 99  # value not in enum
        # Returns the current host platform
        self.StaticObjectCache: dict = {}
        self.AnimatedObjectCollectionCache: dict = {}

    @abstractmethod
    def LoadObject(self, path: str, encoding: str) -> tuple[bool, UnifiedObject]:

        key = (path, False, datetime.datetime.fromtimestamp(os.path.getmtime(path)))

        staticObject = self.StaticObjectCache.get(key)
        if staticObject is not None:
            Object = staticObject.Clone()
            return True, Object

        animatedObject = self.AnimatedObjectCollectionCache.get(path)
        if animatedObject is not None:
            Object = animatedObject.Clone()
            return True, Object

        Object = None
        return False, Object

    @abstractmethod
    def register_sound(self, path: str, handle: 'SoundHandle') -> bool:
        """Register a sound to the host platform."""
        handle = None  # handle is initialized to None
        return False  # Returns False by defaul

