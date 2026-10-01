import ast
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:\swprojects\sw-skill-fork")
RAW = Path(r"D:\AI\SW\_raw")
OUT = Path(r"D:\AI\SW\output\zero-arg-method-callsites.json")


def reflection() -> dict:
    table: dict = defaultdict(list)
    for p in RAW.rglob("iface_*.txt"):
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            s = line.strip()
            m = re.match(r"^[\w.\[\]]+\s+(\w+)\s*\((.*)\)$", s)
            if m:
                table[m.group(1)].append(m.group(2).strip())
    return table


def sites():
    out = []
    for base in ("scripts", "mcp-server"):
        for p in sorted((ROOT / base).glob("*.py")):
            try:
                tree = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                f = node.func
                nm = f.id if isinstance(f, ast.Name) else (f.attr if isinstance(f, ast.Attribute) else None)
                if nm not in ("get_com_member", "safe_get_com_member"):
                    continue
                if len(node.args) != 2 or node.keywords:
                    continue
                a1 = node.args[1]
                if not isinstance(a1, ast.Constant) or not isinstance(a1.value, str):
                    continue
                out.append((str(p.relative_to(ROOT)), node.lineno, a1.value))
    return out


tab = reflection()
ss = sites()
print("  无实参 `get_com_member` 调用点: **%d**" % len(ss))
danger, safe, unknown = [], [], []
for f, ln, member in ss:
    sigs = tab.get(member)
    if not sigs:
        unknown.append((f, ln, member))
        continue
    #: 有**零参**重载 ⇒ 试探调用**会成功执行**
    if any(s == "" for s in sigs):
        danger.append((f, ln, member))
    else:
        safe.append((f, ln, member, sigs[0][:36]))
print()
print("  ★★★ **危险（反射里有零参重载 ⇒ 试探调用会真的执行）: %d 处**" % len(danger))
for f, ln, member in danger:
    print("     %-42s L%-5d %s" % (f, ln, member))
print()
print("  ✓ 安全（反射里该方法**都要实参** ⇒ 上轮的修复已挡住）: %d 处" % len(safe))
for f, ln, member, sig in safe[:10]:
    print("     %-42s L%-5d %-26s (%s)" % (f, ln, member, sig))
if len(safe) > 10:
    print("     …（还有 %d 处）" % (len(safe) - 10))
print()
print("  ⚑ 反射里查不到该名字（铁律 5：查不到就说查不到）: %d 处（%d 个名字）"
      % (len(unknown), len({u[2] for u in unknown})))
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps({"danger": danger, "safe": safe,
                           "unknown": [list(u) for u in unknown]},
                          ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("  证据: %s" % OUT)
