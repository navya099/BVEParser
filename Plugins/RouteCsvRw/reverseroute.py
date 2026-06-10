import math

from Plugins.RouteCsvRw.RouteData import RouteData
import copy
from loggermodule import logger
from RouteManager2.CurrentRoute import CurrentRoute


class RouteReverser:
    """역방향 루트 생성을 위한 리버서"""
    def __init__(self, data: RouteData):

        self.data = data
    def convert_to_reverse_route(self):
        """역방향 실행 메서드"""
        current_track_position = None
        current_track_position_freeobj = None
        # 1. 블록 리스트를 역순으로 뒤집기
        self.data.Blocks.reverse()

        # 2. 역방향 기하학적 요소 변경
        for i in range(len(self.data.Blocks)):
            block = self.data.Blocks[i]
            last_block = self.data.Blocks[-1]
            last_track_position = self.data.TrackPosition
            current_track_position = i * self.data.BlockInterval
            current_reverse_track_position = last_track_position - current_track_position
            # 종단구배 반전 (오르막 <-> 내리막)
            current_pitch = block.Pitch
            block.Pitch = -current_pitch

            # 메인 선로 곡선 반전 (우곡선 <-> 좌곡선)
            if block.CurrentTrackState.CurveRadius != 0.0:
                current_radius = block.CurrentTrackState.CurveRadius
                block.CurrentTrackState.CurveRadius = -current_radius

            # 캔트(Cant) 방향도 반전
            if block.CurrentTrackState.CurveCant != 0.0:
                current_cant = block.CurrentTrackState.CurveCant
                block.CurrentTrackState.CurveCant = -current_cant

            # 타 레일(부본선 등) 위치 좌표 수정
            for key, rail in block.Rails.items():
                # 좌우 오프셋 반전
                rail.RailStart.x = -rail.RailStart.x
                rail.RailEnd.x = -rail.RailEnd.x
                if hasattr(rail, 'MidPoint'):
                    rail.MidPoint.x = -rail.MidPoint.x

                # 타 레일의 곡선/캔트 반전
                rail.CurveCant = -rail.CurveCant

            # Free Object(지상물)들의 좌우 오프셋 방향 반전 필요 시
            # free_obj.X = -free_obj.X 형태의 로직을 추가할 수 있습니다.

    def preprocess_reverse_route(self, current_route: CurrentRoute):
        """역방향 루트 생성 전 원본 루트에서 필요한 값 추출"""

        # 600m 여유 블록을 제외하고, 실제 선로 데이터가 끝나는 정확한 블록 인덱스 계산
        # 예: TrackPosition이 1000m이고 Interval이 25m이면, 정확히 40번 블록이 데이터의 끝입니다.
        actual_last_idx = int(self.data.TrackPosition / self.data.BlockInterval)

        elements = current_route.Tracks[0].Elements
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
            current_route.Atmosphere.InitialX = last_world_pos.x
            current_route.Atmosphere.InitialY = last_world_pos.z
            current_route.Atmosphere.InitialElevation = last_world_pos.y
            current_route.Atmosphere.InitialDirection = reverse_degree

            logger.debug(f'실제 종점 데이터 매칭 성공 (인덱스: {last_element_idx}) - X: {last_world_pos.x}, Z: {last_world_pos.z}')