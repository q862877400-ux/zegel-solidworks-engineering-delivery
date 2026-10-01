import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

# ── ① 事实 101 追加：AddRelation 的调用形态 ──────────────────────────
K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
ADD = "".join([
    "〔★★★ **2026-10-01 轮 161 补记**：`ISketchRelationManager.AddRelation` 在真机上**从未跑通过** —— ",
    "官方有**两个重载**（`SketchRelation AddRelation(Object, Int32)` 与 `Void AddRelation(String)`），",
    "而那个 `Object` 是 **SAFEARRAY** ⇒ **直接传 Python `list` / `tuple` 都不行**：",
    "`list`/`tuple` ⇒ `com_error 0x80010105`「服务器出现意外情况」且**计数不变**；",
    "**`VARIANT(VT_ARRAY | VT_DISPATCH, [实体…])` ⇒ 无错、`GetRelationsCount` 真的 +1**。",
    "⚠ 那个错误码与事实 28/47 的「服务器出现意外情况」**同码不同因** —— 本轮的形态是",
    "「**数组实参没包 VARIANT**」，报错本身看不出是哪一种。",
    "★ 已修：`sketch_relations._dispatch_array()` 把实体序列包成 SAFEARRAY。",
    "⚠ **仍未绿**：在上下文编辑那条链卡在「拿到 `IComponent2` 并选中它的边」这一步 —— ",
    "`asm.GetComponents(True)` 给回来的对象上**没有 `GetBody2`**（接口族可能不是 `IComponent2`），",
    "按事实 53 **停下不再换写法**。〕 ",
])
MARK = "★ 本轮实现的三个封装（`sw_assembly_doc.py`）"
if MARK in tk and "轮 161 补记" not in tk:
    K.write_text(tk.replace(MARK, ADD + MARK, 1), encoding="utf-8")
    print("  ok 事实 101 已补记 AddRelation 的调用形态")
else:
    print("  事实 101：锚点在=%s 已补=%s" % (MARK in tk, "轮 161 补记" in tk))

# ── ② 能力条目补一条证据 ────────────────────────────────────────────
Q = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(Q.read_text(encoding="utf-8"))
EV = ("python tools/probe_add_relation_forms.py（**真机**，轮 161，2 条直线的草图）："
      "★ **找到 `AddRelation` 的可行调用形态** —— `list`/`tuple` 报 `com_error 0x80010105` 且计数不变；"
      "**`VARIANT(VT_ARRAY|VT_DISPATCH, [实体…])` ⇒ 无错、`GetRelationsCount` 3 → 4**。"
      "⇒ `sketch_relations.add_relation` 已按此修（它此前**从没在真机上跑通过**）。")
for c in d["capabilities"]:
    if c.get("id") == "part_and_features":
        c["evidence"] = list(c.get("evidence") or []) + [EV]
        print("  ok part_and_features 已更新")
Q.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
