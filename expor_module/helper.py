from openbve.OpenBveApi.Math.Vectors.Vector3 import Vector3
from openbve.OpenBveApi.World.Transformations import Transformation
from openbve.Plugins.RouteCsvRw.ObjectDictionary import ObjectDictionary


def calculate_world_position(origin_coord: Vector3,  track_position: float, starting_distance: float, world_side: Transformation, world_up: Transformation, world_direction: Transformation) -> Vector3:
    """
    월드좌표 계산 함수
    Arguments:
        origin_coord: 배치할 선로 중심 좌표
        track_position: 선로 중심 좌표의 측점(m)
        starting_distance: 설치할 좌표의 측점(m)
        world_direction:
    """
    worid_position = origin_coord.clone() # 안전하게 복사
    dz = track_position - starting_distance # 선로 중심 측점과 대상 측점의 거리차 계산
    worid_position += origin_coord.x * world_side.X + \
                     origin_coord.y * world_up.Y + \
                     dz * world_direction.Z
    return worid_position

def get_object_name(index: int, obj_dict: ObjectDictionary):
    """오브젝트 딕셔너리에서 인덱스로 이름 반환"""
    try:
        return obj_dict.get(index)
    except KeyError:
        return None