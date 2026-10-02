import inspect
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path[:0] = [r"" + _ROOT_S + r"\scripts", r"" + _ROOT_S + r"\mcp-server",
                r"" + _ROOT_S + r""]

import register_capabilities as rc

print("  ══ ① MCP 里跟「自定义属性」有关的工具 ══")
for x in rc.all_specs():
    if re.search(r"propert|custom", x.name + " " + (x.doc or "") + " " + x.module, re.I):
        print("    [batch] %-46s module=%-18s fn=%s" % (x.name, x.module, x.function))
SRV = Path(r"" + _ROOT_S + r"\mcp-server\server.py").read_text(encoding="utf-8")
for m in re.finditer(r'@mcp\.tool\(\s*(?:[^)]*?)name="([^"]+)"', SRV, re.S):
    if re.search(r"propert|custom", m.group(1), re.I):
        print("    [server] %s" % m.group(1))

print()
print("  ══ ② scripts/ 里跟「自定义属性」有关的函数（读 / 写）══")
for mod_name in ("sw_part", "sw_delivery", "sw_pdm", "sw_appearance", "sw_document"):
    try:
        m = __import__(mod_name)
    except Exception:                                          # noqa: BLE001
        continue
    for n in sorted(dir(m)):
        if n.startswith("_"):
            continue
        o = getattr(m, n)
        if callable(o) and getattr(o, "__module__", "").endswith(mod_name):
            if re.search(r"propert|custom_info", n, re.I):
                try:
                    print("    %-16s %-40s %s" % (mod_name, n, str(inspect.signature(o))[:50]))
                except Exception:                              # noqa: BLE001
                    pass

print()
print("  ══ ③ 官方：IModelDocExtension.CustomPropertyManager 的存在 ══")
p = Path(r"C:\swapi\types\IModelDocExtension\CustomPropertyManager.md")
print("    swapi 有该页:", p.is_file())
if p.is_file():
    for l in p.read_text(encoding="utf-8").splitlines()[:14]:
        print("      %s" % l[:100])
