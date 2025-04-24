import time

from Plugins.RouteCsvRw.RouteData import RouteData
from OpenBveApi.Math.Vectors.Vector3 import Vector3
from OpenBveApi.Math.Vectors.Vector2 import Vector2
from OpenBveApi.Routes.Track import Track

import math
import numpy as np
from tqdm import tqdm

from uitl import Util


class Parser8:
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
        direction = Vector2.Down()
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

        # 블록 처리용 프로그레스 바 준비
        total_blocks = len(data.Blocks) - data.FirstUsedBlock
        pbar = tqdm(total=total_blocks, desc="Processing Blocks")

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
                    track.Elements.extend([None] * (new_length - len(track.Elements)))
            current_track_length += 1
            self.CurrentRoute.Tracks[0].Elements[n] = world_track_element
            self.CurrentRoute.Tracks[0].Elements[n].WorldPosition = position

            coordinates.append(f'{position.x}, {position.z}, {position.y}')
            self.CurrentRoute.Tracks[0].Elements[n].WorldDirection = Vector3.get_vector3(direction,
                                                                                         data.Blocks[i].Pitch)
            self.CurrentRoute.Tracks[0].Elements[n].WorldSide = Vector3(direction.y, 0.0, -direction.x)
            self.CurrentRoute.Tracks[0].Elements[n].WorldUp = \
                Vector3.cross(self.CurrentRoute.Tracks[0].Elements[n].WorldDirection,
                              self.CurrentRoute.Tracks[0].Elements[n].WorldSide)
            self.CurrentRoute.Tracks[0].Elements[n].StartingTrackPosition = starting_distance

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

            track_yaw = math.atan2(direction.x, direction.y)
            track_pitch = math.atan(data.Blocks[i].Pitch)

            extract_radius = world_track_element.CurveRadius
            extract_cant = world_track_element.CurveCant
            # Add x and z values to the list
            curve_info.append(f"{starting_distance},{extract_radius},{extract_cant}")

            extrac_height_list.append(f"{starting_distance},{extrac_height}")

            # finalize block
            position.x += direction.x * c
            position.y += h
            position.z += direction.y * c

            if a != 0.0:
                direction.rotate(math.cos(-a), math.sin(-a))
            pbar.update(1)
        pbar.close()
        # Write x and z values to a TXT file
        Util.write_all_lines(r"c:\temp\pitch_info.txt", pitch_info)
        Util.write_all_lines(r"c:\temp\curve_info.txt", curve_info)
        Util.write_all_lines(r"c:\temp\rail_info.txt", rail_info)
        Util.write_all_lines(r"c:\temp\bve_coordinates.txt", coordinates)
        Util.write_all_lines(r"c:\temp\bve_stationcoordinates.txt", stacoordinates)
        Util.write_all_lines(r"c:\temp\height_info.txt", extrac_height_list)
        Util.write_all_lines(r"c:\temp\bve_freeobjcoordinates.txt", freeobjcoordinates)

        return data
