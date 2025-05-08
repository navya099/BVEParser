import time

from Plugins.RouteCsvRw.RouteData import RouteData
from OpenBveApi.Math.Vectors.Vector3 import Vector3
from OpenBveApi.Math.Vectors.Vector2 import Vector2
from OpenBveApi.Routes.Track import Track
from OpenBveApi.World.Transformations import Transformation
from OpenBveApi.Routes.TrackElement import TrackElement

import math
import numpy as np
from tqdm import tqdm

from uitl import Util


class Parser8:
    def __init__(self):
        super().__init__()  # 💡 중요!

    def apply_route_data(self, filename: str, data: RouteData, preview_only: bool) -> RouteData:

        last_block = int(math.floor((data.TrackPosition + 600.0) / data.BlockInterval + 0.001) + 1)
        if abs(data.Blocks[len(data.Blocks) - 1].CurrentTrackState.CurveRadius) < 300:
            '''
            * The track end event is placed 600m after the end of the final block
            * If our curve radius in the final block is < 300, then our train will
            * re-appear erroneously if the player is watching the final block
            '''
            data.Blocks[len(data.Blocks) - 1].CurrentTrackState.CurveRadius = 0.0

        self.CurrentRoute.BlockLength = data.BlockInterval
        self.CurrentRoute.AccurateObjectDisposal = self.Plugin.CurrentOptions.ObjectDisposalMode
        data.create_missing_blocks(last_block, preview_only)
        # interpolate height
        if not preview_only:
            z = 0
            for i in range(len(data.Blocks)):
                if not math.isnan(data.Blocks[i].Height):
                    for j in range(i - 1, -1, -1):
                        if not math.isnan(data.Blocks[j].Height):
                            a = data.Blocks[j].Height
                            b = data.Blocks[i].Height
                            d = (b - a) / (i - j)
                            for k in range(j + 1, i):
                                a += d
                                data.Blocks[k].Height = a
                            break
                    z = i
            for i in range(z + 1, len(data.Blocks)):
                data.Blocks[i].Height = data.Blocks[z].Height
        # create objects and track

        position = Vector3.Zero()
        position.y = self.CurrentRoute.Atmosphere.InitialElevation  # elvation 설정
        position.x = self.CurrentRoute.Atmosphere.InitialX  # X 좌표
        position.z = self.CurrentRoute.Atmosphere.InitialY  # Z 좌표
        direction = Vector2.Down()

        # 여기서부터 코드 수정
        degree = self.CurrentRoute.Atmosphere.InitialDirection
        rad = degree * math.pi / 180.0  # 각도를 라디안으로 변환
        dx241 = math.cos(rad)  # 임시변수
        dy241 = math.sin(rad)  # 임시변수
        direction = Vector2(dx241, dy241)

        if data.FirstUsedBlock < 0:
            data.FirstUsedBlock = 0
        current_track_length = 0
        for i in range(data.FirstUsedBlock, len(data.Blocks)):
            for d, (key, rail) in enumerate(data.Blocks[i].Rails.items()):
                if key not in self.CurrentRoute.Tracks:
                    self.CurrentRoute.Tracks[key] = Track()
        # process blocks
        progress_factor = 1.0 if len(data.Blocks) - data.FirstUsedBlock == 0 else 1.0 / (
                len(data.Blocks) - data.FirstUsedBlock)

        # initial list
        # List to store x and z values
        coordinates = []
        pitch_info = []
        curve_info = []
        rail_info = []
        stacoordinates = []
        extrac_height_list = []
        freeobjcoordinates = []

        for i in range(data.FirstUsedBlock, len(data.Blocks)):
            self.Plugin.CurrentProgress = 0.6667 + (i - data.FirstUsedBlock) * progress_factor
            if (i & 15) == 0:
                # time.sleep(1)
                if self.Plugin.Cancel:
                    self.Plugin.IsLoading = False
                    return

            starting_distance = i * data.BlockInterval
            ending_distance = starting_distance + data.BlockInterval
            direction.normalize()

            world_track_element = data.Blocks[i].CurrentTrackState
            n = current_track_length
            for key, track in self.CurrentRoute.Tracks.items():
                if n >= len(track.Elements):
                    new_length = len(track.Elements) * 2

                    track.Elements.extend([TrackElement() for _ in range(new_length - len(track.Elements))])
            current_track_length += 1
            self.CurrentRoute.Tracks[0].Elements[n] = world_track_element
            self.CurrentRoute.Tracks[0].Elements[n].WorldPosition = Vector3(position.x, position.y, position.z)

            coordinates.append(f'{position.x}, {position.z}, {position.y}')
            self.CurrentRoute.Tracks[0].Elements[n].WorldDirection = Vector3.get_vector3(direction,
                                                                                         data.Blocks[i].Pitch)
            self.CurrentRoute.Tracks[0].Elements[n].WorldSide = Vector3(direction.y, 0.0, -direction.x)
            self.CurrentRoute.Tracks[0].Elements[n].WorldUp = \
                Vector3.cross(self.CurrentRoute.Tracks[0].Elements[n].WorldDirection,
                              self.CurrentRoute.Tracks[0].Elements[n].WorldSide)
            self.CurrentRoute.Tracks[0].Elements[n].StartingTrackPosition = starting_distance
            # station
            if data.Blocks[i].Station >= 0:
                # station
                s = data.Blocks[i].Station
                t = self.CurrentRoute.Stations[s].Name
                stacoordinates.append(f'{position.x},{position.z},{t}')

            # Pitch
            self.CurrentRoute.Tracks[0].Elements[n].Pitch = data.Blocks[i].Pitch
            extrac_pitch = data.Blocks[i].Pitch

            # Add x and z values to the list
            pitch_info.append(f"{starting_distance},{extrac_pitch}")

            # height txt
            extrac_height = data.Blocks[i].Height

            # curves
            a = 0.0
            c = data.BlockInterval
            h = 0.0
            if world_track_element.CurveRadius != 0.0 and data.Blocks[i].Pitch != 0.0:
                d = data.BlockInterval
                p = data.Blocks[i].Pitch
                r = world_track_element.CurveRadius
                s = d / math.sqrt(1.0 + p * p)
                h = s * p
                b = s / abs(r)
                c = math.sqrt(2.0 * r * r * (1.0 - math.cos(b)))

                a = 0.5 * np.sign(r) * b
                direction.rotate(math.cos(-a), math.sin(-a))
            elif world_track_element.CurveRadius != 0.0:
                d = data.BlockInterval
                r = world_track_element.CurveRadius
                b = d / abs(r)
                c = math.sqrt(2.0 * r * r * (1.0 - math.cos(b)))
                a = 0.5 * np.sign(r) * b
                direction.rotate(math.cos(-a), math.sin(-a))
            elif data.Blocks[i].Pitch != 0.0:
                p = data.Blocks[i].Pitch
                d = data.BlockInterval
                c = d / math.sqrt(1.0 + p * p)
                h = c * p

            TrackYaw = math.atan2(direction.x, direction.y)
            TrackPitch = math.atan(data.Blocks[i].Pitch)
            GroundTransformation = Transformation(TrackYaw, 0.0, 0.0)
            TrackTransformation = Transformation(TrackYaw, TrackPitch, 0.0)

            extract_radius = world_track_element.CurveRadius
            extract_cant = world_track_element.CurveCant
            # Add x and z values to the list
            curve_info.append(f"{starting_distance},{extract_radius},{extract_cant}")

            extrac_height_list.append(f"{starting_distance},{extrac_height}")

            # rail-aligned objects

            for railInBlock in range(len(data.Blocks[i].Rails)):
                railKey = list(data.Blocks[i].Rails.keys())[railInBlock]
                if railKey > 0 and not data.Blocks[i].Rails[railKey].RailStarted and not \
                        self.Plugin.CurrentRoute.Tracks[railKey].Elements[n].ContainsSwitch:
                    # NOTE: If element contains a switch, it must be valid
                    self.Plugin.CurrentRoute.Tracks[railKey].Elements[n].InvalidElement = True

                # rail
                pos = 0

                RailTransformation = Transformation()
                planar, updown = 0.0, 0.0
                if railKey == 0:
                    # rail 0
                    RailTransformation = Transformation(TrackTransformation, planar, updown, 0.0)
                    pos = position
                else:
                    # rails 1-infinity
                    x = data.Blocks[i].Rails[railKey].RailStart.x
                    y = data.Blocks[i].Rails[railKey].RailStart.y
                    offset = Vector3(direction.y * x, y, -direction.x * x)
                    pos = position + offset
                    if i < len(data.Blocks) - 1 and railKey in data.Blocks[i + 1].Rails:
                        # take orientation of upcoming block into account
                        direction2 = direction
                        position2 = position
                        position2.x += direction.x * c
                        position2.y += h
                        position2.z += direction.y * c
                        if a != 0.0:
                            direction2.rotate(math.cos(-a), math.sin(-a))
                        if data.Blocks[i + 1].Turn != 0.0:
                            ag = -math.atan(data.Blocks[i + 1].Turn)
                            cosag = math.cos(ag)
                            sinag = math.sin(ag)
                        a2 = 0.0
                        # double c2 = Data.BlockInterval;
                        # double h2 = 0.0;
                        if data.Blocks[i + 1].CurrentTrackState.CurveRadius != 0.0 and data.Blocks[i + 1].Pitch != 0.0:
                            d2 = data.BlockInterval
                            p2 = data.Blocks[i + 1].Pitch
                            r2 = data.Blocks[i + 1].CurrentTrackState.CurveRadius
                            s2 = d2 / math.sqrt(1.0 + p2 * p2)
                            # h2 = s2 * p2;
                            b2 = s2 / abs(r2)
                            # c2 = Math.Sqrt(2.0 * r2 * r2 * (1.0 - Math.Cos(b2)))
                            a2 = 0.5 * np.sign(r2) * b2
                            direction2.rotate(math.cos(-a2), math.sin(-a2))
                        elif data.Blocks[i + 1].CurrentTrackState.CurveRadius != 0.0:
                            d2 = data.BlockInterval
                            r2 = data.Blocks[i + 1].CurrentTrackState.CurveRadius
                            b2 = d2 / abs(r2)
                            # c2 = Math.Sqrt(2.0 * r2 * r2 * (1.0 - Math.Cos(b2)))
                            a2 = 0.5 * np.sign(r2) * b2
                            direction2.rotate(math.cos(-a2), math.sin(-a2))
                        '''
                        // else if (Data.Blocks[i + 1].Pitch != 0.0) {
                        // double p2 = Data.Blocks[i + 1].Pitch;
                        // double d2 = Data.BlockInterval;
                        // c2 = d2 / Math.Sqrt(1.0 + p2 * p2);
                        // h2 = c2 * p2;
                        // }
                        
                        //These generate a compiler warning, as secondary tracks do not generate yaw, as they have no
                        //concept of a curve, but rather are a straight line between two points
                        //TODO: Revist the handling of secondary tracks ==> !!BACKWARDS INCOMPATIBLE!!
                        /*
                        double TrackYaw2 = Math.Atan2(Direction2.X, Direction2.Y);
                        double TrackPitch2 = Math.Atan(Data.Blocks[i + 1].Pitch);
                        Transformation GroundTransformation2 = new Transformation(TrackYaw2, 0.0, 0.0);
                        Transformation TrackTransformation2 = new Transformation(TrackYaw2, TrackPitch2, 0.0);
                        */
                        '''
                        x2 = data.Blocks[i + 1].Rails[railKey].RailEnd.x
                        y2 = data.Blocks[i + 1].Rails[railKey].RailEnd.y
                        offset2 = Vector3(direction2.y * x2, y2, -direction2.x * x2)
                        pos2 = position2 + offset2
                        r = Vector3(pos2.x - pos.x, pos2.y - pos.y, pos2.z - pos.z)
                        r.normalize()
                        RailTransformation.Z = r
                        RailTransformation.X = Vector3(r.z, 0.0, -r.x)
                        self.normalize(RailTransformation.X.x, RailTransformation.X.z)
                        RailTransformation.Y = Vector3.cross(RailTransformation.Z, RailTransformation.X)
                        planar = math.atan(data.Blocks[i + 1].Rails[railKey].MidPoint.x / c)
                        updown = math.atan(data.Blocks[i + 1].Rails[railKey].MidPoint.y / c)
                    else:
                        planar = 0.0
                        updown = 0.0
                        RailTransformation = Transformation(TrackTransformation, 0.0, 0.0, 0.0)
                    self.CurrentRoute.Tracks[railKey].Elements[n].StartingTrackPosition = starting_distance;
                    self.CurrentRoute.Tracks[railKey].Elements[n].WorldPosition = pos
                    self.CurrentRoute.Tracks[railKey].Elements[n].WorldDirection = RailTransformation.Z
                    self.CurrentRoute.Tracks[railKey].Elements[n].WorldSide = RailTransformation.X
                    self.CurrentRoute.Tracks[railKey].Elements[n].WorldUp = RailTransformation.Y
                    self.CurrentRoute.Tracks[railKey].Elements[n].CurveCant = data.Blocks[i].Rails[railKey].CurveCant
                    self.CurrentRoute.Tracks[railKey].Elements[n].AdhesionMultiplier = data.Blocks[i].Rails[
                        railKey].AdhesionMultiplier
                    self.CurrentRoute.Tracks[railKey].Elements[n].IsDriveable = data.Blocks[i].Rails[railKey].IsDriveable

                    # extract key
                    if data.Blocks[i].Rails[railKey].RailStarted:
                        rail_info.append(f'{railKey},{pos.x},{pos.y},{pos.z}')
                    else:
                        continue
                if not preview_only:
                    # free objects
                    if railKey in data.Blocks[i].RailFreeObj:
                        for k in range(len(data.Blocks[i].RailFreeObj[railKey])):
                            worldposition = data.Blocks[i].RailFreeObj[railKey][k].CreateRailAligned(
                                data.Structure.FreeObjects,
                                pos.clone(),
                                RailTransformation,
                                starting_distance,
                                ending_distance
                            )
                            freeobjtype = data.Blocks[i].RailFreeObj[railKey][k].Type
                            extreact_TrackPosition = data.Blocks[i].RailFreeObj[railKey][k].TrackPosition
                            freeobjcoordinates.append(f"{extreact_TrackPosition},{railKey},{freeobjtype},"
                                                      f"{worldposition.x},{worldposition.z},{worldposition.y}")


            # finalize block
            position.x += direction.x * c
            position.y += h
            position.z += direction.y * c

            if a != 0.0:
                direction.rotate(math.cos(-a), math.sin(-a))

        # Write x and z values to a TXT file
        Util.write_all_lines(r"c:\temp\pitch_info.txt", pitch_info)
        Util.write_all_lines(r"c:\temp\curve_info.txt", curve_info)
        Util.write_all_lines(r"c:\temp\rail_info.txt", rail_info)
        Util.write_all_lines(r"c:\temp\bve_coordinates.txt", coordinates)
        Util.write_all_lines(r"c:\temp\bve_stationcoordinates.txt", stacoordinates)
        Util.write_all_lines(r"c:\temp\height_info.txt", extrac_height_list)
        Util.write_all_lines(r"c:\temp\bve_freeobjcoordinates.txt", freeobjcoordinates)

        return data
