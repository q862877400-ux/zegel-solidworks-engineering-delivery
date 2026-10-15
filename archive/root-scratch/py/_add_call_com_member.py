import ast
import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:\swprojects\sw-skill-fork")

# ── ① 在 sw_connect.py 里加显式的 `call_com_member` ──────────────
P = ROOT / "scripts" / "sw_connect.py"
t = P.read_text(encoding="utf-8")
ANCHOR = "def get_com_member_raw(obj, attr_name):"
ADD = '''def call_com_member(obj, attr_name, *args):
    """★ 「**就是去调它**」—— 与 `get_com_member` **行为完全相同**，差别在**名字**。

    :returns: **调用的结果**（会把成员调一次）。

    ⚠ **为什么要单独一个名字**（2026-10-01 轮 145）：审计 24 处「会改东西的零参调用」
    时发现，**作者全部是故意的**（拿返回值当成败 / 要的就是那个动作）——
    但**代码里读不出来**：`get_com_member(study, "RunAnalysis")` 看不出它会**跑求解**。
    ⇒ ★ 在**故意要调**的地方用本函数，**名字即意图**，读代码的人不必再去查语义。

    ⚠ 只在**确实要调用**时用它；**要"只取不调"用 `get_com_member_raw`**；
    两者都拿不准时用 `get_com_member`（语义是"取或调"，**名字不表态**）。
    """
    return get_com_member(obj, attr_name, *args)


'''
if "def call_com_member(" not in t:
    assert ANCHOR in t, "锚点不符"
    t = t.replace(ANCHOR, ADD + ANCHOR, 1)
    P.write_text(t, encoding="utf-8")
    print("  ok 已加 call_com_member")
ast.parse(P.read_text(encoding="utf-8"))
print("  语法 OK")

# ── ② 迁移那 24 处（按行号精确替换，**只改那一处调用**）────────────
d = json.loads(Path(r"D:\AI\SW\output\zero-arg-method-callsites.json").read_text(encoding="utf-8"))
MUT = ("Insert", "Add", "Delete", "Remove", "Create", "Set", "Run", "Update",
       "Mesh", "Scale", "Start", "Stop", "Save", "Close", "Open", "Edit", "Modify",
       "Rebuild", "Redraw", "Zoom", "Clear", "Reset", "Apply", "Execute", "Load",
       "Write", "Export", "Import", "Refresh", "Select", "Activate", "Break", "Merge")
hot = [x for x in d["danger"] if str(x[2]).startswith(MUT)]
byfile: dict = {}
for f, ln, m in hot:
    byfile.setdefault(f, []).append((ln, m))

changed = 0
for f, items in byfile.items():
    p = ROOT / f
    lines = p.read_text(encoding="utf-8").splitlines(keepends=True)
    for ln, m in items:
        i = ln - 1
        if "get_com_member(" in lines[i]:
            lines[i] = lines[i].replace("get_com_member(", "call_com_member(")
            changed += 1
        else:
            print("  ⚠ %s:%d 那一行没有 get_com_member(" % (f, ln))
    p.write_text("".join(lines), encoding="utf-8")
    ast.parse(p.read_text(encoding="utf-8"))
print("  ok 迁移了 %d 处（跨 %d 个文件）" % (changed, len(byfile)))
