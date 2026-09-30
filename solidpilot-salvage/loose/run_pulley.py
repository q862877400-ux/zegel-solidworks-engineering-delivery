import json, uuid, httpx

BASE = "http://localhost:5000"

def run(tool, params, sv):
    body = {"operationId": str(uuid.uuid4()), "tool": tool, "stateVersion": sv, "params": params}
    r = httpx.post(BASE + "/api/tool/execute", json=body, timeout=90)
    j = r.json()
    err = (j.get("error") or {}).get("message") if j.get("error") else ""
    print(f"[{tool}] http={r.status_code} status={j.get('status')} sv={j.get('stateVersion')} {err}")
    # surface result text if COMPLETED
    if j.get("status") == "COMPLETED":
        print("    ", str(j.get("result"))[:200])
    return j.get("stateVersion", sv)

segments = json.loads(open("C:/Users/Zegel/solidpilot-mcp/gt3_profile_segments.json").read())

sv = 2
sv = run("create_sketch", {"plane": "Front Plane", "on_face": False,
                           "face_x": 0.0, "face_y": 0.0, "face_z": 0.0}, sv)
sv = run("add_sketch_entities", {"segments": segments}, sv)
sv = run("extrude_feature", {"feature_type": "boss", "depth": 0.007}, sv)
print("DONE sv=", sv)
