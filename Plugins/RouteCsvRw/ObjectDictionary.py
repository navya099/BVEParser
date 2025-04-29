from typing import Dict
from loggermodule import logger

from OpenBveApi.Objects.ObjectTypes.UnifiedObject import UnifiedObject
from OpenBveApi.Routes.BackgroundHandle import BackgroundHandle
from RouteManager2.SignalManager.SignalObject import SignalObject


class ObjectDictionary(Dict[int, UnifiedObject]):
    def __init__(self):
        super().__init__()

    def Add(self, key: int, unified_object: UnifiedObject, Type: str, overwriteWarning: bool = False):
        if key in self:
            self[key] = unified_object
            logger.error(f"The {Type} with an index of {key} has been declared twice: "
                         f"The most recent declaration will be used.")
            if overwriteWarning:
                # Poles contain 4 default objects
                # Don't complain about overwriting these
                logger.error(f"The object with an index of {key} has been declared twice: "
                             f"The most recent declaration will be used.")
        else:
            self[key] = unified_object

class SignalDictionary(Dict[int, SignalObject]):
    pass

class BackgroundDictionary(Dict[int, BackgroundHandle]):
    pass

class PoleDictionary(Dict[int, ObjectDictionary]):
    def Add(self, key: int, _dict: ObjectDictionary):
        if key in self:
            self[key] = _dict
            logger.error(f"The Pole with an index of {key} has been declared twice: "
                         f"The most recent declaration will be used.")
        else:
            self[key] = _dict
