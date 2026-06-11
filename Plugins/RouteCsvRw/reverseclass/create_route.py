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

        # 💡 [종점 마감 핵심] 각 레일 번호별로 "마지막으로 등장한 거리"를 추적하기 위한 맵
        last_seen_positions = {}

        for i, block in enumerate(data.Blocks):
            track_position = i * data.BlockInterval

            # 선형 요소 직렬화
            srializedata['TrackCommand'][track_position]['Curve']['radius'] = block.CurrentTrackState.CurveRadius
            srializedata['TrackCommand'][track_position]['Curve']['cant'] = block.CurrentTrackState.CurveCant
            srializedata['TrackCommand'][track_position]['Pitch'] = block.CurrentTrackState.Pitch

            # 레일 요소 직렬화
            for key, rail in block.Rails.items():
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

                # 1) 기본 플래그 조합 기반 분기
                if rail.RailStarted and not rail.RailEnded:
                    rail_data['command'] = 'rail'
                elif rail.RailEnded and not rail.RailStarted:
                    rail_data['x'] = rail.RailEnd.x
                    rail_data['y'] = rail.RailEnd.y
                    rail_data['command'] = 'railend'
                elif rail.RailStarted and rail.RailEnded:
                    rail_data['command'] = 'KeepAlive'
                else:
                    rail_data['command'] = 'KeepAlive'

                # 💡 [종점 마감 핵심] 해당 레일 번호가 살아있는 상태라면, 마지막 발견 거리를 계속 갱신합니다.
                if rail_data['command'] in ('rail', 'KeepAlive'):
                    last_seen_positions[key] = (track_position, rail.RailEnd.x, rail.RailEnd.y)

            # 역(Station) 요소 직렬화
            if block.Station >= 0 and block.Station < len(current_route.Stations):
                station_obj = current_route.Stations[block.Station]
                srializedata['TrackCommand'][track_position]['Station']['Name'] = station_obj.Name
                srializedata['TrackCommand'][track_position]['Station']['StopPosition'] = station_obj.StopPosition

        # -------------------------------------------------------------------
        # 💡 [종점 마감 작업] 루프가 끝난 후, 닫히지 않고 증발한 레일들을 강제로 .railend 처리
        # -------------------------------------------------------------------
        for key, (last_dist, end_x, end_y) in last_seen_positions.items():
            current_cmd = srializedata['TrackCommand'][last_dist]['Rail'][key].get('command')

            # 만약 마지막으로 발견된 지점의 명령어가 .rail 이거나 KeepAlive 상태로 방치되어 있다면
            if current_cmd in ('rail', 'KeepAlive'):
                # 루트 맨 마지막 블록이거나 선로가 끊어지는 지점이므로 안전하게 종단 처리합니다.
                srializedata['TrackCommand'][last_dist]['Rail'][key]['x'] = end_x
                srializedata['TrackCommand'][last_dist]['Rail'][key]['y'] = end_y
                srializedata['TrackCommand'][last_dist]['Rail'][key]['command'] = 'railend'

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

                    # defaultdict의 부작용을 막기 위해 안전하게 .get()으로 커맨드 타입을 읽어옵니다.
                    cmd_type = rail_info.get('command')

                    # 💡 물리적 인덱스 기준에 따라 발급된 단어만 골라서 출력합니다.
                    if cmd_type == 'rail':
                        # 역방향 루트의 맨 첫 블록 (i == 0 지점)
                        csv_lines.append(f"{dist},.rail {rail_idx};{rail_info['x']};{rail_info['y']}")
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

                # 정차 마커 동적 오프셋 계산
                stop_position_offset = block_data['Station']['StopPosition']
                if stop_position_offset > 0:
                    csv_lines.append(f"{dist + stop_position_offset},.stop 0;")
                else:
                    csv_lines.append(f"{dist + 100.0},.stop 0;")  # 방어용 기본값

        # 3. 실제 파일 쓰기
        import os
        os.makedirs('c:/temp', exist_ok=True)
        with open('c:/temp/route_reversed.csv', 'w', encoding='utf-8') as f:
            for line in csv_lines:
                f.write(line + '\n')

        print("🎉 [Exporter] 역방향 2-Pass 대응 CSV 빌드 완료! (c:/temp/route_reversed.csv)")