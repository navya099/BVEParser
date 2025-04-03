from functools import singledispatch
import math

class RouteData:
    def __init__(self):
        self.TrackPosition = 0.0
        self.BlockInterval = 25.0
        self.Blocks = []
        # Blocks[0]을 추가하고 설정하는 코드
        block = Block()
        self.Blocks.append(block)
        
class Rails:
    def __init__(self):
        self.Rails = {}

class TrackElement:
    def __init__(self, StartingTrackPosition):
        self.StartingTrackPosition = StartingTrackPosition
        self.CurveRadius = 0.0
        self.CurveCant = 0.0
        self.Pitch = 0.0
        vector3 = Vector3()
        self.WorldPosition = vector3.zero()

class Block:
    def __init__(self):
        self.CurrentTrackState = TrackElement(0.0)
        self.Pitch = 0.0

class Vector3:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return f"({self.x}, {self.y}, {self.z})"

    def zero(self):
        self.x = 0
        self.y = 0
        self.z = 0
        return self.x, self.y, self.z
    
    def rotate(self, cos_angle, sin_angle):
        """Rotate this vector in 2D by the given cosine and sine values."""
        x_new = cos_angle * self.x - sin_angle * self.y
        y_new = sin_angle * self.x + cos_angle * self.y
        self.x, self.y = x_new, y_new
        
class Transformation:
    def __init__(self, yaw, pitch, roll):
        self.yaw = yaw
        self.pitch = pitch
        self.roll = roll

    def rotate_vector(self, vector):
        """Rotate a 2D vector by the yaw angle."""
        cos_yaw = math.cos(self.yaw)
        sin_yaw = math.sin(self.yaw)
        vector.rotate(cos_yaw, sin_yaw)
        return vector

def ReadAllLines(FileName, Encoding):
    # 'r' 모드로 파일을 읽고, 파일의 인코딩을 지정
    with open(FileName, 'r', encoding=Encoding) as file:
        # 파일의 모든 줄을 읽어 리스트로 반환
        return file.readlines()
    
class Parser:
    def __init__(self):
        pass
    
    def ParseRoute(self, FileName, Encoding):
        Data = RouteData()
        Lines = self.ParseRouteForData(FileName, Encoding, Data)
        self.ApplyRouteData(Lines, Data)
        return Data
    
    def ParseRouteForData(self, FileName: str, Encoding, RouteData: RouteData):
        Lines = ReadAllLines(FileName, Encoding)
        return Lines

    def ApplyRouteData(self, Lines, Data):
        for i, line in enumerate(Lines):
            parts = line.split(',')
            sta , radius ,cant = parts
            block = Block()
            Data.Blocks.append(block)
            Data.Blocks[i].CurrentTrackState.CurveRadius = radius
            Data.Blocks[i].CurrentTrackState.CurveCant = cant
            Data.TrackPosition = sta
            
CsvRwRouteParser = Parser()
DATA = CsvRwRouteParser.ParseRoute('c:/temp/curve_info.txt' , 'utf-8')
for i in range(len(DATA.Blocks)):
    #print(DATA.Blocks[i].CurrentTrackState.CurveRadius)
    pass
