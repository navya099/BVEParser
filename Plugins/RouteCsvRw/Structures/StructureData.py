from dataclasses import dataclass, field
from typing import List, Dict, Optional

# 의존 타입들은 외부에서 정의되어야 합니다
# 예시:
# ObjectDictionary = dict[int, str]  # 필요시 실제 타입 정의
# PoleDictionary = dict[int, str]
# LightDefinition = ...  # 별도 정의 필요

@dataclass
class StructureData:
    # All currently defined Structure.Rail objects
    RailObjects: Optional['ObjectDictionary'] = None
    # All currently defined Structure.Pole objects
    Poles: Optional['PoleDictionary'] = None
    # All currently defined Structure.Ground objects
    Ground: Optional['ObjectDictionary'] = None
    # All currently defined Structure.WallL objects
    WallL: Optional['ObjectDictionary'] = None
    # All currently defined Structure.WallR objects
    WallR: Optional['ObjectDictionary'] = None
    # All currently defined Structure.DikeL objects
    DikeL: Optional['ObjectDictionary'] = None
    # All currently defined Structure.DikeR objects
    DikeR: Optional['ObjectDictionary'] = None
    # All currently defined Structure.FormL objects
    FormL: Optional['ObjectDictionary'] = None
    # All currently defined Structure.FormR objects
    FormR: Optional['ObjectDictionary'] = None
    # All currently defined Structure.FormCL objects
    FormCL: Optional['ObjectDictionary'] = None
    # All currently defined Structure.FormCR objects
    FormCR: Optional['ObjectDictionary'] = None
    # All currently defined Structure.RoofL objects
    RoofL: Optional['ObjectDictionary'] = None
    # All currently defined Structure.RoofR objects
    RoofR: Optional['ObjectDictionary'] = None
    # All currently defined Structure.RoofCL objects
    RoofCL: Optional['ObjectDictionary'] = None
    # All currently defined Structure.RoofCR objects
    RoofCR: Optional['ObjectDictionary'] = None
    # All currently defined Structure.CrackL objects
    CrackL: Optional['ObjectDictionary'] = None
    # All currently defined Structure.CrackR objects
    CrackR: Optional['ObjectDictionary'] = None
    # All currently defined Structure.FreeObj objects
    FreeObjects: Optional['ObjectDictionary'] = None
    # All currently defined Structure.Beacon objects
    Beacon: Optional['ObjectDictionary'] = None
    # All currenly defined Structure.Weather objects
    WeatherObjects: Optional['ObjectDictionary'] = None
    # All currently defined cycles
    Cycles: Optional[List[List[int]]] = None
    # All currently defined RailCycles
    RailCycles: Optional[List[List[int]]] = None
    # The Run sound index to be played for each railtype idx
    Run: Optional[List[int]] = None
    # The flange sound index to be played for each railtype idx
    Flange: Optional[List[int]] = None
    # Contains the available dynamic lighting sets
    LightDefinitions: Optional[Dict[int, List['LightDefinition']]] = None
