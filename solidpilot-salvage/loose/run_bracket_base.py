import json, uuid, httpx

BASE = "http://localhost:5000"

def run(tool, params, sv):
    body = {"operationId": str(uuid.uuid4()), "tool": tool, "stateVersion": sv, "params": params}
    r = httpx.post(BASE + "/api/tool/execute", json=body, timeout=90)
    j = r.json()
    err = (j.get("error") or {}).get("message") if j.get("error") else ""
    print(f"[{tool}] http={r.status_code} status={j.get('status')} sv={j.get('stateVersion')} {err}")
    return j.get("stateVersion", sv)

# Base plate cross-section on Front plane: x[-0.0325,0.0325], y[0,0.003]; extrude +Z 0.068
W=0.0325; T=0.003; D=0.068
sv=4
sv=run("create_sketch",{"plane":"Front Plane","on_face":False,"face_x":0.0,"face_y":0.0,"face_z":0.0},sv)
sv=run("add_sketch_entities",{"segments":[
    {"entity_type":"rectangle","x1":-W,"y1":0.0,"x2":W,"y2":T},
]},sv)
sv=run("extrude_feature",{"feature_type":"boss","depth":D},sv)
print("DONE sv=",sv)
