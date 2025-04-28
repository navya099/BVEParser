from enum import Enum


class SafetySystem(Enum):
    # Any available safety system should be used
    # (Either that from the previous station if defined or NONE)
    Any = -1
    # ATS should be used- The track is NOT fitted with ATC
    Ats = 0
    # ATC should be used
    Atc = 1