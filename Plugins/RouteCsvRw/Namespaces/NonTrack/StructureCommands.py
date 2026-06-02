from enum import Enum


class StructureCommand(Enum):
    """
    Enumeration of StructureCommands used for various object types.
    """

    # The object used for RailType N
    Rail = 0
    # The object used for BeaconType N
    Beacon = 1
    # The object used for PoleType N
    Pole = 2
    # The object used for Ground N
    Ground = 3
    # The left Wall object for type N
    WallL = 4
    # The right Wall object for type N
    WallR = 5
    # The left Dike object for type N
    DikeL = 6
    # The right Dike object for type N
    DikeR = 7
    # The left Form object for type N
    FormL = 8
    # The right Form object for type N
    FormR = 9
    # The left FormCenter object for type N
    FormCL = 10
    # The right FormCenter object for type N
    FormCR = 11
    # The left FormRoof object for type N
    RoofL = 12
    # The right FormRoof object for type N
    RoofR = 13
    # The left FormRoofCenter object for type N
    RoofCL = 14
    # The right FormRoofCenter object for type N
    RoofCR = 15
    # The left Crack object for type N
    CrackL = 16
    # The right Crack object for type N
    CrackR = 17
    # The object used for FreeObject N
    FreeObj = 18
    # The image / object used for Background N
    Background = 19
    # The image / object used for Background N
    Back = 20
    # The image / object used for Background N
    BackgroundX = 21
    # The image / object used for Background N
    BackX = 22
    # If Background N is an image, sets the aspect ratio used in wrapping
    BackgroundAspect = 23
    # If Background N is an image, sets the aspect ratio used in wrapping
    BackAspect = 24
    # The object used for RainType N
    Weather = 25
    # Loads a dynamic lighting set
    DynamicLight = 26

    # HMMSIM
    # The object used for Object N (Equivalent to .FreeObj)
    Object = 27
