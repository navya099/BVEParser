from Plugins.RouteCsvRw.RouteData import RouteData
from RouteManager2.CurrentRoute import CurrentRoute


class RailReverse:
    """레일 역방향 변환 클래스"""
    @staticmethod
    def reverse_rail(block):
        # 타 레일(부본선 등) 위치 좌표 수정
        for key, rail in block.Rails.items():
            # 좌우 오프셋 반전
            rail.RailStart.x = -rail.RailStart.x
            rail.RailEnd.x = -rail.RailEnd.x
            if hasattr(rail, 'MidPoint'):
                rail.MidPoint.x = -rail.MidPoint.x

            # 타 레일의 곡선/캔트 반전
            rail.CurveCant = -rail.CurveCant

            # bool 속성 반전
            current_is_started = rail.RailStarted
            current_is_ended = rail.RailEnded
            # 3. [핵심] bool 속성 완벽 반전 (Swap)
            # 정방향의 시작점은 역방향의 끝점으로, 정방향의 끝점은 역방향의 시작점으로 바꿉니다.
            rail.RailStarted, rail.RailEnded = rail.RailEnded, rail.RailStarted