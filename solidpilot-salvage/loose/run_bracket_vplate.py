import json, uuid, httpx

BASE = "http://localhost:5000"

def run(tool, params, sv):
    body = {"operationId": str(uuid.uuid4()), "tool": tool, "stateVersion": sv, "params": params}
    r = httpx.post(BASE + "/api/tool/execute", json=body, timeout=90)
    j = r.json()
    err = (j.get("error") or {}).get("message") if j.get("error") else ""
    print(f"[{tool}] http={r.status_code} status={j.get('status')} sv={j.get('stateVersion')} {err}")
    return j.get("stateVersion", sv)

# NEMA23 (57 motor) vertical plate: 65 x 68 x 3, pilot O38.2, 4x O5.2 on 47x47 (units m)
W=0.0325; H=0.068; T=0.003
yc=0.040              # motor center y (29mm from top)
Rp=0.0191             # pilot radius O38.2
Rh=0.0026             # O5.2
Hx=0.0235             # 47/2
segs=[
  {"entity_type":"rectangle","x1":-W,"y1":0.0,"x2":W,"y2":H},
  {"entity_type":"circle","cx":0.0,"cy":yc,"radius":Rp},
]
for sx in (-Hx,Hx):
    for sy in (-Hx,Hx):
        segs.append({"entity_type":"circle","cx":sx,"cy":yc+sy,"radius":Rh})

sv=1
sv=run("create_sketch",{"plane":"Front Plane","on_face":False,"face_x":0.0,"face_y":0.0,"face_z":0.0},sv)
sv=run("add_sketch_entities",{"segments":segs},sv)
sv=run("extrude_feature",{"feature_type":"boss","depth":T},sv)
print("DONE sv=",sv)
