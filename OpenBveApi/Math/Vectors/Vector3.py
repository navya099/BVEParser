class Vector3:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return f"({self.x}, {self.y}, {self.z})"

    def zero(self):
        self.x = 0
        self.y = 0
        self.z = 0
        return self.x, self.y, self.z
    
    def rotate(self, cos_angle, sin_angle):
        """Rotate this vector in 2D by the given cosine and sine values."""
        x_new = cos_angle * self.x - sin_angle * self.y
        y_new = sin_angle * self.x + cos_angle * self.y
        self.x, self.y = x_new, y_new
