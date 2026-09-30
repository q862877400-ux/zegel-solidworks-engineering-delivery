"""
型材截面面积与米重计算工具 GUI v1.0
基于 AlWeight-Python v8.0

运行方式：
    python gui_profile_calc.py

依赖：
    pip install ezdxf
"""

import math
import csv
import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

try:
    import ezdxf
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "ezdxf"])
    import ezdxf

# ============================================================
# 核心计算逻辑（来自 AlWeight-Python v8.0）
# ============================================================

MATERIAL_DENSITY = {
    "6063 铝合金": 2700.0,
    "7075 铝合金": 2810.0,
    "2024 铝合金": 2780.0,
    "6061 铝合金": 2720.0,
    "5052 铝合金": 2680.0,
    "Q235 碳钢":   7850.0,
    "Q345 碳钢":   7850.0,
    "304 不锈钢":  7930.0,
    "316 不锈钢":  7980.0,
    "纯铜":        8960.0,
    "黄铜":        8500.0,
    "钛合金":      4507.0,
}


def polygon_area(vertices):
    n = len(vertices)
    if n < 3:
        return 0.0
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += vertices[i][0] * vertices[j][1]
        area -= vertices[j][0] * vertices[i][1]
    return abs(area) / 2.0


def circle_area(radius):
    return math.pi * radius * radius


def ellipse_area(major_r, minor_r):
    return math.pi * major_r * minor_r


def bulge_arc_points(start, end, bulge, num_segments=16):
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    dist = math.sqrt(dx * dx + dy * dy)
    if dist == 0 or bulge == 0:
        return [start]
    angle = 4 * math.atan(abs(bulge))
    if angle < 1e-10 or angle > 2 * math.pi - 1e-10:
        return [start, end]
    radius = dist / (2 * math.sin(angle / 2))
    if radius <= 0:
        return [start, end]
    mid_x = (start[0] + end[0]) / 2
    mid_y = (start[1] + end[1]) / 2
    perp_dist = radius * math.cos(angle / 2)
    ux, uy = dx / dist, dy / dist
    if bulge > 0:
        px, py = -uy, ux
    else:
        px, py = uy, -ux
    cx = mid_x + perp_dist * px
    cy = mid_y + perp_dist * py
    start_a = math.atan2(start[1] - cy, start[0] - cx)
    end_a = math.atan2(end[1] - cy, end[0] - cx)
    if bulge > 0:
        if end_a <= start_a:
            end_a += 2 * math.pi
    else:
        if end_a >= start_a:
            end_a -= 2 * math.pi
    points = []
    for j in range(num_segments):
        t = j / num_segments
        a = start_a + t * (end_a - start_a)
        points.append((cx + radius * math.cos(a), cy + radius * math.sin(a)))
    return points


def extract_lwpolyline_vertices(entity, close_if_needed=False):
    vertices = []
    points = entity.get_points()
    for i in range(len(points)):
        pt = points[i]
        x = float(pt[0])
        y = float(pt[1])
        bulge = float(pt[4]) if len(pt) > 4 else 0.0
        start = (x, y)
        if bulge != 0.0 and i < len(points) - 1:
            next_pt = points[i + 1]
            end = (float(next_pt[0]), float(next_pt[1]))
            arc_pts = bulge_arc_points(start, end, bulge, num_segments=16)
            vertices.extend(arc_pts)
        else:
            vertices.append(start)
    if len(points) > 1 and len(points[-1]) > 4:
        last_bulge = float(points[-1][4])
        if last_bulge != 0.0 and (entity.closed or close_if_needed):
            end = (float(points[0][0]), float(points[0][1]))
            arc_pts = bulge_arc_points(vertices[-1] if vertices else start, end, last_bulge, num_segments=16)
            vertices.extend(arc_pts)
    return vertices


def exact_lwpolyline_area(entity, close_if_needed=False):
    pts = entity.get_points()
    n = len(pts)
    if n < 3:
        return 0.0
    vertices = [(float(p[0]), float(p[1])) for p in pts]
    bulges = [float(p[4]) if len(p) > 4 else 0.0 for p in pts]
    start = vertices[0]
    end = vertices[-1]
    gap = math.sqrt((start[0] - end[0]) ** 2 + (start[1] - end[1]) ** 2)
    is_closed = entity.closed or close_if_needed
    if not is_closed:
        return 0.0
    is_near_duplicate = gap < 0.01
    if is_near_duplicate:
        vertices = vertices[:-1]
        bulges = bulges[:-1]
        n = len(vertices)
    if n < 3:
        return 0.0
    num_edges = n
    shoelace = 0.0
    for i in range(num_edges):
        j = (i + 1) % n
        shoelace += vertices[i][0] * vertices[j][1]
        shoelace -= vertices[j][0] * vertices[i][1]
    shoelace /= 2.0
    total_correction = 0.0
    for i in range(num_edges):
        b = bulges[i]
        if abs(b) < 1e-10:
            continue
        j = (i + 1) % n
        x1, y1 = vertices[i]
        x2, y2 = vertices[j]
        chord = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        if chord < 1e-10:
            continue
        theta = 4.0 * math.atan(abs(b))
        if theta < 1e-10 or theta > 2 * math.pi - 1e-10:
            continue
        sin_half = math.sin(theta / 2.0)
        if abs(sin_half) < 1e-10:
            continue
        r = chord / (2.0 * sin_half)
        segment_area = r ** 2 * (theta - math.sin(theta)) / 2.0
        correction = math.copysign(segment_area, b)
        total_correction += correction
    exact_signed = shoelace + total_correction
    return abs(exact_signed)


def exact_combined_pair_area(entity_a, entity_b):
    pts_a = entity_a.get_points()
    pts_b = entity_b.get_points()
    verts_a = [(float(p[0]), float(p[1])) for p in pts_a]
    bulges_a = [float(p[4]) if len(p) > 4 else 0.0 for p in pts_a]
    verts_b = [(float(p[0]), float(p[1])) for p in pts_b]
    bulges_b = [float(p[4]) if len(p) > 4 else 0.0 for p in pts_b]
    tol = 0.01
    end_a = verts_a[-1]
    start_b = verts_b[0]
    end_b = verts_b[-1]
    start_a = verts_a[0]
    m1 = abs(end_a[0] - start_b[0]) < tol and abs(end_a[1] - start_b[1]) < tol
    m2 = abs(end_b[0] - start_a[0]) < tol and abs(end_b[1] - start_a[1]) < tol
    m3 = abs(start_a[0] - start_b[0]) < tol and abs(start_a[1] - start_b[1]) < tol
    m4 = abs(end_a[0] - end_b[0]) < tol and abs(end_a[1] - end_b[1]) < tol
    if m1 and m2:
        combined = list(verts_a)
        combined.extend(verts_b[1:])
    elif m3 and m4:
        reversed_b = list(reversed(verts_b))
        reversed_bulges_b = list(reversed(bulges_b))
        combined = list(verts_a)
        combined.extend(reversed_b[1:])
        bulges_b = reversed_bulges_b
    else:
        return 0.0
    n = len(combined)
    if n < 3:
        return 0.0
    shoelace = 0.0
    for i in range(n):
        j = (i + 1) % n
        shoelace += combined[i][0] * combined[j][1]
        shoelace -= combined[j][0] * combined[i][1]
    shoelace /= 2.0
    total_correction = 0.0

    def arc_correction(v1, v2, bulge_val):
        if abs(bulge_val) < 1e-10:
            return 0.0
        chord = math.sqrt((v2[0] - v1[0]) ** 2 + (v2[1] - v1[1]) ** 2)
        if chord < 1e-10:
            return 0.0
        theta = 4.0 * math.atan(abs(bulge_val))
        if theta < 1e-10 or theta > 2 * math.pi - 1e-10:
            return 0.0
        sin_half = math.sin(theta / 2.0)
        if abs(sin_half) < 1e-10:
            return 0.0
        r = chord / (2.0 * sin_half)
        segment_area = r ** 2 * (theta - math.sin(theta)) / 2.0
        return math.copysign(segment_area, bulge_val)

    for i in range(len(verts_a) - 1):
        total_correction += arc_correction(verts_a[i], verts_a[i + 1], bulges_a[i])
    for i in range(len(verts_b) - 1):
        total_correction += arc_correction(verts_b[i], verts_b[i + 1], bulges_b[i])
    exact_signed = shoelace + total_correction
    return abs(exact_signed)


def point_in_polygon(point, polygon):
    x, y = point
    n = len(polygon)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def get_all_contours_from_dxf(filepath):
    try:
        doc = ezdxf.readfile(filepath)
    except Exception as e:
        raise RuntimeError(f"读取 DXF 文件失败: {e}")
    msp = doc.modelspace()
    contours = []
    closed_polys = []
    effectively_closed = []
    open_polys = []
    for entity in msp:
        if entity.dxftype() != 'LWPOLYLINE':
            continue
        layer = entity.dxf.layer
        handle = entity.dxf.handle
        pts_raw = [(float(p[0]), float(p[1])) for p in entity.get_points()]
        if entity.closed:
            area = exact_lwpolyline_area(entity)
            verts = extract_lwpolyline_vertices(entity)
            xs = [p[0] for p in pts_raw]
            ys = [p[1] for p in pts_raw]
            bbox = (min(xs), min(ys), max(xs), max(ys))
            center = ((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)
            closed_polys.append({
                'source': 'closed_lwpoly', 'type': 'LWPOLYLINE(closed)',
                'area': area, 'layer': layer, 'handle': handle,
                'bbox': bbox, 'center': center, 'vertices': verts,
                'npts': len(pts_raw), 'entity': entity,
            })
        else:
            if len(pts_raw) < 2:
                continue
            start = pts_raw[0]
            end = pts_raw[-1]
            gap = math.sqrt((start[0] - end[0]) ** 2 + (start[1] - end[1]) ** 2)
            area = exact_lwpolyline_area(entity, close_if_needed=True)
            if area > 0.001:
                verts_full = extract_lwpolyline_vertices(entity, close_if_needed=True)
                xs = [v[0] for v in verts_full]
                ys = [v[1] for v in verts_full]
                bbox = (min(xs), min(ys), max(xs), max(ys))
                center = ((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)
                effectively_closed.append({
                    'source': 'effectively_closed' if gap < 0.1 else 'implicit_closed',
                    'type': 'LWPOLYLINE(eff_closed)' if gap < 0.1 else 'LWPOLYLINE(impl_closed)',
                    'area': area, 'layer': layer, 'handle': handle,
                    'bbox': bbox, 'center': center, 'vertices': verts_full,
                    'npts': len(pts_raw), 'gap': gap,
                })
            else:
                pass
    combined_pairs = []
    used_indices = set()
    for i, a in enumerate(open_polys):
        if i in used_indices:
            continue
        for j, b in enumerate(open_polys):
            if j in used_indices or j <= i:
                continue
            tol = 0.01
            m1 = abs(a['start'][0] - b['end'][0]) < tol and abs(a['start'][1] - b['end'][1]) < tol
            m2 = abs(a['end'][0] - b['start'][0]) < tol and abs(a['end'][1] - b['start'][1]) < tol
            m3 = abs(a['start'][0] - b['start'][0]) < tol and abs(a['start'][1] - b['start'][1]) < tol
            m4 = abs(a['end'][0] - b['end'][0]) < tol and abs(a['end'][1] - b['end'][1]) < tol
            if (m1 and m2) or (m3 and m4):
                area = exact_combined_pair_area(a['entity'], b['entity'])
                verts_a = extract_lwpolyline_vertices(a['entity'], close_if_needed=False)
                verts_b = extract_lwpolyline_vertices(b['entity'], close_if_needed=False)
                combined_verts = verts_a + verts_b
                xs = [v[0] for v in combined_verts]
                ys = [v[1] for v in combined_verts]
                bbox = (min(xs), min(ys), max(xs), max(ys))
                center = ((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)
                combined_pairs.append({
                    'source': 'combined_pair', 'type': 'LWPOLYLINE(combined)',
                    'area': area, 'layer': a['layer'],
                    'handle': a['handle'] + '+' + b['handle'],
                    'bbox': bbox, 'center': center, 'vertices': combined_verts,
                    'npts': a['npts'] + b['npts'],
                })
                used_indices.add(i)
                used_indices.add(j)
                break
    other_shapes = []
    for entity in msp:
        dxf_type = entity.dxftype()
        if dxf_type == 'LWPOLYLINE':
            continue
        layer = entity.dxf.layer if hasattr(entity.dxf, 'layer') else '0'
        handle = entity.dxf.handle if hasattr(entity.dxf, 'handle') else ''
        area = 0.0
        shape_type = dxf_type
        bbox = None
        vertices_raw = None
        if dxf_type == 'CIRCLE':
            r = float(entity.dxf.radius)
            cx, cy = float(entity.dxf.center.x), float(entity.dxf.center.y)
            area = circle_area(r)
            bbox = (cx - r, cy - r, cx + r, cy + r)
        elif dxf_type == 'ELLIPSE':
            major = entity.dxf.major_axis
            ratio = entity.dxf.ratio if hasattr(entity.dxf, 'ratio') else 1.0
            major_len = math.sqrt(major[0] ** 2 + major[1] ** 2 + major[2] ** 2)
            minor_len = major_len * ratio
            start_p = entity.dxf.start_param if hasattr(entity.dxf, 'start_param') else 0
            end_p = entity.dxf.end_param if hasattr(entity.dxf, 'end_param') else 2 * math.pi
            if abs(end_p - start_p - 2 * math.pi) < 0.01:
                area = ellipse_area(major_len, minor_len)
                cx, cy = float(entity.dxf.center.x), float(entity.dxf.center.y)
                bbox = (cx - major_len, cy - minor_len, cx + major_len, cy + minor_len)
        elif dxf_type == 'POLYLINE':
            if entity.is_2d_polyline and entity.closed:
                vertices_raw = []
                for vtx in entity.vertices:
                    loc = vtx.dxf.location
                    vertices_raw.append((float(loc.x), float(loc.y)))
                area = polygon_area(vertices_raw)
                shape_type = 'POLYLINE2D(closed)'
        if area > 0:
            if bbox is None and vertices_raw and len(vertices_raw) >= 3:
                xs = [v[0] for v in vertices_raw]
                ys = [v[1] for v in vertices_raw]
                bbox = (min(xs), min(ys), max(xs), max(ys))
            center = ((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2) if bbox else None
            other_shapes.append({
                'source': 'other_entity', 'type': shape_type,
                'area': area, 'layer': layer, 'handle': handle,
                'bbox': bbox, 'center': center, 'vertices': vertices_raw,
            })
    all_contours = closed_polys + effectively_closed + combined_pairs + other_shapes
    all_contours = [c for c in all_contours if c['area'] > 0.1]
    return all_contours


def point_inside_contour(point, contour):
    bbox = contour.get('bbox')
    if not bbox:
        return False
    if not (bbox[0] <= point[0] <= bbox[2] and bbox[1] <= point[1] <= bbox[3]):
        return False
    verts = contour.get('vertices')
    source = contour.get('source', '')
    if verts and len(verts) >= 3:
        result = point_in_polygon(point, verts)
        if result:
            return True
        if source == 'implicit_closed':
            return True
        return False
    return True


def group_contours_by_profiles(contours):
    if len(contours) <= 1:
        return [contours] if contours else []
    sorted_contours = sorted(contours, key=lambda c: c['area'], reverse=True)
    containment_parent = [-1] * len(sorted_contours)
    for i in range(len(sorted_contours)):
        ci = sorted_contours[i]
        if ci.get('center') is None:
            continue
        best_parent = -1
        best_parent_area = float('inf')
        for j in range(i):
            cj = sorted_contours[j]
            if point_inside_contour(ci['center'], cj):
                if cj['area'] < best_parent_area:
                    best_parent = j
                    best_parent_area = cj['area']
            elif ci.get('bbox') and cj.get('bbox'):
                bi = ci['bbox']
                bj = cj['bbox']
                if (bi[0] >= bj[0] and bi[2] <= bj[2] and
                    bi[1] >= bj[1] and bi[3] <= bj[3] and
                    ci['area'] < cj['area']):
                    if cj['area'] < best_parent_area:
                        best_parent = j
                        best_parent_area = cj['area']
        containment_parent[i] = best_parent
    groups = {}
    def find_root(idx):
        while containment_parent[idx] != -1:
            idx = containment_parent[idx]
        return idx

    groups = {}
    for i in range(len(sorted_contours)):
        root = find_root(i)
        if root not in groups:
            groups[root] = []
        groups[root].append(sorted_contours[i])

    final_groups = list(groups.values())

    def group_position_x(group):
        centers_x = [c['center'][0] for c in group if c.get('center')]
        return min(centers_x) if centers_x else 0

    final_groups.sort(key=group_position_x)
    return final_groups


def get_net_area_for_group(group):
    if not group:
        return None, None, [], []
    if len(group) == 1:
        return group[0]['area'], group[0], [], []
    sorted_shapes = sorted(group, key=lambda s: s['area'], reverse=True)
    outer = sorted_shapes[0]
    holes = []
    for s in sorted_shapes[1:]:
        holes.append(s)
    net_area = outer['area']
    for h in holes:
        net_area -= h['area']
    return net_area, outer, holes, []


def calc_weight(net_area_mm2, density_kg_m3):
    return net_area_mm2 / 1000000.0 * density_kg_m3


def run_calculation(filepath, density):
    """执行计算，返回 (profiles, lines) 其中 lines 是格式化文本行列表"""
    lines = []
    contours = get_all_contours_from_dxf(filepath)
    lines.append(f"找到 {len(contours)} 个封闭轮廓")
    if not contours:
        lines.append("⚠️  未找到有效封闭轮廓，请检查 DXF 文件")
        return [], lines
    groups = group_contours_by_profiles(contours) if len(contours) > 1 else [contours]
    lines.append(f"分组为 {len(groups)} 个型材")
    lines.append("")
    profiles = []
    for gi, group in enumerate(groups):
        net_area, outer, holes, _ = get_net_area_for_group(group)
        profile = {'net_area': net_area, 'outer': outer, 'holes': holes, 'shapes': group}
        profiles.append(profile)
        pos_x = min([c['center'][0] for c in group if c.get('center')], default=0)
        w_kg = calc_weight(net_area, density) if net_area and net_area > 0 else 0
        w_g = w_kg * 1000
        lines.append(f"  ┌─ 型材 #{gi + 1}  (位置 x={pos_x:.1f})")
        if outer:
            lines.append(f"  │  外轮廓面积: {outer['area']:.2f} mm²")
        for h in holes:
            lines.append(f"  │  孔洞面积:   {h['area']:.2f} mm²")
        if net_area is not None and net_area > 0:
            lines.append(f"  │  净截面面积: {net_area:.2f} mm²")
            lines.append(f"  └─ 米重: {w_kg:.4f} kg/m  ({w_g:.2f} g/m)")
        elif net_area is not None and net_area <= 0:
            lines.append(f"  └─ ⚠️  净面积为负值 ({net_area:.2f} mm²)，请检查图纸")
        else:
            lines.append(f"  └─ ❌  无法计算面积")
        lines.append("")
    valid = [p for p in profiles if p['net_area'] and p['net_area'] > 0]
    if valid:
        lines.append("=" * 50)
        lines.append(f"汇总：共 {len(valid)} 个型材（从左到右）")
        lines.append("=" * 50)
        for i, p in enumerate(valid):
            w = calc_weight(p['net_area'], density)
            pos_x = min([c['center'][0] for c in p['shapes'] if c.get('center')], default=0)
            lines.append(f"  #{i + 1}: x={pos_x:.1f}  {p['net_area']:.2f} mm²  =  {w:.4f} kg/m  ({w * 1000:.2f} g/m)")
        lines.append("=" * 50)
    return profiles, lines


def export_csv(profiles, output_path, density, material_name):
    with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['序号', '位置X', '净截面面积(mm²)', '密度(kg/m³)',
                         '材料', '米重(kg/m)', '米重(g/m)', '外轮廓面积(mm²)', '孔洞面积(mm²)', '形状数'])
        for i, p in enumerate(profiles, 1):
            net = p['net_area'] or 0
            w_kg = calc_weight(net, density) if net > 0 else 0
            outer_area = p['outer']['area'] if p.get('outer') else 0
            hole_areas = '+'.join([f"{h['area']:.2f}" for h in p.get('holes', [])])
            shape_count = 1 + len(p.get('holes', []))
            pos_x = min([c['center'][0] for c in p['shapes'] if c.get('center')], default=0)
            writer.writerow([
                i, f"{pos_x:.1f}", f"{net:.2f}", f"{density:.1f}",
                material_name, f"{w_kg:.4f}", f"{w_kg * 1000:.2f}",
                f"{outer_area:.2f}", hole_areas, shape_count,
            ])


# ============================================================
# GUI
# ============================================================

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("型材截面米重计算工具  v1.0")
        self.geometry("720x580")
        self.resizable(True, True)
        self.configure(bg="#f5f5f5")
        self._profiles = []
        self._last_dxf = ""
        self._build_ui()

    def _build_ui(self):
        # ── 顶部：文件选择 ─────────────────────────────
        frame_file = tk.LabelFrame(self, text="  DXF 文件  ", bg="#f5f5f5",
                                   font=("微软雅黑", 10, "bold"), padx=8, pady=6)
        frame_file.pack(fill=tk.X, padx=14, pady=(12, 4))

        self.var_path = tk.StringVar()
        tk.Entry(frame_file, textvariable=self.var_path, font=("微软雅黑", 10),
                 relief=tk.FLAT, bg="white", bd=1).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        tk.Button(frame_file, text="浏览…", font=("微软雅黑", 10),
                  command=self._browse, bg="#4a90d9", fg="white",
                  relief=tk.FLAT, padx=12, pady=3).pack(side=tk.LEFT)

        # ── 材料选择 ───────────────────────────────────
        frame_mat = tk.LabelFrame(self, text="  材料与密度  ", bg="#f5f5f5",
                                  font=("微软雅黑", 10, "bold"), padx=8, pady=6)
        frame_mat.pack(fill=tk.X, padx=14, pady=4)

        tk.Label(frame_mat, text="材料：", bg="#f5f5f5", font=("微软雅黑", 10)).pack(side=tk.LEFT)
        self.var_material = tk.StringVar(value=list(MATERIAL_DENSITY.keys())[0])
        combo = ttk.Combobox(frame_mat, textvariable=self.var_material,
                             values=list(MATERIAL_DENSITY.keys()),
                             state="readonly", font=("微软雅黑", 10), width=16)
        combo.pack(side=tk.LEFT, padx=(0, 16))
        combo.bind("<<ComboboxSelected>>", self._on_material_change)

        tk.Label(frame_mat, text="密度 (kg/m³)：", bg="#f5f5f5", font=("微软雅黑", 10)).pack(side=tk.LEFT)
        self.var_density = tk.StringVar(value=str(MATERIAL_DENSITY[self.var_material.get()]))
        tk.Entry(frame_mat, textvariable=self.var_density, font=("微软雅黑", 10),
                 width=8, relief=tk.FLAT, bg="white", bd=1).pack(side=tk.LEFT)
        tk.Label(frame_mat, text="  （可手动修改）", bg="#f5f5f5",
                 font=("微软雅黑", 9), fg="#888").pack(side=tk.LEFT)

        # ── 按钮行 ─────────────────────────────────────
        frame_btn = tk.Frame(self, bg="#f5f5f5")
        frame_btn.pack(fill=tk.X, padx=14, pady=6)

        self.btn_calc = tk.Button(frame_btn, text="▶  开始计算", font=("微软雅黑", 11, "bold"),
                                  command=self._calc, bg="#27ae60", fg="white",
                                  relief=tk.FLAT, padx=20, pady=6)
        self.btn_calc.pack(side=tk.LEFT, padx=(0, 10))

        self.btn_export = tk.Button(frame_btn, text="导出 CSV", font=("微软雅黑", 10),
                                    command=self._export, bg="#7f8c8d", fg="white",
                                    relief=tk.FLAT, padx=14, pady=6, state=tk.DISABLED)
        self.btn_export.pack(side=tk.LEFT)

        self.lbl_status = tk.Label(frame_btn, text="", bg="#f5f5f5",
                                   font=("微软雅黑", 9), fg="#555")
        self.lbl_status.pack(side=tk.LEFT, padx=12)

        # ── 结果文本区 ─────────────────────────────────
        frame_out = tk.LabelFrame(self, text="  计算结果  ", bg="#f5f5f5",
                                  font=("微软雅黑", 10, "bold"), padx=8, pady=6)
        frame_out.pack(fill=tk.BOTH, expand=True, padx=14, pady=(4, 12))

        self.txt_result = scrolledtext.ScrolledText(
            frame_out, font=("Consolas", 10), bg="white", relief=tk.FLAT,
            bd=1, state=tk.DISABLED, wrap=tk.WORD)
        self.txt_result.pack(fill=tk.BOTH, expand=True)

        # ── 底部说明 ───────────────────────────────────
        tk.Label(self, text="基于 AlWeight-Python v8.0  |  算法与 AutoCAD vla-get-Area 等价",
                 bg="#f5f5f5", font=("微软雅黑", 8), fg="#aaa").pack(pady=(0, 6))

    def _browse(self):
        path = filedialog.askopenfilename(
            title="选择 DXF 文件",
            filetypes=[("DXF 文件", "*.dxf"), ("所有文件", "*.*")]
        )
        if path:
            self.var_path.set(path)

    def _on_material_change(self, _=None):
        mat = self.var_material.get()
        if mat in MATERIAL_DENSITY:
            self.var_density.set(str(MATERIAL_DENSITY[mat]))

    def _set_result(self, text):
        self.txt_result.config(state=tk.NORMAL)
        self.txt_result.delete("1.0", tk.END)
        self.txt_result.insert(tk.END, text)
        self.txt_result.config(state=tk.DISABLED)

    def _calc(self):
        filepath = self.var_path.get().strip()
        if not filepath:
            messagebox.showwarning("提示", "请先选择 DXF 文件")
            return
        if not os.path.exists(filepath):
            messagebox.showerror("错误", f"文件不存在：\n{filepath}")
            return
        try:
            density = float(self.var_density.get())
        except ValueError:
            messagebox.showerror("错误", "密度值无效，请输入数字")
            return

        self.btn_calc.config(state=tk.DISABLED, text="计算中…")
        self.btn_export.config(state=tk.DISABLED)
        self.lbl_status.config(text="")
        self._set_result("正在解析 DXF 文件，请稍候…")

        def worker():
            try:
                profiles, lines = run_calculation(filepath, density)
                self._profiles = profiles
                self._last_dxf = filepath
                result_text = "\n".join(lines)
                self.after(0, lambda: self._on_calc_done(result_text, len(profiles)))
            except Exception as e:
                err_msg = f"计算出错：{e}"
                self.after(0, lambda: self._on_calc_error(err_msg))

        threading.Thread(target=worker, daemon=True).start()

    def _on_calc_done(self, text, count):
        self._set_result(text)
        self.btn_calc.config(state=tk.NORMAL, text="▶  开始计算")
        if count > 0:
            self.btn_export.config(state=tk.NORMAL)
            self.lbl_status.config(text=f"✓ 完成，共 {count} 个型材", fg="#27ae60")
        else:
            self.lbl_status.config(text="未找到有效型材", fg="#e74c3c")

    def _on_calc_error(self, msg):
        self._set_result(msg)
        self.btn_calc.config(state=tk.NORMAL, text="▶  开始计算")
        self.lbl_status.config(text="❌ 计算失败", fg="#e74c3c")

    def _export(self):
        if not self._profiles:
            messagebox.showwarning("提示", "请先计算")
            return
        try:
            density = float(self.var_density.get())
        except ValueError:
            messagebox.showerror("错误", "密度值无效")
            return
        default_name = os.path.splitext(self._last_dxf)[0] + "_weight.csv" if self._last_dxf else "output.csv"
        out_path = filedialog.asksaveasfilename(
            title="保存 CSV",
            defaultextension=".csv",
            initialfile=os.path.basename(default_name),
            filetypes=[("CSV 文件", "*.csv"), ("所有文件", "*.*")]
        )
        if not out_path:
            return
        try:
            material_name = self.var_material.get()
            export_csv(self._profiles, out_path, density, material_name)
            messagebox.showinfo("导出成功", f"已保存到：\n{out_path}")
        except Exception as e:
            messagebox.showerror("导出失败", str(e))


if __name__ == "__main__":
    app = App()
    app.mainloop()
