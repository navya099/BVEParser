import csv
import xml.etree.ElementTree as ET
import math
from expor_module.schemas import AlignmentRecord


class LandXMLExporter:
    @staticmethod
    def extract_and_save(alignments: list[AlignmentRecord], save_path: str):
        root = LandXMLExporter.create_landxml_templete()
        LandXMLExporter.create_alignment_templete(root, alignments)
        LandXMLExporter.save(root, save_path)

    @staticmethod
    def create_landxml_templete():
        # 1. XML Root 및 기본 구조 생성
        root = ET.Element("LandXML", {
            "version": "1.2",
            "xmlns": "http://www.landxml.org/schema/LandXML-1.2"
        })

        units = ET.SubElement(root, "Units")
        ET.SubElement(units, "Metric", {
            "areaUnit": "squareMeter",
            "linearUnit": "meter",
            "volumeUnit": "cubicMeter",
            "temperatureUnit": "celsius",
            "pressureUnit": "milliBars",
            "diameterUnit": "millimeter",
            "angularUnit": "decimal degrees",
            "directionUnit": "decimal degrees"
        })
        return root

    @staticmethod
    def create_alignment_templete(root, data: list[AlignmentRecord]):
        #기본 템플릿 작성
        route_length = data[-1].starting_distance #노선 길이
        startig_statiion = data[0].starting_distance #시작 측점

        alignments = ET.SubElement(root, "Alignments", {"name": ""})
        alignment = ET.SubElement(alignments, "Alignment", {
            "name": "VermouteExportedRoute",
            "length": str(route_length),
            "staStart": str(startig_statiion),
            "desc": "이 선형은 BVEEXporter에서 추출한 선형입니다.",
        })
        coord_geom = ET.SubElement(alignment, "CoordGeom")

        #루프 순회
        for i in range(len(data) - 1):
            #시작 선형, 끝선형
            start_al = data[i]
            end_al = data[i + 1]

            radius = start_al.radius
            #시작 방향벡터
            start_dir_y = start_al.direction_y
            start_dir_x = start_al.direction_x
            #끝 방향벡터
            end_dir_y = end_al.direction_y
            end_dir_x = end_al.direction_x

            start_azimuth_deg = math.degrees(math.atan2(start_dir_y, start_dir_x)) #시작 방위각(수학좌표계 도)
            end_azimuth_deg = math.degrees(math.atan2(end_dir_y, end_dir_x)) #끝 방위각(수학좌표계 도)

            p1_xy = start_al.x, start_al.y #시작 좌표ㅕ
            p2_xy = end_al.x, end_al.y #끝 좌표

            # 💡 직선 구간 판단
            if abs(radius) == 0.0 or abs(radius) > 900000.0:
                LandXMLExporter.create_straight_geom(coord_geom, start_azimuth_deg, p1_xy, p2_xy,)

            # 💡 곡선(Arc) 구간 판단
            else:
                LandXMLExporter.create_curve_geom(coord_geom, start_azimuth_deg, end_azimuth_deg, p1_xy, p2_xy, radius)

    @staticmethod
    def create_straight_geom(coord_geom, start_azimuth_deg, start_coord: tuple[float,float], end_coord: tuple[float,float]):
        """직선 구간 처리"""
        line_elem = ET.SubElement(coord_geom, "Line", {"dir": str(start_azimuth_deg), "length": '25.0'})

        start_pt = ET.SubElement(line_elem, "Start")
        start_pt.text = f"{start_coord[1]} {start_coord[0]}"

        end_pt = ET.SubElement(line_elem, "End")
        end_pt.text = f"{end_coord[1]} {end_coord[0]}"

    @staticmethod
    def create_curve_geom(coord_geom, start_azimuth_deg, end_azimuth_deg ,start_coord, end_coord, radius):
        """곡선 구간 처리"""
        #방향 판단
        rot = "cw" if radius > 0 else "ccw"
        from utils.curve_direction import CurveDirection
        curve_direction = CurveDirection.RIGHT if radius > 0 else CurveDirection.LEFT

        abs_radius = abs(radius)
        from utils.math_utils import calculate_simple_curve_geometry

        #곡선 제원 산출(반경, 교각ia(rad) , 접선장 tl, 중앙종거 m, 외할 sl

        r, ia, tl, m, sl = calculate_simple_curve_geometry(abs_radius, 25.0) #bve항상 25

        #좌표값을 미리 언팩
        p1_x, p1_y = start_coord
        p2_x, p2_y = end_coord

        # 💡 현의 길이(Chord) 계산 (시작점과 끝점 사이의 직선 거리)
        chord_length = math.hypot(p2_x - p1_x, p2_y - p1_y)

        curve_elem = ET.SubElement(coord_geom, "Curve", {
            "rot": rot,
            "chord": str(chord_length),
            "crvType": "arc",
            "delta": str(math.degrees(ia)),
            "dirEnd": str(end_azimuth_deg),
            "dirStart": str(start_azimuth_deg),
            "external": str(sl),
            "midOrd": str(m),
            "length": str(25.0),
            "radius": str(abs_radius),
            "tangent": str(tl)
        })

        #pi 구하기
        from utils.math_utils import intersection_of_two_lines
        pi = intersection_of_two_lines(p1=start_coord, angle1_deg=start_azimuth_deg, p2=end_coord, angle2_deg=end_azimuth_deg)

        #곡선 센터 구하기
        from utils.math_utils import calculate_curve_center
        center = calculate_curve_center(bc=start_coord, ec=end_coord, radius=radius, direction=curve_direction)

        start_pt = ET.SubElement(curve_elem, "Start")
        start_pt.text = f"{p1_y} {p1_x}"

        center_pt = ET.SubElement(curve_elem, "Center")
        center_pt.text = f"{center[1]} {center[0]}"

        end_pt = ET.SubElement(curve_elem, "End")
        end_pt.text = f"{p2_y} {p2_x}"

        pi_pt = ET.SubElement(curve_elem, "PI")
        if pi:
            pi_pt.text = f"{pi[1]} {pi[0]}"
        else:
            pi_pt.text = "0.0 0.0"

    @staticmethod
    def save(root, save_file_path, filename='alignment.xml'):
        # 4. XML 파일 저장
        import os
        path = os.path.join(save_file_path, filename)
        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ")
        tree.write(path, encoding="utf-8", xml_declaration=True)
        print(f"[Vermoute] LandXML (Line & Curve 혼합) 변환 완료: {path}")