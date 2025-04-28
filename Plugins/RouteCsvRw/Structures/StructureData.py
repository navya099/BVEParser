from dataclasses import dataclass, field
from typing import List, Dict, Optional

# Define ObjectDictionary and PoleDictionary properly first
# Here as simple dicts for now:
ObjectDictionary = Dict[int, 'UnifiedObject']
PoleDictionary = Dict[int, 'UnifiedObject']
LightDefinition = object  # Placeholder


@dataclass
class StructureData:
    # All currently defined Structure.Rail objects
    RailObjects: Optional[ObjectDictionary] = field(default_factory=dict)
    # All currently defined Structure.Pole objects
    Poles: Optional[PoleDictionary] = field(default_factory=dict)
    # All currently defined Structure.Ground objects
    Ground: Optional[ObjectDictionary] = field(default_factory=dict)
    WallL: Optional[ObjectDictionary] = field(default_factory=dict)
    WallR: Optional[ObjectDictionary] = field(default_factory=dict)
    DikeL: Optional[ObjectDictionary] = field(default_factory=dict)
    DikeR: Optional[ObjectDictionary] = field(default_factory=dict)
    FormL: Optional[ObjectDictionary] = field(default_factory=dict)
    FormR: Optional[ObjectDictionary] = field(default_factory=dict)
    FormCL: Optional[ObjectDictionary] = field(default_factory=dict)
    FormCR: Optional[ObjectDictionary] = field(default_factory=dict)
    RoofL: Optional[ObjectDictionary] = field(default_factory=dict)
    RoofR: Optional[ObjectDictionary] = field(default_factory=dict)
    RoofCL: Optional[ObjectDictionary] = field(default_factory=dict)
    RoofCR: Optional[ObjectDictionary] = field(default_factory=dict)
    CrackL: Optional[ObjectDictionary] = field(default_factory=dict)
    CrackR: Optional[ObjectDictionary] = field(default_factory=dict)
    FreeObjects: Optional[ObjectDictionary] = field(default_factory=dict)
    Beacon: Optional[ObjectDictionary] = field(default_factory=dict)
    WeatherObjects: Optional[ObjectDictionary] = field(default_factory=dict)
    # Cycles
    Cycles: Optional[List[List[int]]] = field(default_factory=list)
    RailCycles: Optional[List[List[int]]] = field(default_factory=list)
    Run: Optional[List[int]] = field(default_factory=list)
    Flange: Optional[List[int]] = field(default_factory=list)
    LightDefinitions: Optional[Dict[int, List[LightDefinition]]] = field(default_factory=dict)
