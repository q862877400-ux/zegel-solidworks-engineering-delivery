import ast
import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:\swprojects\sw-skill-fork")

# ── ① 修 `sw_assembly.py` 的导入（**真 bug**：12 处调用没有名字）──────
P = ROOT / "scripts" / "sw_assembly.py"
t = P.read_text(encoding="utf-8")
before = t
t = t.replace("from .sw_connect import open_document, safe_get_com_member",
              "from .sw_connect import get_com_member, open_document, safe_get_com_member")
t = t.replace("from sw_connect import open_document, safe_get_com_member",
              "from sw_connect import get_com_member, open_document, safe_get_com_member")
assert t != before, "sw_assembly 导入锚点不符"
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  ✓ sw_assembly.py 已补 get_com_member 导入")

# ── ② 迁移两处新发现的「名字像改东西」────────────────────────────
for f, member in (("scripts/sw_drawing_view.py", "ScaleDecimal"),
                  ("scripts/sw_part.py", "InsertDome")):
    p = ROOT / f
    src = p.read_text(encoding="utf-8")
    pat = re.compile(r"get_com_member\((\s*[\w.\[\]'\"]+\s*,\s*[\"']%s[\"']\s*)\)" % member)
    n = len(pat.findall(src))
    src2 = pat.sub(lambda m: "call_com_member(%s)" % m.group(1), src)
    if n:
        p.write_text(src2, encoding="utf-8")
        ast.parse(src2)
        print("  ✓ %s: 迁移 %d 处 `%s`" % (f.split("/")[-1], n, member))
    else:
        print("  ⚠ %s: 没找到 `%s` 的调用" % (f.split("/")[-1], member))

# ── ③ 补这两处的导入 ──────────────────────────────────────────
SINGLE = re.compile(r"(?m)^(\s*)from (\.?)sw_connect import ([^(\n]+?)\s*(#.*)?$")
MULTI = re.compile(r"(?m)^(\s*)from (\.?)sw_connect import \(\s*$")
for f in ("scripts/sw_drawing_view.py", "scripts/sw_part.py"):
    p = ROOT / f
    src = p.read_text(encoding="utf-8")
    if "call_com_member" not in src.split("def ")[0]:
        def add_single(m):
            indent, dot, names, comment = m.group(1), m.group(2), m.group(3), m.group(4) or ""
            lst = [x.strip() for x in names.split(",") if x.strip()]
            if "call_com_member" in lst:
                return m.group(0)
            lst.append("call_com_member")
            lst = sorted(set(lst), key=lambda s: (s != "get_com_member", s))
            return "%sfrom %ssw_connect import %s%s" % (indent, dot, ", ".join(lst), comment)
        src = SINGLE.sub(add_single, src)
        if "call_com_member" not in src.split("def ")[0]:
            src = MULTI.sub(lambda m: m.group(0) + "\n%s    call_com_member," % m.group(1), src, count=1)
        p.write_text(src, encoding="utf-8")
        ast.parse(src)
        print("  ✓ %s: 已补 call_com_member 导入" % f.split("/")[-1])
