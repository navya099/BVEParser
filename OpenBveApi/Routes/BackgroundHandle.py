from abc import ABC, abstractmethod
from OpenBveApi.Routes.BackgroundTransitionMode import BackgroundTransitionMode


class BackgroundHandle(ABC):
    def __init__(self):
        self.BackgroundImageDistance: float = 600.0
        self.Mode: BackgroundTransitionMode = BackgroundTransitionMode.Null
        self.Countdown: int = 0
        self.CurrentAlpha: float = 1.0

    @abstractmethod
    def update_background(self, seconds_since_midnight: float, elapsed_time: float, target: bool):
        """
        Called once per frame to update the current state of the background.

        Args:
            seconds_since_midnight (float): The current in-game time, expressed as the number of seconds since midnight on the first day.
            elapsed_time (float): The total elapsed frame time (in seconds).
            target (bool): Whether this is the target background during a transition (affects alpha rendering).
        """
        pass

