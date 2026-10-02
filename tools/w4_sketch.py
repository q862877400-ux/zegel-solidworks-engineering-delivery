import inspect
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path[:0] = [r"" + _ROOT_S + r"\mcp-server", r"" + _ROOT_S + r"",
                r"" + _ROOT_S + r"\scripts"]
import register_capabilities as rc

srv = Path(r"" + _ROOT_S + r"\mcp-server\server.py").read_text(encoding="utf-8")
allnames = [x.name for x in rc.all_specs()] + re.findall(
    r'name="((?:solidworks|cadstudio)_[a-z0-9_]+)"', srv)

print("  ── MCP 里跟「草图 / 划线 / 拉伸」有关的工具 ──")
n_hit = 0
for n in sorted(set(allnames)):
    if re.search(r"sketch|line|circle|rect|extrude|boss|cut", n, re.I):
        n_hit += 1
        print("    %s" % n)
print("    （共 %d 个）" % n_hit)

print()
print("  ── 能力层里「建草图 / 画几何」的函数（首参 model 的）──")
import sw_part as p
cnt = 0
for n in sorted(dir(p)):
    if n.startswith("_"):
        continue
    o = getattr(p, n)
    if callable(o) and getattr(o, "__module__", "").endswith("sw_part"):
        if re.search(r"sketch|line|circle|rect", n, re.I):
            try:
                sig = inspect.signature(o)
                if list(sig.parameters)[:1] == ["model"]:
                    cnt += 1
                    print("    %-30s %s" % (n, str(sig)[:60]))
            except Exception:                                  # noqa: BLE001
                pass
print("    （共 %d 个）" % cnt)
