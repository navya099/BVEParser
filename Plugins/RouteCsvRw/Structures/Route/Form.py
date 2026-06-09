from Plugins.RouteCsvRw.Structures.StructureData import StructureData


class Form:
    """
    Attributes:
        primary_rail: The platform face rail
        secondary_rail: The rail for the rear transformation
        form_type: The index of the FormType to use
        roof_type: The index of the RoofType to use
        SecondaryRailStub: Magic number constants used by BVE2 /4
        SecondaryRailL: Magic number constants used by BVE2 /4
        SecondaryRailR: Magic number constants used by BVE2 /4
    """
    SecondaryRailStub = 0
    SecondaryRailL = -1
    SecondaryRailR = -2

    def __init__(self, primary_rail: int, secondary_rail: int, form_type: int, roof_type: int, structure: StructureData):
        self.primary_rail = primary_rail
        self.secondary_rail = secondary_rail
        self.form_type = form_type
        self.roof_type = roof_type
        self.structure = structure
