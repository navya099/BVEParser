import math

from Plugins.RouteCsvRw.RouteData import RouteData
from Plugins.RouteCsvRw.Structures.Block import Block
from RouteManager2.CurrentRoute import CurrentRoute
from copy import deepcopy


class StationReverse:
    """정거장 및 정차 마커 역방향 정밀 물리 변환 클래스 (진짜 역 기점 오프셋 동적 추적 방식)"""

    def __init__(self, data: RouteData, current_route: CurrentRoute):
        self.data = data
        self.current_route = current_route
        self.total_stations_count = len(current_route.Stations)

    def reverse_stations(self):
        """전체 역 목록 자체를 역순으로 1회 스왑하고 속성(출입문)을 반전합니다."""
        if self.total_stations_count == 0:
            return

        original_stations = self.current_route.Stations
        reversed_stations = []

        for index in range(self.total_stations_count - 1, -1, -1):
            station = original_stations[index]
            # 출입문 개방 방향 좌우 반전 스왑
            station.OpenLeftDoors, station.OpenRightDoors = station.OpenRightDoors, station.OpenLeftDoors
            # DefaultTrackPosition 반전
            #먼저 정방향 stop의 블록을 찾아서 trackposition을 꺼내야함
            #data.Blocks[block_index].StopPositions
            stop_positions = self.get_stop_trackposition_by_station_index(index)
            #가장 큰 stop_position 선택
            select_stop_position = max(stop_positions)
            #DefaultTrackPosition에 적용
            station.DefaultTrackPosition = self.data.TrackPosition - select_stop_position
            reversed_stations.append(station)

        self.current_route.Stations = reversed_stations

    def reverse_block_station_id(self):
        """블록을 뒤집은 후 current_route의 역 ID를 역방향 타겟 블록 역 ID로 전환합니다."""
        # 1. 모든 블록을 -1로 초기화
        for block in self.data.Blocks:
            block.Station = -1

        #역방향 DefaultTrackPosition에 해당하는 블록 인덱스 얻기
        for i, station in enumerate(self.current_route.Stations):
            station = self.current_route.Stations[i]
            current_track_position = station.DefaultTrackPosition #역방향
            block_index = int(math.floor(current_track_position / self.data.BlockInterval + 0.001))
            target_block = self.data.Blocks[block_index]

            #station id 매핑
            target_block.Station = i

    def reverse_stoppositions(self, i: int, block: Block):
        """
        [최종 교정 마스터피스]
        마커가 속한 블록이 아니라, 마커의 '진짜 주인 역(Station)'의 블록 기점을 추적하여
        역방향 월드에서도 [.sta 블록 기점 + 정밀 오프셋] 구조를 완벽하게 강제 매칭합니다.
        """
        if not block.StopPositions:
            return

        new_stops = []
        last_track_position = self.data.TrackPosition
        block_interval = self.data.BlockInterval

        for stop in block.StopPositions:
            rev_stop = deepcopy(stop)

            # 💡 [원래 정방향 역 정보 역산]
            # 이 마커가 정방향 시절 소속되어 있던 순정 역 ID (아직 변환 전 보존된 상태)
            orig_station_idx = stop.StationIndex

            # 💡 [역방향 역 ID 변환] 타겟 역 인덱스 역순 스왑
            target_station_idx = self.total_stations_count - 1 - orig_station_idx
            rev_stop.StationIndex = target_station_idx

            # 전방/후방 허용 오차(Tolerance) 스왑
            rev_stop.ForwardTolerance, rev_stop.BackwardTolerance = rev_stop.BackwardTolerance, rev_stop.ForwardTolerance

            # -------------------------------------------------------------------
            # 💡 핵심 기하학 추적 연산: 마커 소속 블록이 아닌 '진짜 역 블록' 기준 추적
            # -------------------------------------------------------------------

            # 1. 정방향 시절 이 역을 품고 있던 원래 정방향 블록 인덱스 추적
            # 역방향 전체 블록 리스트를 뒤집기 전 상태를 역산하기 위해
            # 현재 역방향 인덱스 i가 아닌, 진짜 역방향 맵에 안착할 타겟 역의 블록 관계를 활용합니다.

            # 정방향 전체 blocks에서 해당 역 ID를 가지고 있던 원본 블록 인덱스를 찾습니다.
            orig_station_block_idx = None

            # 안전하게 역방향 뒤집히기 전 원래 정방향 인덱스 배열 위치 추적
            # 역방향 인덱스 i에 대응되는 원래 정방향 블록의 인덱스는 (total_blocks - 1 - i) 입니다.
            # 하지만 .stop이 역과 다른 블록에 있을 수 있으므로, 원본 블록셋을 역 추적합니다.
            # self.data.Blocks는 이미 메인 루프에서 뒤집혀 있으므로,
            # 뒤집힌 block.Station은 이미 target_station_idx로 바뀌어 있습니다!

            # 역방향 현재 블록에 적힌 역 ID가 유효하다면 그 위치가 곧 역의 기점 블록입니다.
            # 만약 .stop 마커 단독 블록이라면, 전체 뒤집힌 리스트에서 target_station_idx를 가진 블록의 인덱스를 뽑아옵니다.
            rev_station_block_idx = i  # 기본값은 현재 블록으로 방어
            for idx, b in enumerate(self.data.Blocks):
                if b.Station == target_station_idx:
                    rev_station_block_idx = idx
                    break

            # 2. 정방향 시절 역의 블록 시작 위치 역산
            # 역방향 리스트에서 찾은 rev_station_block_idx의 원래 정방향 위치를 구합니다.
            total_blocks = len(self.data.Blocks)
            orig_station_block_idx_true = total_blocks - 1 - rev_station_block_idx
            orig_station_block_start = orig_station_block_idx_true * block_interval

            # 3. [진짜 정방향 오프셋 추출] 진짜 역 블록 기점으로부터의 거리 차이 계산
            orig_offset = stop.TrackPosition - orig_station_block_start

            # 4. [역방향 정밀 재조립] 역방향 월드의 진짜 역 블록 기점에 오프셋 결합!
            rev_station_block_start = rev_station_block_idx * block_interval
            rev_stop.TrackPosition = rev_station_block_start + orig_offset

            new_stops.append(rev_stop)

        block.StopPositions = new_stops

    def get_stop_trackposition_by_station_index(self, station_index):
        """station_index를 기반으로 stoppositions 얻기"""
        stoppositions = []
        for block in self.data.Blocks:
            if block.StopPositions:
                for stopposition in block.StopPositions:
                    if stopposition.StationIndex == station_index:
                        stoppositions.append(stopposition.TrackPosition)
        return stoppositions