import math

from Plugins.RouteCsvRw.RouteData import RouteData
import copy

from Plugins.RouteCsvRw.reverseclass.alignment_reverse import AlignmentReverse
from Plugins.RouteCsvRw.reverseclass.create_route import CreateRouteFILE
from Plugins.RouteCsvRw.reverseclass.object_reverse import ObjectReverse
from Plugins.RouteCsvRw.reverseclass.rail_reverse import RailReverse
from Plugins.RouteCsvRw.reverseclass.station_reverse import StationReverse
from loggermodule import logger
from RouteManager2.CurrentRoute import CurrentRoute


class RouteReverser:
    """역방향 루트 생성을 위한 리버서"""
    def __init__(self, data: RouteData, current_route: CurrentRoute):
        self.current_route = current_route
        self.data = data

    def convert_to_reverse_route(self):
        """역방향 실행 메서드"""
        current_track_position = None
        current_track_position_freeobj = None
        actual_block_count = int(self.data.TrackPosition / self.data.BlockInterval) + 1
        # 원래 데이터 크기만큼만 남기고 뒤에 붙은 유령 블록들은 제거합니다.
        if len(self.data.Blocks) > actual_block_count:
            logger.debug(f"역방향 인덱스 보정: 유령 블록 {len(self.data.Blocks) - actual_block_count}개 제거")
            self.data.Blocks = self.data.Blocks[:actual_block_count]

        # 역(station) 반전
        station_reverser = StationReverse(self.data, self.current_route)
        station_reverser.reverse_stations()

        # -------------------------------------------------------------------
        # [교정 2] 블록 리스트를 뒤집기 "전"에, 정방향 인덱스 기준으로 Station ID를 먼저 매칭!
        # -------------------------------------------------------------------
        for block in self.data.Blocks:
            station_reverser.reverse_block_station_id(block)

        # 1. 이제 순수한 블록 리스트만 남았으므로 역순으로 뒤집기
        self.data.Blocks.reverse()

        # 2. 역방향 기하학적 요소 변경
        total_blocks = len(self.data.Blocks)
        for i in range(len(self.data.Blocks) - 1):
            block = self.data.Blocks[i]
            # 마지막 블록일 때는 next_block에 None을 주어 종단 마감을 유도합니다.
            next_block = self.data.Blocks[i + 1] if i < total_blocks - 1 else None

            last_track_position = self.data.TrackPosition
            current_track_position = i * self.data.BlockInterval
            current_reverse_track_position = last_track_position - current_track_position

            #선형 뒤집기(next_block 전달로 1칸 시프트 완벽 결합)
            AlignmentReverse.reverse_alignment(block, next_block)
            #레일 뒤집기
            RailReverse.reverse_rail(block)
            # ③ [추가] 지상물 오브젝트 뒤집기 (Ground 및 Rail 오브젝트 전수조사 반전)
            ObjectReverse.reverse_objects(block)

            # 💡 [추가] 가공전선주(전신주) 좌우 방향 및 위치 반전
            ObjectReverse.reverse_poles(block, next_block)

            # -------------------------------------------------------------------
            # [교정 3] 블록이 뒤집힌 상태이므로 인덱스 i를 전달해 정차 위치(Stop)를 최종 교정!
            # -------------------------------------------------------------------
            station_reverser.reverse_stoppositions(i, block)

        #직렬화 및 저장
        CreateRouteFILE.serialize_route_data(self.current_route, self.data)

    def preprocess_reverse_route(self):
        """역방향 루트 생성 전 원본 루트에서 필요한 값 추출"""

        # 600m 여유 블록을 제외하고, 실제 선로 데이터가 끝나는 정확한 블록 인덱스 계산
        # 예: TrackPosition이 1000m이고 Interval이 25m이면, 정확히 40번 블록이 데이터의 끝입니다.
        actual_last_idx = int(self.data.TrackPosition / self.data.BlockInterval)

        elements = self.current_route.Tracks[0].Elements
        max_available_idx = len(elements) - 1

        # 안전장치: 계산된 인덱스가 현재 할당된 배열 크기(4096 등)를 넘지 않도록 보정
        start_search_idx = min(actual_last_idx, max_available_idx)

        # 실제 마지막 데이터 블록 위치부터 거꾸로 스캔하며 None이 아닌 실데이터 추출
        last_element_idx = start_search_idx
        while last_element_idx >= 0 and elements[last_element_idx] is None:
            last_element_idx -= 1

        if last_element_idx >= 0:
            last_element = elements[last_element_idx]
            last_world_pos = last_element.WorldPosition
            last_world_dir = last_element.WorldDirection

            # 종점 방위각 계산 및 역방향(+180도) 전환
            forward_rad = math.atan2(last_world_dir.z, last_world_dir.x)
            reverse_degree = (forward_rad * 180.0 / math.pi) + 180.0

            # 2-Pass(역방향 빌드)의 시작 좌표로 정방향 종점 좌표를 주입
            self.current_route.Atmosphere.InitialX = last_world_pos.x
            self.current_route.Atmosphere.InitialY = last_world_pos.z
            self.current_route.Atmosphere.InitialElevation = last_world_pos.y
            self.current_route.Atmosphere.InitialDirection = reverse_degree

            logger.debug(f'실제 종점 데이터 매칭 성공 (인덱스: {last_element_idx}) - X: {last_world_pos.x}, Z: {last_world_pos.z}')