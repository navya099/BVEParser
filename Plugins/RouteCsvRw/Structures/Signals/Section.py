from Plugins.RouteCsvRw.Structures.AbstractStructure import AbstractStructure
from RouteManager2.SignalManager.SectionTypes import SectionType


class Section(AbstractStructure):
    def __init__(self, track_position: float, aspects: list[int], departure_station_index: int, section_type: SectionType, invisible: bool=False):
        super().__init__(track_position)
        self.aspects = aspects
        self.departure_station_index = departure_station_index
        self.section_type = section_type
        self.invisible = invisible

