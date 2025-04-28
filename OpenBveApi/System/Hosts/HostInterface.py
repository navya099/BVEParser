from abc import ABC, abstractmethod


class HostInterface(ABC):
    def __init__(self):
        self.MonoRuntime: bool = True if type("Mono.Runtime") else False
        self.cachedPlatform: 'HostPlatform' = 99 # value not in enum
        # Returns the current host platform

    @abstractmethod
    def register_sound(self, path: str, handle: 'SoundHandle') -> bool:
        """Register a sound to the host platform."""
        handle = None  # handle is initialized to None
        return False  # Returns False by defaul

