import os
from loggermodule import logger


class Parser11:
    def __init__(self):
        super().__init__()

    def locate_object(self, filename: str, object_path: str) -> tuple[bool, str]:
        n = ''
        try:
            # Catch completely malformed path references
            n = os.path.join(object_path, filename)
        except FileNotFoundError:
            return False, filename
        if os.path.exists(n):
            filename = n
            # The object exists, and does not require a compatibility object
            return True, filename

        if self.Plugin.CurrentOptions.EnableBveTsHacks:
            fn = ''
            # The Midland Suburban Line has a malformed object zip, so let's try again....
            if filename.lower().startswith("Midland Suburban Line"):
                fn = "Midland Suburban Line Objects" + filename[21:]
                try:
                    # Catch completely malformed path references
                    n = os.path.join(object_path, fn)
                except FileNotFoundError:
                    return False, filename
                if os.path.exists(n):
                    filename = n
                    return True, filename
            # The Midland Suburban Line expects BRSema4Sigs to be placed in it's object folder,
            # but we've probably got them elsewhere
            if filename.lower().startswith("Midland Suburban Line\\BrSema4Sigs".lower()):
                fn = "BrSema4Sigs" + filename[33:]
                try:
                    # Catch completely malformed path references
                    n = os.path.join(object_path, fn)
                except FileNotFoundError:
                    return False, filename
                if os.path.exists(n):
                    filename = n
                    # The object exists, and does not require a compatibility object
                    return True, filename
            # Malformed First Brno Track: Origins downloads-
            # https://bveworldwide.forumotion.com/t2317-fbt-cannot-start-routes-missing-objects#21405
            if filename.lower().startswith("FirstBrnoTrack-Origins".lower()):
                fn = "FirstBrnoTrack" + filename[22:]
                try:
                    # Catch completely malformed path references
                    n = os.path.join(object_path, fn)
                except FileNotFoundError:
                    return False, filename
                if os.path.exists(n):
                    filename = n
                    # The object exists, and does not require a compatibility object
                    return True, filename
            # Wood Lane (2010) looks for BRSigs inside the NWM folder
            # Later versions don't have these here, so let's try for the 'standard' copy.....
            if filename.lower().startswith("NWM\brsigs".lower()):
                fn = "brsigs" + filename[10:]
                try:
                    # Catch completely malformed path references
                    n = os.path.join(object_path, fn)
                except FileNotFoundError:
                    return False, filename
                if os.path.exists(n):
                    filename = n
                    # The object exists, and does not require a compatibility object
                    return True, filename
        # We haven't found the object on-disk, so check the compatibility objects to see if a replacement is available
        for i in range(len(CompatibilityObjects.AvailableReplacements)):
            if len(CompatibilityObjects.AvailableReplacements[i].ObjectNames) == 0:
                continue
            for j in range(len(CompatibilityObjects.AvailableReplacements[i].ObjectNames)):
                if CompatibilityObjects.AvailableReplacements[i].ObjectNames[j].lower() == filename.lower():
                    # Available replacement found
                    filename = CompatibilityObjects.AvailableReplacements[i].ReplacementPath
                    if CompatibilityObjects.AvailableReplacements[i].Message:
                        logger.warning(f'{CompatibilityObjects.AvailableReplacements[i].Message}')
                    Parser.CompatibilityObjectsUsed += 1
                    return True, filename
            return False, filename
        return False, filename

    # The total number of compatability objects used by the current route
    CompatibilityObjectsUsed: int = 0


class CompatibilityObjects:
    class ReplacementObject:
        def __init__(self):
            self.ObjectNames: str = ''
            self.ReplacementPath: str = ''
            self.Message: str = ''

    SignalPost = None
    LimitPostStraight = None
    LimitPostLeft = None
    LimitPostRight = None
    LimitPostInfinite = None
    LimitOneDigit = None
    LimitTwoDigits = None
    LimitThreeDigits = None
    StopPost = None
    TransponderS = None
    TransponderSN = None
    TransponderFalseStart = None
    TransponderPOrigin = None
    TransponderPStop = None

    LimitGraphicsPath = None

    CompatabilityObjectsLoaded = False

    AvailableReplacements: list[ReplacementObject] = []
    AvailableSounds: list[ReplacementObject] = []
