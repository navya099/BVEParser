import math
from copy import deepcopy

from Plugins.RouteCsvRw.Structures.Block import Block
from Plugins.RouteCsvRw.Structures.Route.Pole import Pole


class ObjectReverse:
    """지상물(Free Object) 역방향 변환 클래스"""

    @staticmethod
    def reverse_objects(block: Block, last_track_position: float):
        """블록 내의 GroundFreeObj와 RailFreeObj를 모두 완벽하게 반전시킵니다."""

        # 1. 월드 바닥 기준 지상물 (GroundFreeObj) 반전
        if hasattr(block, 'GroundFreeObj') and block.GroundFreeObj:
            for free_obj in block.GroundFreeObj:
                ObjectReverse._apply_reverse(free_obj, last_track_position)

        # 2. 특정 레일 종속 지상물 (RailFreeObj) 반전
        if hasattr(block, 'RailFreeObj') and block.RailFreeObj:
            for rail_key in block.RailFreeObj:
                for free_obj in block.RailFreeObj[rail_key]:
                    ObjectReverse._apply_reverse(free_obj, last_track_position)

    @staticmethod
    def _apply_reverse(free_obj, last_track_position):
        """개별 FreeObj 객체의 좌표와 회전각을 기하학적으로 역산합니다."""
        # ① 좌우 오프셋 반전 (파서 명세에 따른 Position.x 추적)
        if hasattr(free_obj, 'Position') and free_obj.Position is not None:
            free_obj.Position.x = -free_obj.Position.x
        elif hasattr(free_obj, 'X'):  # 혹시 모를 하위 호환성 대비
            free_obj.X = -free_obj.X

        # ② Yaw(진행 방향 회전각) 반전
        # 파서 원형에서 math.radians(yaw)로 주입했으므로 라디안(math.pi) 기준으로 계산합니다.
        if hasattr(free_obj, 'Yaw'):
            free_obj.Yaw = (free_obj.Yaw + math.pi) % (2.0 * math.pi)

        #station 반전
        if hasattr(free_obj, 'TrackPosition'):
            free_obj.TrackPosition = last_track_position - free_obj.TrackPosition
    @staticmethod
    def reverse_poles(block: Block, next_block: Block = None):
        """
        블록 내부의 RailPole(전신주)들의 좌우 위치를 반전시키고 구간 타이밍을 정렬합니다.
        구간 데이터의 특성을 고려하여 next_block의 상태를 시프트 수혈합니다.
        """
        # 현재 블록에 RailPole 리스트 속성이 없다면 빈 리스트로 초기화 방어
        if not hasattr(block, 'RailPole') or block.RailPole is None:
            block.RailPole = []

        if next_block and hasattr(next_block, 'RailPole') and next_block.RailPole:
            for idx, orig_pole in enumerate(next_block.RailPole):
                # 💡 [교정 2] 참조 오염을 원천 차단하기 위해 deepcopy 기법 도입
                # 인덱스를 확장할 때 독립된 새 인스턴스로 깊은 복사하여 채워넣습니다.
                if idx >= len(block.RailPole):
                    block.RailPole.append(deepcopy(orig_pole))

                # 내 앞 블록(next_block)의 물리적 속성을 내 현재 마디로 정밀 이식
                block.RailPole[idx].Exists = orig_pole.Exists
                block.RailPole[idx].Mode = orig_pole.Mode
                block.RailPole[idx].Type = orig_pole.Type
                block.RailPole[idx].Interval = orig_pole.Interval

                # 💡 좌우 대칭 반전 (Location 부호 반전으로 완벽한 좌우 미러링)
                block.RailPole[idx].Location = -orig_pole.Location
        else:
            # 타겟 영역이 없는 마지막 종착 블록 마디는 전신주 루프 종료 플래그(False) 강제 하강
            for pole in block.RailPole:
                pole.Exists = False