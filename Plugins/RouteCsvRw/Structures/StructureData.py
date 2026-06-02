from dataclasses import dataclass, field
from typing import List, Dict, Optional

from OpenBveApi.Routes.LightDefinition import LightDefinition
from Plugins.RouteCsvRw.ObjectDictionary import ObjectDictionary, PoleDictionary
from loggermodule import logger
from OpenBveApi.Objects.ObjectTypes.UnifiedObject import UnifiedObject


@dataclass
class StructureData:
    # All currently defined Structure.Rail objects
    RailObjects: Optional[ObjectDictionary] = field(default_factory=ObjectDictionary)
    # All currently defined Structure.Pole objects
    Poles: Optional[PoleDictionary] = field(default_factory=PoleDictionary)
    # All currently defined Structure.Ground objects
    Ground: Optional[ObjectDictionary] = field(default_factory=ObjectDictionary)
    WallL: Optional[ObjectDictionary] = field(default_factory=ObjectDictionary)
    WallR: Optional[ObjectDictionary] = field(default_factory=ObjectDictionary)
    DikeL: Optional[ObjectDictionary] = field(default_factory=ObjectDictionary)
    DikeR: Optional[ObjectDictionary] = field(default_factory=ObjectDictionary)
    FormL: Optional[ObjectDictionary] = field(default_factory=ObjectDictionary)
    FormR: Optional[ObjectDictionary] = field(default_factory=ObjectDictionary)
    FormCL: Optional[ObjectDictionary] = field(default_factory=ObjectDictionary)
    FormCR: Optional[ObjectDictionary] = field(default_factory=ObjectDictionary)
    RoofL: Optional[ObjectDictionary] = field(default_factory=ObjectDictionary)
    RoofR: Optional[ObjectDictionary] = field(default_factory=ObjectDictionary)
    RoofCL: Optional[ObjectDictionary] = field(default_factory=ObjectDictionary)
    RoofCR: Optional[ObjectDictionary] = field(default_factory=ObjectDictionary)
    CrackL: Optional[ObjectDictionary] = field(default_factory=ObjectDictionary)
    CrackR: Optional[ObjectDictionary] = field(default_factory=ObjectDictionary)
    FreeObjects: Optional[ObjectDictionary] = field(default_factory=ObjectDictionary)
    Beacon: Optional[ObjectDictionary] = field(default_factory=ObjectDictionary)
    WeatherObjects: Optional[ObjectDictionary] = field(default_factory=ObjectDictionary)
    # Cycles
    Cycles: Optional[List[List[int]]] = field(default_factory=list)
    RailCycles: Optional[List[List[int]]] = field(default_factory=list)
    Run: Optional[List[int]] = field(default_factory=list)
    Flange: Optional[List[int]] = field(default_factory=list)
    LightDefinitions: Optional[Dict[int, List[LightDefinition]]] = field(default_factory=dict)
