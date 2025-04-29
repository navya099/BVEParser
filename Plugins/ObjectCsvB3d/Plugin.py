import os.path

from OpenBveApi.Objects.ObjectInterface import ObjectInterface, CompatabilityHacks
from OpenBveApi.Objects.ObjectTypes.UnifiedObject import UnifiedObject
from OpenBveApi.System.Files import FileFormats
from OpenBveApi.System.Hosts.HostInterface import HostInterface
from Plugins.ObjectCsvB3d.Parser import Plugin1
from loggermodule import logger


class Plugin(ObjectInterface, Plugin1):
    currentHost: HostInterface = None
    enabledHacks: CompatabilityHacks = None
    CompatibilityFolder: str = ''

    def __init__(self):
        super().__init__()
        self._static_extensions = ['.b3d', '.csv']
        self._animated_extensions = ['.animated']

    @property
    def SupportedStaticObjectExtensions(self) -> list[str]:
        return self._static_extensions

    @property
    def SupportedAnimatedObjectExtensions(self) -> list[str]:
        return self._animated_extensions

    def Load(self, host: HostInterface, fileSystem: 'FileSystem'):
        Plugin.currentHost = host
        self.CompatibilityFolder = "Compatibility"

    def SetCompatibilityHacks(self, enabled_hacks: CompatabilityHacks):
        Plugin.enabledHacks = enabled_hacks

    def CanLoadObject(self, path: str) -> bool:
        if path == '' or not os.path.isfile(path):
            return False
        if path.lower().endswith('.b3d') or path.lower().endswith('.csv'):
            if os.path.isfile(path) and FileFormats.IsNautilusFile(path):
                return False

            currently_loading = True

            try:
                with open(path, 'r', encoding='utf-8') as file:
                    for i in range(100):
                        try:
                            line = file.readline()
                            if 'meshbuilder' in line.lower():
                                # We have found the MeshBuilder statement within the first 100 lines
                                # This must be an object (we hope)
                                # Use a slightly larger value than for routes, as we're hoping for a positive match
                                return True
                        except Exception as ex:
                            pass  # ignored

            except Exception as ex:
                return False

            if currently_loading:
                '''
                * https://github.com/leezer3/OpenBVE/issues/666
                * https://github.com/leezer3/OpenBVE/issues/661
                *
                * In BVE routes, a null (empty) object may be used
                * in circumstances where we want a rail / wall / ground etc.
                * to continue, but show nothing
                *
                * These have no set format, and likely are undetectable, especially
                * if they're an empty file in the first place.....
                *
                * However, we *still* want to be able to detect that we can't load a file
                * and pass it off to Object Viewer if it thinks it can handle it, so we need to
                * know if a Route Plugin is loading (if so, it must be a null object) versus not-
                * Don't do anything
                *
                * TODO: Add a way to have 'proper' empty railtypes without this kludge and 
                * add appropriate info message here
                '''
                return True
        return False

    def LoadObject(self, path: str, encoding: str) -> tuple[bool, UnifiedObject]:
        try:
            unified_object = self.ReadObject(path, encoding)
            return True, unified_object
        except Exception as ex:
            unified_object = None
            logger.critical("An unexpected error occured whilst attempting to load the following object: " + path)
        return False, unified_object

