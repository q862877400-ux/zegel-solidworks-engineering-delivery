"""
型材截面面积与米重计算工具 GUI v11.30
基于 AlWeight-Python v8.4

运行方式：
    python profile_weight.py            # 启动 GUI
    python profile_weight.py a.dxf --material "6063 铝合金" --export xlsx   # 命令行

依赖：
    pip install ezdxf
"""

# 应用版本号，每次发布时同步 .version_log.md 的最新版本
APP_VERSION = "v11.31"

import math
import csv
import os
from collections import defaultdict
import sys
import threading

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


def _exact_area_from_verts_and_bulges(vertices, bulges):
    """从顶点和bulge数组计算精确面积（算法③多段线拼接后使用）。"""
    n = len(vertices)
    if n < 3:
        return 0.0
    shoelace = 0.0
    for i in range(n):
        j = (i + 1) % n
        shoelace += vertices[i][0] * vertices[j][1]
        shoelace -= vertices[j][0] * vertices[i][1]
    shoelace /= 2.0
    total_correction = 0.0
    for i in range(n):
        b = bulges[i] if i < len(bulges) else 0.0
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
        total_correction += math.copysign(segment_area, b)
    return abs(shoelace + total_correction)


def _try_chain_open_polylines(pl_indices, open_pl_data, snap_tol=0.01):
    """尝试将相连的开口多段线首尾拼接为闭合轮廓（算法③：多段线首尾拼接）。

    当多个开放 LWPOLYLINE 的端点首尾相连形成闭合环路时，
    将它们拼接成一个完整的闭合多边形，用精确 bulge 校正计算面积。

    返回: {'vertices': [...], 'area': float, 'handles': [...]} 或 None
    """
    n = len(pl_indices)
    if n < 2:
        return None

    def _snap(x, y):
        return (round(x / snap_tol) * snap_tol, round(y / snap_tol) * snap_tol)

    # 提取每条多段线的有向边信息
    edges = []
    for idx in pl_indices:
        handle, entity, open_verts, area_eff, gap, npts = open_pl_data[idx]
        pts = [(float(p[0]), float(p[1])) for p in entity.get_points()]
        bulges = [float(p[4]) if len(p) > 4 else 0.0 for p in entity.get_points()]
        m = len(pts)

        # 反向bulge：rev_bulges[j] = -bulges[(m-2-j) % m]
        rev_bulges = [-bulges[(m - 2 - j) % m] for j in range(m)]

        edges.append({
            'idx': idx, 'handle': handle,
            'start_snap': _snap(pts[0][0], pts[0][1]),
            'end_snap': _snap(pts[-1][0], pts[-1][1]),
            'pts': pts, 'bulges': bulges, 'm': m,
            'rev_pts': list(reversed(pts)),
            'rev_bulges': rev_bulges,
        })

    # 构建端点→边索引的邻接表，每个端点必须恰好出现2次
    ep_map = {}
    for ei, e in enumerate(edges):
        for ep in (e['start_snap'], e['end_snap']):
            ep_map.setdefault(ep, []).append(ei)
    for ep_list in ep_map.values():
        if len(ep_list) != 2:
            return None  # 存在悬挂端点，不能形成闭合环路

    # 沿环链条边
    used = [False] * n
    chain = []  # [(edge_idx, reversed), ...]
    cur_ei = 0
    used[0] = True
    chain.append((0, False))
    cur_ep = edges[0]['end_snap']

    for _ in range(n - 1):
        found = False
        for ei in ep_map.get(cur_ep, []):
            if used[ei]:
                continue
            used[ei] = True
            e = edges[ei]
            if e['start_snap'] == cur_ep:
                chain.append((ei, False))
                cur_ep = e['end_snap']
            else:
                chain.append((ei, True))
                cur_ep = e['start_snap']
            found = True
            break
        if not found:
            return None

    # 验证闭合
    if cur_ep != edges[0]['start_snap']:
        return None

    # 拼接顶点和bulge
    all_pts = []
    all_bulges = []

    for ei, rev in chain:
        e = edges[ei]
        pts = e['rev_pts'] if rev else e['pts']
        bulges_arr = e['rev_bulges'] if rev else list(e['bulges'])
        m_e = len(pts)

        if not all_pts:
            all_pts.extend(pts)
            all_bulges.extend(bulges_arr)
        else:
            # 跳过首点（与前一段末点重复）
            all_pts.extend(pts[1:])
            all_bulges.extend(bulges_arr[1:])

    # 去掉闭合重复点
    if len(all_pts) >= 2:
        if (abs(all_pts[0][0] - all_pts[-1][0]) < 0.01 and
                abs(all_pts[0][1] - all_pts[-1][1]) < 0.01):
            all_pts = all_pts[:-1]
            all_bulges = all_bulges[:-1]

    area = _exact_area_from_verts_and_bulges(all_pts, all_bulges)
    handles = [edges[ei]['handle'] for ei, _ in chain]

    return {'vertices': all_pts, 'area': area, 'handles': handles}


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
    
    # Build endpoint graph — 就近合并：端点欧氏距离 < snap_tol 视为同一节点
    # （v11.25 根因修复：旧版用 round(pt/snap_tol)*snap_tol 绝对网格量化，
    #  同一几何在不同绝对位置会量化到不同网格，接缝端点压在网格边界时焊不上，
    #  导致相同型材因摆放位置不同而时成时败。改为相对距离合并后与位置无关。）
    node_pts = {}      # nid -> (x, y) 代表点
    next_nid = 0
    _tol_sq = snap_tol * snap_tol
    
    def _get_node(pt):
        nonlocal next_nid
        for nid, q in node_pts.items():
            dx = pt[0] - q[0]
            dy = pt[1] - q[1]
            if dx * dx + dy * dy <= _tol_sq:
                return nid
        nid = next_nid
        node_pts[nid] = (float(pt[0]), float(pt[1]))
        next_nid += 1
        return nid
    
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


def _group_fragments(arcs, lines, group_tol=0.5):
    """把零散 ARC/LINE 按端点邻接聚成若干连通分量（并查集）。
    返回 [(sub_arcs, sub_lines), ...]，每组对应一个物理轮廓的碎片。
    group_tol 用较宽松容差（默认 0.5mm）仅用于"分组"，真正焊接容差由
    Phase 3 逐组调 rebuild 时另行指定，从而实现"逐分量独立兜底"：
    某一型材焊不成时不影响其它已成环型材，也能对它单独放宽容差重试。
    """
    segs = []  # (kind, tuple, p1, p2)
    for a in arcs:
        segs.append(('A', a, (a[0], a[1]), (a[2], a[3])))
    for l in lines:
        segs.append(('L', l, (l[0], l[1]), (l[2], l[3])))
    n = len(segs)
    if n == 0:
        return []
    parent = list(range(n))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i, j):
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[ri] = rj

    tol_sq = group_tol * group_tol
    for i in range(n):
        for j in range(i + 1, n):
            if find(i) == find(j):
                continue
            connected = False
            for pi in (segs[i][2], segs[i][3]):
                for pj in (segs[j][2], segs[j][3]):
                    dx = pi[0] - pj[0]
                    dy = pi[1] - pj[1]
                    if dx * dx + dy * dy <= tol_sq:
                        connected = True
                        break
                if connected:
                    break
            if connected:
                union(i, j)

    from collections import defaultdict as _dd
    buckets = _dd(lambda: ([], []))
    for i, seg in enumerate(segs):
        root = find(i)
        if seg[0] == 'A':
            buckets[root][0].append(seg[1])
        else:
            buckets[root][1].append(seg[1])
    return list(buckets.values())


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


def _fragment_gap_diagnosis(arc_tuples, line_tuples):
    """测量零散 ARC/LINE 无法闭合时的断点数量与最大缺口（用于诊断报告）。
    返回 (break_count, max_gap_mm)。arc_tuples 为 9 元组，line_tuples 为 4 元组。
    """
    import math
    pts = []
    for sx, sy, ex, ey, *_ in arc_tuples:
        pts.append((sx, sy))
        pts.append((ex, ey))
    for x1, y1, x2, y2 in line_tuples:
        pts.append((x1, y1))
        pts.append((x2, y2))
    if len(pts) < 2:
        return 0, 0.0
    # 最近异点距离（最大缺口）
    max_gap = 0.0
    for i in range(len(pts)):
        best = float('inf')
        for j in range(len(pts)):
            if i == j:
                continue
            d = math.hypot(pts[i][0] - pts[j][0], pts[i][1] - pts[j][1])
            if d < best:
                best = d
        if best > max_gap:
            max_gap = best
    # 在 0.05mm 量化下统计奇数度节点（断点）
    snap = 0.05
    node_map = {}
    nid = 0

    def get_node(p):
        nonlocal nid
        s = (round(p[0] / snap) * snap, round(p[1] / snap) * snap)
        if s not in node_map:
            node_map[s] = nid
            nid += 1
        return node_map[s]

    deg = {}
    for k in range(0, len(pts), 2):
        n1 = get_node(pts[k])
        n2 = get_node(pts[k + 1])
        deg[n1] = deg.get(n1, 0) + 1
        deg[n2] = deg.get(n2, 0) + 1
    break_count = sum(1 for d in deg.values() if d % 2 == 1)
    return break_count, max_gap


def get_all_contours_from_dxf(filepath):
    """从 DXF 提取所有轮廓，支持碎片合并 + 共享边扩展检测。"""
    try:
        doc = ezdxf.readfile(filepath)
    except Exception as e:
        raise RuntimeError(f"读取 DXF 文件失败: {e}")

    msp = doc.modelspace()
    all_contours = []
    consumed_handles = set()
    diag = {'frag_count': 0, 'estimate': False, 'rebuild_failed': False,
            'break_count': 0, 'max_gap': 0.0}

    # 程序自身生成的标注图层（来自 generate_annotation_dxf）：这些图层上的
    # 圆/框/填充/引线仅用于标注重叠型材，不应被当作型材轮廓重新识别
    # （否则拿 `_标注.dxf` 再算会出现重复轮廓 / 净面积错乱）。
    _SKIP_LAYERS = {
        'ANNO_NORMAL', 'ANNO_ERROR', 'ANNO_REBUILT',
        'ERROR_MARKERS',
    }

    # ── Phase 1: 闭合 LWPOLYLINE ─────────────────
    for entity in msp:
        if entity.dxf.layer in _SKIP_LAYERS:
            continue
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
        if entity.dxf.layer in _SKIP_LAYERS:
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

    # ── Phase 2b.5: 多段线首尾拼接（算法③）──
    # 尝试将同一连通分量内、未与 LINE/ARC 相连的多条开口多段线拼接为闭合轮廓
    chained_handles = set()
    for root in set(_find(i) for i in range(pl_count)):
        comp_indices = [i for i in range(pl_count) if _find(i) == root]
        if len(comp_indices) < 2:
            continue
        if comp_has_la.get(root, False):
            continue  # 与 LINE/ARC 相连 → 走碎片合并路径
        result = _try_chain_open_polylines(comp_indices, open_pl_data, SNAP)
        if result:
            c = _make_contour(result['area'], result['vertices'],
                              'chained_open', 'LWPOLYLINE(chained)')
            if c:
                c['chain_handles'] = result['handles']
                all_contours.append(c)
            for h in result['handles']:
                consumed_handles.add(h)
                chained_handles.add(h)

    # ── Phase 2c: 处理 open LWPOLYLINE ──
    frag_lines = []   # (x1, y1, x2, y2)
    frag_arcs = []    # (sx, sy, ex, ey, cx, cy, r, sa, ea)

    for i, (handle, entity, open_verts, area_eff, gap, n) in enumerate(open_pl_data):
        if handle in chained_handles:
            continue  # 已在 Phase 2b.5 中作为拼接轮廓处理
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

        elif should_fragment and area_eff > 0.001:
            # 连通分量连接 LINE/ARC → 拆碎合并（如 #58: 11A+11B+11C）
            raw_pts = entity.get_points()
            for j in range(n - 1):
                p1, p2 = raw_pts[j], raw_pts[j + 1]
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

        else:
            # 面积 ≈ 0 的开口线（无论 gap 大小）→ 冗余短线 / 非截面，跳过
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

    # ── Phase 3: 碎片合并成闭合轮廓（v11.25 改为逐连通分量兜底）──
    if frag_lines or frag_arcs:
        ar_tuples = frag_arcs  # 已是 9 元组
        li_tuples = frag_lines
        diag['frag_count'] = len(ar_tuples) + len(li_tuples)
        # 先把碎片按端点邻接聚成若干连通分量，每个分量对应一个物理型材；
        # 逐分量独立焊接 + 独立兜底：某型材 0.1mm 焊不成时单独放宽到 0.5mm，
        # 不会因为其它型材已成环（旧全局逻辑 merged 非空即跳过回退）而被整组丢弃。
        groups = _group_fragments(ar_tuples, li_tuples, group_tol=0.5)
        if not groups:
            groups = [(ar_tuples, li_tuples)]
        merged_all = []
        any_estimate = False
        any_failed = False
        worst_bc = 0
        worst_gap = 0.0
        for g_arcs, g_lines in groups:
            # 主尝试：0.1mm 焊接容差（覆盖绝大多数制图接缝误差）
            m = rebuild_contour_from_arc_line(g_arcs, g_lines, snap_tol=0.1)
            if not m:
                # 宽松回退：0.5mm 容差，能成环则标记为"估算值"
                m = rebuild_contour_from_arc_line(g_arcs, g_lines, snap_tol=0.5)
                if m:
                    any_estimate = True
                else:
                    any_failed = True
                    bc, mg = _fragment_gap_diagnosis(g_arcs, g_lines)
                    if bc > worst_bc:
                        worst_bc = bc
                    if mg > worst_gap:
                        worst_gap = mg
            merged_all.extend(m)
        if any_estimate:
            diag['estimate'] = True
        if any_failed:
            diag['rebuild_failed'] = True
            diag['break_count'] = worst_bc
            diag['max_gap'] = worst_gap
        for rc in merged_all:
            c = _make_contour(rc['area'], rc['vertices'],
                              'merged_fragments', 'FRAGMENTS(merged)')
            if c:
                all_contours.append(c)

    # ── Phase 4: 其他图形（CIRCLE, ELLIPSE, HATCH, SOLID, POLYLINE）──
    for entity in msp:
        handle = entity.dxf.handle if hasattr(entity.dxf, 'handle') else ''
        if handle in consumed_handles:
            continue
        if entity.dxf.layer in _SKIP_LAYERS:
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
                # 用 ezdxf 官方工具把 HATCH 边界（PolylinePath / EdgePath，含带孔）
                # 展平为顶点序列，避免手搓 ArcEdge 采样导致面积算错（自交/方向错）。
                from ezdxf.path import from_hatch
                try:
                    ez_hatch_paths = list(from_hatch(entity))
                except Exception:
                    ez_hatch_paths = []
                for pi, ezp in enumerate(ez_hatch_paths):
                    try:
                        v = list(ezp.flattening(0.01))
                    except Exception:
                        v = []
                    if len(v) < 3:
                        continue
                    a = polygon_area(v)
                    flags = entity.paths[pi].path_type_flags if pi < len(entity.paths) else 1
                    if flags & 1:  # 外部边界
                        hatch_area += a
                    else:  # 内孔边界
                        hatch_area -= a
                    all_hatch_verts.extend(v)

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

    # ── Phase 5: 重复轮廓去重（线框与填充重叠表达同一截面）──
    all_contours, _dd = _dedupe_contours(all_contours)
    if _dd:
        diag['deduped'] = len(_dd)
        diag['dedup_details'] = _dd

    return all_contours, diag


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


def _dedupe_contours(contours, iou_thr=0.95, area_thr=0.02, center_thr=1.0):
    """合并几何重合的重复轮廓（如 LINE+ARC 线框 与 HATCH 填充表达同一截面）。

    判据（三者同时满足）：bbox IoU > iou_thr 且 面积差/较大面积 < area_thr
    且 中心偏移 < center_thr。保留面积更大者（通常 HATCH 顶点更密更准）。
    返回 (去重后列表, 合并详情列表)。
    """
    def _iou(b1, b2):
        if not b1 or not b2:
            return 0.0
        ix1, iy1 = max(b1[0], b2[0]), max(b1[1], b2[1])
        ix2, iy2 = min(b1[2], b2[2]), min(b1[3], b2[3])
        iw, ih = max(0.0, ix2 - ix1), max(0.0, iy2 - iy1)
        inter = iw * ih
        if inter <= 0:
            return 0.0
        a1 = (b1[2] - b1[0]) * (b1[3] - b1[1])
        a2 = (b2[2] - b2[0]) * (b2[3] - b2[1])
        union = a1 + a2 - inter
        return inter / union if union > 0 else 0.0

    kept = []
    details = []
    for c in contours:
        merged = False
        cb = c.get('bbox')
        ca = c.get('area', 0.0) or 0.0
        cc = c.get('center')
        for k in kept:
            kb = k.get('bbox')
            ka = k.get('area', 0.0) or 0.0
            kc = k.get('center')
            iou = _iou(cb, kb)
            big = max(ca, ka)
            adiff = (abs(ca - ka) / big) if big > 0 else 0.0
            cdist = 0.0
            if cc and kc:
                cdist = math.hypot(cc[0] - kc[0], cc[1] - kc[1])
            if iou > iou_thr and adiff < area_thr and cdist < center_thr:
                if ca >= ka:
                    idx = kept.index(k)
                    kept[idx] = c
                    removed = k
                else:
                    removed = c
                details.append({
                    'kept_handle': (c.get('handle') if ca >= ka else k.get('handle')),
                    'kept_source': (c.get('source') if ca >= ka else k.get('source')),
                    'removed_handle': (k.get('handle') if ca >= ka else c.get('handle')),
                    'removed_source': (k.get('source') if ca >= ka else c.get('source')),
                    'removed_bbox': (k.get('bbox') if ca >= ka else c.get('bbox')),
                    'removed_area': (ka if ca >= ka else ca),
                    'kept_area': (ca if ca >= ka else ka),
                })
                merged = True
                break
        if not merged:
            kept.append(c)
    return kept, details


def _extract_drawing_numbers(dxf_path, profiles, search_radius=80, include_anno_layers=False):
    """从 DXF 提取每个型材附近的标注序号（如 "1#"）作为型材编号。

    对每个 profile 的外轮廓 bbox 向外扩展 search_radius mm，查找落入该区域内的
    TEXT/MTEXT 实体，匹配 "1# X=..." 格式提取序号。无匹配则留空。

    Args:
        include_anno_layers: 是否包含 ANNO_* 图层（从 _标注.dxf 提取时应为 True，
                            因为程序导出的序号标注写在 ANNO_NORMAL 层上）
    """
    import re
    try:
        import ezdxf as _ez
        doc = _ez.readfile(dxf_path)
    except Exception:
        return

    # 排除的图层（DEFPOINTS 始终排除；ANNO_* 仅在非标注文件模式下排除）
    _always_skip = {'DEFPOINTS', 'Defpoints'}
    _anno_skip_layers = {
        'ANNO_NORMAL', 'ANNO_ERROR', 'ERROR_MARKERS',
    }

    def _extract_seq(text):
        """从标注文本 '1# X=10132 0.2443 kg/m' 提取 '1#'。"""
        m = re.match(r'^(\d+#)', text)
        return m.group(1) if m else None

    # 仅收集带序号的标注文本（如 "1# X=10132 0.2443 kg/m"），提取 "1#" 作为型材编号
    annotation_entities = []   # (x, y, seq)
    for e in doc.modelspace():
        if e.dxftype() not in ('TEXT', 'MTEXT'):
            continue
        lyr = e.dxf.layer
        if (lyr in _always_skip
                or lyr.upper() in {s.upper() for s in _always_skip}):
            continue
        # ANNO 图层：从原始文件提取时跳过（避免读到旧标注），从标注文件提取时保留
        if (not include_anno_layers
                and (lyr in _anno_skip_layers or lyr.startswith('ANNO'))):
            continue
            continue
        try:
            text_str = e.dxf.text.strip()
            if not text_str or len(text_str) >= 60:
                continue
            seq = _extract_seq(text_str)
            if seq:
                insert = e.dxf.insert
                annotation_entities.append((insert[0], insert[1], seq))
        except Exception:
            continue

    # ── 为每个 profile 匹配型材编号（仅取标注序号，无则留空）──
    for p in profiles:
        shapes = p.get('shapes', [])
        if not shapes:
            p['drawing_number'] = ''   # 无形状 → 空白
            continue

        outer = p.get('outer')
        if outer and outer.get('bbox'):
            bx0, by0, bx1, by1 = outer['bbox']
        else:
            bboxes = [s['bbox'] for s in shapes if s.get('bbox')]
            if not bboxes:
                p['drawing_number'] = ''   # 无 bbox → 空白
                continue
            bx0 = min(b[0] for b in bboxes)
            by0 = min(b[1] for b in bboxes)
            bx1 = max(b[2] for b in bboxes)
            by1 = max(b[3] for b in bboxes)

        bx0 -= search_radius
        by0 -= search_radius
        bx1 += search_radius
        by1 += search_radius
        cx = (bx0 + bx1) / 2 - search_radius
        cy = (by0 + by1) / 2 - search_radius

        # 只匹配标注序号（如 "1#" from "1# X=10132 0.2443 kg/m"），没有就空白
        best_seq = ''
        best_seq_dist = float('inf')
        for tx, ty, seq in annotation_entities:
            if tx < bx0 or tx > bx1 or ty < by0 or ty > by1:
                continue
            dist = ((tx - cx) ** 2 + (ty - cy) ** 2) ** 0.5
            if dist < best_seq_dist:
                best_seq_dist = dist
                best_seq = seq

        if best_seq:
            p['drawing_number'] = best_seq   # 找到则 "1#"，否则保留已有值（不覆盖为空）


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

    # ── 检测3: effectively_closed 大开口线 → 算法② 精度警告 ──
    for s in [outer] + holes:
        if s.get('source') == 'effectively_closed':
            gap_v = s.get('gap', 0)
            if gap_v > 5.0:
                already_reported = any(
                    e.get('type') == 'large_gap' and e.get('handle') == s.get('handle')
                    for e in errors
                )
                if not already_reported:
                    errors.append({
                        'type': 'large_gap',
                        'severity': 'warning',
                        'contour': s,
                        'handle': s.get('handle', ''),
                        'gap': gap_v,
                        'message': (f"型材含有大开口线 {s.get('type','?')} "
                                    f"(handle={s.get('handle','?')}, gap={gap_v:.1f}mm)，"
                                    f"以假想直线闭合后的面积仅供参考"),
                        'fix': f"请在 CAD 中手动闭合该多段线 (gap={gap_v:.1f}mm 过大)",
                    })

    net_area = outer['area']
    for h in holes:
        # shared_edge / open_polyline 是图纸结构性错误 → 不扣除
        # large_gap / 其他警告 → 仍作为正常孔洞扣除，仅精度仅供参考
        is_structural_err = any(
            e.get('handle') == h.get('handle')
            and e.get('type') in ('shared_edge', 'open_polyline')
            for e in errors
        )
        if not is_structural_err:
            net_area -= h['area']

    return net_area, outer, holes, errors


def calc_weight(net_area_mm2, density_kg_m3):
    return net_area_mm2 / 1000000.0 * density_kg_m3


def run_calculation(filepath, density):
    """执行计算，返回 (profiles, lines) 其中 lines 是格式化文本行列表"""
    lines = []
    contours, diag = get_all_contours_from_dxf(filepath)
    lines.append(f"找到 {len(contours)} 个封闭轮廓")
    if diag.get('deduped'):
        lines.append(f"🟡 [重复轮廓] 检测到 {diag['deduped']} 处重复表达（线框与填充重叠），已自动合并为 1 个，请人工核对截面面积")
    if diag.get('estimate'):
        lines.append("🟡  部分型材存在细微缺口（0.5mm 容差焊接），米重基本准确，建议核对截面")
    if not contours:
        fc = diag.get('frag_count', 0)
        if fc > 0:
            lines.append(f"⚠️  未找到有效封闭轮廓，但检测到 {fc} 段图元（线段/圆弧）无法精确闭合")
            lines.append(f"     → 最大缺口约 {diag.get('max_gap', 0):.3f}mm，可能存在接缝间隙或断点")
            lines.append("     → 修复: 请在 CAD 中用 PEDIT 将线段/圆弧合并为闭合多段线后重试")
        else:
            lines.append("⚠️  未找到有效封闭轮廓，请检查 DXF 文件")
        return [], lines
    groups = group_contours_by_profiles(contours) if len(contours) > 1 else [contours]
    lines.append(f"分组为 {len(groups)} 个型材")
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
        profile['rebuilt'] = any(s.get('source') == 'merged_fragments' for s in group)
        # 标记该型材是否参与了去重合并（其轮廓 handle 在 kept_handle 列表中）
        _ddetails = diag.get('dedup_details', [])
        if _ddetails:
            _kept = {d.get('kept_handle', '') for d in _ddetails}
            profile['has_dup'] = any(s.get('handle') in _kept for s in group)
        else:
            profile['has_dup'] = False
        profiles.append(profile)
        w_g = w_kg * 1000

        if errors:
            has_any_error = True
            # ── 错误型材：突出显示错误信息 ──
            lines.append(f"  ┌─ 型材 {gi + 1}#  (位置 x={pos_x:.1f})  ⚠️ 图纸错误!")
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
            lines.append(f"  ┌─ 型材 {gi + 1}#  (位置 x={pos_x:.1f})")
            if outer:
                lines.append(f"  │  外轮廓面积: {outer['area']:.2f} mm²  ({outer.get('type','?')} {outer.get('handle','')})")
            for h in holes:
                lines.append(f"  │  孔洞面积:   {h['area']:.2f} mm²  ({h.get('type','?')} {h.get('handle','')})")
            if profile.get('rebuilt'):
                lines.append(f"  │  🟡  该型材存在细微缺口（由零散线段/圆弧焊接闭合），米重基本准确")
            if net_area is not None and net_area > 0:
                lines.append(f"  │  净截面面积: {net_area:.2f} mm²")
                lines.append(f"  └─ 米重: {w_kg:.4f} kg/m  ({w_g:.2f} g/m)")
            elif net_area is not None and net_area <= 0:
                lines.append(f"  └─ ⚠️  净面积为负值 ({net_area:.2f} mm²)，请检查图纸")
            else:
                lines.append(f"  └─ ❌  无法计算面积")
            lines.append("")
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
            _seq = valid.index(p) + 1 if p in valid else '?'
            lines.append(f"  型材 {_seq}#: x={pos_x:.1f}")
            for err in p['errors']:
                lines.append(f"    - {err['fix']}")
        lines.append("")
        lines.append("  💡 提示: 可使用「导出错误标注DXF」功能，")
        lines.append("     在 CAD 中打开标注文件定位到具体错误位置。")
        lines.append("=" * 50)
    rebuilt_profiles = [p for p in profiles if p.get('rebuilt')]
    if rebuilt_profiles:
        lines.append("")
        lines.append("=" * 50)
        lines.append(f"🟡  发现 {len(rebuilt_profiles)} 个型材存在细微缺口（由碎片焊接闭合）")
        lines.append("     缺口在 0.1~0.5mm 以内，米重基本准确，建议核对截面形状")
        lines.append("=" * 50)
    # ── 提取图纸编号（每个型材附近的 TEXT/MTEXT）──
    if profiles:
        _extract_drawing_numbers(filepath, profiles)
    return profiles, lines, diag


def export_xlsx(profiles, output_path, density, material_name):
    """导出 Excel（.xlsx）。整行按三级状态上色，与 DXF 标注颜色统一：
    绿=正常 / 黄=小问题(微缺口、去重) / 红=大问题(错误)。"""
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

    headers = ['序号', '文件名', '型材编号', '位置X', '净截面面积(mm²)', '密度(kg/m³)',
               '材料', '米重(kg/m)', '外轮廓面积(mm²)',
               '孔洞面积(mm²)', '形状数', '错误数', '错误详情', '状态']

    # 三级底色（与 DXF 绿/黄/红一致）
    GREEN_FILL = PatternFill('solid', fgColor='EAF3DE')
    YELLOW_FILL = PatternFill('solid', fgColor='FAEEDA')
    RED_FILL = PatternFill('solid', fgColor='FCEBEB')
    HEADER_FILL = PatternFill('solid', fgColor='D3D1C7')
    thin = Side(style='thin', color='B4B2A9')
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    header_font = Font(bold=True)
    center = Alignment(horizontal='center', vertical='center')
    left = Alignment(horizontal='left', vertical='center', wrap_text=True)

    wb = Workbook()
    ws = wb.active
    ws.title = "型材米重"
    ws.append(headers)
    for ci in range(1, len(headers) + 1):
        c = ws.cell(row=1, column=ci)
        c.fill = HEADER_FILL
        c.font = header_font
        c.alignment = center
        c.border = border

    for i, p in enumerate(profiles, 1):
        net = p['net_area'] or 0
        w_kg = calc_weight(net, density) if net > 0 else 0
        outer_area = p['outer']['area'] if p.get('outer') else 0
        hole_areas = '+'.join([f"{h['area']:.2f}" for h in p.get('holes', [])])
        shape_count = 1 + len(p.get('holes', []))
        pos_x = min([c['center'][0] for c in p['shapes'] if c.get('center')], default=0)
        err_count = len(p.get('errors', []))
        err_detail = ' | '.join([e['message'] for e in p.get('errors', [])])
        fname = p.get('source_file', '')
        drawing_num = p.get('drawing_number', '')
        has_err = bool(p.get('errors'))
        _st_parts = []
        if has_err:
            _st_parts.append("错误")
        if p.get('has_dup'):
            _st_parts.append("去重")
        if p.get('rebuilt'):
            _st_parts.append("微缺口")
        status = "/".join(_st_parts) if _st_parts else "正常"
        row = [i, fname, drawing_num, f"{pos_x:.1f}", f"{net:.2f}", f"{density:.1f}",
               material_name, f"{w_kg:.4f}", f"{outer_area:.2f}", hole_areas,
               shape_count, err_count, err_detail, status]
        ws.append(row)
        r = ws.max_row
        fill = RED_FILL if has_err else (YELLOW_FILL if (p.get('rebuilt') or p.get('has_dup')) else GREEN_FILL)
        for ci in range(1, len(headers) + 1):
            c = ws.cell(row=r, column=ci)
            c.fill = fill
            c.border = border
            c.alignment = left if ci == 13 else center

    widths = [6, 24, 10, 8, 16, 12, 10, 12, 14, 16, 8, 8, 42, 12]
    for ci, w in enumerate(widths, 1):
        ws.column_dimensions[ws.cell(row=1, column=ci).column_letter].width = w
    ws.freeze_panes = "A2"

    try:
        wb.save(output_path)
    except Exception as e:
        raise RuntimeError(f"保存 Excel 失败: {e}")


def export_csv(profiles, output_path, density, material_name):
    """导出 CSV（列定义与 SKILL.md 一致）。"""
    import csv
    cols = ['No', 'Position(X)', 'NetArea(mm2)', 'Density(kg/m3)', 'Material',
            'Weight(kg/m)', 'Weight(g/m)', 'OuterArea(mm2)', 'HoleAreas(mm2)',
            'Shapes', 'SourceType', 'Status']
    with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(cols)
        for i, p in enumerate(profiles, 1):
            net = p.get('net_area') or 0
            wk = calc_weight(net, density) if net > 0 else 0
            outer = p['outer']['area'] if p.get('outer') else 0
            holes = '+'.join([f"{h['area']:.2f}" for h in p.get('holes', [])])
            src = ';'.join(sorted({s.get('source', '') for s in p.get('shapes', [])}))
            status = 'ERROR' if p.get('errors') else ('OK' if net > 0 else 'NA')
            w.writerow([i, f"{p.get('pos_x', 0):.1f}", f"{net:.2f}", f"{density:.1f}",
                        material_name, f"{wk:.4f}", f"{wk * 1000:.2f}", f"{outer:.2f}",
                        holes, len(p.get('shapes', [])), src, status])


def generate_annotation_dxf(profiles, input_dxf_path, output_path, dedup_details=None, dxf_version='AC1024'):
    """生成全量标注 DXF。DXF 标注与导出表格颜色统一：绿=正常 / 黄=小问题 / 红=大问题。

    在原始 DXF 上添加标注图层：
    - ANNO_NORMAL (绿色): 正常型材 — 一行文字（不画框）
    - ANNO_REBUILT (黄色): 小问题型材 — 黄色矩形框 + 文字（尾注 [微缺口]/[去重]）
    - ANNO_ERROR + ERROR_MARKERS (红色): 大问题型材 — 红色矩形框 + 一行文字（尾注 [缺口]/[共享边]/[冗余线]）

    去重信息已合并到 ANNO_REBUILT 的 [去重] 标签中，不再单独绘制。
    """
    import ezdxf as ezdxf_mod
    from ezdxf import colors as dxf_colors

    try:
        doc = ezdxf_mod.readfile(input_dxf_path)
    except Exception as e:
        raise RuntimeError(f"读取 DXF 失败: {e}")

    # 强制降版本为 R2010/AC1024（默认）：部分国产 CAD（浩辰/中望/ZWCAD 等）无法正确解析
    # AC1032（AutoCAD 2018）格式，尤其原图含大量图层/复杂结构时会静默丢弃新增图层
    # 与实体（如 077后续.dxf 含 71 图层）。AC1024 是兼容性最广的 DXF 版本，可规避此问题。
    # 版本可由 GUI 的"标注DXF版本"下拉框覆盖（dxf_version 参数）。
    try:
        doc.dxfversion = dxf_version
    except Exception:
        pass

    msp = doc.modelspace()

    GREEN, YELLOW, RED = dxf_colors.GREEN, dxf_colors.YELLOW, dxf_colors.RED
    # 创建图层
    for layer_name, color in [('ANNO_NORMAL', GREEN),
                                ('ANNO_ERROR', RED),
                                ('ERROR_MARKERS', RED),
                                ('ANNO_REBUILT', YELLOW)]:
        if layer_name not in doc.layers:
            doc.layers.add(name=layer_name, color=color)

    marker_pad = 12.0     # 红/黄框相对型材外扩
    text_height = 4.0

    # 错误类型 → 简短中文标签（用于红字尾注；按周总要求只标一次、不堆内部诊断长句）
    _ERR_LABEL = {
        'large_gap': '缺口',
        'shared_edge': '共享边',
        'open_polyline': '冗余线',
    }

    for pi, p in enumerate(profiles):
        seq = p.get('index', pi + 1)
        pos_x = p.get('pos_x', 0)
        weight_kgm = p.get('weight_kgm', 0)
        has_err = bool(p.get('errors'))

        shapes = p.get('shapes', [])
        if not shapes:
            continue

        # 型材整体 bbox（所有 shape 并集），作为框/文字基准
        bx0 = by0 = float('inf')
        bx1 = by1 = float('-inf')
        for s in shapes:
            b = s.get('bbox')
            if b:
                bx0 = min(bx0, b[0]); by0 = min(by0, b[1])
                bx1 = max(bx1, b[2]); by1 = max(by1, b[3])
        if bx0 == float('inf'):
            c = (shapes[0].get('center') or (0, 0))
            bx0, by0, bx1, by1 = c[0] - 10, c[1] - 10, c[0] + 10, c[1] + 10
        cx, cy = (bx0 + bx1) / 2, (by0 + by1) / 2

        # ── 大问题 → 红色矩形框 + 一行红字（取消实心填充圆/引线/英文/逐条长句）──
        if has_err:
            corners = [
                (bx0 - marker_pad, by0 - marker_pad),
                (bx1 + marker_pad, by0 - marker_pad),
                (bx1 + marker_pad, by1 + marker_pad),
                (bx0 - marker_pad, by1 + marker_pad),
            ]
            msp.add_lwpolyline(corners, close=True,
                               dxfattribs={'layer': 'ERROR_MARKERS', 'color': RED})
            labels = []
            for err in p.get('errors', []):
                lbl = _ERR_LABEL.get(err.get('type', ''), '错误')
                if lbl not in labels:
                    labels.append(lbl)
            label_text = f"{seq}# X={pos_x:.0f} {weight_kgm:.4f} kg/m [{'/'.join(labels)}]"
            msp.add_text(label_text,
                         dxfattribs={'layer': 'ANNO_ERROR', 'color': RED,
                                     'height': text_height,
                                     'insert': (bx0 - marker_pad, by1 + marker_pad * 0.6)})

        # ── 小问题（微缺口/去重）→ 黄色矩形框 + 黄色文字 ──
        elif p.get('rebuilt') or p.get('has_dup'):
            corners = [
                (bx0 - marker_pad, by0 - marker_pad),
                (bx1 + marker_pad, by0 - marker_pad),
                (bx1 + marker_pad, by1 + marker_pad),
                (bx0 - marker_pad, by1 + marker_pad),
            ]
            msp.add_lwpolyline(corners, close=True,
                               dxfattribs={'layer': 'ANNO_REBUILT', 'color': YELLOW})
            tags = []
            if p.get('rebuilt'):
                tags.append("微缺口")
            if p.get('has_dup'):
                tags.append("去重")
            label_text = f"{seq}# X={pos_x:.0f} {weight_kgm:.4f} kg/m [{'/'.join(tags)}]"
            msp.add_text(label_text,
                         dxfattribs={'layer': 'ANNO_REBUILT', 'color': YELLOW,
                                     'height': text_height,
                                     'insert': (bx0 - marker_pad, by1 + marker_pad * 0.6)})

        # ── 正常 → 绿色文字（不加框）──
        else:
            label_text = f"{seq}# X={pos_x:.0f} {weight_kgm:.4f} kg/m"
            msp.add_text(label_text,
                         dxfattribs={'layer': 'ANNO_NORMAL', 'color': GREEN,
                                     'height': text_height,
                                     'insert': (bx0 - marker_pad, by1 + marker_pad * 0.6)})

    # 注：重复轮廓的合并提示已不再单独画黄色标注，相关信息合并在主标注的
    # `[去重]` 标签中（见上方 elif 分支）；GUI 状态栏仍会汇总"检测到 N 处
    # 重复轮廓已合并"。dedup_details 参数保留供调用方传入，此处不再使用。

    # 保存（单次；重复 saveas 在 Windows 实时点击时可能撞文件锁/缓冲导致写入残缺）
    try:
        doc.saveas(output_path)
    except Exception as e:
        raise RuntimeError(f"保存 DXF 失败: {e}")

    return output_path


# ============================================================
# GUI
# ============================================================



# ============================================================
# CustomTkinter GUI 层（统一 UI 架构，便于嵌入主窗口 Tab）
# 依赖：pip install customtkinter
# ============================================================
import tkinter as tk
from tkinter import filedialog, ttk
import customtkinter as ctk


class CalcThread:
    """后台计算线程（threading 实现，结果回主线程更新 UI）。"""

    def __init__(self, master, filepaths, density, on_done, on_error):
        self.master = master
        self.filepaths = filepaths  # list of paths (batch) or [single_path]
        self.density = density
        self._on_done = on_done
        self._on_error = on_error

    def start(self):
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        try:
            all_profiles = []
            all_lines = []
            all_diag = {}
            total_deduped = 0

            for fp in self.filepaths:
                fname = os.path.basename(fp)
                profiles, lines, diag = run_calculation(fp, self.density)
                # 给每个 profile 打上来源文件标记
                for p in profiles:
                    p['source_file'] = fname
                all_profiles.extend(profiles)
                if len(self.filepaths) > 1:
                    all_lines.append(f"═══ {fname} ═══")
                all_lines.extend(lines)
                if diag.get('deduped'):
                    total_deduped += diag['deduped']
                all_diag[fname] = diag

            text = "\n".join(all_lines)
            has_err = any(p.get('errors') for p in all_profiles)
            err_count = sum(1 for p in all_profiles if p.get('errors'))
            if total_deduped:
                all_diag['_batch_deduped'] = total_deduped
            # 切回主线程更新 UI
            self.master.after(0, self._on_done, all_profiles, text,
                              has_err, err_count, all_diag)
        except Exception as e:
            self.master.after(0, self._on_error, f"计算出错：{e}")


class ProfileWeightApp(ctk.CTkFrame):
    """型材米重计算 UI（CustomTkinter）。

    既可作为独立窗口内容，也可被嵌入主窗口 Tab（第2步整合时复用）。
    """

    def __init__(self, master):
        super().__init__(master)
        self._profiles = []
        self._last_dxf = ""
        self._diag = {}
        self._batch_paths = None       # 多选文件路径列表（None=未选择/单文件模式）
        self._batch_results = []       # [(filepath, profiles, diag), ...] 每文件结果
        self._annotation_paths = {}    # {源文件路径: 标注文件实际保存路径} 用于 CSV 补充编号
        self.columnconfigure(0, weight=1)
        self.rowconfigure(5, weight=1)
        self._build_ui()

    def _build_ui(self):
        title = ctk.CTkLabel(self, text="型材米重计算器",
                             font=("Microsoft YaHei UI", 16, "bold"))
        title.grid(row=0, column=0, sticky="w", padx=16, pady=(16, 8))

        # ── 文件选择 ──
        f_file = ctk.CTkFrame(self)
        f_file.grid(row=1, column=0, sticky="ew", padx=16, pady=4)
        f_file.columnconfigure(1, weight=1)
        ctk.CTkLabel(f_file, text="DXF 文件").grid(row=0, column=0, padx=8, pady=8)
        self.le_path = ctk.CTkEntry(f_file, placeholder_text="选择 DXF 文件…")
        self.le_path.grid(row=0, column=1, sticky="ew", padx=8, pady=8)
        ctk.CTkButton(f_file, text="浏览", width=80,
                      command=self._browse).grid(row=0, column=2, padx=8, pady=8)

        # ── 材料 + 版本设置（两行布局）──
        f_mat = ctk.CTkFrame(self)
        f_mat.grid(row=2, column=0, sticky="ew", padx=16, pady=4)
        # 第1行：材料 / 密度
        ctk.CTkLabel(f_mat, text="材料").grid(row=0, column=0, padx=8, pady=(8, 2))
        self.cb_material = ctk.CTkComboBox(
            f_mat, values=list(MATERIAL_DENSITY.keys()),
            command=self._on_material_change, width=140)
        self.cb_material.set(list(MATERIAL_DENSITY.keys())[0])
        self.cb_material.grid(row=0, column=1, padx=8, pady=(8, 2))
        ctk.CTkLabel(f_mat, text="密度 (kg/m³)").grid(row=0, column=2, padx=(12, 4), pady=(8, 2))
        self.le_density = ctk.CTkEntry(f_mat, width=90)
        self.le_density.insert(0, str(MATERIAL_DENSITY[self.cb_material.get()]))
        self.le_density.grid(row=0, column=3, padx=8, pady=(8, 2))
        ctk.CTkLabel(f_mat, text="（可手动修改）").grid(row=0, column=4, padx=4, pady=(8, 2))
        # 第2行：标注DXF版本
        ctk.CTkLabel(f_mat, text="标注DXF版本").grid(row=1, column=0, padx=8, pady=(2, 8), sticky="e")
        self.cb_dxfver = ctk.CTkComboBox(
            f_mat,
            width=200,
            values=["AC1024 (R2010 推荐)", "AC1032 (R2018 原格式)", "AC1015 (R2000 旧版)"],
            state="readonly")
        self.cb_dxfver.set("AC1032 (R2018 原格式)")
        self.cb_dxfver.grid(row=1, column=1, columnspan=3, padx=8, pady=(2, 8), sticky="w")

        # ── 按钮行 ──
        f_btn = ctk.CTkFrame(self, fg_color="transparent")
        f_btn.grid(row=3, column=0, sticky="ew", padx=16, pady=(4, 8))
        self.btn_calc = ctk.CTkButton(f_btn, text="▶  开始计算", command=self._calc)
        self.btn_calc.pack(side="left", padx=4)
        self.btn_export = ctk.CTkButton(f_btn, text="导出 Excel",
                                        command=self._export, state="disabled")
        self.btn_export.pack(side="left", padx=4)
        self.btn_err = ctk.CTkButton(f_btn, text="📐 导出标注 DXF",
                                     command=self._export_annotations, state="disabled")
        self.btn_err.pack(side="left", padx=4)

        # ── 底部状态栏 ──
        f_status = ctk.CTkFrame(self, fg_color="#f8fafc", corner_radius=8)
        f_status.grid(row=6, column=0, sticky="ew", padx=16, pady=(4, 16))
        self.lbl_status = ctk.CTkLabel(
            f_status, text="",
            font=("Microsoft YaHei UI", 12),
            text_color="#64748b",
            wraplength=760,
            justify="left")
        self.lbl_status.pack(side="left", padx=8, pady=6)

        # ── 结果区（表格 + 详情）──
        ctk.CTkLabel(self, text="计算结果",
                     font=("Microsoft YaHei UI", 13, "bold")).grid(
            row=4, column=0, sticky="w", padx=16, pady=(4, 2))

        f_result = ctk.CTkFrame(self)
        f_result.grid(row=5, column=0, sticky="nsew", padx=16, pady=(2, 12))
        f_result.columnconfigure(0, weight=1)
        f_result.rowconfigure(0, weight=3)
        f_result.rowconfigure(1, weight=2)

        cols = ["序号", "文件名", "位置X (mm)", "净面积 (mm²)", "米重 (kg/m)", "孔洞", "状态"]
        self.table = ttk.Treeview(f_result, columns=cols, show="headings", height=12)
        for c in cols:
            self.table.heading(c, text=c)
            self.table.column(c, anchor="center", width=90)
        self.table.column("序号", width=50)
        self.table.column("文件名", width=160)
        self.table.column("位置X (mm)", width=100)
        self.table.column("净面积 (mm²)", width=110)
        self.table.column("米重 (kg/m)", width=100)
        self.table.tag_configure("err", background="#fcebeb", foreground="#a32d2d")
        self.table.bind("<<TreeviewSelect>>", self._on_row_selected)
        self.table.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)

        self.detail = ctk.CTkTextbox(f_result, font=("Consolas", 12))
        self.detail.grid(row=1, column=0, sticky="nsew", padx=4, pady=4)

        self._set_status(
            "基于 AlWeight-Python v8.4 | 支持碎片合并 + 错误检测标注", "#64748b")

    def _browse(self):
        paths = filedialog.askopenfilenames(
            title="选择 DXF 文件（可多选）",
            filetypes=[("DXF 文件", "*.dxf"), ("所有文件", "*.*")])
        if paths:
            self._batch_paths = list(paths)
            display = paths[0] if len(paths) == 1 else f"已选择 {len(paths)} 个文件"
            self.le_path.delete(0, tk.END)
            self.le_path.insert(0, display)

    def _on_material_change(self, choice):
        if choice in MATERIAL_DENSITY:
            self.le_density.delete(0, tk.END)
            self.le_density.insert(0, str(MATERIAL_DENSITY[choice]))

    def _on_row_selected(self, event=None):
        sel = self.table.selection()
        if sel:
            idx = self.table.index(sel[0])
            try:
                self.detail.yview_moveto(min(1.0, (idx + 1) * 0.02))
            except Exception:
                pass

    def _fill_table(self, profiles):
        self.table.delete(*self.table.get_children())
        for i, p in enumerate(profiles):
            has_err = bool(p.get('errors'))
            net = p.get('net_area')
            w = p.get('weight_kgm', 0) or 0
            holes = p.get('holes') or []
            pos_x = p.get('pos_x', 0)
            idx = p.get('index', i + 1)
            fname = p.get('source_file', '')
            has_err = bool(p.get('errors'))
            _st_parts = []
            if has_err:
                _st_parts.append("错误")
            if p.get('has_dup'):
                _st_parts.append("去重")
            if p.get('rebuilt'):
                _st_parts.append("微缺口")
            status_text = "/".join(_st_parts) if _st_parts else "正常"
            vals = [
                str(idx),
                fname,
                f"{pos_x:.1f}",
                f"{net:.2f}" if net else "—",
                f"{w:.4f}" if net else "—",
                str(len(holes)),
                status_text,
            ]
            self.table.insert("", "end", values=vals, tags=("err",) if has_err else ())

    def _set_detail(self, text):
        self.detail.delete("1.0", tk.END)
        self.detail.insert("1.0", text)

    def _set_status(self, text, color):
        self.lbl_status.configure(text=text, text_color=color)

    def _calc(self):
        paths = getattr(self, '_batch_paths', None)
        if not paths:
            filepath = self.le_path.get().strip()
            if not filepath:
                self._set_status("⚠️ 请先选择 DXF 文件", "#e67e22")
                return
            if not os.path.exists(filepath):
                self._set_status(f"❌ 文件不存在：{filepath}", "#e74c3c")
                return
            paths = [filepath]
        else:
            # 验证所有文件存在
            missing = [p for p in paths if not os.path.exists(p)]
            if missing:
                self._set_status(f"❌ {len(missing)} 个文件不存在（如 {os.path.basename(missing[0])}）", "#e74c3c")
                return

        try:
            density = float(self.le_density.get())
        except ValueError:
            self._set_status("❌ 密度值无效，请输入数字", "#e74c3c")
            return

        self.btn_calc.configure(state="disabled", text="计算中…")
        self.btn_export.configure(state="disabled")
        self.btn_err.configure(state="disabled")
        n = len(paths)
        label = f"正在解析 {n} 个 DXF 文件，请稍候…" if n > 1 else "正在解析 DXF 文件，请稍候…"
        self._set_status(label, "#64748b")
        self._set_detail(label)

        self.thread = CalcThread(self, paths, density,
                                 self._on_calc_done, self._on_calc_error)
        self.thread.start()

    def _on_calc_done(self, profiles, text, has_errors, err_count, diag=None):
        self._profiles = profiles
        # 批量模式：diag 是 {filename: {...}} 或混合结构；提取文件路径列表
        self._diag = diag or {}
        paths = getattr(self, '_batch_paths', None)
        if paths and len(paths) > 1:
            self._last_dxf = None  # 批量模式下无单一源文件
            self._batch_results = []
            for fp in paths:
                fname = os.path.basename(fp)
                fprofiles = [p for p in profiles if p.get('source_file') == fname]
                fdiag = diag.get(fname, {}) if isinstance(diag, dict) else {}
                self._batch_results.append((fp, fprofiles, fdiag))
        else:
            self._last_dxf = self.le_path.get().strip()
            fname = os.path.basename(self._last_dxf) if self._last_dxf else ''
            # 单文件也统一打标记（兼容 _fill_table）
            for p in profiles:
                p.setdefault('source_file', fname)
            self._batch_results = [(self._last_dxf, profiles, diag)] if self._last_dxf else []

        self._fill_table(profiles)
        rebuilt_count = sum(1 for p in profiles if p.get('rebuilt'))
        self._set_detail(text)
        # ── 计算完成即按序号填充型材编号（"1#"/"2#"…，与标注格式一致）──
        # 不依赖是否导出过标注 DXF；导出 CSV 时若标注文件存在会再覆盖补充
        for _fp, _fprofiles, _ in self._batch_results:
            for _i, _p in enumerate(_fprofiles, 1):
                if not _p.get('drawing_number'):
                    _p['drawing_number'] = f"{_i}#"
        self.btn_calc.configure(state="normal", text="▶  开始计算")
        if profiles:
            self.btn_export.configure(state="normal")
            self.btn_err.configure(state="normal")
            n_files = len(self._batch_results)
            if n_files > 1:
                file_label = f"{n_files} 个文件"
            else:
                file_label = ""
            if has_errors:
                self._set_status(
                    f"完成{f'，共{file_label}' if file_label else ''}，"
                    f"共 {len(profiles)} 个型材，其中 {err_count} 个图纸有问题",
                    "#e67e22")
            elif self._diag.get('_batch_deduped') or any(
                d.get('deduped', 0) for d in self._diag.values()
            ):
                _dd = self._diag.get('_batch_deduped') or sum(
                    d.get('deduped', 0) for d in self._diag.values())
                self._set_status(
                    f"完成{f'，共{file_label}' if file_label else ''}，"
                    f"共 {len(profiles)} 个型材，"
                    f"检测到 {_dd} 处重复轮廓已合并（请人工核对）",
                    "#d4a017")
            elif rebuilt_count:
                self._set_status(
                    f"完成{f'，共{file_label}' if file_label else ''}，"
                    f"共 {len(profiles)} 个型材，"
                    f"{rebuilt_count} 个存在细微缺口(焊接闭合)",
                    "#d4a017")
            else:
                self._set_status(
                    f"完成{f'，共{file_label}' if file_label else ''}，"
                    f"共 {len(profiles)} 个型材", "#27ae60")
        else:
            self._set_status("未找到有效型材", "#e74c3c")

    def _on_calc_error(self, msg):
        self._set_detail(msg)
        self.btn_calc.configure(state="normal", text="▶  开始计算")
        self._set_status("❌ 计算失败", "#e74c3c")

    def _export_annotations(self):
        if not self._profiles:
            self._set_status("⚠️ 请先计算结果", "#e67e22")
            return

        batch_results = getattr(self, '_batch_results', [])
        is_batch = len(batch_results) > 1

        if not is_batch and not self._last_dxf:
            self._set_status("⚠️ 请先选择 DXF 文件", "#e67e22")
            return

        dxf_ver = self.cb_dxfver.get().split()[0]

        try:
            if is_batch:
                # ── 批量模式：选输出目录，每个源文件生成一份标注 DXF ──
                out_dir = filedialog.askdirectory(
                    title="选择标注 DXF 输出目录（将按文件名分别导出）")
                if not out_dir:
                    return
                success = 0
                fail = 0
                for src_path, fprofiles, fdiag in batch_results:
                    fname = os.path.basename(src_path)
                    base = os.path.splitext(fname)[0]
                    out_path = os.path.join(out_dir, base + "_标注.dxf")
                    try:
                        generate_annotation_dxf(fprofiles, src_path, out_path,
                                                dedup_details=fdiag.get('dedup_details'),
                                                dxf_version=dxf_ver)
                        self._annotation_paths[src_path] = out_path   # 记录实际路径
                        success += 1
                    except Exception as ex:
                        fail += 1
                total = len(batch_results)
                msg = f"✓ 批量标注已导出 ({dxf_ver}): {success}/{total} 成功"
                if fail:
                    msg += f"，{fail} 个失败"
                self._set_status(msg, "#27ae60" if fail == 0 else "#e67e22")
            else:
                # ── 单文件模式：选保存路径（原有逻辑）──
                default_name = os.path.splitext(self._last_dxf)[0] + "_标注.dxf"
                out_path = filedialog.asksaveasfilename(
                    title="保存标注 DXF", initialfile=os.path.basename(default_name),
                    defaultextension=".dxf",
                    filetypes=[("DXF 文件", "*.dxf"), ("所有文件", "*.*")])
                if not out_path:
                    return
                # 单文件模式：self._diag 结构为 {fname: {dedup_details:[...],...}}，需嵌套提取
                _single_diag = next(iter(self._diag.values()), {}) if self._diag else {}
                generate_annotation_dxf(self._profiles, self._last_dxf, out_path,
                                        dedup_details=_single_diag.get('dedup_details'),
                                        dxf_version=dxf_ver)
                self._annotation_paths[self._last_dxf] = out_path   # 记录实际路径
                n_err = sum(1 for p in self._profiles if p.get('errors'))
                self._set_status(f"✓ 标注已导出 ({dxf_ver}): {os.path.basename(out_path)}", "#27ae60")
        except Exception as e:
            self._set_status(f"❌ 导出失败: {e}", "#e74c3c")

    def _export(self):
        if not self._profiles:
            self._set_status("⚠️ 请先计算", "#e67e22")
            return
        try:
            density = float(self.le_density.get())
        except ValueError:
            self._set_status("❌ 密度值无效", "#e74c3c")
            return

        batch_results = getattr(self, '_batch_results', [])
        is_batch = len(batch_results) > 1

        if is_batch:
            default_name = "批量结果_weight.xlsx"
        else:
            default_name = (os.path.splitext(self._last_dxf)[0] + "_weight.xlsx"
                            if self._last_dxf else "output.xlsx")
        out_path = filedialog.asksaveasfilename(
            title="保存 Excel", initialfile=os.path.basename(default_name),
            defaultextension=".xlsx",
            filetypes=[("Excel 文件", "*.xlsx"), ("所有文件", "*.*")])
        if not out_path:
            return
        try:
            material_name = self.cb_material.get()
            # ── 导出前从 _标注.dxf 补充型材编号 ──
            if batch_results:
                for bfp, fprofiles, _ in batch_results:
                    # 优先用"导出标注"时记录的实际路径，否则 fallback 到同目录查找
                    ann = self._annotation_paths.get(bfp)
                    if not ann or not os.path.exists(ann):
                        ann = os.path.splitext(bfp)[0] + "_标注.dxf"
                    if os.path.exists(ann) and fprofiles:
                        _extract_drawing_numbers(ann, fprofiles, include_anno_layers=True)
            elif self._last_dxf:
                ann = self._annotation_paths.get(self._last_dxf)
                if not ann or not os.path.exists(ann):
                    ann = os.path.splitext(self._last_dxf)[0] + "_标注.dxf"
                if os.path.exists(ann) and self._profiles:
                    _extract_drawing_numbers(ann, self._profiles, include_anno_layers=True)

            export_xlsx(self._profiles, out_path, density, material_name)
            self._set_status(f"✓ Excel 已导出 ({len(self._profiles)} 条): {os.path.basename(out_path)}", "#27ae60")
        except Exception as e:
            self._set_status(f"❌ 导出失败: {e}", "#e74c3c")


def run_profile_weight():
    app = ctk.CTk()
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    app.title(f"型材截面米重计算工具 {APP_VERSION} (CustomTkinter)")
    app.geometry("820x700")
    pw = ProfileWeightApp(app)
    pw.pack(fill="both", expand=True)
    app.mainloop()


def main_cli():
    """命令行入口：有 DXF 参数时做无界面计算/导出，否则启动 GUI。"""
    import argparse
    ap = argparse.ArgumentParser(
        prog="profile_weight.py",
        description="型材截面面积与米重计算（省略参数则启动 GUI）")
    ap.add_argument("dxf", nargs="?", help="DXF 文件路径；省略则启动 GUI")
    ap.add_argument("--material", default="6063 铝合金",
                    help="材料名（见 references/material_density.md），默认 6063 铝合金")
    ap.add_argument("--density", type=float, default=None,
                    help="自定义密度 kg/m3（优先于 --material）")
    ap.add_argument("--export", choices=["xlsx", "csv", "dxf"], default=None,
                    help="导出格式：xlsx / csv / dxf(标注)")
    ap.add_argument("-o", "--output", default=None, help="导出文件路径")
    args = ap.parse_args()

    if not args.dxf:
        run_profile_weight()
        return

    density = args.density
    if density is None:
        if args.material not in MATERIAL_DENSITY:
            sys.stderr.write("未知材料: %s\n可选: %s\n" % (
                args.material, "、".join(MATERIAL_DENSITY)))
            sys.exit(2)
        density = MATERIAL_DENSITY[args.material]

    profiles, lines, diag = run_calculation(args.dxf, density)
    for ln in lines:
        print(ln)
    if not profiles:
        sys.exit(1)

    if args.export:
        out = args.output or (os.path.splitext(args.dxf)[0] + "_weight." + args.export)
        if args.export == "xlsx":
            export_xlsx(profiles, out, density, args.material)
        elif args.export == "csv":
            export_csv(profiles, out, density, args.material)
        elif args.export == "dxf":
            generate_annotation_dxf(profiles, args.dxf, out)
        print("\n已导出: " + out)


if __name__ == "__main__":
    main_cli()
