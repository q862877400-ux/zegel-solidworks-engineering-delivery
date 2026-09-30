import json, math

# ---- 3GT parameters (all mm -> stored as meters) ----
P = 3.0            # pitch mm
N = 20             # teeth
rp = N*P/(2*math.pi)            # 9.5493 pitch radius mm
r_outer = 9.13     # pulley land / OD radius mm (d=18.26)
r_root  = 8.23     # groove root radius mm (groove depth ~0.90mm)
groove_frac = 0.55 # fraction of pitch the groove occupies (land 0.45)
pts_per_tooth = 6

MM = 1e-3

def radius(theta_local_frac):
    """theta in [0,1) across one pitch; return radius (mm)."""
    # land where far from center; groove (rounded) near center
    c = 0.5
    half = groove_frac/2.0
    if abs(theta_local_frac - c) >= half:
        return r_outer
    # rounded groove: 0 at edges, 1 at center
    x = (theta_local_frac - c)/half          # -1..1
    bump = 0.5*(1.0+math.cos(math.pi*x))
    return r_outer - (r_outer - r_root)*bump

pts = []  # (x_m, y_m)
pitch_ang = 2*math.pi/N
# build contour CCW, one tooth at a time, connecting across pitch boundaries
for i in range(N):
    base = i*pitch_ang
    for k in range(pts_per_tooth):
        frac = k/pts_per_tooth                    # 0..(n-1)/n within this tooth
        theta = base + frac*pitch_ang
        r = radius(frac)
        pts.append((r*MM*math.cos(theta), r*MM*math.sin(theta)))
# close the loop back to first point (handled by shared endpoint in segments)

# Build segments: lines connecting consecutive points (closed)
segs = []
np_ = len(pts)
for j in range(np_):
    x1,y1 = pts[j]
    x2,y2 = pts[(j+1)%np_]
    segs.append({"entity_type":"line","x1":x1,"y1":y1,"x2":x2,"y2":y2})

# Bore circle (through hole), radius 3.175mm = 1/4"
bore_r = 3.175*MM
segs.append({"entity_type":"circle","cx":0.0,"cy":0.0,"radius":bore_r})

out = {"pitch_mm":P,"teeth":N,"od_mm":r_outer*2,"root_mm":r_root*2,
       "pc_mm":rp*2,"bore_mm":bore_r*2*1000,"segment_count":len(segs)}
with open("C:/Users/Zegel/solidpilot-mcp/gt3_profile_segments.json","w") as f:
    json.dump(segs,f)
print(json.dumps(out))
