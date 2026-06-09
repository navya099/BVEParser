from OpenBveApi.Routes.BackgroundHandle import BackgroundHandle
from OpenBveApi.Routes.StaticBackground import StaticBackground


class DynamicBackground(BackgroundHandle):
    def __init__(self, static_backgrounds: list[StaticBackground]):
        super().__init__()
        self.static_backgrounds = static_backgrounds
        self.current_background_index = 0
        self.previous_background_index = 0

    def update_background(self, seconds_since_midnight: float, elapsed_time: float, target: bool):
        pass


