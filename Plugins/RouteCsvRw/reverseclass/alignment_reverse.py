from Plugins.RouteCsvRw.RouteData import RouteData
from RouteManager2.CurrentRoute import CurrentRoute


class AlignmentReverse:
    """선형 역방향 변환 클래스"""
    @staticmethod
    def reverse_alignment(block):
        # 종단구배 반전 (오르막 <-> 내리막)
        if block.CurrentTrackState.Pitch != 0.0:
            current_pitch = block.Pitch
            block.Pitch = -current_pitch
            block.CurrentTrackState.Pitch = -current_pitch

        # 메인 선로 곡선 반전 (우곡선 <-> 좌곡선)
        if block.CurrentTrackState.CurveRadius != 0.0:
            current_radius = block.CurrentTrackState.CurveRadius
            block.CurrentTrackState.CurveRadius = -current_radius

        # 캔트(Cant) 방향도 반전
        if block.CurrentTrackState.CurveCant != 0.0:
            current_cant = block.CurrentTrackState.CurveCant
            block.CurrentTrackState.CurveCant = -current_cant