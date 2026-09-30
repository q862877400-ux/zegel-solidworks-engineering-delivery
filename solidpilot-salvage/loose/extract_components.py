import httpx, uuid, json

BASE = "http://localhost:5000"
sv = int(httpx.get(BASE + "/api/tool/state").json().get("stateVersion", 0))
body = {"operationId": str(uuid.uuid4()), "tool": "analyze_assembly",
        "stateVersion": sv, "params": {"analysis_type": "components"}}
j = httpx.post(BASE + "/api/tool/execute", json=body, timeout=120).json()
feats = j["cadState"]["features"]
if isinstance(feats, list):
    data = json.loads(feats[0]) if feats else {"components": []}
elif isinstance(feats, str):
    data = json.loads(feats)
else:
    data = feats
comps = data.get("components", data if isinstance(data, list) else [])
print("component_count:", data.get("component_count"), " parsed:", len(comps))

# unique parts by source path
uniq = {}
for c in comps:
    p = c.get("path")
    if p and p not in uniq:
        uniq[p] = {"name": c.get("name"), "path": p}
parts = [{"name": v["name"], "path": v["path"]} for v in uniq.values()]
with open("C:/Users/Zegel/solidpilot-mcp/cnc_unique_parts.json", "w", encoding="utf-8") as f:
    json.dump(parts, f, ensure_ascii=False, indent=2)
print("unique parts:", len(parts))
