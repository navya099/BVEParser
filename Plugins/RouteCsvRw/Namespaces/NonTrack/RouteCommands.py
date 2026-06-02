from enum import Enum


class RouteCommand(Enum):
    """Enum to represent various route commands for BVE and OpenBVE"""

    # Used by BVE to allow for debugging, unused by OpenBVE

    DeveloperID = 0
    # A textual description of the route to be displayed in the main menu
    Comment = 1
    # An image of the route to be displayed in the main menu
    Image = 2
    # The timetable image to be displayed in-cab
    TimeTable = 3
    # The mode for the train's safety system to start in
    Change = 4
    # The rail gauge
    Gauge = 5
    # Sets a speed limit for each signal aspect
    Signal = 6
    # The acceleration due to gravity
    AccelerationDueToGravity = 7
    # The game starting time
    StartTime = 8
    # Sets the background to be displayed on loading screens
    LoadingScreen = 9
    # Sets a custom unit of speed to be displayed in in-game messages
    DisplaySpeed = 10
    # Sets briefing data
    Briefing = 11
    # Sets the initial elevation above sea-level
    Elevation = 12
    # Sets the initial air temperature
    Temperature = 13
    # Sets the initial air pressure
    Pressure = 14
    # Sets the ambient light color
    AmbientLight = 15
    # Sets the directional light color
    DirectionalLight = 16
    # Sets the position of the directional light
    LightDirection = 17
    # Adds dynamic lighting
    DynamicLight = 18
    # Sets the initial viewpoint for the camera
    InitialViewPoint = 19
    # Adds AI trains
    TfoXML = 20
    # 초기x좌표
    PositionX = 21
    PositionY = 22
    Direction = 23
