from OpenBveApi.Objects.ObjectTypes.StaticObject import StaticObject
import os


class Plugin1:
    def __init__(self):
        super().__init__()

    def ReadObject(self, filename: str, encoding: str) -> StaticObject:

        is_b3d = os.path.splitext(filename)[1].lower() == ".b3d"
        return StaticObject(None)

