import json, math, uuid, httpx

BASE = "http://localhost:5000"

def run(tool, params, sv):
    body = {"operationId": str(uuid.uuid4()), "tool": tool, "stateVersion": sv, "params": params}
    r = httpx.post(BASE + "/api/tool/execute", json=body, timeout=90)
    j = r.json()
    err = (j.get("error") or {}).get("message") if j.get("error") else ""
    print(f"[{tool}] http={r.status_code} status={j.get('status')} sv={j.get('stateVersion')} {err}")
    return j.get("stateVersion", sv)

# slot in FACE-11 LOCAL frame: xdir=globalX, ydir=-globalZ. global z in [0.012,0.058] -> local y in [-0.058,-0.012].
r=0.0021; y0=-0.058; y1=-0.012
def slot_segs(cx):
    pts=[]
    for k in range(9):
        a=math.pi + k*(math.pi/8)
        pts.append((cx+r*math.cos(a), (y0+r)+r*math.sin(a)))
    pts.append((cx+r, y1-r))
    for k in range(1,9):
        a=k*(math.pi/8)
        pts.append((cx+r*math.cos(a), (y1-r)+r*math.sin(a)))
    segs=[]
    n=len(pts)
    for j0 in range(n):
        x1,y1p=pts[j0]; x2,y2p=pts[(j0+1)%n]
        segs.append({"entity_type":"line","x1":x1,"y1":y1p,"x2":x2,"y2":y2p})
    return segs

segs = slot_segs(-0.020) + slot_segs(0.020)

sv=int(httpx.get(BASE+"/api/tool/state").json().get("stateVersion",0))
print("current sv=",sv)
sv=run("create_sketch",{"plane":"","on_face":True,"face_index":11,"face_x":0.0,"face_y":0.0,"face_z":0.0},sv)
sv=run("add_sketch_entities",{"segments":segs},sv)
sv=run("extrude_feature",{"feature_type":"cut","through":True,"reverse":False},sv)
print("DONE sv=",sv)
