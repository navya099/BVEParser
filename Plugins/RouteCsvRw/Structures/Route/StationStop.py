from Plugins.RouteCsvRw.Structures.AbstractStructure import AbstractStructure


class Stop(AbstractStructure):
    def __init__(self, track_position: float, station_index: int, direction: int,
                 forward_tolerance: float, backward_tolerance: float, number_of_cars: int):
        super().__init__(track_position)
        self.StationIndex = station_index
        self.Direction = direction
        self.ForwardTolerance = forward_tolerance
        self.BackwardTolerance = backward_tolerance
        self.Cars = number_of_cars
