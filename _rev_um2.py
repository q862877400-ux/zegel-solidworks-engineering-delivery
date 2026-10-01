import sys, json
sys.path.insert(0, "tools"); sys.path.insert(0, "mcp-server")
import build_union_map as bum
import importlib
ours = bum._our_operations()
data = json.loads(bum.SOURCES.read_text(encoding="utf-8"))
ext = {}
for src in data["sources"]:
    for op in (src.get("operations") or []):
        ext.setdefault(bum.__dict__.get("_domain", None) and op, None)
# 用脚本自己的采集逻辑重建 ext 集合
from build_union_sources import _domain, _normalize
ext = {}
for src in data["sources"]:
    for op in (src.get("operations") or []):
        ext.setdefault(op, None)
extset = set(ext)
u = set(ours) | extset
print("NOW   : ours=%d ext=%d union=%d gap=%d exclusive=%d" %
      (len(ours), len(extset), len(u), len(u - set(ours)), len(set(ours) - extset)))
# 去掉 batch11-16 的 15 个新工具后的状态
new = set()
for i in range(11, 17):
    m = importlib.import_module("tool_specs_batch%d" % i)
    specs = next(getattr(m, n) for n in dir(m) if n.startswith("SPECS_"))
    for s in specs:
        new.add(_normalize(s.name))
print("new ops from batch11-16:", len(new))
ours_old = set(ours) - new
u_old = ours_old | extset
print("BEFORE: ours=%d union=%d gap=%d exclusive=%d" %
      (len(ours_old), len(u_old), len(u_old - ours_old), len(ours_old - extset)))
