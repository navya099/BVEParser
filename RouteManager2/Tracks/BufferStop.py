class BufferStop:
    def __init__(self, track_index: int, track_position: float, player_train_only: bool):
        self.track_index = track_index
        self.track_position = track_position
        self.player_train_only = player_train_only
