from RouteManager2.CurrentRoute import CurrentRoute
from .PreprocessOptions import PreprocessMixin2
from .RouteData import RouteData
from .Preprocess import PreprocessMixin
from OpenBveApi.Objects.ObjectInterface import ObjectInterface, CompatabilityHacks
from typing import List
from tqdm import tqdm
import time


class Parser(PreprocessMixin, PreprocessMixin2):
    EnabledHacks = CompatabilityHacks()

    def __init__(self):
        super().__init__()
        self.ObjectPath = ''
        self.SoundPath = ''
        self.TrainPath = ''
        self.CompatibilityFolder = ''
        self.IsRW = None
        self.IsHmmsim = None
        self.CurrentRoute = CurrentRoute()
        self.Plugin = None  # 여긴 직접 생성 X
        self.AllowTrackPositionArguments = False
        self.SplitLineHack = True

    def parse_route(self, file_name, is_rw, encoding, train_path, object_path, sound_path, preview_only, host_plugin):
        self.Plugin = host_plugin
        self.CurrentRoute = self.Plugin.CurrentRoute
        self.ObjectPath = object_path
        self.SoundPath = sound_path
        self.TrainPath = train_path
        self.IsRW = is_rw

        freeobj_count = 0
        railtype_count = 0
        data = RouteData(preview_only)

        self.parse_route_for_data(file_name, encoding, data, preview_only)

        if self.Plugin.Cancel:
            self.Plugin.IsLoading = False
            return
        self.apply_route_data(file_name, data, preview_only)

    def parse_route_for_data(self, file_name, encoding, data, preview_only):
        with open(file_name, 'r', encoding=encoding) as f:
            lines: List[str] = f.readlines()
        start_time = time.time()
        expressions = self.preprocess_split_into_expressions(file_name, lines, True)
        expressions = self.preprocess_chr_rnd_sub(file_name, encoding, expressions)
        print('루프탈출')
        unit_of_length = [1.0]
        # Set units of speed initially to km/h
        # This represents 1km/h in m/s
        data.UnitOfSpeed = 0.277777777777778
        self.pre_process_options(expressions, data, unit_of_length, preview_only)
        expressions = self.preprocess_sort_by_track_position(unit_of_length, expressions)
        print('정렬성공')
        end_time = time.time()
        elapsed = end_time - start_time

        test(expressions)
        print('테스트성공')
    @staticmethod
    def apply_route_data(file_name, data, preview_only):
        pass


def test(Expressions):
    with open("C:/TEMP/expressions_all.txt", "w", encoding="utf-8") as f:
        for i in range(len(Expressions)):
            f.write(
                f"{i} , {Expressions[i].Line} , {Expressions[i].Text}, {Expressions[i].TrackPositionOffset}, {Expressions[i].File}\n")
    pass
