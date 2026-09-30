import httpx, uuid, json

BASE = "http://localhost:5000"

def run(tool, params, sv):
    body = {"operationId": str(uuid.uuid4()), "tool": tool, "stateVersion": sv, "params": params}
    r = httpx.post(BASE + "/api/tool/execute", json=body, timeout=90)
    j = r.json()
    er = (j.get("error") or {}).get("message") if j.get("error") else ""
    print(f"[{tool}] http={r.status_code} status={j.get('status')} sv={j.get('stateVersion')} {er}")
    return j

def cur_sv():
    return int(httpx.get(BASE + "/api/tool/state").json().get("stateVersion", 0))

part = r"C:\Users\Zegel\Desktop\Hobby\DIY\CNC\缩小导轨丝杆尺寸\三轴\X轴\X轴-底板.SLDPRT"
sv = cur_sv()
j = run("open_document", {"file_path": part}, sv)
sv = cur_sv()
run("set_part_material", {"material_name": "6061 Alloy", "library": "SolidWorks Materials"}, sv)
sv = cur_sv()
run("save_document", {"file_path": ""}, sv)
print("done")
