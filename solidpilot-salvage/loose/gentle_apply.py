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
    try:
        return int(httpx.get(BASE + "/api/tool/state", timeout=5).json().get("stateVersion", 0))
    except Exception:
        return 0

def health():
    try:
        return httpx.get(BASE + "/health", timeout=5).json().get("status")
    except Exception:
        return "DOWN"

def material_for(name):
    n = name.lower()
    if '3030b' in n or '3060b' in n: return ("6063-T6", "SolidWorks Materials")
    if '挡水板' in name:              return ("ABS", "SolidWorks Materials")
    if '螺母座' in name:              return ("6061-T6", "SolidWorks Materials")
    if '丝杆' in name or '滑轨' in name or '滑块' in name: return ("AISI 4340 Steel", "SolidWorks Materials")
    if 'socket head cap screw' in n:  return ("AISI 4340 Steel", "SolidWorks Materials")
    return ("6061-T6", "SolidWorks Materials")

# parts already confirmed OK in run1 (skip re-touching them)
already_ok = set(["X轴-底板-2","1205丝杆螺母座-1","张大头57步进电机56长+闭环-1","主轴抱座浙江省永润机械-1",
                  "前塑料挡水板^装配体1 - 副本-2","后塑料挡水板^装配体1 - 副本-1"])

parts = json.load(open("C:/Users/Zegel/solidpilot-mcp/cnc_unique_parts.json", encoding="utf-8"))
# gentle order: normal desktop parts first, temp/toolbox last (risky ones)
def risk(path):
    if 'AppData\\Local\\Temp' in path or 'solidworks data\\browser' in path: return 1
    return 0
parts = sorted(parts, key=lambda p: (risk(p["path"]), p["name"]))

results = []
for idx, p in enumerate(parts):
    name, path = p["name"], p["path"]
    if name in already_ok:
        continue
    mat, lib = material_for(name)
    sv = cur_sv(); run("open_document", {"file_path": path}, sv); time.sleep(0.4)
    sv = cur_sv(); j = run("set_part_material", {"material_name": mat, "library": lib}, sv)
    if j.get("status") != "COMPLETED":
        time.sleep(0.8); sv = cur_sv(); j = run("set_part_material", {"material_name": mat, "library": lib}, sv)
    sv = cur_sv(); run("save_document", {"file_path": ""}, sv)
    sv = cur_sv(); run("close_document", {"save": False}, sv)
    time.sleep(0.4)
    ok = (j.get("status") == "COMPLETED")
    results.append((name, mat, ok))
    print(f"{'OK ' if ok else 'FAIL'}  {name[:32]:34} -> {mat}")

    # gentle health monitor every 5
    if (idx+1) % 5 == 0:
        h = health()
        print(f"  ...health={h}")
        if h != "UP":
            print("ABORT: execution layer unhealthy"); break

fails = [r for r in results if not r[2]]
print("\n=== SUMMARY ===")
print("processed:", len(results), " ok:", len(results)-len(fails), " fail:", len(fails))
for f in fails: print("  FAIL:", f[0], "->", f[1])
