import math

from ezdxf.math import chord_length

from utils.curve_direction import CurveDirection
import numpy as np

def _to_xy(p):
    """다양한 타입을 (x, y) 튜플로 변환"""
    if hasattr(p, "x") and hasattr(p, "y"):
        return float(p.x), float(p.y)


    if isinstance(p, (tuple, list, np.ndarray)) and len(p) >= 2:
        return float(p[0]), float(p[1])

    raise TypeError(f"Unsupported type {type(p)}")


def intersection_of_two_lines(p1: any, angle1_deg: float, p2: any, angle2_deg: float) -> tuple[float, float]:
    """두 점과 각도(도 단위)로 정의된 직선의 교점 계산"""
    p1 = _to_xy(p1)
    p2 = _to_xy(p2)

    # 도(Degree)를 라디안(Radian)으로 변환 후 기울기 계산
    m1 = math.tan(math.radians(angle1_deg))
    b1 = p1[1] - m1 * p1[0]

    m2 = math.tan(math.radians(angle2_deg))
    b2 = p2[1] - m2 * p2[0]

    if math.isclose(m1, m2):
        return None  # 평행이면 교점 없음

    x = (b2 - b1) / (m1 - m2)
    y = m1 * x + b1
    return x, y


def calculate_curve_center(bc, ec, radius: float, direction: CurveDirection) -> tuple[float, float]:
    """두 점(BC, EC)과 반지름, 방향으로 원의 중심 좌표 계산"""
    bc = _to_xy(bc)
    ec = _to_xy(ec)
    dx = ec[0] - bc[0]
    dy = ec[1] - bc[1]
    d = math.hypot(dx, dy)

    if d == 0 or d > 2 * abs(radius):
        raise ValueError("Invalid BC/EC distance for given radius")

    # 중점
    mx = (bc[0] + ec[0]) / 2
    my = (bc[1] + ec[1]) / 2

    # chord의 수직거리 h
    h = math.sqrt(radius ** 2 - (d / 2) ** 2)

    # 단위 수직벡터
    ux = -dy / d
    uy = dx / d

    # 방향 선택 (1=RIGHT, 0=LEFT)
    sign = -1 if direction == CurveDirection.RIGHT else 1

    # 중심 좌표 계산
    cx = mx + sign * ux * h
    cy = my + sign * uy * h

    return cx, cy

def calculate_simple_curve_geometry(radius: float, cl: float) -> tuple:
    """R과 CL로 단곡선 제원 계산"""
    r = abs(radius)  # 곡선반경
    ia = cl / r  # 교각 (라디안)

    tl = r * math.tan(ia / 2)  # 접선장
    m = r * (1 - math.cos(ia / 2))  # 중앙종거
    sl = r * (1 / math.cos(ia / 2) - 1)  # 외거
    return r, ia, tl, m, sl