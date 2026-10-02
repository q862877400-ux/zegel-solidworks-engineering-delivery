import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path[:0] = [r"" + _ROOT_S + r"\tools", r"" + _ROOT_S + r"",
                r"" + _ROOT_S + r"\mcp-server", r"" + _ROOT_S + r"\scripts"]
import build_union_map as b
from build_union_sources import _domain, _normalize
import register_capabilities as rc

u = json.loads(Path(r"" + _ROOT_S + r"\tools\union-sources.json").read_text(encoding="utf-8"))
allops = {_normalize(t) for s in u["sources"] for t in (s.get("tools") or [])}
ours = {_normalize(x.name.replace("solidworks_", "").replace("cadstudio_", "")) for x in rc.all_specs()}

print("  DOMAIN_LABELS:", {k: v for k, v in b.DOMAIN_LABELS.items()})

#: ① 会话/文档/文件 域的键
keys = [k for k, v in b.DOMAIN_LABELS.items() if "会话" in str(v) or "文档" in str(v) or "session" in str(k).lower()]
print("  该域候选键:", keys)
for key in keys:
    gap = sorted(o for o in allops if _domain(o) == key and o not in ours)
    print()
    print("  ══ domain=%s ⇒ 缺口 **%d** 个 ══" % (key, len(gap)))
    for i, g in enumerate(gap):
        print("    %2d. %s" % (i + 1, g))
