import math
from Plugins.RouteCsvRw.Structures.Block import Block

class SignalReverser:
    """신호(Signal) 역방향 변환 클래스"""
    @staticmethod
    def reverse_limit(block: Block, last_track_position: float):
        if block.Limits:
            for limit in block.Limits:
                limit.TrackPosition = last_track_position - limit.TrackPosition