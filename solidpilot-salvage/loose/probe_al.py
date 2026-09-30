import httpx, uuid

BASE = "http://localhost:5000"
def run(tool, params, sv):
    body = {"operationId": str(uuid.uuid4()), "tool": tool, "stateVersion": sv, "params": params}
    r = httpx.post(BASE + "/api/tool/execute", json=body, timeout=60)
    return r.json().get("status")
def cur_sv():
    return int(httpx.get(BASE + "/api/tool/state").json().get("stateVersion", 0))

libs = ["SolidWorks Materials", "自定义材料", "custom materials", "SolidWorks DIN Materials", "Ican工具箱材质库"]
names = ["6061-T6","6061 Alloy","Aluminum 6061-T6","6063-T6","6063 Alloy","AL6061-T6","6061","Aluminum Alloy","1060 Alloy","Aluminum 1060"]

# ensure part open
sv=cur_sv(); run("open_document", {"file_path": r"C:\Users\Zegel\Desktop\Hobby\DIY\CNC\缩小导轨丝杆尺寸\三轴\X轴\X轴-底板.SLDPRT"}, sv)

for lib in libs:
    found=[]
    for n in names:
        sv=cur_sv()
        if run("set_part_material", {"material_name": n, "library": lib}, sv)=="COMPLETED":
            found.append(n)
    print(f"library '{lib}'  ->  {found if found else '(none)'}")
