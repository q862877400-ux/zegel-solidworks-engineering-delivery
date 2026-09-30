import httpx, uuid, json, time

BASE = "http://localhost:5000"

def run(tool, params, sv):
    body = {"operationId": str(uuid.uuid4()), "tool": tool, "stateVersion": sv, "params": params}
    try:
        r = httpx.post(BASE + "/api/tool/execute", json=body, timeout=60)
        return r.json()
    except Exception as e:
        return {"status": "EXC", "error": {"message": str(e)}}

def cur_sv():
    return int(httpx.get(BASE + "/api/tool/state").json().get("stateVersion", 0))

def material_for(name):
    n = name.lower()
    if '3030b' in n or '3060b' in n: return ("6063 Alloy", "SolidWorks Materials")
    if '挡水板' in name:              return ("ABS", "SolidWorks Materials")
    if '螺母座' in name:              return ("6061 Alloy", "SolidWorks Materials")
    if '丝杆' in name or '滑轨' in name or '滑块' in name: return ("AISI 4340 Steel", "SolidWorks Materials")
    if 'socket head cap screw' in n:  return ("AISI 4340 Steel", "SolidWorks Materials")
    return ("6061 Alloy", "SolidWorks Materials")

parts = json.load(open("C:/Users/Zegel/solidpilot-mcp/cnc_unique_parts.json", encoding="utf-8"))
results=[]
for p in parts:
    name=p["name"]; path=p["path"]
    mat, lib = material_for(name)
    sv=cur_sv(); j1=run("open_document", {"file_path": path}, sv)
    time.sleep(0.3)
    j2=None
    for attempt in range(4):
        sv=cur_sv(); j2=run("set_part_material", {"material_name": mat, "library": lib}, sv)
        if j2.get("status")=="COMPLETED":
            break
        time.sleep(0.6)
    sv=cur_sv(); j3=run("save_document", {"file_path": ""}, sv)
    ok = (j2.get("status")=="COMPLETED")
    results.append((name, mat, "OK" if ok else "FAIL", (j2.get("error") or {}).get("message","") if not ok else ""))
    print(f"{'OK ' if ok else 'FAIL'}  {name[:30]:32} -> {mat}")

fails=[r for r in results if r[2]!="OK"]
print("\n=== SUMMARY ===")
print("total:", len(results), " ok:", len(results)-len(fails), " fail:", len(fails))
for f in fails: print("  FAIL:", f)
