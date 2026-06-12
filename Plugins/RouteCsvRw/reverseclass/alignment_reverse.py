from Plugins.RouteCsvRw.RouteData import RouteData
from RouteManager2.CurrentRoute import CurrentRoute


class AlignmentReverse:
    """선형(곡선, 캔트, 구배) 역방향 변환 클래스 (1칸 시프트 교정판)"""

    @staticmethod
    def reverse_alignment(block, next_block=None):
        """
        레일 좌표는 점 데이터라 그대로 두면 맞지만, 선형(곡선/구배)은 구간 데이터이므로
        'next_block(정방향 시절 내 한 칸 앞 상자)'의 데이터를 가져와 부호를 반전시켜야
        철길 좌표 축과 선형 도화지의 타이밍이 100% 일치하게 됩니다.
        """
        if next_block:
            # 1. 메인 선로 곡선 반전 (우곡선 <-> 좌곡선)
            # 역방향 진행 기준 다음 칸의 곡률 반경을 가져와 부호를 반전시킵니다.
            orig_radius = next_block.CurrentTrackState.CurveRadius
            block.CurrentTrackState.CurveRadius = -orig_radius if orig_radius != 0.0 else 0.0

            # 2. 캔트(Cant) 방향 반전
            orig_cant = next_block.CurrentTrackState.CurveCant
            block.CurrentTrackState.CurveCant = -orig_cant if orig_cant != 0.0 else 0.0

            # 3. 종단구배 반전 (오르막 <-> 내리막)
            # 올라가던 고개는 거꾸로 달리면 내려가는 고개(-)가 됩니다.
            # block.Pitch와 block.CurrentTrackState.Pitch의 정적 동기화를 보장합니다.
            orig_pitch = next_block.CurrentTrackState.Pitch
            if orig_pitch != 0.0:
                block.CurrentTrackState.Pitch = -orig_pitch
                if hasattr(block, 'Pitch'):
                    block.Pitch = -orig_pitch
            else:
                block.CurrentTrackState.Pitch = 0.0
                if hasattr(block, 'Pitch'):
                    block.Pitch = 0.0
        else:
            # 💡 [역방향 종단 방어 마감]
            # 역방향 루트의 완전히 마지막 최종 블록은 뒤에 읽어올 앞 상자가 없으므로,
            # 안전하게 평탄한 직선 선로(0.0) 상태로 초기화하여 선형을 폐합합니다.
            block.CurrentTrackState.CurveRadius = 0.0
            block.CurrentTrackState.CurveCant = 0.0
            block.CurrentTrackState.Pitch = 0.0
            if hasattr(block, 'Pitch'):
                block.Pitch = 0.0