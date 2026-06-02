from enum import Enum


class TrackCommand(Enum):
    # Controls the position and type of a rail
    Rail = 0
    # Starts a rail
    RailStart = 1
    # Ends a rail
    RailEnd = 2
    # Changes the RailType of a rail
    RailType = 3
    # Changes the accuracy (bounce / spread) value
    Accuracy = 4
    # Changes the pitch of Rail 0
    Pitch = 5
    # Changes the curve of Rail 0
    Curve = 6
    # Adds a turn on Rail 0
    Turn = 7
    # Changes the adhesion value of Rail 0
    Adhesion = 8
    # Changes the overall brightness value
    Brightness = 9
    # Controls a region of fog
    Fog = 10
    # Adds a signalling section
    Section = 11
    # Adds a signalling section
    SectionS = 12
    # Adds a signal object
    SigF = 13
    # Adds a signal object
    Signal = 14
    # Adds a signal object
    Sig = 15
    # Adds a relay
    Relay = 16
    # Adds a destination change event
    Destination = 17
    # Adds a beacon
    Beacon = 18
    # Adds a transponder
    Transponder = 19
    # Adds a transponder
    Tr = 20
    # Adds an ATS-SN transponder
    ATSSn = 21
    # Adds an ATS-P transponder
    ATSP = 22
    # Adds an ATS-P pattern transponder
    Pattern = 23
    # Adds an ATS-P limit transponder
    PLimit = 24
    # Adds a speed limit
    Limit = 25
    # Adds a station stop point
    Stop = 26
    # Adds a station
    Sta = 27
    # Adds a station
    Station = 28
    # Adds a station defined in an external XML file
    StationXML = 29
    # Adds a buffer stop to Rail 0
    Buffer = 30
    # Adds a platform
    Form = 31
    # Starts OHLE poles on the selected rail(s)
    Pole = 32
    # Ends OHLE poles on the selected rail(s)
    PoleEnd = 33
    # Starts a wall on the selected rail
    Wall = 34
    # Ends a wall on the selected rail
    WallEnd = 35
    # Starts a dike on the selected rail
    Dike = 36
    # Ends a dike on the selected rail
    DikeEnd = 37
    # Adds a graphical marker
    Marker = 38
    # Adds a textual marker
    TextMarker = 39
    # Changes the height of Rail 0 above the ground
    Height = 40
    # Changes the ground object
    Ground = 41
    # Creates a crack fill object between two rails
    Crack = 42
    # Adds a FreeObject
    FreeObj = 43
    # Changes the displayed background
    Back = 44
    # Changes the displayed background
    Background = 45
    # Adds an announcement played in the cab
    Announce = 46
    # Adds an announcement played in all cars
    AnnounceAll = 47
    # Adds a doppler sound played in the cab
    Doppler = 48
    # Adds a doppler sound played in all cars
    DopplerAll = 49
    # Adds a reigon where an announcement can be played in-game using the microphone
    MicSound = 50
    # Controls the calling time of the PreTrain
    PreTrain = 51
    # Adds a PointOfInterest
    PointOfInterest = 52
    # Adds a PointOfInterest
    POI = 53
    # Adds a horn blow event
    HornBlow = 54
    # Sets the rain intensity
    Rain = 55
    # Sets the snow intensity
    Snow = 56
    # Changes the ambient lighting
    # Ignored when dynamic lighting is active
    AmbientLight = 57
    # Changes the directional light
    # Ignored when directional lighting is active
    DirectionalLight = 58
    # Changes the light direction
    # Ignored when directional lighting is active
    LightDirection = 59
    # Changes the dynamic lighting set in use
    DynamicLight = 60
    # Creates a facing switch
    Switch = 61
    # Creates a trailing switch
    SwitchT = 62
    # Sets the speed limit for a rail
    RailLimit = 63
    # Adds a buffer stop
    RailBuffer = 64
    # Sets the accuracy value for a rail
    RailAccuracy = 65
    # Sets the adhesion value for a rail
    RailAdhesion = 66
    # Changes the player path
    PlayerPath = 67

    # HMMSIM
    # Adds a station stop point
    # Eqivilant of .Stop
    StopPos = 68
    # Starts a repeating object cycle
    PatternObj = 69
    # Ends a repeating object cycle
    PatternEnd = 70
