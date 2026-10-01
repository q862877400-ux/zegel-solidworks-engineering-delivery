"""从 308 个「孤立能力」里挑暴露试点：按模块分组 + 标出有无测试。"""
import re, sys
from collections import defaultdict
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")

DEF = re.compile(r"^def ([a-z_]\w*)\(", re.M)
funcs = {}
for p in sorted((R / "scripts").glob("sw_*.py")):
    for fn in DEF.findall(p.read_text(encoding="utf-8", errors="ignore")):
        funcs.setdefault(fn, p.name)

srv = (R / "mcp-server" / "server.py").read_text(encoding="utf-8", errors="ignore")
disp = {fn for _, _, fn in re.findall(r'"(\w+)":\s*([A-Za-z_]\w*)\.([A-Za-z_]\w*)\s*,', srv)}
spec = set()
for p in (R / "mcp-server").glob("tool_specs_*.py"):
    spec |= set(re.findall(r'function="([\w]+)"', p.read_text(encoding="utf-8", errors="ignore")))
exposed = disp | spec

# 调用者（生产 + 测试）
prod_calls, test_calls = set(), set()
for d, bucket in (("scripts", prod_calls), ("subskills", prod_calls), ("examples", prod_calls),
                  ("mcp-server", prod_calls), ("tests", test_calls)):
    base = R / d
    if not base.is_dir():
        continue
    for p in base.rglob("*.py"):
        src = p.read_text(encoding="utf-8", errors="ignore")
        others = {f for f, o in funcs.items() if o != p.name}
        for m in re.finditer(r"\b(\w+)\s*\(", src):
            if m.group(1) in others:
                bucket.add(m.group(1))

INTERNAL = re.compile(r"(_to_|_from_|^parse|^normalize|^empty|^variant|^callout|^pump|^_|^make_empty|^coerce|^get_com)")
orphans = []
for f, mod in funcs.items():
    if f in exposed or INTERNAL.search(f):
        continue
    if f in prod_calls or f in test_calls:
        continue
    orphans.append((f, mod))

by_mod = defaultdict(list)
for f, m in orphans:
    by_mod[m].append(f)

# 每个模块：孤立数 + 该模块在 tests/ 里被引用的函数数
print("孤立能力最多的 12 个模块（按孤立数）：")
rows = sorted(by_mod.items(), key=lambda kv: -len(kv[1]))[:12]
for mod, fs in rows:
    tests = sum(1 for f in fs
                if any(re.search(r"\b%s\b" % re.escape(f), p.read_text(encoding="utf-8", errors="ignore"))
                       for p in (R / "tests").glob("*.py")))
    print("  %-26s 孤立 %3d 个 · 其中 %2d 个在 tests 里出现过" % (mod, len(fs), tests))
    print("       %s" % ", ".join(sorted(fs)[:6]))
