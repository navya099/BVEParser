import math

from Plugins.RouteCsvRw.RouteData import RouteData
from Plugins.RouteCsvRw.Structures.Block import Block
from Plugins.RouteCsvRw.Structures.Route.StationStop import Stop
from RouteManager2.CurrentRoute import CurrentRoute
from copy import deepcopy

class Stationinfo:
    """정거장 관리를 위한 객체
    Attributes:
        name: 역 이름
        start: 역 시작 측점(sta)
        end: 역 끝 측점(stop)
        index: 역 인덱스
    """
    def __init__(self, name: str, start: float, end: float, index: int):
        self.name = name
        self.start = start
        self.end = end
        self.index = index

class StopPositionInfo:
    """StopPosition 관리를 위한 객체
    Attributes:
        index: 블록 인덱스
        stop_positions: stop_positions
    """
    def __init__(self, index: int, stop_positions: list[Stop]):
        self.index = index
        self.stop_positions = stop_positions

class StationReverse:
    """정거장 및 정차 마커 역방향 정밀 물리 변환 클래스 (진짜 역 기점 오프셋 동적 추적 방식)
    Attributes:
        data: RouteData
        current_route: CurrentRoute
        total_stations_count: 전체 역 갯수
        infos: Stationinfo
        stopinfos: stop_position
    """

    def __init__(self, data: RouteData, current_route: CurrentRoute):
        self.data = data
        self.current_route = current_route
        self.total_stations_count = len(current_route.Stations)

        #초기속성
        self.infos: list[Stationinfo] = []
        self.stopinfos: list[StopPositionInfo] = []

        #1회 수집 콜렉트 메서드
        self._collect_stationinfos()
        self._collect_stoppositions()

    def _collect_stationinfos(self):
        """정방향 Station 데이터 수집 후 info객체로 속성 저장"""
        infos = []
        for i, station in enumerate(self.current_route.Stations):
            name = station.Name
            start_track_position = station.DefaultTrackPosition
            stop_positions = self.get_stop_trackposition_by_station_index(i)
            if not stop_positions:
                continue
            start_pos = start_track_position
            end_pos = max(stop_positions)
            infos.append(Stationinfo(name, start_pos, end_pos, i))
        self.infos = infos

    def _collect_stoppositions(self):
        """정방향 stopposition 데이터 수집 후 속성 저장"""
        collected = []
        for block in self.data.Blocks:
            if block.StopPositions:
                collected.append(StopPositionInfo(self.get_block_index(block.CurrentTrackState.StartingTrackPosition), block.StopPositions))

        self.stopinfos = deepcopy(collected)

    def reverse_stations(self):
        """전체 역 목록 자체를 역순으로 정렬하고 속성(출입문)을 반전합니다."""
        if self.total_stations_count == 0:
            return
        original_stations = self.current_route.Stations
        reversed_stations = []

        #역순으로 순회(3,2,1,0)
        for info in reversed(self.infos):
            station = original_stations[info.index]
            # 출입문 개방 방향 좌우 반전 스왑
            station.OpenLeftDoors, station.OpenRightDoors = station.OpenRightDoors, station.OpenLeftDoors
            # 정방향 stop trackposition 가져오기
            stop_position = info.end
            # DefaultTrackPosition에 반전 적용
            station.DefaultTrackPosition = self.data.TrackPosition - stop_position
            reversed_stations.append(station)

        self.current_route.Stations = reversed_stations

    def revere_stoppositions(self):
        """전체 stop 목록 자체를 역순으로 정렬하고 속성을 반전합니다.
            블록을 뒤집은 후 실행.
        """
        if self.total_stations_count == 0:
            return
        #블록 초기화
        self.reset_blocks()
        reversed_stops = []
        # 역순으로 순회(3,2,1,0)
        for info, stopinfo in zip(reversed(self.infos), reversed(self.stopinfos)):
            station_index = info.index #역 인덱스
            start_station = info.start #시작 측점(정방향)
            end_station = info.end #끝 측점(정방향)
            offset = end_station - start_station #offset
            block_index = self.get_block_index(self.data.TrackPosition - start_station) #역방향 인덱스
            target_block = self.data.Blocks[block_index] #역방향 블록 내 타겟블록 가져오기
            reversed_stops = []
            for stop_position in stopinfo.stop_positions:
                new_stop = Stop(
                    track_position=self.data.TrackPosition - end_station + offset,  # 역방향 stop + offset
                    station_index=self.total_stations_count - 1 - station_index,
                    forward_tolerance=stop_position.BackwardTolerance,
                    backward_tolerance=stop_position.ForwardTolerance,
                    direction=stop_position.Direction * -1,
                    number_of_cars=stop_position.Cars
                )
                reversed_stops.append(new_stop)

            target_block.StopPositions = reversed_stops

    def apply_station_index_at_block(self):
        """블록에 station 인덱스 할당
           블록을 뒤집은 후 실행
        """
        for i, station in enumerate(self.current_route.Stations):
            track_position = station.DefaultTrackPosition
            block_index = self.get_block_index(track_position)
            target_block = self.data.Blocks[block_index]
            target_block.Station = i  # 이미 역순으로 뒤집힌 상태라 i가 역방향 인덱스

    # 헬퍼 메서드
    def get_stop_trackposition_by_station_index(self, station_index: int):
        """station_index를 바탕으로 stop_trackposition 얻기"""
        stoppositions = []
        for block in self.data.Blocks:
            if block.StopPositions:
                for stopposition in block.StopPositions:
                    if stopposition.StationIndex == station_index:
                        stoppositions.append(stopposition.TrackPosition)
        return stoppositions

    def get_block_index(self, track_position: float):
        """주어진 track_position의 블록 인덱스 반환"""
        return int(math.floor(track_position / self.data.BlockInterval + 0.001))

    def reset_blocks(self):
        """모든 블록의 정거장 속성 stoppositions, station 초기화"""
        for block in self.data.Blocks:
            block.Station = -1
            block.StopPositions = []