import collections
import math
import os
from RouteManager2.CurrentRoute import CurrentRoute
from Plugins.RouteCsvRw.RouteData import RouteData
from loggermodule import logger

class CreateRouteFILE:
    @staticmethod
    def save_csv(srializedata, block_interval: float):
        """트리 구조의 데이터를 BVE CSV 공식 문법 문자열로 변환하여 파일 저장"""
        csv_lines = []

        # 1. Options & Route 헤더 영역 작성
        if 'BlockLength' in srializedata['OptionsCommand']:
            csv_lines.append(f"With Options\n.BlockLength {srializedata['OptionsCommand']['BlockLength']}")

        csv_lines.append("With Route")
        if 'Comment' in srializedata['RouteCommand']:
            csv_lines.append(f".Comment {srializedata['RouteCommand']['Comment']}")
        csv_lines.append(f".Elevation {srializedata['RouteCommand']['Elevation']}")
        csv_lines.append(f".PositionX {srializedata['RouteCommand']['PositionX']}")
        csv_lines.append(f".PositionY {srializedata['RouteCommand']['PositionY']}")
        csv_lines.append(f".Direction {srializedata['RouteCommand']['Direction']}")

        # 💡 3. [신설] 오브젝트 사전 정의(Structure) 명령어 삽입 영역
        csv_lines.append("\n;=========================================================")
        csv_lines.append("; STRUCTURE OBJECT DEFINITIONS")
        csv_lines.append(";=========================================================")
        # With Track 이전에 선언되어야 오픈BVE 엔진이 3D 구조물 리소스를 정상 인지합니다.
        if 'StructureCommand' in srializedata and srializedata['StructureCommand']:
            for obj_cmd in srializedata['StructureCommand']:
                csv_lines.append(obj_cmd)
            csv_lines.append("")  # 가독성을 위한 공백 패딩

        csv_lines.append("With Track")

        # 2. Track 명령어 영역 거리순 정렬 추출
        sorted_distances = sorted(list(srializedata['TrackCommand'].keys()))

        for dist in sorted_distances:
            block_data = srializedata['TrackCommand'][dist]

            # ① 곡선 (.curve) 문법 조립
            radius = block_data['Curve']['radius']
            cant = block_data['Curve']['cant']
            csv_lines.append(f"{dist},.curve {radius};{cant * 1000.0}")

            # ② 구배 (.pitch) 문법 조립
            pitch = block_data['Pitch']
            csv_lines.append(f"{dist},.pitch {pitch * 1000.0}")

            # ③ [핵심 교정] 레일 (.rail / .railend) 문법 조립
            if 'Rail' in block_data:
                # 레일 인덱스 번호 순서대로 정렬하여 출력 규칙 준수
                for rail_idx in sorted(list(block_data['Rail'].keys())):
                    rail_info = block_data['Rail'][rail_idx]
                    stttype = rail_info.get('object_type', None)
                    if stttype is None:
                        stttype = 0
                    if rail_idx == 0:
                        csv_lines.append(f"{dist},.railtype {rail_idx};{stttype};")
                        continue  # 자선(0번)은 railtype구문만 존재로 railtype구문 생성후 스킵
                    # defaultdict의 부작용을 막기 위해 안전하게 .get()으로 커맨드 타입을 읽어옵니다.
                    cmd_type = rail_info.get('command')

                    # 💡 물리적 인덱스 기준에 따라 발급된 단어만 골라서 출력합니다.
                    if cmd_type == 'rail':
                        # 역방향 루트의 맨 첫 블록 (i == 0 지점)
                        csv_lines.append(f"{dist},.rail {rail_idx};{rail_info['x']};{rail_info['y']};{stttype};")
                    elif cmd_type == 'railend':
                        # 역방향 루트의 맨 마지막 블록 (i == total_blocks - 1 지점)
                        csv_lines.append(f"{dist},.railend {rail_idx};{rail_info['x']};{rail_info['y']}")
                    elif cmd_type == 'KeepAlive':
                        # 💡 거대한 중간 구간 마디들은 .rail을 중복 선언하면 선로가 찢어집니다!
                        # 문법을 출력하지 않고 그냥 패스함으로써 선로의 무한 연속성을 보장합니다.
                        pass

            # ④ 정거장 (.sta) 및 정차 마커 (.stop) 문법 조립
            if 'Station' in block_data and 'Name' in block_data['Station']:
                st_name = block_data['Station']['Name']
                csv_lines.append(f"{dist},.sta {st_name};")

            # stop 위치
            if 'Stop' in block_data:
                # 💡 [교정 핵심] .values()를 통해 딕셔너리에 저장된 stop.TrackPosition 실제 값을 추출합니다.
                for actual_stop_pos in block_data['Stop'].values():
                    # actual_stop_pos는 이미 변환 과정에서 역방향 기준으로 가공된 절대 거리 좌표입니다.
                    # BVE 문법 규칙에 맞게 절대 거리 헤더를 붙여 출력합니다.
                    csv_lines.append(f"{actual_stop_pos},.stop 0;")
            #height
            if 'Height' in block_data:
                csv_lines.append(f"{dist},.Height {block_data['Height']};")

            # 💡 ④ [신설] 지상물 오브젝트 (.freeobj) 문법 조립
            # 정밀 절대 위치(actual_obj_pos)를 거리 헤더로 취하여 공간 무결성을 완벽히 보존합니다.
            if 'FreeObj' in block_data and block_data['FreeObj']:
                for fobj in block_data['FreeObj']:
                    actual_obj_pos = fobj['track_position']

                    # 라디안/도 변환 오차를 고려해 안전하게 소수점 포맷팅 제어
                    # 문법: 거리,.freeobj 레일번호;종류번호;X;Y;Yaw;Pitch;Roll
                    freeobj_string = (
                        f"{actual_obj_pos:.2f},.freeobj {fobj['RailIndex']};{fobj['StructureType']};"
                        f"{fobj['x']:.3f};{fobj['y']:.3f};{math.degrees(fobj['yaw']):.2f};{math.degrees(fobj['pitch']):.2f};{math.degrees(fobj['roll']):.2f}"
                    )
                    csv_lines.append(freeobj_string)
            #pole
            if 'Pole' in block_data:
                # 수집단에서 정의한 rail_idx 순서대로 정렬 순회
                for rail_idx in sorted(list(block_data['Pole'].keys())):
                    pole_info = block_data['Pole'][rail_idx]
                    is_existing = pole_info['exists']

                    if is_existing:
                        # ➔ 깔끔하게 .pole 출력
                        csv_lines.append(
                            f"{dist},.pole {rail_idx};{pole_info['mode']};{pole_info['loc']:.2f};"
                            f"{pole_info['interval']:.1f};{pole_info['type']}"
                        )
                    else:
                        # ➔ 정확한 위치에서 .poleend 출력
                        csv_lines.append(f"{dist},.poleend {rail_idx}")
            #dike
            if 'Dike' in block_data:
                # 수집단에서 정의한 rail_idx 순서대로 정렬 순회
                for rail_idx in sorted(list(block_data['Dike'].keys())):
                    dike_info = block_data['Dike'][rail_idx]
                    is_existing = dike_info['exists']
                    if is_existing:
                        # ➔ 깔끔하게 .dike 출력
                        csv_lines.append(
                            f"{dist},.Dike {rail_idx};{dike_info['direction']};{dike_info['object_type']};"
                        )
                    else:
                        # ➔ 정확한 위치에서 .poleend 출력
                        csv_lines.append(f"{dist},.DikeEnd {rail_idx}")
            # wall
            if 'Wall' in block_data:
                # 수집단에서 정의한 rail_idx 순서대로 정렬 순회
                for rail_idx in sorted(list(block_data['Wall'].keys())):
                    wall_info = block_data['Wall'][rail_idx]
                    is_existing = wall_info['exists']
                    if is_existing:
                        # ➔ 깔끔하게 .Wall 출력
                        csv_lines.append(
                            f"{dist},.Wall {rail_idx};{wall_info['direction']};{wall_info['object_type']};"
                        )
                    else:
                        # ➔ 정확한 위치에서 Wallend 출력
                        csv_lines.append(f"{dist},.WallEnd {rail_idx}")
        # 3. 실제 파일 쓰기
        import os
        os.makedirs('c:/temp', exist_ok=True)
        with open('c:/temp/route_reversed.csv', 'w', encoding='utf-8') as f:
            for line in csv_lines:
                f.write(line + '\n')

        print("🎉 [Exporter] 역방향 2-Pass 대응 CSV 빌드 완료! (c:/temp/route_reversed.csv)")