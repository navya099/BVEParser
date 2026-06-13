import math
from Plugins.RouteCsvRw.Structures.Block import Block

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