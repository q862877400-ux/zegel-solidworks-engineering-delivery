import httpx, uuid

BASE = "http://localhost:5000"

def run(tool, params, sv):
    body = {"operationId": str(uuid.uuid4()), "tool": tool, "stateVersion": sv, "params": params}
    r = httpx.post(BASE + "/api/tool/execute", json=body, timeout=60)
    j = r.json()
    return j.get("status")

def cur_sv():
    return int(httpx.get(BASE + "/api/tool/state").json().get("stateVersion", 0))

import os
part = r"C:\Users\Zegel\Desktop\Hobby\DIY\CNC\缩小导轨丝杆尺寸\三轴\X轴\X轴-底板.SLDPRT"
sv = cur_sv()
run("open_document", {"file_path": part}, sv)

candidates = ["Aluminum 6061 Alloy","6061 Alloy","Aluminum 6063 Alloy","6063 Alloy","Aluminum 1060 Alloy",
              "AISI 1045 Steel","AISI 1020 Steel","AISI 1020 Steel (SS)","AISI 304","AISI 304 Steel",
              "Alloy Steel","Stainless Steel","AISI 4340 Steel","ABS","Nylon 6/6","Polycarbonate","Acrylic"]
for name in candidates:
    sv = cur_sv()
    st = run("set_part_material", {"material_name": name, "library": "SolidWorks Materials"}, sv)
    print(f"{'OK ' if st=='COMPLETED' else 'NO '} {name}")
