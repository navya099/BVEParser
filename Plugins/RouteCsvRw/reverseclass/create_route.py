import collections
from RouteManager2.CurrentRoute import CurrentRoute
from Plugins.RouteCsvRw.RouteData import RouteData


class CreateRouteFILE:
    @staticmethod
    def serialize_route_data(current_route: CurrentRoute, data: RouteData):
        # 💡 [교정] 중첩 딕셔너리를 자동으로 생성해주는 무한 트리 구조 정의 (KeyError 방지)
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

    @staticmethod
    def serialize_option_command(current_route: CurrentRoute, srializedata):
        # 파이썬은 정수/실수 단위 출력을 선호하므로 round 처리 혹은 그대로 대입
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
        for i, block in enumerate(data.Blocks):
            # 💡 [안전장치] 블록 번호와 인터벌을 곱해 정밀한 이정(Distance) 키 생성
            track_position = i * data.BlockInterval

            radius = block.CurrentTrackState.CurveRadius
            cant = block.CurrentTrackState.CurveCant
            pitch = block.CurrentTrackState.Pitch

            # 선형 요소 직렬화
            srializedata['TrackCommand'][track_position]['Curve']['radius'] = radius
            srializedata['TrackCommand'][track_position]['Curve']['cant'] = cant
            srializedata['TrackCommand'][track_position]['Pitch'] = pitch

            # 레일 요소 직렬화
            for key, rail in block.Rails.items():
                srializedata['TrackCommand'][track_position]['Rail'][key]['x'] = rail.RailStart.x
                srializedata['TrackCommand'][track_position]['Rail'][key]['y'] = rail.RailStart.y
                srializedata['TrackCommand'][track_position]['Rail'][key]['isstart'] = rail.RailStarted
                srializedata['TrackCommand'][track_position]['Rail'][key]['isend'] = rail.RailEnded

            # 역(Station) 요소 직렬화 (블록에 속해있을 경우만 기록)
            if block.Station >= 0 and block.Station < len(current_route.Stations):
                station_obj = current_route.Stations[block.Station]
                srializedata['TrackCommand'][track_position]['Station']['Name'] = station_obj.Name
                srializedata['TrackCommand'][track_position]['Station'][
                    'Door'] = "Left" if station_obj.OpenLeftDoors else "Right"
                # 필요시 도어 Both 예외처리나 타 속성 추가 가능

    @staticmethod
    def save_csv(srializedata, block_interval: float):
        """트리 구조의 데이터를 BVE CSV 공식 문법 문자열로 변환하여 파일 저장"""
        csv_lines = []

        # 1. Options & Route 헤더 영역 작성
        csv_lines.append("Options.ObjectVisibility 1")
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

        # 2. Track 명령어 영역 작성 (거리 순서대로 정렬하여 추출)
        # srializedata['TrackCommand'].keys() 에는 0, 25, 50 같은 정수/실수 거리가 들어있습니다.
        sorted_distances = sorted(list(srializedata['TrackCommand'].keys()))

        for dist in sorted_distances:
            block_data = srializedata['TrackCommand'][dist]

            # ① 곡선 (.curve) 문법 조립
            radius = block_data['Curve']['radius']
            cant = block_data['Curve']['cant']
            # BVE 문법은 Cant 단위가 mm이므로 파서 내부 값(m)에 1000을 곱합니다.
            if radius != 0.0:
                csv_lines.append(f"{dist},.curve {radius};{cant * 1000.0}")

            # ② 구배 (.pitch) 문법 조립
            pitch = block_data['Pitch']
            if pitch != 0.0:
                csv_lines.append(f"{dist},.pitch {pitch}")

            # ③ 레일 (.rail / .railend) 문법 조립
            for rail_idx in block_data['Rail']:
                rail_info = block_data['Rail'][rail_idx]
                # 앞서 우리가 스왑한 플래그에 근거하여 문법 명세를 지정합니다.
                if rail_info['isstart']:
                    # 다음 블록으로 이어지는 구조이므로 End 좌표 계산 로직을 물려주거나 패딩
                    csv_lines.append(f"{dist},.rail {rail_idx};{rail_info['x']};{rail_info['y']}")
                elif rail_info['isend']:
                    csv_lines.append(f"{dist},.railend {rail_idx};{rail_info['x']};{rail_info['y']}")

            # ④ 역정거장 (.sta) 문법 조립
            if 'Station' in block_data and 'Name' in block_data['Station']:
                st_name = block_data['Station']['Name']
                st_door = block_data['Station']['Door']
                # 순정 .sta 인자 양식 매칭
                csv_lines.append(f"{dist},.sta {st_name};;;;{st_door}")

        # 3. 실제 파일 쓰기
        import os
        os.makedirs('c:/temp', exist_ok=True)
        with open('c:/temp/route_reversed.csv', 'w', encoding='utf-8') as f:
            for line in csv_lines:
                f.write(line + '\n')

        print("🎉 [Exporter] 역방향 CSV 파일 저장 완료! (c:/temp/route_reversed.csv)")