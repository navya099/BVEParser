class RailReverse:
    """레일 역방향 변환 클래스 (덤프 명세 반영 완전판)"""

    @staticmethod
    def reverse_rail(block):
        if not block.Rails:
            return

        new_rails = {}

        for key, rail in block.Rails.items():
            # 유령 블록(89225m 이후의 모두 False인 데이터)은 아예 연산에서 스킵 및 제거
            if not rail.RailStarted and not rail.RailEnded and not rail.RailStartRefreshed:
                continue

            # 1) 원본 데이터 백업
            orig_started = rail.RailStarted
            orig_ended = rail.RailEnded
            sx, sy = rail.RailStart.x, rail.RailStart.y
            ex, ey = rail.RailEnd.x, rail.RailEnd.y

            from copy import deepcopy
            rev_rail = deepcopy(rail)

            # 2) 덤프 기반 플래그 및 좌표 완전 변환 연산
            if orig_started and not orig_ended:
                # [Case A] 정방향 중간 구간들 (Started=True, Ended=False)
                # ➔ 역방향 기차 시점에서도 끊김 없이 이어지는 중간 구간이어야 하므로 그대로 유지합니다.
                rev_rail.RailStarted = True
                rev_rail.RailEnded = False
                rev_rail.RailStartRefreshed = True

                # 중간 구간 좌표 교차 매칭
                rev_rail.RailStart.x = -ex
                rev_rail.RailStart.y = ey
                rev_rail.RailEnd.x = -sx
                rev_rail.RailEnd.y = sy

            elif not orig_started and orig_ended:
                # [Case B] 정방향의 최종 종점 블록 (Started=False, Ended=True)
                # ➔ 역방향 기차 기준으로는 "여기서 선로가 새로 시작(.rail)"되는 기점 블록이 됩니다!
                rev_rail.RailStarted = True
                rev_rail.RailEnded = False
                rev_rail.RailStartRefreshed = True

                # 정방향의 종점 좌표(ex)가 역방향의 새로운 출발지(RailStart)가 됨
                rev_rail.RailStart.x = -ex
                rev_rail.RailStart.y = ey
                rev_rail.RailEnd.x = rev_rail.RailStart.x
                rev_rail.RailEnd.y = rev_rail.RailStart.y

            # 3) 💡 [가장 중요] 역방향의 종점(.railend) 타이밍은 어떻게 잡나?
            # 정방향 루트의 맨 첫 번째 블록(Index 0)은 스왑 후 역방향의 맨 마지막 블록이 됩니다.
            # 이 지점은 밖에서 '루프의 인덱스가 마지막일 때' 강제로 꺾어주거나,
            # 직렬화 레이어에서 이정 거리를 보고 깔끔하게 마무리 처리하는 것이 훨씬 안전합니다.

            if hasattr(rev_rail, 'MidPoint') and rev_rail.MidPoint is not None:
                rev_rail.MidPoint.x = -rev_rail.MidPoint.x
            rev_rail.CurveCant = -rev_rail.CurveCant

            new_rails[key] = rev_rail

        block.Rails = new_rails