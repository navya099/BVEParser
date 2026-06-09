from Plugins.RouteCsvRw.ObjectDictionary import ObjectDictionary
from Plugins.RouteCsvRw.Structures.Direction import Direction


class WallDike:
    """
    Attributes:
        exists: Whether the wall/ dike is shown for this block
        object_type: The routefile index of the object
        direction: The direction the object(s) are placed in: -1 for left, 0 for both, 1 for right
        left_objects: Reference to the appropriate left-sided object array
        right_objects: Reference to the appropriate right-sided object array

    """
    def __init__(self, object_type: int, direction: Direction, left_objects: ObjectDictionary, right_objects: ObjectDictionary, exists: bool= True) -> None:
        self.object_type = object_type
        self.direction = direction
        self.left_objects = left_objects
        self.right_objects = right_objects
        self.exists = exists

    def clone(self) -> "WallDike":
        return WallDike(
            self.object_type,
            self.direction,
            self.left_objects,
            self.right_objects,
            self.exists
        )