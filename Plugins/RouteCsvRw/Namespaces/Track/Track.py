from Plugins.RouteCsvRw.Namespaces.Track.TrackCommands import TrackCommand
from Plugins.RouteCsvRw.RouteData import RouteData
from Plugins.RouteCsvRw.Structures.Expression import Expression
from OpenBveApi.Math.Math import NumberFormats

import math
import numpy as np


class Parser7:
    def __init__(self):
        self.CurrentStation: int = -1
        self.CurrentStop: int = -1
        self.CurrentSection: int = 0
        self.DepartureSignalUsed: bool = False

    def parse_track_command(self, command: TrackCommand, arguments: list[str], filename: str,
                            unit_of_lngth: list[float], expression: Expression, data: RouteData, block_index: int,
                            preview_only: bool, is_rw: bool, rail_index: int = 0) -> RouteData:
        match command:
            case TrackCommand.RailStart:
                pass
            case TrackCommand.Rail:
                pass
            case TrackCommand.RailEnd:
                pass
            case TrackCommand.RailType:
                pass
            case TrackCommand.Accuracy:
                pass
            case TrackCommand.Pitch:
                sucess, p = NumberFormats.try_parse_double_vb6(arguments[0])
                if len(arguments) >= 1 and len(arguments[0]) > 0 and not sucess:
                    print(f'ValueInPermille is invalid in {command} at line '
                          f'{expression.Line} , column {expression.Column}'
                          f' in file {expression.File}')
                    p = 0.0
                data.Blocks[block_index].Pitch = 0.001 * p
            case TrackCommand.Curve:
                radius = 0.0
                sucess, radius = NumberFormats.try_parse_double_vb6(arguments[0])
                if len(arguments) >= 1 and len(arguments[0]) > 0 and not sucess:
                    print(f'Radius is invalid in {command} at line '
                          f'{expression.Line} , column {expression.Column}'
                          f' in file {expression.File}')
                    radius = 0.0
                cant = 0.0
                sucess, cant = NumberFormats.try_parse_double_vb6(arguments[1])
                if len(arguments) >= 2 and len(arguments[1]) > 0 and not sucess:
                    print(f'CantInMillimeters is invalid in {command} at line '
                          f'{expression.Line} , column {expression.Column}'
                          f' in file {expression.File}')
                    cant = 0.0
                else:
                    cant *= 0.001
                if data.SignedCant:
                    if radius != 0.0:
                        cant *= np.sign(radius)
                else:
                    cant = abs(cant) * np.sign(radius)
                data.Blocks[block_index].CurrentTrackState.CurveRadius = radius
                data.Blocks[block_index].CurrentTrackState.CurveCant = cant
                data.Blocks[block_index].CurrentTrackState.CurveCantTangent = 0.0

            case TrackCommand.Turn:
                pass
            case TrackCommand.Adhesion:
                pass
            case TrackCommand.Brightness:
                pass
            case TrackCommand.Fog:
                pass
            case TrackCommand.Section:
                pass
            case TrackCommand.SectionS:
                pass
            case TrackCommand.SigF:
                pass
            case TrackCommand.Signal:
                pass
            case TrackCommand.Sig:
                pass
            case TrackCommand.Relay:
                pass
            case TrackCommand.Destination:
                pass
            case TrackCommand.Beacon:
                pass
            case TrackCommand.Transponder:
                pass
            case TrackCommand.Tr:
                pass
            case TrackCommand.ATSSn:
                pass
            case TrackCommand.ATSP:
                pass
            case TrackCommand.Pattern:
                pass
            case TrackCommand.PLimit:
                pass
            case TrackCommand.Limit:
                pass
            case TrackCommand.Stop:
                pass
            case TrackCommand.StopPos:
                pass
            case TrackCommand.Sta:
                pass
            case TrackCommand.Station:
                pass
            case TrackCommand.StationXML:
                pass
            case TrackCommand.Buffer:
                pass
            case TrackCommand.Form:
                pass
            case TrackCommand.Pole:
                pass
            case TrackCommand.PoleEnd:
                pass
            case TrackCommand.Wall:
                pass
            case TrackCommand.WallEnd:
                pass
            case TrackCommand.Dike:
                pass
            case TrackCommand.DikeEnd:
                pass
            case TrackCommand.Marker:
                pass
            case TrackCommand.TextMarker:
                pass
            case TrackCommand.Height:
                if not preview_only:
                    success, h = NumberFormats.try_parse_double_vb6(arguments[0], unit_of_lngth)
                    if len(arguments) >= 1 and len(arguments[0]) > 0 and not sucess:
                        print(f'Height is invalid in Track.Height at line '
                              f'{expression.Line} , column {expression.Column}'
                              f' in file {expression.File}')
                        h = 0.0
                    data.Blocks[block_index].Height = h + 0.3 if is_rw else h
            case TrackCommand.Ground:
                pass
            case TrackCommand.Crack:
                pass
            case TrackCommand.FreeObj:
                pass
            case TrackCommand.Back:
                pass
            case TrackCommand.Background:
                pass
            case TrackCommand.Announce:
                pass
            case TrackCommand.AnnounceAll:
                pass
            case TrackCommand.Doppler:
                pass
            case TrackCommand.DopplerAll:
                pass
            case TrackCommand.MicSound:
                pass
            case TrackCommand.PreTrain:
                pass
            case TrackCommand.PointOfInterest:
                pass
            case TrackCommand.POI:
                pass
            case TrackCommand.HornBlow:
                pass
            case TrackCommand.Rain:
                pass
            case TrackCommand.Snow:
                pass
            case TrackCommand.DynamicLight:
                pass
            case TrackCommand.DirectionalLight:
                pass
            case TrackCommand.AmbientLight:
                pass
            case TrackCommand.LightDirection:
                pass
            case TrackCommand.PatternObj:
                pass
            case TrackCommand.PatternEnd:
                pass
            case TrackCommand.Switch:
                pass
            case TrackCommand.SwitchT:
                pass
            case TrackCommand.PlayerPath:
                pass
            case TrackCommand.RailLimit:
                pass
            case TrackCommand.RailBuffer:
                pass
            case TrackCommand.RailAccuracy:
                pass
            case TrackCommand.RailAdhesion:
                pass
        return data



