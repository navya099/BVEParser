import collections
from loggermodule import logger
from Plugins.RouteCsvRw.RouteData import RouteData
from Plugins.RouteCsvRw.reverseclass.create_route import CreateRouteFILE
from RouteManager2.CurrentRoute import CurrentRoute


class SerializeRouteData:
    @staticmethod
    def serialize_route_data(current_route: CurrentRoute, data: RouteData):
        def tree():
            return collections.defaultdict(tree)

        srializedata = tree()

        # 1. OPTIONS 섹션
        SerializeRouteData.serialize_option_command(current_route, srializedata)
        # 2. 루트 네임스페이스 섹션
        SerializeRouteData.serialize_route_command(current_route, srializedata)
        # 3. 스트럭쳐 네임스페이스 섹션
        SerializeRouteData.serialize_structure_command(data, srializedata)
        # 3. 트랙 네임스페이스 섹션
        SerializeRouteData.serialize_track_command(current_route, data, srializedata)

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
    def serialize_structure_command(data: RouteData, serializedata):
        """
        Parser10 적재 원형(리스트 형태 [f] 및 순수 문자열 f)에 완벽히 동기화된
        Structure 정의 명령어 직렬화 마스터 메서드
        """
        if 'StructureCommand' not in serializedata:
            serializedata['StructureCommand'] = []

        # 1. 일반 ObjectDictionary 계열 속성 이름과 BVE CSV 명령어 접두사 매핑
        structure_mappings = {
            'RailObjects': 'Structure.Rail',
            'Ground': 'Structure.Ground',
            'WallL': 'Structure.WallL',
            'WallR': 'Structure.WallR',
            'DikeL': 'Structure.DikeL',
            'DikeR': 'Structure.DikeR',
            'FormL': 'Structure.FormL',
            'FormR': 'Structure.FormR',
            'FormCL': 'Structure.FormCL',
            'FormCR': 'Structure.FormCR',
            'RoofL': 'Structure.RoofL',
            'RoofR': 'Structure.RoofR',
            'RoofCL': 'Structure.RoofCL',
            'RoofCR': 'Structure.RoofCR',
            'CrackL': 'Structure.CrackL',
            'CrackR': 'Structure.CrackR',
            'FreeObjects': 'Structure.FreeObj',
            'Beacon': 'Structure.Beacon',
            'WeatherObjects': 'Structure.Weather'
        }

        # [내부 헬퍼] Parser10 데이터 구조에서 동적 상대 경로만 추출
        def extract_pure_path(obj_val) -> str:
            raw_path = ""
            if obj_val is None:
                return ""

            if isinstance(obj_val, (list, tuple)) and len(obj_val) > 0:
                raw_path = str(obj_val[0])
            elif isinstance(obj_val, str):
                raw_path = obj_val
            else:
                for attr in ['FilePath', 'Path', 'path', 'FileName']:
                    if hasattr(obj_val, attr):
                        val = getattr(obj_val, attr)
                        if isinstance(val, str) and val:
                            raw_path = val
                            break
                if not raw_path:
                    raw_path = str(obj_val)

            # 💡 [동적 경로 슬라이싱 가드 적용]
            # 1. 먼저 슬래시를 윈도우/BVE 표준 역슬래시로 통일
            raw_path = raw_path.replace('/', '\\')

            # 2. 대소문자 무관하게 'object\'가 포함된 마디의 시작점 추적
            lower_path = raw_path.lower()
            target_keyword = "object\\"

            if target_keyword in lower_path:
                # 'object\' 키워드가 시작되는 인덱스를 찾고, 그 단어 길이만큼 건너뜁니다.
                idx = lower_path.index(target_keyword)
                # 'D:\BVE\루트\Railway\Object\경북선\...' 에서 'Object\' 뒤의 문자열만 슬라이싱
                raw_path = raw_path[idx + len(target_keyword):]

            return raw_path

        # 2. 일반 구조물 사전 순회 및 명령어 생성
        for attr_name, bve_prefix in structure_mappings.items():
            current_dict = getattr(data.Structure, attr_name, None)

            if current_dict and isinstance(current_dict, dict):
                for key, obj_val in current_dict.items():
                    obj_path = extract_pure_path(obj_val)
                    if obj_path:
                        # 출력 형식: Structure.Rail(40) Obj\Rail\rail_concrete.csv
                        cmd_string = f"{bve_prefix}({key}) {obj_path}"
                        serializedata['StructureCommand'].append(cmd_string)

        # 3. 전신주(Poles) 특수 2중 중첩 사전 구조 해결
        # 파서 원형: data.Structure.Poles[command_indices[0]].Add(command_indices[1], obj)
        if hasattr(data.Structure, 'Poles') and data.Structure.Poles:
            poles_root = data.Structure.Poles
            if isinstance(poles_root, dict):
                for first_idx, sub_dict in poles_root.items():
                    if sub_dict and isinstance(sub_dict, dict):
                        for second_idx, obj_val in sub_dict.items():
                            obj_path = extract_pure_path(obj_val)
                            if obj_path:
                                # 출력 형식: Structure.Pole(0; 1) Obj\Pole\pole_double.b3d
                                cmd_string = f"Structure.Pole({first_idx}; {second_idx}) {obj_path}"
                                serializedata['StructureCommand'].append(cmd_string)


        logger.debug(f"[Structure 원형 직렬화 완료] 총 {len(serializedata['StructureCommand'])}개 명령어 캡처 완료")

    @staticmethod
    def serialize_track_command(current_route: CurrentRoute, data: RouteData, srializedata):
        total_blocks = len(data.Blocks)

        for i, block in enumerate(data.Blocks):
            track_position = i * data.BlockInterval
            next_block = data.Blocks[i + 1] if i <total_blocks - 1 else None
            # 선형 요소 직렬화
            srializedata['TrackCommand'][track_position]['Curve']['radius'] = block.CurrentTrackState.CurveRadius
            srializedata['TrackCommand'][track_position]['Curve']['cant'] = block.CurrentTrackState.CurveCant
            srializedata['TrackCommand'][track_position]['Pitch'] = block.CurrentTrackState.Pitch

            # 💡 다음 블록에 존재하는 레일 인덱스 세트 미리 추출 (Look-Ahead)
            next_block_rails = set()
            if next_block:
                for n_key, n_rail in next_block.Rails.items():
                    # 다음 블록에서 유효한 유령이 아닌 레일만 수집
                    if n_rail.RailStarted or n_rail.RailEnded or n_rail.RailStartRefreshed:
                        next_block_rails.add(n_key)

            # 레일 요소 직렬화
            for key, rail in block.Rails.items():
                try:
                    if next_block:
                        current_sttype = next_block.RailType[key]
                except KeyError:
                    logger.error(f'unexpected rail key {key} in occured at track_position={track_position} with serialize_track_command')
                    current_sttype = 0

                except IndexError:
                    logger.error(f'not found rail key {key} in occured at track_position={track_position} with serialize_track_command')
                    current_sttype = 0

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
            # stop 요소 직렬화
            for idx, stop in enumerate(block.StopPositions):
                srializedata['TrackCommand'][track_position]['Stop'][idx] = stop.TrackPosition

            # height 요소 작렬화
            if block.Height is not None:
                srializedata['TrackCommand'][track_position]['Height'] = block.Height

            # freeobj 직렬화
            if block.RailFreeObj:
                srializedata['TrackCommand'][track_position]['FreeObj'] = []
                for rail_key, freeobjs in block.RailFreeObj.items():
                    if freeobjs:
                        for freeobj in freeobjs:
                            obj_data = {
                                'track_position': freeobj.TrackPosition,
                                'RailIndex': rail_key,
                                'StructureType': freeobj.Type,
                                'x': freeobj.Position.x,
                                'y': freeobj.Position.y,
                                'yaw': freeobj.Yaw,
                                'pitch': freeobj.Pitch,
                                'roll': freeobj.Roll
                            }
                            srializedata['TrackCommand'][track_position]['FreeObj'].append(obj_data)
            # pole 직렬화
            if hasattr(block, 'RailPole') and block.RailPole:
                # save_csv에서 편하게 접근할 수 있도록 딕셔너리로 초기화
                srializedata['TrackCommand'][track_position]['Pole'] = {}

                for rail_idx, pole in block.RailPole.items():
                    # 레일 인덱스를 Key로 하여 구조화된 딕셔너리 주입
                    srializedata['TrackCommand'][track_position]['Pole'][rail_idx] = {
                        'exists': pole.Exists,
                        'mode': pole.Mode,
                        'type': pole.Type,
                        'loc': pole.Location,
                        'interval': pole.Interval
                    }
            #DIKE 직렬화
            if hasattr(block, 'RailDike') and block.RailDike:
                # save_csv에서 편하게 접근할 수 있도록 딕셔너리로 초기화
                srializedata['TrackCommand'][track_position]['Dike'] = {}

                for rail_idx, dike in block.RailDike.items():
                    # 레일 인덱스를 Key로 하여 구조화된 딕셔너리 주입
                    srializedata['TrackCommand'][track_position]['Dike'][rail_idx] = {
                        'object_type': dike.object_type,
                        'direction': dike.direction,
                        'exists': dike.exists
                    }
            # Wall 직렬화
            if hasattr(block, 'RailWall') and block.RailWall:
                # save_csv에서 편하게 접근할 수 있도록 딕셔너리로 초기화
                srializedata['TrackCommand'][track_position]['Wall'] = {}

                for rail_idx, wall in block.RailWall.items():
                    # 레일 인덱스를 Key로 하여 구조화된 딕셔너리 주입
                    srializedata['TrackCommand'][track_position]['Wall'][rail_idx] = {
                        'object_type': wall.object_type,
                        'direction': wall.direction,
                        'exists': wall.exists
                    }