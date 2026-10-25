import ezdxf
import math
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import random

from expor_module.schemas import AlignmentRecord


class DXFManger:
    def __init__(self):
        self.doc = ezdxf.new(dxfversion='R2010')
        self.msp = self.doc.modelspace()

    def create_dxf(self, alignmnets: list[AlignmentRecord], output_dir: str, filename: str):
        self.alignments = alignmnets

        #평면선형 작성
        self.create_plan()

        #평면 정거장 작성
        #self.create_plan_stations()

        #종단선형 작성
        #self.create_profile()

        #freeobj작성
        #self.create_freeobj()

        #배선 작성
        #self.create_layout()
        #저장
        dxf_path = os.path.join(output_dir, filename)
        self.doc.saveas(dxf_path)

    def create_plan(self):
        # Create a 3D polyline
        plan_2d_name = "plan2d"
        plan_3d_name = "plan3d"
        layer_color = 1
        plan_2d_layer = self.doc.layers.new(name=plan_2d_name, dxfattribs={'color': layer_color})
        plan_3d_layer = self.doc.layers.new(name=plan_3d_name, dxfattribs={'color': layer_color})

        xyz_coords = [(al.x, al.y, al.z) for al in self.alignments]
        chainages = [(al.starting_distance, al.x, al.y, al.z)  for al in self.alignments]

        # 각 측점 위치에 텍스트 추가
        for chain, x, y ,z in chainages:
            self.msp.add_text(str(chain), dxfattribs={'height': 4, 'layer': 'chainage', 'insert': (x, y)})

        self.msp.add_polyline3d(xyz_coords, dxfattribs={'layer': plan_3d_name})
        self.msp.add_lwpolyline(xyz_coords, dxfattribs={'layer': plan_2d_name, 'const_width': 4})

    def create_plan_stations(self):
        # 역 표시용 레이어 생성
        station_layer = "plan_station"
        self.doc.layers.new(name=station_layer, dxfattribs={'color': 1})  # 빨강

        # 텍스트 스타일
        self.doc.styles.new("myStandard", dxfattribs={"font": "Gulim.ttf"})

        text_height = 40
        radius = 20
        blank = 15
        textmargin = 5
        num_segments = 36

        for sta, x, y, name in self.stations:
            coord = (x, y)
            offset = (x + text_height, y + text_height)
            offsetx, offsety = offset

            # 원
            self.msp.add_circle(center=coord, radius=radius,
                                dxfattribs={'layer': station_layer})
            hatch = self.msp.add_hatch(color=130, dxfattribs={'layer': station_layer})
            edge_path = hatch.paths.add_edge_path()
            edge_path.add_arc(center=coord, radius=radius, start_angle=0, end_angle=360)

            # 원을 근사하는 폴리선
            points = []
            for i in range(num_segments):
                angle = 2 * math.pi * i / num_segments
                px = x + radius * math.cos(angle)
                py = y + radius * math.sin(angle)
                points.append((px, py))
            points.append(points[0])
            self.msp.add_lwpolyline(points, dxfattribs={'const_width': 2, 'layer': station_layer})

            # 역 이름 텍스트
            self.msp.add_text(name, dxfattribs={'insert': offset, 'height': text_height,
                                                'color': 250, 'style': "myStandard",
                                                'layer': station_layer})

            # 텍스트 박스
            text_width = 40 * len(name) + (blank * len(name))
            lower_left = (offsetx, offsety - textmargin)
            lower_right = (offsetx + text_width, offsety - textmargin)
            upper_left = (offsetx, offsety + text_height + textmargin)
            upper_right = (offsetx + text_width, offsety + text_height + textmargin)

            self.msp.add_lwpolyline([lower_left, lower_right, upper_right, upper_left, lower_left],
                                    dxfattribs={'const_width': 2, 'layer': station_layer})

    def create_profile(self):
        profile_layer = "profile"
        ground_layer = "ground"
        grid_layer = "grid"
        station_layer = "profile_station"

        self.doc.layers.new(name=profile_layer, dxfattribs={'color': 1})  # 빨강
        self.doc.layers.new(name=ground_layer, dxfattribs={'color': 3})  # 녹색
        self.doc.layers.new(name=grid_layer, dxfattribs={'color': 8})  # 회색 (보조선)
        self.doc.layers.new(name=station_layer, dxfattribs={'color': 6})  # 마젠타

        profile_coords = [(data.station, data.z) for data in self.bvedatas]
        ground_coords = [(data.station, data.z - data.height) for data in self.bvedatas]

        # 종단선형 polyline
        self.msp.add_lwpolyline(profile_coords, dxfattribs={'layer': profile_layer})
        self.msp.add_lwpolyline(ground_coords, dxfattribs={'layer': ground_layer})

        # 텍스트
        for sta, h in profile_coords:
            self.msp.add_text(f"{h:.2f}m",
                              dxfattribs={'insert': (sta, h + 10),
                                          'height': 5,
                                          'layer': profile_layer,
                                          'color': 2})
            self.msp.add_text(f"{int(sta)}",
                              dxfattribs={'insert': (sta, 0),
                                          'height': 5,
                                          'layer': profile_layer,
                                          'color': 1})

        # 가로선 (예: 0m ~ 최대고도까지 50m 간격)
        sta_min = min([d.station for d in self.bvedatas])
        sta_max = max([d.station for d in self.bvedatas])
        h_min = min([d.z for d in self.bvedatas]) - 20
        h_max = max([d.z for d in self.bvedatas]) + 20

        for h in range(int(h_min), int(h_max) + 1, 50):
            self.msp.add_line((sta_min, h), (sta_max, h), dxfattribs={'layer': grid_layer})

        # 세로선 (예: 100m 간격)
        for sta in range(int(sta_min), int(sta_max) + 1, 100):
            self.msp.add_line((sta, h_min), (sta, h_max), dxfattribs={'layer': grid_layer})

            # 범위 계산
            sta_min = min([d.station for d in self.bvedatas])
            sta_max = max([d.station for d in self.bvedatas])
            h_min = min([d.z for d in self.bvedatas]) - 20
            h_max = max([d.z for d in self.bvedatas]) + 20

        # 정거장 표시 (수직선 + 텍스트 + 원)

        for chain, x, y, name in self.stations:
            sta = chain
            # 해당 station과 가장 가까운 bvedata 찾기
            nearest = min(self.bvedatas, key=lambda d: abs(d.station - sta))
            level = nearest.z
            # 수직선
            self.msp.add_line((sta, level), (sta, level + 100),
                              dxfattribs={'layer': station_layer})

            # 원 기호 (기준선 근처)
            self.msp.add_circle(center=(sta, level + 50), radius=5,
                                dxfattribs={'layer': station_layer})

            # 텍스트 (원 옆에 배치)
            self.msp.add_text(name,
                              dxfattribs={'insert': (sta + 10, level + 70),
                                          'height': 8,
                                          'layer': station_layer,
                                          'color': 6,
                                          'style': "myStandard"})
    def create_freeobj(self):
        # 프리오브젝트
        if self.freeobjects:
            for objidx, name, x, y, z in self.freeobjects:
                coord = (x, y)
                objname = f'{str(objidx)}[{name}]'
                text = self.msp.add_text(objname,
                                    dxfattribs={'insert': coord, 'height': 1, 'color': 6,
                                                "style": "myStandard"})

    def create_layout(self):
        if not self.bverails:
            return
        # 레이어 및 색상 처리
        color_map = {}
        used_colors = set()
        aci_colors = list(range(256))
        aci_colors.remove(10)  # 10번 컬러는 사용하지 않음

        def get_random_color():
            while True:

                color = random.choice(aci_colors)
                if color not in used_colors:
                    used_colors.add(color)
                    return color

        # Group coordinates by railindex
        rail_coordinates = {}
        stationtexts = {}

        for rail in self.bverails:
            station = rail.station
            railindex = rail.index
            x, y, z = rail.x , rail.y, rail.z

            if railindex not in rail_coordinates:
                rail_coordinates[railindex] = []
            rail_coordinates[railindex].append((x, y, z))

            if railindex not in stationtexts:
                stationtexts[railindex] = []
            stationtexts[railindex].append((station, x, y))

        # Create layers and add polylines for each railindex
        for railindex, coords in rail_coordinates.items():
            layer_name = f"rail {railindex}"
            layer_color = get_random_color()

            # Add layer with specified color
            layer = self.doc.layers.new(name=layer_name, dxfattribs={'color': layer_color})

            # Add 3D polylines to the modelspace
            self.msp.add_polyline3d(coords, dxfattribs={'layer': layer_name})

            # 각 station 위치에 텍스트 추가
            for station, x, y in stationtexts[railindex]:
                self.msp.add_text(str(station), dxfattribs={'height': 4, 'layer': layer_name, 'insert': (x, y)})
class BveDxfConverter:
    def __init__(self, root):
        self.root = root
        root.title("BVE DXF 변환기")

        # 좌표 파일
        tk.Label(root, text="BVE선형 파일:").grid(row=0, column=0, sticky="w")
        self.entry_input1 = tk.Entry(root, width=50)
        self.entry_input1.grid(row=0, column=1, padx=5, pady=2)
        tk.Button(root, text="찾기", command=self.browse_input1).grid(row=0, column=2, padx=5)

        # 역 좌표 파일
        tk.Label(root, text="역 좌표 파일:").grid(row=1, column=0, sticky="w")
        self.entry_input2 = tk.Entry(root, width=50)
        self.entry_input2.grid(row=1, column=1, padx=5, pady=2)
        tk.Button(root, text="찾기", command=self.browse_input2).grid(row=1, column=2, padx=5)

        #프리오브젝트 파일
        tk.Label(root, text="프리오브젝트 파일:").grid(row=2, column=0, sticky="w")
        self.entry_input3 = tk.Entry(root, width=50)
        self.entry_input3.grid(row=2, column=1, padx=5, pady=2)
        tk.Button(root, text="찾기", command=self.browse_input3).grid(row=2, column=2, padx=5)

        #배선 파일
        tk.Label(root, text="배선 파일:").grid(row=3, column=0, sticky="w")
        self.layout_entry = tk.Entry(root, width=50)
        self.layout_entry.grid(row=3, column=1, padx=5, pady=2)
        tk.Button(root, text="찾기", command=self.browse_railinfo).grid(row=3, column=2, padx=5)

        # 출력 파일
        tk.Label(root, text="출력 DXF 파일:").grid(row=4, column=0, sticky="w")
        self.entry_output = tk.Entry(root, width=50)
        self.entry_output.grid(row=4, column=1, padx=5, pady=2)
        tk.Button(root, text="저장", command=self.browse_output).grid(row=4, column=2, padx=5)

        frame_buttons = tk.Frame(root)
        frame_buttons.grid(row=5, column=0, columnspan=3, pady=10)

        tk.Button(frame_buttons, text="DXF 생성", command=self.run_process,
                  width=10, bg="lightblue").pack(side="left", padx=5)

        tk.Button(frame_buttons, text="종료", command=root.destroy,
                  width=10, bg="lightblue").pack(side="left", padx=5)

    def run_process(self):
        input_file = self.entry_input1.get()
        input_file2 = self.entry_input2.get()
        input_file3 = self.entry_input3.get() if self.entry_input3.get() else None
        output_file = self.entry_output.get()
        layoutfile = self.layout_entry.get()

        if not input_file or not os.path.exists(input_file):
            messagebox.showerror("에러", "좌표 파일을 선택하세요.")
            return
        if not input_file2 or not os.path.exists(input_file2):
            messagebox.showerror("에러", "역 좌표 파일을 선택하세요.")
            return
        if not output_file:
            messagebox.showerror("에러", "출력 DXF 파일 경로를 지정하세요.")
            return
        # 2. 통합 파서 인스턴스 생성 및 호출
        loader = BVEDataLoader()
        dxfmger = DXFManger()
        try:
            bvedatas = loader.load_track_alignment(input_file)
            stations = loader.load_stations(input_file2)
            freeobjects = loader.load_free_objects(input_file3) if input_file3 else None
            bverails = loader.load_rail_info(layoutfile) if layoutfile else None

            dxfmger.create_dxf(bvedatas, stations, freeobjects, output_file, bverails)
            messagebox.showinfo("완료", f"DXF 파일이 생성되었습니다.\n{output_file}")
        except Exception as e:
            messagebox.showerror("에러", f"처리 중 오류 발생:\n{e}")

    def browse_input1(self):
        filename = filedialog.askopenfilename(title="선형 파일 선택",
                                              filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if filename:
            self.entry_input1.delete(0, tk.END)
            self.entry_input1.insert(0, filename)

    def browse_input2(self):
        filename = filedialog.askopenfilename(title="역 좌표 파일 선택",
                                              filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if filename:
            self.entry_input2.delete(0, tk.END)
            self.entry_input2.insert(0, filename)

    def browse_input3(self):
        filename = filedialog.askopenfilename(title="프리오브젝트 파일 선택",
                                              filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if filename:
            self.entry_input3.delete(0, tk.END)
            self.entry_input3.insert(0, filename)

    def browse_railinfo(self):
        filename = filedialog.askopenfilename(title="배선 파일 선택",
                                              filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if filename:
            self.layout_entry.delete(0, tk.END)
            self.layout_entry.insert(0, filename)

    def browse_output(self):
        filename = filedialog.asksaveasfilename(title="DXF 파일 저장",
                                                defaultextension=".dxf",
                                                filetypes=[("DXF files", "*.dxf"), ("All files", "*.*")])
        if filename:
            self.entry_output.delete(0, tk.END)
            self.entry_output.insert(0, filename)
    def destroy(self):
        self.root.destroy()