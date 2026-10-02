import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path[:0] = [r"" + _ROOT_S + r"\mcp-server", r"" + _ROOT_S + r""]
import register_capabilities as rc

SRV = Path(r"" + _ROOT_S + r"\mcp-server\server.py").read_text(encoding="utf-8")

print("  ── ① 我们 MCP 里已有的「文档 / 会话 / 导出」工具 ──")
KEY = re.compile(r"document|doc|file|export|session|open|close|new|save|template|rebuild", re.I)
seen = []
for x in rc.all_specs():
    if KEY.search(x.name) or KEY.search(x.doc or ""):
        seen.append(("batch", x.name, x.function))
for m in re.finditer(r'@mcp\.tool\(\s*(?:[^)]*?)name="([^"]+)"', SRV, re.S):
    nm = m.group(1)
    if KEY.search(nm):
        seen.append(("server", nm, ""))
for src, nm, fn in seen:
    print("    [%-6s] %-46s %s" % (src, nm, fn))
print("    （共 %d 个）" % len(seen))

print()
print("  ── ② scripts/ 里跟「文档信息 / 引用 / 模板」有关的能力层函数 ──")
import inspect
for mod in ("sw_connect", "sw_delivery", "sw_export", "sw_pdm", "sw_document"):
    try:
        m = __import__(mod)
    except Exception:                                          # noqa: BLE001
        continue
    for n in sorted(dir(m)):
        if n.startswith("_"):
            continue
        o = getattr(m, n)
        if callable(o) and getattr(o, "__module__", "").endswith(mod):
            if re.search(r"document|referenc|template|info|title|path|config", n, re.I):
                try:
                    print("    %-18s %-34s %s" % (mod, n, str(inspect.signature(o))[:56]))
                except Exception:                              # noqa: BLE001
                    pass
