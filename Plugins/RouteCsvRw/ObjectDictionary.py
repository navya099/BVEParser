from typing import Dict

from OpenBveApi.Objects.ObjectTypes.UnifiedObject import UnifiedObject
from OpenBveApi.Routes.BackgroundHandle import BackgroundHandle
from RouteManager2.SignalManager.SignalObject import SignalObject


class ObjectDictionary(Dict[int, UnifiedObject]):
    pass

class SignalDictionary(Dict[int, SignalObject]):
    pass

class BackgroundDictionary(Dict[int, BackgroundHandle]):
    pass

class PoleDictionary(Dict[int, ObjectDictionary]):
    pass
