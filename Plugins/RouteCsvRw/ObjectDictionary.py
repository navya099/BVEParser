from typing import Dict, Union

from OpenBveApi.Objects.ObjectTypes.StaticObject import StaticObject
from loggermodule import logger

from OpenBveApi.Objects.ObjectTypes.UnifiedObject import UnifiedObject
from OpenBveApi.Routes.BackgroundHandle import BackgroundHandle
from RouteManager2.SignalManager.SignalObject import SignalObject


class ObjectDictionary(Dict[int, UnifiedObject]):
    def __init__(self):
        super().__init__()

    def Add(self, key: int, obj: Union[UnifiedObject, StaticObject], *args):
        Type = "object"
        overwriteWarning = True

        # 추가 인자 처리
        if len(args) == 1:
            if isinstance(args[0], str):
                Type = args[0]
            elif isinstance(args[0], bool):
                overwriteWarning = args[0]
        elif len(args) == 2:
            Type = args[0]
            overwriteWarning = args[1]

        if key in self:
            self[key] = obj
            if overwriteWarning:
                logger.error(f'The {Type} with an index of {key} has been declared twice: '
                             f"The most recent declaration will be used.")
        else:
            self[key] = obj

class SignalDictionary(Dict[int, SignalObject]):
    pass

class BackgroundDictionary(Dict[int, BackgroundHandle]):
    pass

class PoleDictionary(Dict[int, ObjectDictionary]):
    def Add(self, key: int, obj_dict: ObjectDictionary):
        if key in self:
            self[key] = obj_dict
            logger.error(f"The Pole with an index of {key} has been declared twice: "
                  f"The most recent declaration will be used.")
        else:
            self[key] = obj_dict
