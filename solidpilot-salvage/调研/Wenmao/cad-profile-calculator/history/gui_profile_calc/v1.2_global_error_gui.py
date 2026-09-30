"""
型材截面面积与米重计算工具 GUI v1.2
基于 AlWeight-Python v8.4.1

运行方式：
    python gui_profile_calc.py

依赖：
    pip install ezdxf
"""

import math
import csv
import os
from collections import defaultdict
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
# 核心计算逻辑（来自 AlWeight-Python v8.1）
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


def bulge_to_arc_params(x1, y1, x2, y2, bulge):
    """将 LWPOLYLINE bulge 边转换为 ARC 参数，供 cycle-tracing 使用。

    返回 9 元组 (sx,sy,ex,ey,cx,cy,r,sa,ea)，弦长为零时返回 None。
    """
    dx, dy = x2 - x1, y2 - y1
    chord = math.sqrt(dx * dx + dy * dy)
    if chord < 1e-10:
        return None
    theta = 4.0 * math.atan(abs(bulge))
    if theta < 1e-10:
        return None
    r = chord / (2.0 * math.sin(theta / 2.0))
    mx, my = (x1 + x2) / 2.0, (y1 + y2) / 2.0
    perp_dist = r * math.cos(theta / 2.0)
    ux, uy = dx / chord, dy / chord
    if bulge > 0:
        px_v, py_v = -uy, ux
    else:
        px_v, py_v = uy, -ux
    cx = mx + perp_dist * px_v
    cy = my + perp_dist * py_v
    sa = math.atan2(y1 - cy, x1 - cx)
    ea = math.atan2(y2 - cy, x2 - cx)
    sweep = ea - sa
    if bulge > 0 and sweep < 0:
        sweep += 2.0 * math.pi
    elif bulge < 0 and sweep > 0:
        sweep -= 2.0 * math.pi
    return (float(x1), float(y1), float(x2), float(y2),
            float(cx), float(cy), float(r), sa, ea)


def share_significant_edge(contour_a, contour_b, tol=0.01):
    """检查两个轮廓是否至少共享一条完整边（用于判断扩展 vs 孔洞）。"""
    verts_a = contour_a.get('vertices')
    verts_b = contour_b.get('vertices')
    if not verts_a or not verts_b or len(verts_a) < 2 or len(verts_b) < 2:
        return False

    def snap(pt):
        return (round(pt[0] / tol) * tol, round(pt[1] / tol) * tol)

    def edge_set(verts):
        es = set()
        n = len(verts)
        for i in range(n):
            j = (i + 1) % n
            pa = snap(verts[i])
            pb = snap(verts[j])
            es.add((pa, pb))
            es.add((pb, pa))
        return es

    ea = edge_set(verts_a)
    eb = edge_set(verts_b)
    shared = ea & eb
    unique_shared = set()
    for (p1, p2) in shared:
        unique_shared.add(tuple(sorted([p1, p2])))
    return len(unique_shared) >= 1


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


# --- v8.2 ARC+LINE cycle-tracing reconstruction ---

def rebuild_contour_from_arc_line(arcs, lines, snap_tol=0.001):
    """Reconstruct closed contour(s) from disconnected ARC+LINE segments.
    
    Algorithm (v8.2):
      1. Build endpoint connectivity graph — snap endpoints within snap_tol
      2. Find connected components via BFS
      3. For each component, find a cycle via DFS back-edge detection
      4. Compute area via shoelace formula + exact ARC bulge correction
    
    This is a pure geometric approach — no template matching, no rasterization.
    Works for any profile composed of ARC+LINE segments, regardless of whether
    a matching LWPOLYLINE/HATCH exists in the drawing.
    
    Returns: list of dicts {area, bbox, center, vertices, n_segments, source}
    """
    if not arcs and not lines:
        return []
    
    import math
    from collections import defaultdict, deque
    
    def _snap(pt):
        return (round(pt[0]/snap_tol)*snap_tol, round(pt[1]/snap_tol)*snap_tol)
    
    # Unified segment list
    segments = []
    for sx, sy, ex, ey, cx, cy, r, sa, ea in arcs:
        sweep = ea - sa
        if sweep < 0:
            sweep += 2 * math.pi
        segments.append({'type': 'ARC', 'p1': (sx, sy), 'p2': (ex, ey),
                         'arc': {'cx': cx, 'cy': cy, 'r': r, 'sa': sa, 'ea': ea, 'sweep': sweep}})
    for x1, y1, x2, y2 in lines:
        segments.append({'type': 'LINE', 'p1': (x1, y1), 'p2': (x2, y2), 'arc': None})
    
    # Build endpoint graph
    node_map = {}
    node_pts = {}
    next_nid = 0
    
    def _get_node(pt):
        nonlocal next_nid
        s = _snap(pt)
        if s not in node_map:
            node_map[s] = next_nid
            node_pts[next_nid] = s
            next_nid += 1
        return node_map[s]
    
    edge_list = []
    seg_orig_nodes = {}  # seg_idx -> (n1, n2) where n1→n2 = p1→p2 direction
    for idx, seg in enumerate(segments):
        n1 = _get_node(seg['p1'])
        n2 = _get_node(seg['p2'])
        if n1 != n2:
            edge_list.append((n1, n2, idx))
            seg_orig_nodes[idx] = (n1, n2)
    
    if not edge_list:
        return []
    
    adj = defaultdict(list)
    for n1, n2, si in edge_list:
        adj[n1].append((n2, si))
        adj[n2].append((n1, si))
    
    visited = set()
    results = []
    
    for start in range(next_nid):
        if start in visited or start not in adj:
            continue
        
        # BFS component
        comp_nodes = set()
        q = deque([start])
        while q:
            v = q.popleft()
            if v in visited:
                continue
            visited.add(v)
            comp_nodes.add(v)
            for nb, _ in adj[v]:
                if nb not in visited:
                    q.append(nb)
        
        comp_edge_indices = set()
        for n in comp_nodes:
            for nb, si in adj[n]:
                if nb in comp_nodes:
                    comp_edge_indices.add(si)
        
        if len(comp_edge_indices) < 3:
            continue
        
        # Find cycle via DFS (back-edge detection)
        parent = {}
        cycle_start = None
        cycle_end = None
        first = next(iter(comp_nodes))
        
        def _dfs(u, p):
            nonlocal cycle_start, cycle_end
            parent[u] = p
            for v, _ in adj[u]:
                if v == p:
                    continue
                if v in parent:
                    cycle_start = v
                    cycle_end = u
                    return True
                if _dfs(v, u):
                    return True
            return False
        
        if not _dfs(first, -1) or cycle_start is None:
            continue
        
        # Reconstruct cycle path
        cycle_nodes = [cycle_start]
        cur = cycle_end
        while cur != cycle_start:
            cycle_nodes.append(cur)
            cur = parent[cur]
        cycle_nodes.append(cycle_start)
        
        pts = [node_pts[n] for n in cycle_nodes]
        
        # Green's theorem area: for each edge, add contribution
        # - LINE edge A→B:   contribution = cross(A, B)  = x1*y2 - x2*y1
        # - ARC edge A→B:    contribution = cross(A,C) + cross(C,B) + r²*sweep_cycle
        #   where sweep_cycle > 0 for A→B = sa→ea, < 0 for reversed
        area = 0.0
        for i in range(len(pts) - 1):
            u, v = cycle_nodes[i], cycle_nodes[i+1]
            x1, y1 = pts[i]
            x2, y2 = pts[i+1]
            
            is_arc = False
            for nb, si in adj[u]:
                if nb == v:
                    seg = segments[si]
                    if seg['type'] == 'ARC' and seg['arc']:
                        a = seg['arc']
                        r = a['r']
                        cx, cy = a['cx'], a['cy']
                        orig = seg_orig_nodes.get(si)
                        cycle_sweep = a['sweep']
                        if orig is not None and not (u == orig[0] and v == orig[1]):
                            cycle_sweep = -a['sweep']
                        arc_contrib = (x1*cy - y1*cx) + (cx*y2 - cy*x2) + r*r*cycle_sweep
                        area += arc_contrib
                        is_arc = True
                    break
            
            if not is_arc:
                area += x1 * y2 - x2 * y1  # LINE edge: standard shoelace
        
        area = abs(area) / 2.0
        
        xs = [node_pts[n][0] for n in comp_nodes]
        ys = [node_pts[n][1] for n in comp_nodes]
        bbox = (min(xs), min(ys), max(xs), max(ys))
        center = ((bbox[0]+bbox[2])/2, (bbox[1]+bbox[3])/2)
        
        results.append({
            'area': area,
            'bbox': bbox,
            'center': center,
            'vertices': pts,
            'n_segments': len(comp_edge_indices),
            'source': 'arc_line_cycle',
        })
    
    return results


def _make_contour(area, verts, source, type_str, layer='0', handle=''):
    """构建统一轮廓字典。"""
    if not verts or len(verts) < 3:
        return None
    xs = [v[0] for v in verts]
    ys = [v[1] for v in verts]
    bbox = (min(xs), min(ys), max(xs), max(ys))
    center = ((bbox[0] + bbox[2]) / 2.0, (bbox[1] + bbox[3]) / 2.0)
    return {
        'source': source, 'type': type_str,
        'area': area, 'layer': layer, 'handle': handle,
        'bbox': bbox, 'center': center, 'vertices': verts,
    }


def _snap_pt(pt, tol=0.001):
    return (round(pt[0] / tol) * tol, round(pt[1] / tol) * tol)


def _make_contour_from_polyline(entity, source_label):
    """从闭合多段线生成轮廓字典（保持原逻辑不变）。"""
    pts_raw = [(float(p[0]), float(p[1])) for p in entity.get_points()]
    area = exact_lwpolyline_area(entity, close_if_needed=(source_label == 'implicit_closed'))
    verts = extract_lwpolyline_vertices(entity, close_if_needed=(source_label == 'implicit_closed'))
    return _make_contour(area, verts, source_label,
                         'LWPOLYLINE(closed)' if entity.closed else 'LWPOLYLINE(impl_closed)',
                         entity.dxf.layer, entity.dxf.handle)


def get_all_contours_from_dxf(filepath):
    """从 DXF 提取所有轮廓，支持碎片合并 + 共享边扩展检测。"""
    try:
        doc = ezdxf.readfile(filepath)
    except Exception as e:
        raise RuntimeError(f"读取 DXF 文件失败: {e}")

    msp = doc.modelspace()

    errors = []
    all_contours = []
    consumed_handles = set()

    # ── Phase 1: 闭合 LWPOLYLINE ─────────────────
    for entity in msp:
        if entity.dxftype() != 'LWPOLYLINE' or not entity.closed:
            continue
        handle = entity.dxf.handle
        pts_raw = [(float(p[0]), float(p[1])) for p in entity.get_points()]
        area = exact_lwpolyline_area(entity)
        verts = extract_lwpolyline_vertices(entity)
        xs = [p[0] for p in pts_raw]
        ys = [p[1] for p in pts_raw]
        bbox = (min(xs), min(ys), max(xs), max(ys))
        center = ((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)
        consumed_handles.add(handle)
        all_contours.append({
            'source': 'closed_lwpoly', 'type': 'LWPOLYLINE(closed)',
            'area': area, 'layer': entity.dxf.layer, 'handle': handle,
            'bbox': bbox, 'center': center, 'vertices': verts,
            'npts': len(pts_raw), '_entity': entity,
        })

    # ── Phase 2a: 预扫描 open LWPOLYLINE + LINE/ARC 端点 ──
    # 构建端点图以判断开口多段线应独立闭合还是碎片合并
    SNAP = 0.01
    def _snap_pt(p):
        return (round(p[0] / SNAP) * SNAP, round(p[1] / SNAP) * SNAP)

    # 收集所有 LINE/ARC 端点（用于判断多段线是否需要合并）
    la_endpoints = set()
    la_entities = {}  # handle -> entity for deferred processing

    # 收集所有 open LWPOLYLINE 及其端点
    open_pl_data = []  # [(handle, entity, [(x1,y1),(x2,y2),...], area_eff, gap)]

    for entity in msp:
        handle = entity.dxf.handle
        if handle in consumed_handles:
            continue
        t = entity.dxftype()

        if t == 'LWPOLYLINE':
            pts = entity.get_points()
            n = len(pts)
            open_verts = [(float(p[0]), float(p[1])) for p in pts]
            start_pt = open_verts[0]
            end_pt = open_verts[-1]
            gap = math.sqrt((start_pt[0]-end_pt[0])**2 + (start_pt[1]-end_pt[1])**2)
            area_eff = exact_lwpolyline_area(entity, close_if_needed=True)
            open_pl_data.append((handle, entity, open_verts, area_eff, gap, n))

        elif t in ('LINE', 'ARC'):
            la_entities[handle] = entity
            if t == 'LINE':
                la_endpoints.add(_snap_pt((float(entity.dxf.start.x), float(entity.dxf.start.y))))
                la_endpoints.add(_snap_pt((float(entity.dxf.end.x), float(entity.dxf.end.y))))
            else:
                c = entity.dxf.center
                r = float(entity.dxf.radius)
                sa = math.radians(float(entity.dxf.start_angle))
                ea = math.radians(float(entity.dxf.end_angle))
                la_endpoints.add(_snap_pt((c.x + r * math.cos(sa), c.y + r * math.sin(sa))))
                la_endpoints.add(_snap_pt((c.x + r * math.cos(ea), c.y + r * math.sin(ea))))

    # ── Phase 2b: 构建 open polylines 连通图（共享端点 → 同一构件）──
    pl_count = len(open_pl_data)
    # 每个 polyline 的端点 snap 集合
    pl_endpoints = []
    for _, _, verts, _, _, _ in open_pl_data:
        pl_endpoints.append({
            _snap_pt(verts[0]),
            _snap_pt(verts[-1]),
        })

    # Union-Find 连通分量
    parent = list(range(pl_count))
    def _find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    def _union(a, b):
        ra, rb = _find(a), _find(b)
        if ra != rb:
            parent[ra] = rb

    for i in range(pl_count):
        for j in range(i + 1, pl_count):
            if pl_endpoints[i] & pl_endpoints[j]:
                _union(i, j)

    # 每个连通分量是否包含与 LINE/ARC 相连的端点
    comp_has_la = {}
    for i in range(pl_count):
        root = _find(i)
        if root not in comp_has_la:
            comp_has_la[root] = False
        if pl_endpoints[i] & la_endpoints:
            comp_has_la[root] = True

    # ── Phase 2c: 处理 open LWPOLYLINE ──
    frag_lines = []   # (x1, y1, x2, y2)
    frag_arcs = []    # (sx, sy, ex, ey, cx, cy, r, sa, ea)

    for i, (handle, entity, open_verts, area_eff, gap, n) in enumerate(open_pl_data):
        root = _find(i)
        should_fragment = comp_has_la.get(root, False)

        # 检查是否与已处理的闭合轮廓共享顶点（≥2 个匹配点）
        attached_to = None
        for contour in all_contours:
            if contour.get('source') not in ('closed_lwpoly',):
                continue
            cv = contour.get('vertices')
            if not cv:
                continue
            snapped_ov = set(_snap_pt(p) for p in open_verts)
            snapped_cv = set(_snap_pt(p) for p in cv)
            shared = snapped_ov & snapped_cv
            if len(shared) >= 2:
                attached_to = contour
                break

        if attached_to:
            area = exact_lwpolyline_area(entity, close_if_needed=True)
            verts_full = extract_lwpolyline_vertices(entity, close_if_needed=True)
            c = _make_contour(area, verts_full, 'attached_open',
                              'LWPOLYLINE(attached)',
                              entity.dxf.layer, handle)
            if c:
                c['_attached_to'] = attached_to.get('handle')
                all_contours.append(c)
            consumed_handles.add(handle)

        elif should_fragment and area_eff > 0.001 and gap > 5.0:
            # 连通分量连接 LINE/ARC → 拆碎合并（如 #58: 11A+11B+11C）
            for j in range(n - 1):
                p1, p2 = open_verts[j], open_verts[j + 1]
                x1, y1 = float(p1[0]), float(p1[1])
                x2, y2 = float(p2[0]), float(p2[1])
                if abs(x2 - x1) < 1e-10 and abs(y2 - y1) < 1e-10:
                    continue
                bulge = float(p1[4]) if len(p1) > 4 else 0.0
                if abs(bulge) > 1e-10:
                    arc_p = bulge_to_arc_params(x1, y1, x2, y2, bulge)
                    if arc_p:
                        frag_arcs.append(arc_p)
                else:
                    frag_lines.append((x1, y1, x2, y2))
            consumed_handles.add(handle)

        if gap >= 0.1:
            # 未闭合多段线，gap 过大，不能当作有效轮廓
            errors.append({
                'type': 'unclosed_lwpolyline',
                'handle': handle,
                'layer': entity.dxf.layer if hasattr(entity.dxf, 'layer') else '0',
                'center': ((min([v[0] for v in open_verts]) + max([v[0] for v in open_verts])) / 2,
                           (min([v[1] for v in open_verts]) + max([v[1] for v in open_verts])) / 2),
                'gap': gap,
                'npts': n,
                'message': (f"LWPOLYLINE 未闭合 (handle={handle}, gap={gap:.2f}mm)。"
                            "型材截面必须闭合，请检查图纸。"),
                'fix': (f"请在 CAD 中将 handle={handle} 的多段线闭合（PEDIT -> CLOSE），"
                        f"或删除/修复未闭合的开口端"),
            })
            consumed_handles.add(handle)

        elif area_eff > 0.001:
            # 连通分量不连接 LINE/ARC → 独立闭合（如 #2: 26E/26F）
            verts_eff = extract_lwpolyline_vertices(entity, close_if_needed=True)
            c = _make_contour(area_eff, verts_eff, 'effectively_closed',
                              'LWPOLYLINE(eff_closed)',
                              entity.dxf.layer, handle)
            if c:
                c['gap'] = gap
                all_contours.append(c)
            consumed_handles.add(handle)

        elif gap > 5.0:
            # 面积 ≈ 0 且 gap > 5mm → 可能是型材轮廓的一部分，拆碎
            for j in range(n - 1):
                p1, p2 = open_verts[j], open_verts[j + 1]
                x1, y1 = float(p1[0]), float(p1[1])
                x2, y2 = float(p2[0]), float(p2[1])
                if abs(x2 - x1) < 1e-10 and abs(y2 - y1) < 1e-10:
                    continue
                bulge = float(p1[4]) if len(p1) > 4 else 0.0
                if abs(bulge) > 1e-10:
                    arc_p = bulge_to_arc_params(x1, y1, x2, y2, bulge)
                    if arc_p:
                        frag_arcs.append(arc_p)
                else:
                    frag_lines.append((x1, y1, x2, y2))
            consumed_handles.add(handle)

        else:
            # gap < 5mm + area ≈ 0 → 可能是冗余短线，跳过
            consumed_handles.add(handle)

    # ── Phase 2d: LINE + ARC 加入碎片池 ──
    for handle, entity in la_entities.items():
        if handle in consumed_handles:
            continue
        t = entity.dxftype()
        if t == 'LINE':
            x1 = float(entity.dxf.start.x)
            y1 = float(entity.dxf.start.y)
            x2 = float(entity.dxf.end.x)
            y2 = float(entity.dxf.end.y)
            if abs(x2 - x1) > 1e-8 or abs(y2 - y1) > 1e-8:
                frag_lines.append((x1, y1, x2, y2))
            consumed_handles.add(handle)
        elif t == 'ARC':
            c = entity.dxf.center
            r = float(entity.dxf.radius)
            sa = math.radians(float(entity.dxf.start_angle))
            ea = math.radians(float(entity.dxf.end_angle))
            sx = c.x + r * math.cos(sa)
            sy = c.y + r * math.sin(sa)
            ex = c.x + r * math.cos(ea)
            ey = c.y + r * math.sin(ea)
            frag_arcs.append((float(sx), float(sy), float(ex), float(ey),
                              float(c.x), float(c.y), float(r), sa, ea))
            consumed_handles.add(handle)

    # ── Phase 3: 碎片合并成闭合轮廓 ─────────────────
    if frag_lines or frag_arcs:
        ar_tuples = frag_arcs  # 已是 9 元组
        li_tuples = frag_lines
        merged = rebuild_contour_from_arc_line(ar_tuples, li_tuples)
        for rc in merged:
            c = _make_contour(rc['area'], rc['vertices'],
                              'merged_fragments', 'FRAGMENTS(merged)')
            if c:
                all_contours.append(c)

    # ── Phase 4: 其他图形（CIRCLE, ELLIPSE, HATCH, SOLID, POLYLINE）──
    for entity in msp:
        handle = entity.dxf.handle if hasattr(entity.dxf, 'handle') else ''
        if handle in consumed_handles:
            continue
        dxf_type = entity.dxftype()
        layer = entity.dxf.layer if hasattr(entity.dxf, 'layer') else '0'
        area = 0.0
        shape_type = dxf_type
        bbox = None
        vertices_raw = None

        if dxf_type == 'CIRCLE':
            r = float(entity.dxf.radius)
            cx_val = float(entity.dxf.center.x)
            cy_val = float(entity.dxf.center.y)
            area = circle_area(r)
            bbox = (cx_val - r, cy_val - r, cx_val + r, cy_val + r)
            vertices_raw = [(cx_val + r * math.cos(2 * math.pi * i / 32),
                             cy_val + r * math.sin(2 * math.pi * i / 32)) for i in range(32)]

        elif dxf_type == 'ELLIPSE':
            major = entity.dxf.major_axis
            ratio = entity.dxf.ratio if hasattr(entity.dxf, 'ratio') else 1.0
            major_len = math.sqrt(major[0] ** 2 + major[1] ** 2 + major[2] ** 2)
            minor_len = major_len * ratio
            start_p = entity.dxf.start_param if hasattr(entity.dxf, 'start_param') else 0
            end_p = entity.dxf.end_param if hasattr(entity.dxf, 'end_param') else 2 * math.pi
            if abs(end_p - start_p - 2 * math.pi) < 0.01:
                area = ellipse_area(major_len, minor_len)
                cx_val = float(entity.dxf.center.x)
                cy_val = float(entity.dxf.center.y)
                bbox = (cx_val - major_len, cy_val - minor_len,
                        cx_val + major_len, cy_val + minor_len)

        elif dxf_type == 'POLYLINE':
            if entity.is_2d_polyline and entity.closed:
                vertices_raw = []
                for vtx in entity.vertices:
                    loc = vtx.dxf.location
                    vertices_raw.append((float(loc.x), float(loc.y)))
                area = polygon_area(vertices_raw)
                shape_type = 'POLYLINE2D(closed)'

        elif dxf_type == 'HATCH':
            try:
                hatch_area = 0.0
                all_hatch_verts = []
                for path in entity.paths:
                    sub_area = 0.0
                    sub_verts = []
                    is_external = bool(
                        path.path_type_flags & 1) if hasattr(path, 'path_type_flags') else True
                    is_hole = not is_external

                    if hasattr(path, 'vertices'):
                        verts_raw = list(path.vertices)
                        n_v = len(verts_raw)
                        if n_v >= 3:
                            shoelace = 0.0
                            for j in range(n_v):
                                k = (j + 1) % n_v
                                shoelace += verts_raw[j][0] * verts_raw[k][1]
                                shoelace -= verts_raw[k][0] * verts_raw[j][1]
                            shoelace /= 2.0
                            arc_correction = 0.0
                            for j in range(n_v):
                                b = verts_raw[j][2]
                                if abs(b) < 1e-10:
                                    continue
                                k = (j + 1) % n_v
                                x1v, y1v = verts_raw[j][0], verts_raw[j][1]
                                x2v, y2v = verts_raw[k][0], verts_raw[k][1]
                                cd = math.sqrt((x2v - x1v) ** 2 + (y2v - y1v) ** 2)
                                if cd < 1e-10:
                                    continue
                                th = 4.0 * math.atan(abs(b))
                                if th < 1e-10 or th > 2 * math.pi - 1e-10:
                                    continue
                                sh = math.sin(th / 2.0)
                                if abs(sh) < 1e-10:
                                    continue
                                rr = cd / (2.0 * sh)
                                arc_correction += math.copysign(
                                    rr ** 2 * (th - math.sin(th)) / 2.0, b)
                            sub_area = abs(shoelace + arc_correction)
                            for j in range(n_v):
                                x1v, y1v = verts_raw[j][0], verts_raw[j][1]
                                b = verts_raw[j][2]
                                k = (j + 1) % n_v
                                x2v, y2v = verts_raw[k][0], verts_raw[k][1]
                                if abs(b) > 1e-10:
                                    dxx, dyy = x2v - x1v, y2v - y1v
                                    cd2 = math.sqrt(dxx * dxx + dyy * dyy)
                                    if cd2 > 1e-10:
                                        th2 = 4.0 * math.atan(abs(b))
                                        sh2 = math.sin(th2 / 2.0)
                                        if abs(sh2) > 1e-10:
                                            rr2 = cd2 / (2.0 * sh2)
                                            mid_x, mid_y = (x1v + x2v) / 2, (y1v + y2v) / 2
                                            pd = rr2 * math.cos(th2 / 2.0)
                                            ux, uy = dxx / cd2, dyy / cd2
                                            if b > 0:
                                                pxv, pyv = -uy, ux
                                            else:
                                                pxv, pyv = uy, -ux
                                            cxx = mid_x + pd * pxv
                                            cyy = mid_y + pd * pyv
                                            sva = math.atan2(y1v - cyy, x1v - cxx)
                                            eva = math.atan2(y2v - cyy, x2v - cxx)
                                            if b > 0:
                                                if eva <= sva:
                                                    eva += 2 * math.pi
                                            else:
                                                if eva >= sva:
                                                    eva -= 2 * math.pi
                                            for m in range(16):
                                                tv = m / 16.0
                                                av = sva + tv * (eva - sva)
                                                sub_verts.append(
                                                    (cxx + rr2 * math.cos(av),
                                                     cyy + rr2 * math.sin(av)))
                                else:
                                    sub_verts.append((x1v, y1v))
                            if sub_verts:
                                all_hatch_verts.extend(sub_verts)
                            else:
                                all_hatch_verts.extend(
                                    [(v[0], v[1]) for v in verts_raw])

                    elif hasattr(path, 'edges'):
                        for edge in path.edges:
                            if edge.EDGE_TYPE == 'LineEdge':
                                sub_verts.append(
                                    (float(edge.start[0]), float(edge.start[1])))
                            elif edge.EDGE_TYPE == 'ArcEdge':
                                for kk in range(17):
                                    tr = edge.start_angle + (
                                        edge.end_angle - edge.start_angle) * kk / 16
                                    sub_verts.append(
                                        (float(edge.center[0]) + float(edge.radius) * math.cos(tr),
                                         float(edge.center[1]) + float(edge.radius) * math.sin(tr)))
                        if len(sub_verts) >= 3:
                            sub_area = polygon_area(sub_verts)
                            all_hatch_verts.extend(sub_verts)
                        else:
                            continue
                    else:
                        continue

                    if is_hole:
                        hatch_area -= sub_area
                    else:
                        hatch_area += sub_area

                area = abs(hatch_area) if hatch_area != 0 else 0
                shape_type = 'HATCH'
                vertices_raw = all_hatch_verts if all_hatch_verts else None
                consumed_handles.add(handle)
            except Exception:
                area = 0.0
                shape_type = 'HATCH(unparsed)'

        elif dxf_type == 'SOLID':
            try:
                pts = []
                for attr in ['corner1', 'corner2', 'corner3', 'corner4']:
                    if hasattr(entity.dxf, attr):
                        p = entity.dxf.__getattr__(attr)
                        pts.append((float(p[0]), float(p[1])))
                if len(pts) >= 3:
                    area = polygon_area(pts)
                    vertices_raw = pts
            except Exception:
                area = 0.0

        if area > 0:
            if bbox is None and vertices_raw and len(vertices_raw) >= 3:
                xs = [v[0] for v in vertices_raw]
                ys = [v[1] for v in vertices_raw]
                bbox = (min(xs), min(ys), max(xs), max(ys))
            center = ((bbox[0] + bbox[2]) / 2,
                      (bbox[1] + bbox[3]) / 2) if bbox else None
            all_contours.append({
                'source': 'other_entity', 'type': shape_type,
                'area': area, 'layer': layer, 'handle': handle,
                'bbox': bbox, 'center': center, 'vertices': vertices_raw,
            })

    all_contours = [c for c in all_contours if c['area'] > 0.1]
    return all_contours, errors


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
    """计算型材净面积。检测共享边错误（图纸错误）。

    返回: (net_area, outer, holes, errors)
      errors = [{'type':'shared_edge'/'open_polyline', 'severity':'error',
                 'contour':dict, 'message':str, 'fix':str}, ...]
    当存在 errors 时，net_area 包含出错轮廓的扣除，结果仅供参考。
    """
    if not group:
        return None, None, [], []
    if len(group) == 1:
        return group[0]['area'], group[0], [], []
    
    sorted_shapes = sorted(group, key=lambda s: s['area'], reverse=True)
    outer = sorted_shapes[0]
    holes = []
    errors = []

    for s in sorted_shapes[1:]:
        source = s.get('source', '')
        h = s.get('handle', '')
        stype = s.get('type', '?')

        # ── 检测1: 非闭合多段线附着到闭合轮廓 → 图纸错误 ──
        if source == 'attached_open':
            errors.append({
                'type': 'open_polyline',
                'severity': 'error',
                'contour': s,
                'handle': h,
                'outer_handle': outer.get('handle', ''),
                'message': (f"非闭合多段线 {stype} (handle={h}) 与外轮廓 "
                            f"(handle={outer.get('handle','?')}) 共享顶点"),
                'fix': (f"请删除冗余线段 handle={h}，或在 CAD 中将该线段"
                        f"与外轮廓合并为单一闭合多段线"),
            })
            # 错误轮廓暂扣（与旧行为兼容：视为孔洞扣除，结果仅供参考）
            holes.append(s)
            continue

        # ── 检测2: 共享完整边 → 图纸错误 ──
        # 例外: 双方都是 effectively_closed → 共享的"边"来自 close_if_needed
        # 的合成闭合线段(图中间隙)，并非真正的图纸共享边，跳过共享边检测
        outer_is_ec = (outer.get('source') == 'effectively_closed')
        this_is_ec = (source == 'effectively_closed')
        if not (outer_is_ec and this_is_ec):
            shares_edge = share_significant_edge(s, outer, tol=0.01)
            if shares_edge:
                errors.append({
                    'type': 'shared_edge',
                    'severity': 'error',
                    'contour': s,
                    'handle': h,
                    'outer_handle': outer.get('handle', ''),
                    'message': (f"{stype} (handle={h}) 与外轮廓 "
                                f"(handle={outer.get('handle','?')}) 共享完整边"),
                    'fix': (f"请删除冗余线段 handle={h}。"
                            f"型材截面中不应存在共享边——这通常意味着制图错误"),
                })
                # 错误轮廓暂扣（结果仅供参考）
                holes.append(s)
                continue

        # ── 正常孔洞判断 ──
        holes.append(s)

    net_area = outer['area']
    for h in holes:
        # 错误轮廓（shared_edge/open_polyline）不算孔洞，不扣除面积
        is_err = any(
            e.get('handle') == h.get('handle')
            for e in errors
        )
        if not is_err:
            net_area -= h['area']

    return net_area, outer, holes, errors


def calc_weight(net_area_mm2, density_kg_m3):
    return net_area_mm2 / 1000000.0 * density_kg_m3


def associate_global_errors_to_profiles(profiles, global_errors):
    """把全局错误（如未闭合 LWPOLYLINE）关联到距离最近的型材。"""
    for ge in global_errors:
        ex, ey = ge.get('center', (0, 0))
        best_p = None
        best_dist = float('inf')
        for p in profiles:
            shapes = p.get('shapes', [])
            if not shapes:
                continue
            center = shapes[0].get('center')
            if not center:
                bbox = shapes[0].get('bbox')
                if bbox:
                    center = ((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)
                else:
                    continue
            sx, sy = center
            d = math.sqrt((ex - sx) ** 2 + (ey - sy) ** 2)
            if d < best_dist:
                best_dist = d
                best_p = p
        if best_p is not None:
            if 'errors' not in best_p:
                best_p['errors'] = []
            best_p['errors'].append(ge)


def run_calculation(filepath, density):
    """执行计算，返回 (profiles, lines) 其中 lines 是格式化文本行列表"""
    lines = []
    contours, global_errors = get_all_contours_from_dxf(filepath)
    lines.append(f"找到 {len(contours)} 个封闭轮廓")
    if not contours:
        lines.append("⚠️  未找到有效封闭轮廓，请检查 DXF 文件")
        return [], lines
    groups = group_contours_by_profiles(contours) if len(contours) > 1 else [contours]
    lines.append(f"分组为 {len(groups)} 个型材")
    if global_errors:
        lines.append("")
        lines.append(f"⚠️  检测到 {len(global_errors)} 个未闭合轮廓（已跳过）：")
        for e in global_errors:
            lines.append(f"    🔴 [{e['type']}] {e['message']}")
    lines.append("")
    profiles = []
    has_any_error = False
    for gi, group in enumerate(groups):
        net_area, outer, holes, errors = get_net_area_for_group(group)
        pos_x = min([c['center'][0] for c in group if c.get('center')], default=0)
        w_kg = calc_weight(net_area, density) if net_area and net_area > 0 else 0
        profile = {'net_area': net_area, 'outer': outer, 'holes': holes,
                   'errors': errors, 'shapes': group,
                   'index': gi + 1, 'pos_x': pos_x, 'weight_kgm': w_kg}
        profiles.append(profile)
        w_g = w_kg * 1000

        if errors:
            has_any_error = True
            # ── 错误型材：突出显示错误信息 ──
            lines.append(f"  ┌─ 型材 #{gi + 1}  (位置 x={pos_x:.1f})  ⚠️ 图纸错误!")
            lines.append(f"  │")
            for err in errors:
                lines.append(f"  │  🔴 [{err['type']}] {err['message']}")
                lines.append(f"  │      → 修复: {err['fix']}")
            lines.append(f"  │  ──────────────────────────────")
            if outer:
                lines.append(f"  │  外轮廓面积: {outer['area']:.2f} mm²  ({outer.get('type','?')} {outer.get('handle','')})")
            # holes 包含了错误轮廓和正常孔洞，都列出
            normal_holes = [h for h in holes if not any(
                h.get('handle') == e.get('handle') for e in errors)]
            error_holes = [h for h in holes if any(
                h.get('handle') == e.get('handle') for e in errors)]
            for h in error_holes:
                lines.append(f"  │  🔴 错误轮廓: {h['area']:.2f} mm²  ({h.get('type','?')} {h.get('handle','')}) — 已暂扣")
            for h in normal_holes:
                lines.append(f"  │  孔洞面积:   {h['area']:.2f} mm²  ({h.get('type','?')} {h.get('handle','')})")
            lines.append(f"  │")
            if net_area is not None and net_area > 0:
                lines.append(f"  │  ⚠️  净截面面积: {net_area:.2f} mm² (仅供参考，请修复图纸错误后重新计算)")
                lines.append(f"  │  ⚠️  米重: {w_kg:.4f} kg/m (仅供参考)")
            elif net_area is not None and net_area <= 0:
                lines.append(f"  └─ ⚠️  净面积为负值 ({net_area:.2f} mm²)，请检查图纸")
            else:
                lines.append(f"  └─ ❌  无法计算面积")
            lines.append("")
        else:
            # ── 正常型材 ──
            lines.append(f"  ┌─ 型材 #{gi + 1}  (位置 x={pos_x:.1f})")
            if outer:
                lines.append(f"  │  外轮廓面积: {outer['area']:.2f} mm²  ({outer.get('type','?')} {outer.get('handle','')})")
            for h in holes:
                lines.append(f"  │  孔洞面积:   {h['area']:.2f} mm²  ({h.get('type','?')} {h.get('handle','')})")
            if net_area is not None and net_area > 0:
                lines.append(f"  │  净截面面积: {net_area:.2f} mm²")
                lines.append(f"  └─ 米重: {w_kg:.4f} kg/m  ({w_g:.2f} g/m)")
            elif net_area is not None and net_area <= 0:
                lines.append(f"  └─ ⚠️  净面积为负值 ({net_area:.2f} mm²)，请检查图纸")
            else:
                lines.append(f"  └─ ❌  无法计算面积")
            lines.append("")

    # 将全局错误关联到最近的型材，使 CSV / 标注 DXF 也能体现这些错误
    associate_global_errors_to_profiles(profiles, global_errors)

    valid = [p for p in profiles if p['net_area'] and p['net_area'] > 0]
    error_profiles = [p for p in profiles if p.get('errors')]
    if valid:
        lines.append("=" * 50)
        lines.append(f"汇总：共 {len(valid)} 个型材（从左到右）")
        lines.append("=" * 50)
        for i, p in enumerate(valid):
            w = calc_weight(p['net_area'], density)
            pos_x = min([c['center'][0] for c in p['shapes'] if c.get('center')], default=0)
            err_mark = " ⚠️有错误!" if p.get('errors') else ""
            lines.append(f"  #{i + 1}: x={pos_x:.1f}  {p['net_area']:.2f} mm²  =  {w:.4f} kg/m  ({w * 1000:.2f} g/m){err_mark}")
        lines.append("=" * 50)
    if error_profiles:
        lines.append("")
        lines.append("=" * 50)
        lines.append(f"⚠️  发现 {len(error_profiles)} 个型材存在图纸错误，需要人工修复!")
        lines.append("=" * 50)
        for i, p in enumerate(error_profiles):
            pos_x = min([c['center'][0] for c in p['shapes'] if c.get('center')], default=0)
            lines.append(f"  型材 #{valid.index(p)+1 if p in valid else '?'}: x={pos_x:.1f}")
            for err in p['errors']:
                lines.append(f"    - {err['fix']}")
        lines.append("")
        lines.append("  💡 提示: 可使用「导出错误标注DXF」功能，")
        lines.append("     在 CAD 中打开标注文件定位到具体错误位置。")
        lines.append("=" * 50)
    return profiles, lines


def export_csv(profiles, output_path, density, material_name):
    with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['序号', '位置X', '净截面面积(mm²)', '密度(kg/m³)',
                         '材料', '米重(kg/m)', '米重(g/m)', '外轮廓面积(mm²)',
                         '孔洞面积(mm²)', '形状数', '错误数', '错误详情'])
        for i, p in enumerate(profiles, 1):
            net = p['net_area'] or 0
            w_kg = calc_weight(net, density) if net > 0 else 0
            outer_area = p['outer']['area'] if p.get('outer') else 0
            hole_areas = '+'.join([f"{h['area']:.2f}" for h in p.get('holes', [])])
            shape_count = 1 + len(p.get('holes', []))
            pos_x = min([c['center'][0] for c in p['shapes'] if c.get('center')], default=0)
            err_count = len(p.get('errors', []))
            err_detail = ' | '.join([e['message'] for e in p.get('errors', [])])
            writer.writerow([
                i, f"{pos_x:.1f}", f"{net:.2f}", f"{density:.1f}",
                material_name, f"{w_kg:.4f}", f"{w_kg * 1000:.2f}",
                f"{outer_area:.2f}", hole_areas, shape_count,
                err_count, err_detail,
            ])


def generate_annotation_dxf(profiles, input_dxf_path, output_path):
    """生成全量标注 DXF。

    在原始 DXF 上添加标注图层：
    - ANNO_NORMAL (青色): 正常型材 — 序号、X坐标、米重
    - ANNO_ERROR (红色): 错误型材 — 同上 + 错误详情
    - ERROR_MARKERS (红色): 错误轮廓圆圈 + 引线
    """
    import ezdxf as ezdxf_mod
    from ezdxf import colors as dxf_colors

    try:
        doc = ezdxf_mod.readfile(input_dxf_path)
    except Exception as e:
        raise RuntimeError(f"读取 DXF 失败: {e}")

    msp = doc.modelspace()

    # 创建图层
    for layer_name, color in [('ANNO_NORMAL', dxf_colors.CYAN),
                                ('ANNO_ERROR', dxf_colors.RED),
                                ('ERROR_MARKERS', dxf_colors.RED)]:
        if layer_name not in doc.layers:
            doc.layers.add(name=layer_name, color=color)

    marker_radius = 15.0
    text_height = 4.0

    for pi, p in enumerate(profiles):
        seq = p.get('index', pi + 1)
        pos_x = p.get('pos_x', 0)
        weight_kgm = p.get('weight_kgm', 0)
        has_err = bool(p.get('errors'))

        # 取第一个轮廓的中心作为标注位置
        shapes = p.get('shapes', [])
        if not shapes:
            continue
        s0 = shapes[0]
        center = s0.get('center')
        if not center:
            bbox = s0.get('bbox')
            if bbox:
                center = ((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)
            else:
                continue

        cx, cy = center

        # ── 错误轮廓 → 红色圆圈 + 引线 + 错误详情 ──
        if has_err:
            # 红色填充圆圈
            msp.add_circle(
                center=(cx, cy),
                radius=marker_radius,
                dxfattribs={'layer': 'ERROR_MARKERS', 'color': dxf_colors.RED}
            )
            hatch = msp.add_hatch(color=dxf_colors.RED)
            hatch.paths.add_polyline_path(
                [(cx + marker_radius * math.cos(2 * math.pi * k / 60),
                  cy + marker_radius * math.sin(2 * math.pi * k / 60))
                 for k in range(60)],
                is_closed=True,
                flags=ezdxf_mod.const.BOUNDARY_PATH_POLYLINE,
            )

            # 引线
            text_y = cy + marker_radius * 3
            msp.add_line(
                start=(cx, cy + marker_radius),
                end=(cx, text_y),
                dxfattribs={'layer': 'ERROR_MARKERS', 'color': dxf_colors.RED}
            )

            # 错误标注文字
            label_text = f"#{seq} X={pos_x:.0f} {weight_kgm:.4f} kg/m [ERROR]"
            msp.add_text(
                label_text,
                dxfattribs={
                    'layer': 'ANNO_ERROR',
                    'color': dxf_colors.RED,
                    'height': text_height,
                    'insert': (cx + marker_radius * 1.5, text_y + marker_radius * 1.0),
                }
            )

            # 逐个错误详情
            for ei, err in enumerate(p.get('errors', [])):
                err_type = err.get('type', '?')
                err_detail = err.get('message', '')
                if len(err_detail) > 80:
                    err_detail = err_detail[:77] + '...'
                msp.add_text(
                    f"  [{err_type}] {err_detail}",
                    dxfattribs={
                        'layer': 'ANNO_ERROR',
                        'color': dxf_colors.RED,
                        'height': text_height * 0.7,
                        'insert': (cx + marker_radius * 1.5,
                                   text_y + marker_radius * 0.2 - ei * text_height * 1.5),
                    }
                )

        # ── 正常型材 → 青色标注 ──
        else:
            label_text = f"#{seq} X={pos_x:.0f} {weight_kgm:.4f} kg/m"
            msp.add_text(
                label_text,
                dxfattribs={
                    'layer': 'ANNO_NORMAL',
                    'color': dxf_colors.CYAN,
                    'height': text_height,
                    'insert': (cx + marker_radius * 0.5, cy + marker_radius * 0.3),
                }
            )

    # 保存
    try:
        doc.saveas(output_path)
    except Exception as e:
        raise RuntimeError(f"保存 DXF 失败: {e}")

    # 保存
    try:
        doc.saveas(output_path)
    except Exception as e:
        raise RuntimeError(f"保存标注 DXF 失败: {e}")

    return output_path


# ============================================================
# GUI
# ============================================================

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("型材截面米重计算工具  v1.2")
        self.geometry("760x640")
        self.resizable(True, True)
        self.configure(bg="#f5f5f5")
        self._profiles = []
        self._last_dxf = ""
        self._has_errors = False
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

        self.btn_err_dxf = tk.Button(frame_btn, text="📐 导出标注DXF", font=("微软雅黑", 10),
                                     command=self._export_annotations, bg="#2980b9", fg="white",
                                     relief=tk.FLAT, padx=14, pady=6, state=tk.DISABLED)
        self.btn_err_dxf.pack(side=tk.LEFT, padx=(6, 0))

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
        tk.Label(self, text="基于 AlWeight-Python v8.5  |  支持碎片合并 + 错误检测标注",
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

        # 配置错误标签（红色加粗）
        self.txt_result.tag_configure("error", foreground="#c0392b",
                                      font=("Consolas", 10, "bold"))
        self.txt_result.tag_configure("error_fix", foreground="#e74c3c",
                                      font=("Consolas", 10))
        self.txt_result.tag_configure("warning", foreground="#e67e22",
                                      font=("Consolas", 10, "bold"))
        self.txt_result.tag_configure("summary", foreground="#2c3e50",
                                      font=("Consolas", 10, "bold"))

        lines = text.split('\n')
        for i, line in enumerate(lines):
            lineno = i + 1
            # 错误行：包含 🔴 或 "图纸错误" 或 "有错误" 或 "需要人工修复" 或 "仅供参考"
            if '🔴' in line or '图纸错误' in line:
                self.txt_result.insert(f"{lineno}.0", line + '\n', "error")
            elif '仅供参考' in line or '请修复' in line:
                self.txt_result.insert(f"{lineno}.0", line + '\n', "error_fix")
            elif '⚠️' in line or '有错误' in line or '需要人工修复' in line:
                self.txt_result.insert(f"{lineno}.0", line + '\n', "warning")
            elif line.startswith('=') or line.startswith('汇总') or line.startswith('💡'):
                self.txt_result.insert(f"{lineno}.0", line + '\n', "summary")
            else:
                self.txt_result.insert(f"{lineno}.0", line + '\n')

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
                has_err = any(p.get('errors') for p in profiles)
                self.after(0, lambda: self._on_calc_done(result_text, len(profiles), has_err))
            except Exception as e:
                err_msg = f"计算出错：{e}"
                self.after(0, lambda: self._on_calc_error(err_msg))

        threading.Thread(target=worker, daemon=True).start()

    def _on_calc_done(self, text, count, has_errors):
        self._set_result(text)
        self._has_errors = has_errors
        self.btn_calc.config(state=tk.NORMAL, text="▶  开始计算")
        if count > 0:
            self.btn_export.config(state=tk.NORMAL)
            self.btn_err_dxf.config(state=tk.NORMAL)  # 始终可用（全量标注）
            if has_errors:
                self.lbl_status.config(text=f"✓ 完成，共 {count} 个型材，⚠️ 存在图纸错误", fg="#e67e22")
            else:
                self.lbl_status.config(text=f"✓ 完成，共 {count} 个型材", fg="#27ae60")
        else:
            self.lbl_status.config(text="未找到有效型材", fg="#e74c3c")

    def _on_calc_error(self, msg):
        self._set_result(msg)
        self.btn_calc.config(state=tk.NORMAL, text="▶  开始计算")
        self.lbl_status.config(text="❌ 计算失败", fg="#e74c3c")

    def _export_annotations(self):
        """导出全量标注 DXF（含正常 + 错误型材）"""
        if not self._profiles:
            messagebox.showwarning("提示", "请先计算结果")
            return
        if not self._last_dxf:
            messagebox.showwarning("提示", "请先选择 DXF 文件")
            return

        default_name = os.path.splitext(self._last_dxf)[0] + "_标注.dxf"
        out_path = filedialog.asksaveasfilename(
            title="保存标注 DXF",
            defaultextension=".dxf",
            initialfile=os.path.basename(default_name),
            filetypes=[("DXF 文件", "*.dxf"), ("所有文件", "*.*")]
        )
        if not out_path:
            return

        try:
            generate_annotation_dxf(self._profiles, self._last_dxf, out_path)
            n_err = sum(1 for p in self._profiles if p.get('errors'))
            self.lbl_status.config(
                text=f"✓ 标注已导出: {os.path.basename(out_path)}", fg="#27ae60")
            msg = (f"标注 DXF 已保存到：\n{out_path}\n\n"
                   f"共 {len(self._profiles)} 个型材（{n_err} 个有错误）。\n"
                   f"青色文字 = 正常型材，红色标记 = 有错误的型材。")
            messagebox.showinfo("导出成功", msg)
        except Exception as e:
            messagebox.showerror("导出失败", str(e))

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
