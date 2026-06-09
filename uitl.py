from enum import Enum
from typing import Type, Tuple, Optional
import json
from dataclasses import is_dataclass, asdict
from tqdm import tqdm
import time
from concurrent.futures import ProcessPoolExecutor


class Util:
    @staticmethod
    def try_parse_enum(enum_type: Type[Enum], value: str, ignore_case: bool = True) -> Tuple[Optional[Enum], bool]:
        if ignore_case:
            value = value.strip().replace(" ", "_").upper()
            enum_dict = {name.upper(): member for name, member in enum_type.__members__.items()}
        else:
            enum_dict = enum_type.__members__

        result = enum_dict.get(value, None)
        return result, result is not None

    @staticmethod
    def write_all_lines(path, text_list):
        with open(path, 'w', encoding='utf-8') as f:
            for txt in text_list:
                f.write(txt + '\n')

    @staticmethod
    def test(expressions):
        with open("C:/TEMP/expressions_all.csv", "w", encoding="utf-8-sig") as f:
            f.write(f"인덱스,줄,텍스트,오프셋,파일\n")
            for i, expr in enumerate(expressions):
                f.write(f"{i},{expr.Line},{expr.Text},{expr.TrackPositionOffset},{expr.File}\n")

    @staticmethod
    def create_csv(expressions):
        sections = {
            "Track": [],
            "Options": [],
            "Route": [],
            "Train": [],
            "Structure": []
        }

        # 맨 처음은 Track 섹션으로 시작
        current_section = "Track"

        for expr in expressions:
            text = expr.Text.strip()

            # 섹션 시작 키워드 체크
            if text.startswith("Options"):
                current_section = "Options"
            elif text == "With Route":
                current_section = "Route"
            elif text == "With Train":
                current_section = "Train"
            elif text == "With Structure":
                current_section = "Structure"
            elif text == "With Track":
                current_section = "Track"

            # 현재 섹션에 데이터 추가
            sections[current_section].append(text)

        # 원하는 순서대로 CSV에 기록
        with open("C:/TEMP/route_revesed.csv", "w", encoding="utf-8-sig") as f:
            for section_name in ["Options", "Route", "Train", "Structure", "Track"]:
                if sections[section_name]:
                    for line in sections[section_name]:
                        f.write(f"{line}\n")


class RecursiveEncoder(json.JSONEncoder):
    def default(self, obj):
        # dataclass인 경우
        if is_dataclass(obj):
            return asdict(obj)

        # __dict__가 있는 클래스 (일반 class)
        if hasattr(obj, "__dict__"):
            return {
                key: self.default(value)
                for key, value in obj.__dict__.items()
                if not key.startswith('_')  # private 속성 제외 (선택)
            }

        # 리스트 or 튜플 처리
        if isinstance(obj, (list, tuple)):
            return [self.default(item) for item in obj]

        # dict 처리
        if isinstance(obj, dict):
            return {
                self.default(key): self.default(value)
                for key, value in obj.items()
            }

        # 기본값: 그냥 반환
        return obj

    @staticmethod
    def _serialize_block(block):
        return RecursiveEncoder().default(block)

    @staticmethod
    def save(path, data, isexcute=False):
        if isexcute:
            try:
                if hasattr(data, "Blocks") and isinstance(data.Blocks, list):
                    print(f"🚀 Blocks ({len(data.Blocks)}개) 병렬 직렬화 중...")
                    start_time = time.time()

                    with ProcessPoolExecutor() as executor:
                        blocks_serialized = list(tqdm(executor.map(RecursiveEncoder._serialize_block, data.Blocks),
                                                      total=len(data.Blocks), desc="Serializing Blocks (parallel)", unit="block"))

                    main_data = RecursiveEncoder().default(data)
                    main_data["Blocks"] = blocks_serialized

                    print(f'📦 JSON 저장 시작...')
                    with open(path, "w", encoding="utf-8") as f:
                        json.dump(main_data, f, indent=4)

                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    print(f'✅ JSON 저장 완료: {path}')
                    print(f'⏱ 경과시간: {elapsed_time:.2f}초')

                else:
                    start_time = time.time()
                    print(f'📦 JSON 저장 시작...')
                    with open(path, "w", encoding="utf-8") as f:
                        json.dump(data, f, cls=RecursiveEncoder, indent=4)
                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    print(f'✅ JSON 저장 완료: {path}')
                    print(f'⏱ 경과시간: {elapsed_time:.2f}초')

            except IOError as ex:
                print(f'❌ JSON 저장 실패: {ex}')
