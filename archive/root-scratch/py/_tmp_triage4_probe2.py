"""临时只读脚本：按 build_union_sources.py 的 param 正则，列出本仓库 MCP 工具名（用完即删）。"""
import json
import re
import urllib.request  # noqa: F401  (unused; kept out of the way)

PAT = re.compile(r"dimension|relation|constraint|equation|global_var|design_table|driving|link_|_scale\b", re.I)

src = open(r"D:\AI\SW\tools\union-sources.json", encoding="utf-8")
data = json.load(src)
print("union param ops:", sorted(set(sum([s["domains"].get("param", []) for s in data["sources"]], []))))

# our tools: read from build_union_map's own extractor result if available, else scan specs
import sys

sys.path.insert(0, r"D:\AI\SW\tools")
try:
    import build_union_map as B  # type: ignore
except Exception as exc:  # pragma: no cover
    print("import build_union_map failed:", exc)
    B = None

if B is not None:
    fn = getattr(B, "_our_tools", None)
    if fn:
        try:
            ours = sorted(fn())
        except TypeError:
            ours = sorted(fn(r"D:\AI\SW"))
        hit = [t for t in ours if PAT.search(t)]
        print("our tools total:", len(ours))
        print("our param-domain tools:", len(hit))
        for t in hit:
            print("   ", t)
