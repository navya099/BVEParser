from Plugins.RouteCsvRw.Structures.AbstractStructure import AbstractStructure
from RouteManager2.CurrentRoute import CurrentRoute


class Brightness(AbstractStructure):
    """A legacy Brightness command
    Applies equally to all tracks in a block
    Attributes:
        value: The new brightness value
    """
    def __init__(self, track_position, value, rail_index=0):
        super().__init__(track_position, rail_index)
        self.value = value

    def create(self, current_route: CurrentRoute, starting_distance: float, current_element: int,
               current_brightness_element: int, current_brightness_event: int, current_brightness_track_position: float,
               current_brightness_value: float):
        for tt in range(len(current_route.Tracks)):
            t = list(current_route.Tracks.keys())[tt]
            d = self.TrackPosition - starting_distance
