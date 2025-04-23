class Atmosphere:
    def __init__(self):
        self.LightPosition: 'Vector3' = None
        self.DiffuseLightColor: 'Color24' = None
        self.AmbientLightColor: 'Color24' = None
        self.InitialElevation: float = 0.0
        self.AccelerationDueToGravity: float = 9.80665
        self.InitialAirPressure: float = 101325.0
        self.SeaLevelAirTemperature: float = 293.15
        self.MolarMass: float = 0.0289644
        self.UniversalGasConstant: float = 8.31447
        self.TemperatureLapseRate: float = -0.0065
        self.CoefficientOfStiffness: float = 144117.325646911
        self.InitialX: float = 0.0
        self.InitialY: float = 0.0
        self.InitialDirection: float = 90.0
