import ast
import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:\swprojects\sw-skill-fork")
FILES = ["sw_document_data", "sw_drawing_view", "sw_geometry_selectors", "sw_gtol",
         "sw_mold", "sw_selection", "sw_sheet_metal", "sw_simulation", "sw_topology",
         "sw_view", "sw_weldment"]

#: 单行导入（相对或绝对，**允许缩进**）
SINGLE = re.compile(r"(?m)^(\s*)from (\.?)sw_connect import ([^(\n]+?)\s*(#.*)?$")
#: 多行导入的开头
MULTI = re.compile(r"(?m)^(\s*)from (\.?)sw_connect import \(\s*$")

for stem in FILES:
    p = ROOT / "scripts" / (stem + ".py")
    t = p.read_text(encoding="utf-8")
    orig = t

    def add_single(m):
        indent, dot, names, comment = m.group(1), m.group(2), m.group(3), m.group(4) or ""
        lst = [x.strip() for x in names.split(",") if x.strip()]
        if "call_com_member" in lst:
            return m.group(0)
        lst.append("call_com_member")
        lst = sorted(set(lst), key=lambda s: (s != "get_com_member", s))
        return "%sfrom %ssw_connect import %s%s" % (indent, dot, ", ".join(lst), comment)

    t = SINGLE.sub(add_single, t)

    #: 多行：在开括号后插一项（只插一次）
    if "call_com_member" not in t.split("def ")[0]:
        def add_multi(m):
            return m.group(0) + "\n%s    call_com_member," % m.group(1)
        t = MULTI.sub(add_multi, t, count=1)

    if t != orig:
        p.write_text(t, encoding="utf-8")
        ast.parse(t)
        print("  ✓ %s" % stem)
    else:
        print("  · %s（没改动）" % stem)

#: ★★ 复核：**用 `hasattr` 验真名字**（import 成功不算）
print()
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import importlib
bad = []
for stem in FILES:
    for pre in ("scripts.", ""):
        try:
            m = importlib.import_module(pre + stem)
            break
        except Exception:      # noqa: BLE001
            m = None
    if m is None:
        bad.append(stem + " (导入失败)")
        continue
    import inspect
    src = inspect.getsource(m)
    if "call_com_member(" in src and not hasattr(m, "call_com_member"):
        bad.append(stem + " (名字缺失)")
print("  ★★ 复核结果：问题模块 %d 个 %s" % (len(bad), bad))
