"""
AlWeight-Python v8.4.0 -- Profile cross-section area & weight per meter calculator

Ported from AlWeight v5.4 AutoLISP (GstarCAD/AutoCAD/ZWCAD)

v8.4.0: Green's theorem ARC area — cross(A,C)+cross(C,B)+r^2*sweep replaces chord+correction
v8.3.0: ARC sweep > 180 deg fix — use entity sweep instead of atan2 for theta
v8.2.0: ARC+LINE cycle-tracing reconstruction (endpoint chaining + DFS + shoelace+bulge)
v8.1.0: ARC+LINE cluster reconstruction (template matching + rasterization fallback)
v8.0.1 fix: effectively_closed gap threshold 0.01→0.1mm, close_if_needed now forces closure

Key improvements over v7.0:
  - EXACT arc area calculation matching AutoCAD's vla-get-Area
    (Shoelace + exact circular arc segment corrections from bulge parameter)
    Previously: ezdxf make_path used Bezier approximation of circular arcs
    Now: mathematically exact, same as AutoCAD's internal calculation

Core algorithm for LWPOLYLINE with bulge arcs:
  1. Shoelace formula on vertex coordinates (straight-line polygon area)
  2. For each bulge arc: exact circular segment correction
     - theta = 4 * atan(|bulge|)  (sweep angle)
     - r = chord / (2 * sin(theta/2))  (radius)
     - segment_area = r^2 * (theta - sin(theta)) / 2
     - correction sign = sign(bulge) * sign(shoelace)

Core logic (same as AW command):
  - Select objects -> find areas -> largest area = outer contour -> rest = holes
  - Net area = outer contour area - sum of hole areas
  - Weight per meter = net_area_mm2 / 1000000 * density_kg_m3

Usage:
  python profile_calc.py <dxf_file> [--density 2700] [--material 6063]
  python profile_calc.py <dxf_file> --export csv [--output report.csv]
  python profile_calc.py --list-materials
"""

import argparse
import csv
import math
import os
import sys
from collections import defaultdict

try:
    import ezdxf
    from ezdxf.path import make_path
    from ezdxf.math import area as ezdxf_area_func
except ImportError:
    print("ERROR: ezdxf not installed. Run: pip install ezdxf")
    sys.exit(1)

# -- Material density table (kg/m3) -----------------------------------------
MATERIAL_DENSITY = {
    # Aluminum alloys
    "6063": 2700.0, "7075": 2810.0, "2024": 2780.0,
    "6061": 2720.0, "5052": 2680.0, "3003": 2730.0, "1100": 2710.0,
    # Steel
    "Q235": 7850.0, "Q345": 7850.0, "304": 7930.0, "316": 7980.0,
    "carbon_steel": 7850.0, "stainless_steel": 7930.0,
    # Copper
    "copper": 8960.0, "brass": 8500.0,
    # Titanium
    "titanium": 4507.0,
    # Generic
    "aluminum": 2700.0, "steel": 7850.0,
}

DEFAULT_MATERIAL = "6063"
DEFAULT_DENSITY = 2700.0


# -- Geometry helpers -------------------------------------------------------

def polygon_area(vertices):
    """Shoelace formula for polygon area. Returns absolute value."""
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
    """Approximate a bulge arc with line segments."""
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

    if dist > 0:
        ux, uy = dx / dist, dy / dist
        if bulge > 0:
            px, py = -uy, ux
        else:
            px, py = uy, -ux
        cx = mid_x + perp_dist * px
        cy = mid_y + perp_dist * py
    else:
        return [start, end]

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
    """Extract vertices from LWPOLYLINE.
    Handles bulge arcs. If close_if_needed=True, forces closure.
    """
    vertices = []
    points = entity.get_points()  # default format: (x, y, sw, ew, bulge)

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

    # Handle last vertex bulge (closing arc for closed polylines)
    if len(points) > 1 and len(points[-1]) > 4:
        last_bulge = float(points[-1][4])
        if last_bulge != 0.0 and (entity.closed or close_if_needed):
            end = (float(points[0][0]), float(points[0][1]))
            arc_pts = bulge_arc_points(vertices[-1] if vertices else start, end, last_bulge, num_segments=16)
            vertices.extend(arc_pts)

    return vertices


def exact_lwpolyline_area(entity, close_if_needed=False):
    """Compute EXACT area of closed LWPOLYLINE matching AutoCAD's vla-get-Area.

    Algorithm: Shoelace formula for straight-line polygon area +
    exact circular arc segment corrections for bulge arcs.

    This produces results identical to AutoCAD's internal calculation,
    because AutoCAD also computes area as: polygon(chord vertices) + arc corrections.
    """
    pts = entity.get_points()  # default format: (x, y, sw, ew, bulge)
    n = len(pts)
    if n < 3:
        return 0.0

    # Extract vertex coordinates and bulges
    vertices = [(float(p[0]), float(p[1])) for p in pts]
    bulges = [float(p[4]) if len(p) > 4 else 0.0 for p in pts]

    # Check if effectively closed (start == end)
    start = vertices[0]
    end = vertices[-1]
    gap = math.sqrt((start[0]-end[0])**2 + (start[1]-end[1])**2)

    # Always treat as closed when entity.closed or close_if_needed
    is_closed = entity.closed or close_if_needed
    if not is_closed:
        return 0.0  # Open polyline can't have closed area

    # Determine if this is an implicit closure (large gap forced closed)
    # For large-gap implicit closures, arc corrections produce phantom area
    # because bulge values were defined for the open-path geometry.
    # Use raw shoelace only — matches AutoCAD AW behavior for these cases.
    is_implicit_close = close_if_needed and not entity.closed and gap > 1.0

    # For truly duplicate start/end (gap < 0.01): remove last vertex
    # (it's a duplicate, shoelace wraps n-1 vertices correctly)
    # For non-trivial gap (including closed=True with gap > 0.01): KEEP all vertices 
    # (closing edge from last->first is a real geometric edge)
    # NOTE: ezdxf does NOT append a duplicate vertex for closed=True polylines,
    # so we must NOT remove the last vertex just because closed=True.
    is_near_duplicate = gap < 0.01
    if is_near_duplicate:
        vertices = vertices[:-1]
        bulges = bulges[:-1]
        n = len(vertices)

    if n < 3:
        return 0.0

    # Number of edges = n (for closed polygon: v_i -> v_{(i+1)%n})
    num_edges = n

    # Shoelace signed area (positive for CCW traversal, negative for CW)
    shoelace = 0.0
    for i in range(num_edges):
        j = (i + 1) % n
        shoelace += vertices[i][0] * vertices[j][1]
        shoelace -= vertices[j][0] * vertices[i][1]
    shoelace /= 2.0

    # Skip arc correction for implicit closures with large gap
    # Raw shoelace matches AutoCAD's AW tool for these cases
    if is_implicit_close:
        return abs(shoelace)

    # Arc corrections for each bulge arc
    # Each bulge b_i at vertex i defines a circular arc from v_i to v_{(i+1)%n}
    # The arc replaces the straight chord, adding/subtracting area
    total_correction = 0.0
    shoelace_sign = 1.0 if shoelace >= 0 else -1.0

    for i in range(num_edges):
        b = bulges[i]
        if abs(b) < 1e-10:
            continue

        j = (i + 1) % n
        x1, y1 = vertices[i]
        x2, y2 = vertices[j]

        # Chord length (straight line from vertex i to vertex j)
        chord = math.sqrt((x2-x1)**2 + (y2-y1)**2)
        if chord < 1e-10:
            continue

        # Sweep angle from bulge: theta = 4 * atan(|b|)
        theta = 4.0 * math.atan(abs(b))
        if theta < 1e-10 or theta > 2*math.pi - 1e-10:
            continue

        # Radius from chord length and sweep angle
        sin_half = math.sin(theta / 2.0)
        if abs(sin_half) < 1e-10:
            continue
        r = chord / (2.0 * sin_half)

        # Circular segment area (area between chord and arc)
        # This is the exact area difference that the arc adds/subtracts
        # segment_area = r^2 * (theta - sin(theta)) / 2
        segment_area = r**2 * (theta - math.sin(theta)) / 2.0

        # Sign of correction:
        # The correction is simply copysign(segment_area, bulge).
        # - Positive bulge: arc goes CCW (left of chord) → correction = +segment_area
        # - Negative bulge: arc goes CW (right of chord) → correction = -segment_area
        # This works for both CCW and CW polygons because:
        # - For CCW (shoelace > 0): positive bulge on interior side ADDS area ✓
        # - For CW (shoelace < 0): negative bulge on interior side makes signed MORE negative → abs increases ✓
        correction = math.copysign(segment_area, b)
        total_correction += correction

    # Exact signed area
    exact_signed = shoelace + total_correction
    return abs(exact_signed)


def exact_combined_pair_area(entity_a, entity_b):
    """Compute EXACT area of two open polylines combined into a closed contour.
    Uses Shoelace + exact arc corrections from both polylines' bulge parameters.
    Matching AutoCAD's vla-get-Area precision.
    """
    pts_a = entity_a.get_points()
    pts_b = entity_b.get_points()

    verts_a = [(float(p[0]), float(p[1])) for p in pts_a]
    bulges_a = [float(p[4]) if len(p) > 4 else 0.0 for p in pts_a]

    verts_b = [(float(p[0]), float(p[1])) for p in pts_b]
    bulges_b = [float(p[4]) if len(p) > 4 else 0.0 for p in pts_b]

    tol = 0.01

    # Determine connection pattern and build combined polygon
    end_a = verts_a[-1]
    start_b = verts_b[0]
    end_b = verts_b[-1]
    start_a = verts_a[0]

    m1 = abs(end_a[0]-start_b[0]) < tol and abs(end_a[1]-start_b[1]) < tol
    m2 = abs(end_b[0]-start_a[0]) < tol and abs(end_b[1]-start_a[1]) < tol
    m3 = abs(start_a[0]-start_b[0]) < tol and abs(start_a[1]-start_b[1]) < tol
    m4 = abs(end_a[0]-end_b[0]) < tol and abs(end_a[1]-end_b[1]) < tol

    if m1 and m2:
        # A connects to B: path a_0->...->a_n->b_0->...->b_m->back to a_0
        combined = list(verts_a)
        if m1:  # a_end == b_start, skip duplicate
            combined.extend(verts_b[1:])
        else:
            combined.extend(verts_b)
    elif m3 and m4:
        # Same-start AND same-end: need to reverse B
        # Path: a_0->...->a_n->b_m->...->b_0->back to a_0
        reversed_b = list(reversed(verts_b))
        reversed_bulges_b = list(reversed(bulges_b))
        combined = list(verts_a)
        if abs(end_a[0]-end_b[0]) < tol and abs(end_a[1]-end_b[1]) < tol:
            combined.extend(reversed_b[1:])  # skip duplicate
        else:
            combined.extend(reversed_b)
        bulges_b = reversed_bulges_b
    else:
        return 0.0

    n = len(combined)
    if n < 3:
        return 0.0

    # Shoelace signed area
    shoelace = 0.0
    for i in range(n):
        j = (i + 1) % n
        shoelace += combined[i][0] * combined[j][1]
        shoelace -= combined[j][0] * combined[i][1]
    shoelace /= 2.0

    shoelace_sign = 1.0 if shoelace >= 0 else -1.0
    total_correction = 0.0

    # Helper: compute arc correction for one edge
    def arc_correction(v1, v2, bulge_val):
        if abs(bulge_val) < 1e-10:
            return 0.0
        chord = math.sqrt((v2[0]-v1[0])**2 + (v2[1]-v1[1])**2)
        if chord < 1e-10:
            return 0.0
        theta = 4.0 * math.atan(abs(bulge_val))
        if theta < 1e-10 or theta > 2*math.pi - 1e-10:
            return 0.0
        sin_half = math.sin(theta / 2.0)
        if abs(sin_half) < 1e-10:
            return 0.0
        r = chord / (2.0 * sin_half)
        segment_area = r**2 * (theta - math.sin(theta)) / 2.0
        return math.copysign(segment_area, bulge_val)

    # Arc corrections from polyline A (edges within A)
    for i in range(len(verts_a) - 1):
        total_correction += arc_correction(verts_a[i], verts_a[i+1], bulges_a[i])

    # Arc corrections from polyline B (edges within B)
    for i in range(len(verts_b) - 1):
        total_correction += arc_correction(verts_b[i], verts_b[i+1], bulges_b[i])

    exact_signed = shoelace + total_correction
    return abs(exact_signed)


def point_in_polygon(point, polygon):
    """Ray casting algorithm to check if point is inside polygon."""
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


# -- DXF parsing (comprehensive) -------------------------------------------

def rebuild_contour_from_arc_line(arcs, lines, snap_tol=0.001, debug=False):
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
    # Also store original direction node IDs per segment for sign checking
    seg_orig_nodes = {}  # seg_idx -> (n1, n2) where n1→n2 is the segment's p1→p2 direction
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
                        if debug:
                            print(f"    ARC r={r:.1f} sweep={abs(cycle_sweep)*180/math.pi:.1f}° "
                                  f"dir={'FWD' if cycle_sweep>0 else 'REV'}")
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


def get_all_contours_from_dxf(filepath):
    """Parse DXF and extract ALL closed contours:
    - closed LWPOLYLINE (closed=True)
    - effectively closed LWPOLYLINE (start==end, closed=False)
    - open LWPOLYLINE pairs that can be combined into closed contours
    - CIRCLE, ELLIPSE, closed POLYLINE, HATCH, SOLID
    - ARC+LINE clusters (v8.1: reconstruct closed contours from segments)

    Returns list of dicts with area, bbox, center, vertices, etc.
    """
    try:
        doc = ezdxf.readfile(filepath)
    except Exception as e:
        print(f"ERROR reading DXF: {e}")
        return []

    msp = doc.modelspace()
    contours = []

    # Track which entities are already consumed by a contour
    consumed_handles = set()

    # Phase 1: Collect all LWPOLYLINE entities
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
            # Use EXACT area calculation matching AutoCAD's vla-get-Area
            area = exact_lwpolyline_area(entity)
            verts = extract_lwpolyline_vertices(entity)
            xs = [p[0] for p in pts_raw]
            ys = [p[1] for p in pts_raw]
            bbox = (min(xs), min(ys), max(xs), max(ys))
            center = ((bbox[0]+bbox[2])/2, (bbox[1]+bbox[3])/2)
            consumed_handles.add(handle)
            closed_polys.append({
                'source': 'closed_lwpoly',
                'type': 'LWPOLYLINE(closed)',
                'area': area, 'layer': layer, 'handle': handle,
                'bbox': bbox, 'center': center,
                'vertices': verts, 'npts': len(pts_raw),
                'entity': entity,
            })
        else:
            if len(pts_raw) < 2:
                continue
            start = pts_raw[0]
            end = pts_raw[-1]
            gap = math.sqrt((start[0]-end[0])**2 + (start[1]-end[1])**2)

            # Always compute closed area (shoelace with closing edge)
            # Only skip if area is zero (degenerate)
            area = exact_lwpolyline_area(entity, close_if_needed=True)
            if area > 0.001:
                verts_full = extract_lwpolyline_vertices(entity, close_if_needed=True)
                xs = [v[0] for v in verts_full]
                ys = [v[1] for v in verts_full]
                bbox = (min(xs), min(ys), max(xs), max(ys))
                center = ((bbox[0]+bbox[2])/2, (bbox[1]+bbox[3])/2)
                consumed_handles.add(handle)

                if gap < 0.1:
                    effectively_closed.append({
                        'source': 'effectively_closed',
                        'type': 'LWPOLYLINE(eff_closed)',
                        'area': area, 'layer': layer, 'handle': handle,
                        'bbox': bbox, 'center': center,
                        'vertices': verts_full, 'npts': len(pts_raw),
                        'gap': gap,
                    })
                else:
                    effectively_closed.append({
                        'source': 'implicit_closed',
                        'type': 'LWPOLYLINE(impl_closed)',
                        'area': area, 'layer': layer, 'handle': handle,
                        'bbox': bbox, 'center': center,
                        'vertices': verts_full, 'npts': len(pts_raw),
                        'gap': gap,
                    })
            else:
                # Area is zero or degenerate, skip
                pass

    # Phase 2: Combine open polyline pairs that share endpoints
    combined_pairs = []
    used_indices = set()

    for i, a in enumerate(open_polys):
        if i in used_indices:
            continue
        for j, b in enumerate(open_polys):
            if j in used_indices or j <= i:
                continue
            tol = 0.01
            m1 = abs(a['start'][0]-b['end'][0]) < tol and abs(a['start'][1]-b['end'][1]) < tol
            m2 = abs(a['end'][0]-b['start'][0]) < tol and abs(a['end'][1]-b['start'][1]) < tol
            m3 = abs(a['start'][0]-b['start'][0]) < tol and abs(a['start'][1]-b['start'][1]) < tol
            m4 = abs(a['end'][0]-b['end'][0]) < tol and abs(a['end'][1]-b['end'][1]) < tol

            if (m1 and m2) or (m3 and m4):
                # Use EXACT area calculation for combined pair (matching AutoCAD)
                area = exact_combined_pair_area(a['entity'], b['entity'])
                verts_a = extract_lwpolyline_vertices(a['entity'], close_if_needed=False)
                verts_b = extract_lwpolyline_vertices(b['entity'], close_if_needed=False)
                combined_verts = verts_a + verts_b

                xs = [v[0] for v in combined_verts]
                ys = [v[1] for v in combined_verts]
                bbox = (min(xs), min(ys), max(xs), max(ys))
                center = ((bbox[0]+bbox[2])/2, (bbox[1]+bbox[3])/2)

                combined_pairs.append({
                    'source': 'combined_pair',
                    'type': 'LWPOLYLINE(combined)',
                    'area': area,
                    'layer': a['layer'],
                    'handle': a['handle'] + '+' + b['handle'],
                    'bbox': bbox, 'center': center,
                    'vertices': combined_verts,
                    'npts': a['npts'] + b['npts'],
                    'pair_handles': (a['handle'], b['handle']),
                })
                used_indices.add(i)
                used_indices.add(j)
                break

    # Phase 3: Other entity types (CIRCLE, ELLIPSE, HATCH, etc.)
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
            bbox = (cx-r, cy-r, cx+r, cy+r)

        elif dxf_type == 'ELLIPSE':
            major = entity.dxf.major_axis
            ratio = entity.dxf.ratio if hasattr(entity.dxf, 'ratio') else 1.0
            major_len = math.sqrt(major[0]**2 + major[1]**2 + major[2]**2)
            minor_len = major_len * ratio
            start_p = entity.dxf.start_param if hasattr(entity.dxf, 'start_param') else 0
            end_p = entity.dxf.end_param if hasattr(entity.dxf, 'end_param') else 2*math.pi
            if abs(end_p - start_p - 2*math.pi) < 0.01:
                area = ellipse_area(major_len, minor_len)
                cx = float(entity.dxf.center.x)
                cy = float(entity.dxf.center.y)
                bbox = (cx-major_len, cy-minor_len, cx+major_len, cy+minor_len)

        elif dxf_type == 'HATCH':
            try:
                hatch_area = 0.0
                for path in entity.paths:
                    sub_area = 0.0
                    # DXF: path_type_flags bit 0 (value 1) = external/outer
                    # Paths without bit 0 set are holes (internal boundaries)
                    is_external = bool(path.path_type_flags & 1) if hasattr(path, 'path_type_flags') else True
                    is_hole = not is_external

                    # Handle PolylinePath (vertices with bulge values)
                    if hasattr(path, 'vertices'):
                        verts_raw = list(path.vertices)  # list of (x, y, bulge)
                        n_v = len(verts_raw)
                        if n_v >= 3:
                            # Compute exact area: shoelace + arc corrections
                            shoelace = 0.0
                            for j in range(n_v):
                                k = (j + 1) % n_v
                                shoelace += verts_raw[j][0] * verts_raw[k][1]
                                shoelace -= verts_raw[k][0] * verts_raw[j][1]
                            shoelace /= 2.0

                            # Arc corrections from bulge values
                            arc_correction = 0.0
                            for j in range(n_v):
                                b = verts_raw[j][2]
                                if abs(b) < 1e-10:
                                    continue
                                k = (j + 1) % n_v
                                x1, y1 = verts_raw[j][0], verts_raw[j][1]
                                x2, y2 = verts_raw[k][0], verts_raw[k][1]
                                chord = math.sqrt((x2-x1)**2 + (y2-y1)**2)
                                if chord < 1e-10:
                                    continue
                                theta = 4.0 * math.atan(abs(b))
                                if theta < 1e-10 or theta > 2*math.pi - 1e-10:
                                    continue
                                sin_half = math.sin(theta / 2.0)
                                if abs(sin_half) < 1e-10:
                                    continue
                                r = chord / (2.0 * sin_half)
                                segment_area = r**2 * (theta - math.sin(theta)) / 2.0
                                arc_correction += math.copysign(segment_area, b)
                            sub_area = abs(shoelace + arc_correction)

                            # Extract vertices for bbox/center
                            sub_verts = []
                            for j in range(n_v):
                                x1, y1 = verts_raw[j][0], verts_raw[j][1]
                                b = verts_raw[j][2]
                                k = (j + 1) % n_v
                                x2, y2 = verts_raw[k][0], verts_raw[k][1]
                                if abs(b) > 1e-10:
                                    dx, dy = x2 - x1, y2 - y1
                                    chord = math.sqrt(dx*dx + dy*dy)
                                    if chord > 1e-10:
                                        theta = 4.0 * math.atan(abs(b))
                                        sin_half = math.sin(theta / 2.0)
                                        if abs(sin_half) > 1e-10:
                                            r = chord / (2.0 * sin_half)
                                            mid_x, mid_y = (x1+x2)/2, (y1+y2)/2
                                            perp_dist = r * math.cos(theta / 2.0)
                                            if chord > 0:
                                                ux, uy = dx/chord, dy/chord
                                                if b > 0:
                                                    px, py = -uy, ux
                                                else:
                                                    px, py = uy, -ux
                                                cx = mid_x + perp_dist * px
                                                cy = mid_y + perp_dist * py
                                                start_a = math.atan2(y1-cy, x1-cx)
                                                end_a = math.atan2(y2-cy, x2-cx)
                                                if b > 0:
                                                    if end_a <= start_a:
                                                        end_a += 2*math.pi
                                                else:
                                                    if end_a >= start_a:
                                                        end_a -= 2*math.pi
                                                for m in range(16):
                                                    t = m / 16.0
                                                    a = start_a + t * (end_a - start_a)
                                                    sub_verts.append((cx + r*math.cos(a), cy + r*math.sin(a)))
                                            else:
                                                sub_verts.append((x1, y1))
                                else:
                                    sub_verts.append((x1, y1))
                            if sub_verts:
                                vertices_raw = sub_verts
                            else:
                                vertices_raw = [(v[0], v[1]) for v in verts_raw]

                    # Handle BoundaryPath (line/arc edges)
                    elif hasattr(path, 'edges'):
                        sub_verts = []
                        for edge in path.edges:
                            if edge.EDGE_TYPE == 'LineEdge':
                                sub_verts.append((float(edge.start[0]), float(edge.start[1])))
                            elif edge.EDGE_TYPE == 'ArcEdge':
                                n_seg = 16
                                for k in range(n_seg + 1):
                                    t_rad = edge.start_angle + (edge.end_angle - edge.start_angle) * k / n_seg
                                    px = float(edge.center[0]) + float(edge.radius) * math.cos(t_rad)
                                    py = float(edge.center[1]) + float(edge.radius) * math.sin(t_rad)
                                    sub_verts.append((px, py))
                        if len(sub_verts) >= 3:
                            sub_area = polygon_area(sub_verts)
                            vertices_raw = sub_verts
                        else:
                            continue
                    else:
                        continue

                    if is_hole:
                        hatch_area -= sub_area
                        is_hole_outmost = True
                    else:
                        hatch_area += sub_area

                area = abs(hatch_area) if hatch_area != 0 else 0
                shape_type = 'HATCH'
                consumed_handles.add(handle)
            except Exception:
                area = 0.0
                shape_type = 'HATCH(unparsed)'

        elif dxf_type == 'POLYLINE':
            if entity.is_2d_polyline and entity.closed:
                vertices_raw = []
                for vtx in entity.vertices:
                    loc = vtx.dxf.location
                    vertices_raw.append((float(loc.x), float(loc.y)))
                area = polygon_area(vertices_raw)
                shape_type = 'POLYLINE2D(closed)'

        elif dxf_type == 'SOLID':
            try:
                pts = []
                for attr in ['corner1', 'corner2', 'corner3', 'corner4']:
                    if hasattr(entity.dxf, attr):
                        p = entity.dxf.__getattr__(attr)
                        pts.append((float(p[0]), float(p[1])))
                if len(pts) >= 3:
                    area = polygon_area(pts)
            except Exception:
                area = 0.0

        if area > 0:
            if bbox is None and vertices_raw and len(vertices_raw) >= 3:
                xs = [v[0] for v in vertices_raw]
                ys = [v[1] for v in vertices_raw]
                bbox = (min(xs), min(ys), max(xs), max(ys))

            center = ((bbox[0]+bbox[2])/2, (bbox[1]+bbox[3])/2) if bbox else None
            other_shapes.append({
                'source': 'other_entity',
                'type': shape_type,
                'area': area, 'layer': layer, 'handle': handle,
                'bbox': bbox, 'center': center,
                'vertices': vertices_raw,
            })

    # Merge all contours
    all_contours = closed_polys + effectively_closed + combined_pairs + other_shapes

    # --- Phase 4: ARC+LINE cycle-tracing reconstruction (v8.2) ---
    # Reconstruct closed contours from remaining ARC+LINE entities.
    # Pure geometric approach: endpoint chaining → cycle detection → shoelace+bulge area.
    # No template matching — works even when no LWPOLYLINE/HATCH reference exists.
    phase4_arcs = []
    phase4_lines = []
    
    for entity in msp:
        t = entity.dxftype()
        h = entity.dxf.handle
        if h in consumed_handles:
            continue
        
        if t == 'ARC':
            c = entity.dxf.center
            r = entity.dxf.radius
            sa = math.radians(float(entity.dxf.start_angle))
            ea = math.radians(float(entity.dxf.end_angle))
            sx = c.x + r * math.cos(sa); sy = c.y + r * math.sin(sa)
            ex = c.x + r * math.cos(ea); ey = c.y + r * math.sin(ea)
            phase4_arcs.append((float(sx), float(sy), float(ex), float(ey),
                               float(c.x), float(c.y), float(r), sa, ea, h))
        elif t == 'LINE':
            x1 = float(entity.dxf.start.x)
            y1 = float(entity.dxf.start.y)
            x2 = float(entity.dxf.end.x)
            y2 = float(entity.dxf.end.y)
            if abs(x2-x1) > 1e-8 or abs(y2-y1) > 1e-8:
                phase4_lines.append((x1, y1, x2, y2, h))
    
    if phase4_arcs or phase4_lines:
        # Build arc/line tuples for the generic cycle-tracer
        ar = [(sx, sy, ex, ey, cx, cy, r, sa, ea) for sx, sy, ex, ey, cx, cy, r, sa, ea, _ in phase4_arcs]
        li = [(x1, y1, x2, y2) for x1, y1, x2, y2, _ in phase4_lines]
        
        rebuilt = rebuild_contour_from_arc_line(ar, li)
        
        for rc in rebuilt:
            # Mark all segment handles as consumed
            for *_, h in phase4_arcs:
                consumed_handles.add(h)
            for *_, h in phase4_lines:
                consumed_handles.add(h)
            
            all_contours.append({
                'source': 'reconstructed',
                'type': 'ARC+LINE(cycle_traced)',
                'area': rc['area'],
                'layer': '0',
                'handle': 'ARC+LINE',
                'bbox': rc['bbox'],
                'center': rc['center'],
                'vertices': rc['vertices'],
                'n_segments': rc['n_segments'],
            })

    # Filter out zero/negative area
    all_contours = [c for c in all_contours if c['area'] > 0.1]

    return all_contours


# -- Spatial grouping (geometry-based) -------------------------------------

def point_inside_contour(point, contour):
    """Check if a point is geometrically inside a contour's polygon.
    Uses point_in_polygon with the contour's vertices.
    For open polylines (implicit_closed), point_in_polygon is unreliable
    because the closing edge is a diagonal that doesn't exist in reality.
    In that case, bbox containment is used as fallback.
    """
    # First check bbox containment (fast pre-filter)
    bbox = contour.get('bbox')
    if not bbox:
        return False
    if not (bbox[0] <= point[0] <= bbox[2] and bbox[1] <= point[1] <= bbox[3]):
        return False

    # Try point_in_polygon for reliable results on closed contours
    verts = contour.get('vertices')
    source = contour.get('source', '')
    if verts and len(verts) >= 3:
        result = point_in_polygon(point, verts)
        if result:
            return True
        # point_in_polygon returned False but bbox contains the point.
        # For implicit_closed (open polylines with large gap), the
        # closing edge is a phantom diagonal that causes false negatives.
        # Trust bbox containment in this case.
        if source == 'implicit_closed':
            return True
        return False
    # Fallback: bbox containment already checked above
    return True


def group_contours_by_profiles(contours):
    """Group contours into profiles using geometric containment.

    Strategy (mimicking AW manual selection):
    1. Sort all contours by area (descending) - largest first
    2. For each contour, find which larger contour it's geometrically inside
    3. Contours that are inside the same outer contour form one profile group
    4. Standalone contours (not inside anything) form their own group
    5. Sort final groups by position (left to right) for clear numbering

    This is closer to how AW works: select objects, largest = outer,
    everything inside it = holes.
    """
    if len(contours) <= 1:
        return [contours] if contours else []

    # Sort by area descending
    sorted_contours = sorted(contours, key=lambda c: c['area'], reverse=True)

    # Build containment tree: each contour knows which larger contour contains it
    # parent[i] = index of the contour that geometrically contains contour i
    # -1 means it's a standalone top-level contour
    containment_parent = [-1] * len(sorted_contours)

    for i in range(len(sorted_contours)):
        ci = sorted_contours[i]
        if ci.get('center') is None:
            continue
        # Find the smallest larger contour that contains ci
        # (smallest = most specific parent)
        best_parent = -1
        best_parent_area = float('inf')
        for j in range(i):  # Only check larger contours (j < i means larger area)
            cj = sorted_contours[j]
            # Check if ci's center is inside cj
            if point_inside_contour(ci['center'], cj):
                if cj['area'] < best_parent_area:
                    best_parent = j
                    best_parent_area = cj['area']
            # Also check bbox containment: if ci's bbox is fully inside cj's bbox,
            # it's almost certainly a hole (handles open polylines where center
            # point test fails due to phantom closing edge)
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

    # Build groups by walking containment tree to root ancestors.
    # This ensures each contour belongs to EXACTLY ONE group, fixing the
    # bug where a contour appeared as both a parent and a child in
    # different groups (multi-level nesting creating duplicate assignments).
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

    # Convert to list of groups
    final_groups = list(groups.values())

    # CRITICAL: Sort groups by leftmost center x-coordinate (left to right)
    # This makes the numbering match the visual layout in the drawing
    def group_position_x(group):
        centers_x = [c['center'][0] for c in group if c.get('center')]
        if centers_x:
            return min(centers_x)
        return 0

    final_groups.sort(key=group_position_x)

    return final_groups


# -- Net area calculation (AW logic) ----------------------------------------

def get_net_area_for_group(group):
    """Calculate net area for a profile group using AW logic:
    Largest area = outer contour, all others that are INSIDE outer = holes.
    Shapes NOT inside outer are separate profiles (not holes).

    Returns: (net_area, outer, holes, separate_shapes)
    """
    if len(group) == 0:
        return None, None, [], []

    if len(group) == 1:
        return group[0]['area'], group[0], [], []

    # Sort by area descending
    sorted_shapes = sorted(group, key=lambda s: s['area'], reverse=True)
    outer = sorted_shapes[0]

    # Since grouping now uses geometric containment, all shapes in a group
    # are either the outer or holes inside the outer.
    # No "separate" shapes should exist within a properly grouped profile.
    holes = []
    separate = []

    # Determine which shapes are holes (geometrically inside outer)
    for s in sorted_shapes[1:]:
        if s.get('center') and point_inside_contour(s['center'], outer):
            holes.append(s)
        else:
            # Edge case: shape is in the group but not inside outer
            # This shouldn't happen with proper containment grouping,
            # but if it does, treat it as a hole anyway (it was grouped
            # together for a reason)
            holes.append(s)

    net_area = outer['area']
    for h in holes:
        net_area -= h['area']

    return net_area, outer, holes, separate


# -- Weight calculation -----------------------------------------------------

def calc_weight(net_area_mm2, density_kg_m3):
    return net_area_mm2 / 1000000.0 * density_kg_m3


def fmt_value(v, precision):
    return f"{abs(v):.{precision}f}"


def fmt_signed(v, precision):
    if v < 0:
        return f"-{abs(v):.{precision}f}"
    return f"{v:.{precision}f}"


# -- Export -----------------------------------------------------------------

def export_profiles_csv(profiles, output_path, density, material):
    with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['Profile#', 'Position(X)', 'NetArea(mm2)', 'Density(kg/m3)',
                         'Material', 'Weight(kg/m)', 'Weight(g/m)',
                         'OuterArea(mm2)', 'HoleAreas(mm2)', 'Shapes', 'SourceType'])

        for i, p in enumerate(profiles, 1):
            net = p['net_area']
            weight_kg = calc_weight(net, density) if net and net > 0 else 0
            weight_g = weight_kg * 1000
            outer_area = p['outer']['area'] if p.get('outer') else 0
            hole_areas = '+'.join([fmt_value(h['area'], 2) for h in p.get('holes', [])])
            shape_count = 1 + len(p.get('holes', []))
            source = p['outer'].get('source', '?') if p.get('outer') else '?'
            # Position: leftmost x coordinate of the profile
            pos_x = min([c['center'][0] for c in p['shapes'] if c.get('center')], default=0)

            writer.writerow([
                i,
                fmt_value(pos_x, 1),
                fmt_value(net, 2) if net else 'N/A',
                fmt_value(density, 1),
                material,
                fmt_value(weight_kg, 4),
                fmt_value(weight_g, 2),
                fmt_value(outer_area, 2),
                hole_areas,
                shape_count,
                source,
            ])
    return output_path


# -- Main -------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description='AlWeight-Python v8.4: Profile cross-section area & weight per meter')
    parser.add_argument('dxf_file', nargs='?', help='DXF file path')
    parser.add_argument('--density', type=float, default=None,
                        help='Material density in kg/m3 (overrides --material)')
    parser.add_argument('--material', default=DEFAULT_MATERIAL,
                        help=f'Material name (default: {DEFAULT_MATERIAL})')
    parser.add_argument('--export', choices=['csv'], help='Export format')
    parser.add_argument('--output', default=None, help='Output file path')
    parser.add_argument('--list-materials', action='store_true',
                        help='List available material densities')
    parser.add_argument('--filter-layer', default=None,
                        help='Only calculate shapes on specified layer')
    parser.add_argument('--all-shapes', action='store_true',
                        help='Show each shape individually')
    parser.add_argument('--no-group', action='store_true',
                        help='Disable auto-grouping; treat all shapes as one profile')
    parser.add_argument('--debug', action='store_true',
                        help='Show detailed grouping info')

    args = parser.parse_args()

    if args.list_materials:
        print("\nAvailable material densities (kg/m3):")
        print("-" * 40)
        for name, d in sorted(MATERIAL_DENSITY.items(), key=lambda x: x[1]):
            print(f"  {name:20s} = {d:.0f}")
        print()
        return

    if not args.dxf_file:
        parser.print_help()
        print("\nERROR: DXF file path required.")
        sys.exit(1)

    dxf_path = args.dxf_file
    if not os.path.exists(dxf_path):
        print(f"ERROR: File not found: {dxf_path}")
        sys.exit(1)

    # Resolve density
    if args.density is not None:
        density = args.density
        material = f"custom({density})"
    else:
        material_input = args.material.replace("-", "_")
        lookup_map = {k.lower(): k for k in MATERIAL_DENSITY}
        material = lookup_map.get(material_input.lower(), None)
        if material is None:
            print(f"WARNING: Material '{args.material}' not found. Using default {DEFAULT_MATERIAL}={DEFAULT_DENSITY}")
            material = DEFAULT_MATERIAL
        density = MATERIAL_DENSITY[material]

    print(f"\n{'='*50}")
    print(f"  AlWeight-Python v8.4")
    print(f"  File:     {dxf_path}")
    print(f"  Material: {material}  Density: {density} kg/m3")
    print(f"{'='*50}")

    # Parse DXF
    contours = get_all_contours_from_dxf(dxf_path)

    if args.filter_layer:
        contours = [c for c in contours if c['layer'] == args.filter_layer]

    print(f"\n  Found {len(contours)} contour(s)")

    # Group contours into profiles
    if args.no_group or len(contours) <= 1:
        groups = [contours]
    else:
        groups = group_contours_by_profiles(contours)

    if args.debug:
        print(f"\n  -- DEBUG: {len(groups)} groups (sorted left-to-right) --")
        for gi, g in enumerate(groups):
            pos_x = min([c['center'][0] for c in g if c.get('center')], default=0)
            print(f"    Group {gi+1}: {len(g)} contours, position_x={pos_x:.1f}")
            for c in g:
                center_str = f"({c['center'][0]:.1f},{c['center'][1]:.1f})" if c.get('center') else "?"
                print(f"      [{c['source']:20s}] area={fmt_value(c['area'], 2)} center={center_str}")

    print(f"\n  Grouped into {len(groups)} profile(s)")

    # Calculate per profile
    profiles = []
    for gi, group in enumerate(groups):
        net_area, outer, holes, separate = get_net_area_for_group(group)

        profile = {
            'net_area': net_area,
            'outer': outer,
            'holes': holes,
            'separate': separate,
            'shapes': group,
        }
        profiles.append(profile)

        weight_kg = calc_weight(net_area, density) if net_area and net_area > 0 else 0
        weight_g = weight_kg * 1000.0

        # Position info for identification
        pos_x = min([c['center'][0] for c in group if c.get('center')], default=0)

        print(f"\n  --- Profile #{gi + 1} (x={pos_x:.1f}) ---")

        if outer:
            center_str = f"({outer['center'][0]:.1f},{outer['center'][1]:.1f})" if outer.get('center') else "?"
            print(f"  Outer:    {fmt_value(outer['area'], 2)} mm2 [{outer['source']}] center={center_str}")
        for h in holes:
            center_str = f"({h['center'][0]:.1f},{h['center'][1]:.1f})" if h.get('center') else "?"
            print(f"  Hole:     {fmt_value(h['area'], 2)} mm2 [{h['source']}] center={center_str}")

        if net_area is not None and net_area > 0:
            print(f"  NetArea:  {fmt_value(net_area, 2)} mm2")
            print(f"  Weight:   {fmt_value(weight_kg, 4)} kg/m")
            print(f"  Weight:   {fmt_value(weight_g, 2)} g/m")
        elif net_area is not None and net_area <= 0:
            print(f"  WARNING: Net area is negative ({fmt_signed(net_area, 2)} mm2)")
        else:
            print(f"  !! Cannot calculate area !!")

    # Summary (sorted left-to-right, matches visual layout)
    valid_profiles = [p for p in profiles if p['net_area'] is not None and p['net_area'] > 0]
    if valid_profiles:
        print(f"\n  {'='*60}")
        print(f"  SUMMARY: {len(valid_profiles)} profile(s) (left -> right)")
        print(f"  {'='*60}")
        for i, p in enumerate(valid_profiles):
            w = calc_weight(p['net_area'], density)
            pos_x = min([c['center'][0] for c in p['shapes'] if c.get('center')], default=0)
            print(f"  #{i+1}: x={pos_x:.1f} | {fmt_value(p['net_area'], 2)} mm2 = {fmt_value(w, 4)} kg/m ({fmt_value(w*1000, 2)} g/m)")
        print(f"  {'='*60}")

    # Export
    if args.export == 'csv':
        out_path = args.output or os.path.splitext(dxf_path)[0] + '_weight.csv'
        export_profiles_csv(profiles, out_path, density, material)
        print(f"\n  Exported to: {out_path}")

    print()


if __name__ == '__main__':
    main()
