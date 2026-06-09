from OpenBveApi.Routes.BackgroundHandle import BackgroundHandle


class StaticBackground(BackgroundHandle):
    def __init__(self, texture, repetition: float, keep_aspect_ratio: float, transition_time: float, time: float,
                 vao: object, display_list: int = 0):
        super().__init__()
        self.texture = texture
        self.repetition = repetition
        self.keep_aspect_ratio = keep_aspect_ratio
        self.transition_time = transition_time
        self.time = time
        self.vao = vao
        self.display_list = display_list
    def update_background(self, seconds_since_midnight: float, elapsed_time: float, target: bool):
        pass


