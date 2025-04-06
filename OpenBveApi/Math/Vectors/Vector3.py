class Vector3:
    Forward = (0.0, 0.0, 1.0)
    Backward = (0.0, 0.0, -1.0)
    Zero = (0.0, 0.0, 0.0)
    Left = (-1.0, 0.0, 0.0)
    Right = (1.0, 0.0, 0.0)
    Down = (0.0, 1.0, 0.0)

    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return f"({self.x}, {self.y}, {self.z})"
    
    def rotate(self, cos_angle, sin_angle):
        """Rotate this vector in 2D by the given cosine and sine values."""
        x_new = cos_angle * self.x - sin_angle * self.y
        y_new = sin_angle * self.x + cos_angle * self.y
        self.x, self.y = x_new, y_new
