import httpx, uuid, time
BASE="http://localhost:5000"
def run(tool, params, sv):
    body={"operationId":str(uuid.uuid4()),"tool":tool,"stateVersion":sv,"params":params}
    r=httpx.post(BASE+"/api/tool/execute",json=body,timeout=60); return r.json()
def cur_sv():
    return int(httpx.get(BASE+"/api/tool/state",timeout=5).json().get("stateVersion",0))

for name,path,mat in [
  ("X轴-底板", r"C:\Users\Zegel\Desktop\Hobby\DIY\CNC\缩小导轨丝杆尺寸\三轴\X轴\X轴-底板.SLDPRT","6061 Alloy"),
  ("3030B-X1", r"C:\Users\Zegel\Desktop\Hobby\DIY\CNC\缩小导轨丝杆尺寸\三轴\X轴\3030B-X1.SLDPRT","6063 Alloy"),
]:
    sv=cur_sv(); run("open_document",{"file_path":path},sv); time.sleep(0.4)
    sv=cur_sv(); j=run("set_part_material",{"material_name":mat,"library":"SolidWorks Materials"},sv)
    er=(j.get("error") or {}).get("message") if j.get("error") else ""
    print(f"{name}: status={j.get('status')} {er}")
