from dataclasses import dataclass

class Interface:
    @dataclass
    class Options:
        user_interface_folder: str = ""
        time_acceleration_factor: int = 1
