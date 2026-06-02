from OpenBveApi.Routes.TrackDirection import TrackDirection
from OpenBveApi.Routes.TrackElement import TrackElement


class Track:
    def __init__(self, trackName=None):
        self.Elements = [TrackElement() for _ in range(256)]
        self.RailGauge = 1.435
        self.Direction = TrackDirection
        self.Name = trackName
