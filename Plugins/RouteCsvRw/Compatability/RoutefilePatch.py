from typing import List, Optional
from ..Structures.Expression import Expression
from ..RouteData import RouteData
from OpenBveApi.System.Path import Path
from loggermodule import logger


class Parser3:
    def __init__(self):
        super().__init__()  # 💡 중요!
        self.available_routefile_patches: dict[str, RoutefilePatch] = {'': RoutefilePatch()}

    def check_for_available_patch(self, file_name: str, data: RouteData,
                                  expressions: List[Expression], preview_only: bool):
        if self.Plugin.CurrentOptions.EnableBveTsHacks is False:
            return

        file_hash = Path.get_checksum(file_name)
        if file_hash in self.available_routefile_patches:
            patch = self.available_routefile_patches[file_hash]
            if patch.incompatible:
                raise Exception(f'This routefile is incompatible with OpenBVE:'
                                f'\n\n{patch.log_message}')
            data.line_ending_fix = patch.line_ending_fix
            data.ignore_pitch_roll = patch.ignore_pitch_roll

            if patch.log_message:
                logger.warning(patch.log_message)
            from Plugins.RouteCsvRw.CsvRwRouteParser import Parser
            Parser.EnabledHacks.CylinderHack = patch.cylinder_hack
            Parser.EnabledHacks.DisableSemiTransparentFaces = patch.DisableSemiTransparentFaces


class RoutefilePatch:
    def __init__(self):
        self.filename: str = ''
        self.line_ending_fix: bool = False
        self.colon_fix: bool = False
        self.ignore_pitch_roll: bool = False
        self.log_message: str = ''
        self.cylinder_hack: bool = False
        self.ExpressionFixes: dict[int, str] = {}
        self.XParser: Optional['XParsers'] = None
        self.Derailments: bool = False
        self.Toppling: bool = False
        self.DummyRailTypes: list[int] = []
        self.DummyGroundTypes: list[int] = []
        self.CompatibilitySignalSet: Optional[str] = None
        self.AccurateObjectDisposal: bool = False  # Forces accurate object disposal on or off
        self.SplitLineHack: bool = False  # Whether certain lines should be split
        self.AllowTrackPositionArguments: bool = False  # Allows arguments after track positions
        # Some files use these as comments
        self.DisableSemiTransparentFaces: bool = False  # Disables semi-transparent faces
        self.ReducedColorTransparency: bool = False  # Whether reduced color transparency should be used
        self.ViewingDistance: int = 2147483647  # The viewing distance to use
        self.Incompatible: bool = False  # Whether the route is incompatible with OpenBVE
        self.AggressiveRwBrackets: bool = False  # Whether aggressive RW bracket fixing is applied
        self.DelayedAnimatedUpdates: bool = False  # Whether animated object update
