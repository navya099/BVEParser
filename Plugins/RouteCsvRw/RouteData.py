from . Structures.Block import Block

class RouteData:
    def __init__(self, previewOnly):
        self.TrackPosition = 0.0
        self.BlockInterval = 25.0
        self.Blocks = []
        # Blocks[0]을 추가하고 설정하는 코드
        block = Block()
        self.Blocks.append(block)
        self.FirstUsedBlock = -1
        
