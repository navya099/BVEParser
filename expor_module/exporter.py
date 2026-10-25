import os
import csv
import json
from dataclasses import asdict

from Plugins.RouteCsvRw.RouteData import RouteData
from RouteManager2.CurrentRoute import CurrentRoute
from .dxf_exporter import DXFManger
from .helper import calculate_world_position, get_object_name
from .landxml_exporter import LandXMLExporter
from .schemas import AlignmentRecord, StructureRecord

class BVEExporter:
    def __init__(self, output_dir: str = r"c:\temp\BVEExporter_output"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def extract_and_save(self, data: RouteData, current_route: CurrentRoute) -> bool:
        """
        apply_route_data 완료 후 RouteData에서 데이터를 추출하여 저장합니다.
        """
        try:
            # 선형 순회
            alignments = self.extract_alignment(current_route)

            # 2. 구조물 추출
            structures = self.extract_structure(data, current_route)

            # 파일 덤프 실행
            self._save_csv(alignments, "alignment.csv")
            self._save_json(structures, "structures.json")
            #LANDXML 추출
            LandXMLExporter.extract_and_save(alignments, self.output_dir)
            #dxf 추출
            dxfmgr = DXFManger()
            dxfmgr.create_dxf(alignments, output_dir=self.output_dir, filename="alignment.dxf")
            print(f"[Vermoute] 데이터 추출 완료! 저장 위치: {self.output_dir}")
            return True
        except Exception as e:
            print(f"[Vermoute] 데이터 추출 예외 발생!\n {e}")
            return False

    def extract_alignment(self, current_route: CurrentRoute):
        """선형 추출 메서드"""

        alignments = []

        """
        current_route.tracks =railkey track 딕셔너리
        track.elements =element 리스트
        element[i].StartingTrackPosition = i * 25
        """
        import copy
        elements = copy.deepcopy(current_route.Tracks[0].Elements) # 안전하게 복사
        last_station = -1.0  # 이전 측점 기록용 변수
        for elem in elements:
            # 1. 선형 데이터 추출 (메인 레일 Rail 0 기준)
            if elem:
                station = elem.StartingTrackPosition
                # 💡 핵심 방어 로직:
                # 측점이 이전보다 작아지거나(역행), 유효한 진행 후 갑자기 0으로 리셋되면
                # 빈 객체(Uninitialized Padding) 영역에 진입한 것이므로 즉시 중단합니다.
                if last_station >= 0 and station <= last_station:
                    break
                last_station = station
                pos = elem.WorldPosition
                side = elem.WorldSide
                up = elem.WorldUp
                direction = elem.WorldDirection
                alignments.append(AlignmentRecord(
                    starting_distance=station,
                    x=pos.x,
                    y=pos.z, # BVE 전후(Z) -> 3D 툴 깊이(Y)
                    z=pos.y, # BVE 전후(Z) -> 3D 툴 깊이(Y)
                    direction_x=direction.x, # BVE 전후(Z) -> 3D 툴 깊이(Y)
                    direction_y=direction.z, # BVE 전후(Z) -> 3D 툴 깊이(Y)
                    direction_z=direction.y, # BVE 전후(Z) -> 3D 툴 깊이(Y)
                    side_x=side.x,
                    side_y=side.z, # BVE 전후(Z) -> 3D 툴 깊이(Y)
                    side_z=side.y, # BVE 전후(Z) -> 3D 툴 깊이(Y)
                    up_x=up.x,
                    up_y=up.z,  # BVE 전후(Z) -> 3D 툴 깊이(Y)
                    up_z=up.y,  # BVE 전후(Z) -> 3D 툴 깊이(Y)
                    curve_cant=getattr(elem, 'CurveCant', 0.0),
                    pitch=getattr(elem, 'Pitch', 0.0),
                    radius=getattr(elem, 'CurveRadius', 0.0),
                ))
            else:
                raise AttributeError("선형 데이터가 비어있습니다.")
        return alignments

    def extract_structure(self, data: RouteData, current_route: CurrentRoute):
        structures = []
        block_interval = getattr(data, 'BlockInterval', 25.0)  # 기본 블록 간격 (보통 25m)

        # 블록 순회 (인덱스와 함께 가져옴)
        for i, block in enumerate(data.Blocks):
            starting_distance = i * block_interval

            # 1. 해당 측점에 일치하는 트랙 엘리먼트 안전하게 찾기
            track_elements = current_route.Tracks[0].Elements
            track_element = next((el for el in track_elements if el.StartingTrackPosition == starting_distance), None)

            if not track_element:
                continue  # 일치하는 트랙 정보가 없으면 스킵

            # 2. 벽체(RailWall) 데이터 추출 및 월드 좌표 계산
            if hasattr(block, 'RailWall') and block.RailWall:
                for rail_key, wall_data in block.RailWall.items():
                    if not wall_data.exists:
                        continue
                    index = wall_data.object_type
                    # 헬퍼 함수를 통한 3D 월드 좌표 산출(world_pos =Vector3)
                    world_pos = calculate_world_position(
                        origin_coord=track_element.WorldPosition,
                        track_position=track_element.StartingTrackPosition,
                        starting_distance=0.0, #wall , dike 등 오브젝트는 항상 25 고정
                        world_side=track_element.WorldSide,
                        world_up=track_element.WorldUp,
                        world_direction=track_element.WorldDirection
                    )

                    # 3. 레일 인덱스를 배제하고 순수 월드 좌표 기반 레코드로 적재
                    structures.append(StructureRecord(
                        starting_distance=starting_distance,
                        category="wall",
                        rail_key=rail_key,
                        object_name=get_object_name(index, data.Structure.WallL),
                        x=world_pos.x,
                        y=world_pos.z, # BVE 전후(Z) -> 3D 툴 깊이(Y)
                        z=world_pos.y  # BVE 전후(Z) -> 3D 툴 깊이(Y)
                    ))

        return structures

    def _save_csv(self, records, filename):
        if not records:
            return
        path = os.path.join(self.output_dir, filename)
        fields = list(asdict(records[0]).keys())
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for r in records:
                writer.writerow(asdict(r))

    def _save_json(self, records, filename):
        path = os.path.join(self.output_dir, filename)
        data_list = [asdict(r) for r in records]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data_list, f, ensure_ascii=False, indent=4)