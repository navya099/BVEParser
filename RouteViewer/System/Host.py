from OpenBveApi.Objects.ObjectTypes.UnifiedObject import UnifiedObject
from OpenBveApi.System.Hosts.HostInterface import HostInterface
from OpenBveApi.System.TextEncoding import TextEncoding
from OpenBveApi.Objects.ObjectTypes.StaticObject import StaticObject
from OpenBveApi.Objects.ObjectTypes.AnimatedObjectCollection import AnimatedObjectCollection
import os


class Host(HostInterface):
    def __init__(self):
        super().__init__()

    def LoadObject(self, path: str, encoding: str) -> tuple[bool, UnifiedObject]:
        # Object 초기화하지 말고
        '''
        result, Object = super().LoadObject(path, encoding)

        if result:
            # 성공하면 obj를 반환
            return True, Object
        if os.path.exists(path) or os.path.isdir(path):
            encoding = TextEncoding.get_system_encoding_from_file(path, encoding)

            if isinstance(Object, StaticObject):
                staticObject = Object
                key = (path, False, os.path.getmtime(path))
                self.StaticObjectCache[key] = staticObject
                return True, StaticObject(None) # 미구현

            if isinstance(Object, AnimatedObjectCollection):
                aoc = Object
                key = path
                self.AnimatedObjectCollectionCache[key] = aoc
                return True, StaticObject(None) # 미구현
            '''
        return True, None  # 미구현
    def register_sound(self, path: str, handle: 'SoundHandle') -> bool:
        """Register a sound to the host platform."""
        handle = None  # handle is initialized to None
        return False  # Returns False by defaul
