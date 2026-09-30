import httpx, uuid

BASE = "http://localhost:5000"
def run(tool, params, sv):
    body = {"operationId": str(uuid.uuid4()), "tool": tool, "stateVersion": sv, "params": params}
    r = httpx.post(BASE + "/api/tool/execute", json=body, timeout=60)
    j = r.json()
    er = (j.get("error") or {}).get("message") if j.get("error") else ""
    print(f"[{tool}] status={j.get('status')} {er}")
    return j.get("status")
def cur_sv():
    return int(httpx.get(BASE + "/api/tool/state").json().get("stateVersion", 0))

part = r"C:\Users\Zegel\Desktop\Hobby\DIY\CNC\缩小导轨丝杆尺寸\三轴\X轴\X轴-底板.SLDPRT"
sv=cur_sv(); run("open_document", {"file_path": part}, sv)
# confirm aluminum cleanly
for name in ["6061 Alloy", "6063 Alloy", "Aluminum 6061 Alloy"]:
    sv=cur_sv()
    print("->", name, run("set_part_material", {"material_name": name, "library": "SolidWorks Materials"}, sv))
