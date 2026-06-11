import collections
import os
from RouteManager2.CurrentRoute import CurrentRoute
from Plugins.RouteCsvRw.RouteData import RouteData


class CreateRouteFILE:
    @staticmethod
    def serialize_route_data(current_route: CurrentRoute, data: RouteData):
        def tree():
            return collections.defaultdict(tree)

        srializedata = tree()

        # 1. OPTIONS 섹션
        CreateRouteFILE.serialize_option_command(current_route, srializedata)
        # 2. 루트 네임스페이스 섹션
        CreateRouteFILE.serialize_route_command(current_route, srializedata)
        # 3. 트랙 네임스페이스 섹션
        CreateRouteFILE.serialize_track_command(current_route, data, srializedata)

        # 4. CSV 파일 조립 및 디스크 작성
        CreateRouteFILE.save_csv(srializedata, data.BlockInterval)
        return srializedata

    @staticmethod
    def serialize_option_command(current_route: CurrentRoute, srializedata):
        srializedata['OptionsCommand']['BlockLength'] = current_route.BlockLength

    @staticmethod
    def serialize_route_command(current_route: CurrentRoute, srializedata):
        srializedata['RouteCommand']['Comment'] = current_route.Comment
        srializedata['RouteCommand']['Elevation'] = current_route.Atmosphere.InitialElevation
        srializedata['RouteCommand']['PositionX'] = current_route.Atmosphere.InitialX
        srializedata['RouteCommand']['PositionY'] = current_route.Atmosphere.InitialY
        srializedata['RouteCommand']['Direction'] = current_route.Atmosphere.InitialDirection

    @staticmethod
    def serialize_track_command(current_route: CurrentRoute, data: RouteData, srializedata):
        total_blocks = len(data.Blocks)

        for i, block in enumerate(data.Blocks):
            track_position = i * data.BlockInterval

            # 선형 요소 직렬화
            srializedata['TrackCommand'][track_position]['Curve']['radius'] = block.CurrentTrackState.CurveRadius
            srializedata['TrackCommand'][track_position]['Curve']['cant'] = block.CurrentTrackState.CurveCant
            srializedata['TrackCommand'][track_position]['Pitch'] = block.CurrentTrackState.Pitch

            # 💡 다음 블록에 존재하는 레일 인덱스 세트 미리 추출 (Look-Ahead)
            next_block_rails = set()
            if i < total_blocks - 1:
                next_block = data.Blocks[i + 1]
                for n_key, n_rail in next_block.Rails.items():
                    # 다음 블록에서 유효한 유령이 아닌 레일만 수집
                    if n_rail.RailStarted or n_rail.RailEnded or n_rail.RailStartRefreshed:
                        next_block_rails.add(n_key)

            # 레일 요소 직렬화
            for key, rail in block.Rails.items():
                current_sttype = block.RailType[key]
                if key == 0:
                    continue  # 자선 스킵

                # 완벽한 공백 유령 레일 객체 필터링 (순수 무효 데이터 드롭)
                if not rail.RailStarted and not rail.RailEnded and not rail.RailStartRefreshed:
                    continue

                rail_data = srializedata['TrackCommand'][track_position]['Rail'][key]
                rail_data['x'] = rail.RailStart.x
                rail_data['y'] = rail.RailStart.y
                rail_data['refreshed'] = rail.RailStartRefreshed
                rail_data['driveable'] = rail.IsDriveable
                rail_data['object_type'] = current_sttype

                # 💡 [핵심 Look-Ahead 종단 판정 규칙]
                # 현재 블록에는 이 레일이 살아있는데, 바로 다음 블록(역방향 진행 방향)에는 레일이 없다면?
                # 혹은 현재 블록이 역방향의 완전히 마지막 블록(i == total_blocks - 1)이라면?
                # ➔ 조건 불문하고 이곳이 이 레일이 폐합되어야 하는 절대 종점(.railend)입니다!
                if (key not in next_block_rails) or (i == total_blocks - 1):
                    rail_data['x'] = rail.RailEnd.x  # 유종의 미를 거두기 위해 끝점 좌표 매핑
                    rail_data['y'] = rail.RailEnd.y
                    rail_data['command'] = 'railend'
                    continue  # 종점 판정 완료되었으므로 아래 일반 분기 스킵

                # 2) 종점이 아닐 경우, 기존 플래그 조합 기반 분기 준수
                if rail.RailStarted and not rail.RailEnded:
                    # 구 정방향 종점 마디 ➔ 역방향 시점에서는 새로운 선로의 기점 (.rail 5)
                    rail_data['command'] = 'rail'
                elif rail.RailEnded and not rail.RailStarted:
                    # 구 정방향 시점 마디 ➔ 역방향 종점 (위의 Look-Ahead가 이미 처리하겠지만 이중 방어)
                    rail_data['x'] = rail.RailEnd.x
                    rail_data['y'] = rail.RailEnd.y
                    rail_data['command'] = 'railend'
                else:
                    # 그 외 중간에 연속적으로 살아 통과하는 구간은 전부 유지 판정
                    rail_data['command'] = 'KeepAlive'

            # 역(Station) 요소 직렬화
            if block.Station >= 0 and block.Station < len(current_route.Stations):
                station_obj = current_route.Stations[block.Station]
                srializedata['TrackCommand'][track_position]['Station']['Name'] = station_obj.Name
            #stop 요소 직렬화
            for idx, stop in enumerate(block.StopPositions):
                srializedata['TrackCommand'][track_position]['Stop'][idx] = stop.TrackPosition

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

        csv_lines.append("With Track")

        # 2. Track 명령어 영역 거리순 정렬 추출
        sorted_distances = sorted(list(srializedata['TrackCommand'].keys()))

        for dist in sorted_distances:
            block_data = srializedata['TrackCommand'][dist]

            # ① 곡선 (.curve) 문법 조립
            radius = block_data['Curve']['radius']
            cant = block_data['Curve']['cant']
            if radius != 0.0:
                csv_lines.append(f"{dist},.curve {radius};{cant * 1000.0}")

            # ② 구배 (.pitch) 문법 조립
            pitch = block_data['Pitch']
            if pitch != 0.0:
                csv_lines.append(f"{dist},.pitch {pitch}")

            # ③ [핵심 교정] 레일 (.rail / .railend) 문법 조립
            if 'Rail' in block_data:
                # 레일 인덱스 번호 순서대로 정렬하여 출력 규칙 준수
                for rail_idx in sorted(list(block_data['Rail'].keys())):
                    if rail_idx == 0:
                        continue  # 자선(0번)은 BVE 표준상 상시 활성화이므로 출력 스킵

                    rail_info = block_data['Rail'][rail_idx]
                    stttype = rail_info.get('object_type', None)
                    if stttype is None:
                        stttype = 0
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

        # 3. 실제 파일 쓰기
        import os
        os.makedirs('c:/temp', exist_ok=True)
        with open('c:/temp/route_reversed.csv', 'w', encoding='utf-8') as f:
            for line in csv_lines:
                f.write(line + '\n')

        print("🎉 [Exporter] 역방향 2-Pass 대응 CSV 빌드 완료! (c:/temp/route_reversed.csv)")