import re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")
funcs = {}
for p in (R / "scripts").glob("sw_*.py"):
    for n in re.findall(r"^def (\w+)\(", p.read_text(encoding="utf-8", errors="ignore"), re.M):
        funcs.setdefault(n, p.name)
tests = {p.name: p.read_text(encoding="utf-8", errors="ignore") for p in (R / "tests").glob("*.py")}
srv = (R / "mcp-server" / "server.py").read_text(encoding="utf-8", errors="ignore")
disp = {f for _, f in re.findall(r'"(\w+)":\s*[A-Za-z_]\w*\.(\w+)\s*,', srv)}
for p2 in (R / "mcp-server").glob("tool_specs_*.py"):
    disp |= set(re.findall(r'function="([\w]+)"', p2.read_text(encoding="utf-8", errors="ignore")))
NAMES = ("get_components", "get_bodies", "export_to_iges", "add_sketch_relation",
         "sketch_polygon", "sketch_slot", "create_semicircular_slot", "set_custom_properties")
for n in NAMES:
    where = funcs.get(n, "**没有**")
    hastest = any(re.search(r"\b%s\b" % re.escape(n), x) for x in tests.values())
    print("  %-26s 定义在 %-22s 测试=%-5s 已暴露=%s"
          % (n, where, "是" if hastest else "否", "是" if n in disp else "否"))
