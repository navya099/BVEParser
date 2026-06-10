from Plugins.RouteCsvRw.RouteData import RouteData
from Plugins.RouteCsvRw.Structures.Block import Block
from RouteManager2.CurrentRoute import CurrentRoute


class StationReverse:
    """정거장 역방향 변환 클래스"""

    def __init__(self, data: RouteData, current_route: CurrentRoute):
        # [교정] 생성자 매개변수 순서를 RouteReverser 호출부와 완벽히 일치시켰습니다.
        self.data = data
        self.current_route = current_route
        self.total_stations_count = len(current_route.Stations)

    def reverse_stations(self):
        """전체 역 목록 자체를 역순으로 1회 스왑하고 속성을 변경합니다."""
        original_stations = self.current_route.Stations
        reversed_stations = []

        for index in range(self.total_stations_count - 1, -1, -1):
            station = original_stations[index]
            # 출입문 개방 방향을 좌우 반전
            station.OpenLeftDoors, station.OpenRightDoors = station.OpenRightDoors, station.OpenLeftDoors
            reversed_stations.append(station)

        self.current_route.Stations = reversed_stations

    def reverse_block_station_id(self, block: Block):
        """[신설] 블록이 뒤집히기 전에 정방향 기준 역 ID를 먼저 리버스 ID로 변환합니다."""
        if block.Station >= 0:
            block.Station = self.total_stations_count - 1 - block.Station

    def reverse_stoppositions(self, i: int, block: Block):
        """블록이 뒤집힌 후, 각 블록 내부의 정차 위치 마커들을 재정렬합니다."""
        for stop in block.StopPositions:
            # 역 ID 재매칭 (이미 block.Station은 위에서 변환했으므로 stop도 동일하게 매칭)
            stop.StationIndex = self.total_stations_count - 1 - stop.StationIndex

            # 전방/후방 허용 오차(Tolerance) 스왑
            stop.ForwardTolerance, stop.BackwardTolerance = stop.BackwardTolerance, stop.ForwardTolerance

            # 역방향 기준으로 변환된 정밀 트랙 포지션 주입
            stop.TrackPosition = i * self.data.BlockInterval