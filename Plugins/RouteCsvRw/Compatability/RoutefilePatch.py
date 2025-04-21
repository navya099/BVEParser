from typing import List
from ..Structures.Expression import Expression
from ..RouteData import RouteData
from OpenBveApi.System.Path import Path


class Parser3:
    def __init__(self):

        self.available_routefile_patches = {'': RoutefilePatch()}

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
                print(f'{patch.LogMessage}')

class RoutefilePatch:
    def __init__(self):
        self.incompatible = False
        self.log_message = ''
        self.line_ending_fix = False
        self.ignore_pitch_roll = False
