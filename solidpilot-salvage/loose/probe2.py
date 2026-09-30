import httpx, uuid, time
BASE="http://localhost:5000"
def run(tool, params, sv):
    body={"operationId":str(uuid.uuid4()),"tool":tool,"stateVersion":sv,"params":params}
    r=httpx.post(BASE+"/api/tool/execute",json=body,timeout=60); return r.json()
def cur_sv():
    return int(httpx.get(BASE+"/api/tool/state",timeout=5).json().get("stateVersion",0))

def probe(path, names):
    sv=cur_sv(); run("open_document",{"file_path":path},sv); time.sleep(0.4)
    for n in names:
        sv=cur_sv(); j=run("set_part_material",{"material_name":n,"library":"SolidWorks Materials"},sv)
        print(f"   {n:24} -> {j.get('status')}")

base=r"C:\Users\Zegel\Desktop\Hobby\DIY\CNC\缩小导轨丝杆尺寸\三轴"
print("=== 钢件 X轴-丝杆 ===")
probe(base+r"\X轴\X轴-丝杆.SLDPRT", ["AISI 304","AISI 304 Steel","AISI 4340 Steel","Alloy Steel","Stainless Steel","AISI 1020 Steel"])
print("=== 铝板 Y轴-底板 ===")
probe(base+r"\Y轴\Y轴-底板.SLDPRT", ["6061-T6","6061","6061 Alloy","Aluminum 6061-T6","5052 Alloy"])
