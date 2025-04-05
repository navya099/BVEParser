from OpenBveApi.Math.Vectors.Vector3 import Vector3

class TrackElement:
    def __init__(self, StartingTrackPosition):
        self.StartingTrackPosition = StartingTrackPosition
        self.CurveRadius = 0.0
        self.CurveCant = 0.0
        self.Pitch = 0.0
        vector3 = Vector3()
        self.WorldPosition = vector3.zero()
