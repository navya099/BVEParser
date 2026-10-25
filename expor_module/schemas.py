from dataclasses import dataclass

@dataclass
class AlignmentRecord:
    """BVE 선로 데이터를 추출하기 위한 데이터셋
    Attributes:
        starting_distance: 측점(m)
        x: 절대좌표 x
        y: 절대좌표 y
        z: 절대좌표 y
        direction_x: 방향벡터 (WorldDirection) x
        direction_y: 방향벡터 (WorldDirection) y
        direction_z: 방향벡터 (WorldDirection) z
        side_x: 좌우 방향 벡터 (WorldSide) x
        side_y: 좌우 방향 벡터 (WorldSide) y
        side_z: 좌우 방향 벡터 (WorldSide) z
        up_x: 상하 방향 벡터 (WorldUp) x
        up_y: 상하 방향 벡터 (WorldUp) y
        up_z: 상하 방향 벡터 (WorldUp) z
        curve_cant: 캔트(m)
        pitch: 구배(0.001)
        radius: 곡선 반경(m). 음수이면 좌측 양수면 우측
    """
    starting_distance: float  # 측점 (m)
    x: float
    y: float
    z: float                  # 선로 중심 월드 좌표
    direction_x: float
    direction_y: float
    direction_z: float

    side_x: float
    side_y: float
    side_z: float             # 좌우 방향 벡터 (WorldSide)
    up_x: float
    up_y: float
    up_z: float               # 상하 방향 벡터 (WorldUp)
    curve_cant: float         # 캔트
    pitch: float              # 구배
    radius: float             # 곡선반경

@dataclass
class StructureRecord:
    """BVE구조물 정보 추출을 위한 데이터클래스
    Attributes:
        starting_distance: 측점(m)
        category: 분류( wall, dike, freeobj , form, 등)
        rail_key: 배치 기준 레일 인덱스
        object_name: 오브젝트 명칭
        x: 오브젝트 최종 x좌표
        y: 오브젝트 최종 y좌표
        z: 오브젝트 최종 z좌표
    """
    starting_distance: float
    category: str             # 구분 ("wall" 등)
    rail_key: int
    object_name: str          # 오브젝트 명칭/인덱스
    x: float
    y: float
    z: float                  # 오브젝트 최종 좌표