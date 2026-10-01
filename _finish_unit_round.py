import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

# ① 写文档
import subprocess
r = subprocess.run([sys.executable, r"D:\AI\SW\_mk_unit_doc.py"],
                   capture_output=True, text=True, encoding="utf-8", errors="replace")
print(r.stdout.strip() or r.stderr.strip()[:400])

# ② 探针源码里写明结论
P = Path(r"C:\swprojects\sw-skill-fork\tools\probe_unit_declarations.py")
t = P.read_text(encoding="utf-8")
NOTE = """# ⚠⚠ **2026-10-01 轮 133 的结论：本探针不能当判据，而且这个判据的原理不成立。**
#   实测假阳性 **4/4 = 100%** —— `lot_size`（批量大小）/ `depth`（树深度）/
#   `width`（窗口宽）/ `dx,dy`（屏幕像素）**全被误判成长度参数**。
#   ★ 根因：**「长度词表」无法区分「几何长度」与「同名的非几何量」** —— 那是**语义**判断。
#   ⇒ 详 `docs/script-layer-units.md`。**不要把它接进门禁。**
#   ★ 脚本层单位的**唯一可靠办法是实测**（`051` 轮 132 就是真机量出来的）。
"""
if "本探针不能当判据" not in t:
    i = t.index("def public_functions(")
    t = t[:i] + NOTE + "\n\n" + t[i:]
    P.write_text(t, encoding="utf-8")
    print("  ok 探针源码已写明结论")
ast.parse(P.read_text(encoding="utf-8"))
print("  语法 OK")

# ③ 已知事实 74
K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
ADD = """

| # | 事实 | 依据 |
|---|---|---|
| 74 | **「脚本层的单位声明」没有可机器化的守卫 —— 判据的原理就不成立** —— 2026-10-01（轮 133）用显式长度词表扫 `scripts/sw_*.py`：**带长度参数却一处单位声明都没有**的 4 个模块，**逐条人工看全是假阳性（4/4 = 100%）**：`sw_costing.set_lot_size(lot_size)` 是**批量大小（件数）**、`sw_jlcfa_gui.find_node(depth)` 是**树深度**、`sw_jlcfa_gui.drag(x1,y1,x2,y2)` 与 `sw_jlcfa_select.crop_region(dx,dy)` 与 `sw_view.translate_view(dx,dy)` 是**屏幕像素**、`sw_view.set_view_frame(width,height)` 是**窗口几何**。★ 根因：**`size`/`depth`/`width`/`dx` 在非几何语境里同样常用，词形判不了语义** ⇒ 缩小词表则覆盖面太小（价值不如维护成本）。⚠ 这也解释了 `051` 那个错**为什么活那么久**：**不是没人管，是"管不了"**。⇒ **不做门禁**；探针保留供人工扫；★ **脚本层单位的唯一可靠办法是实测**（`051` 就是真机量出来的）。★ 与 `029`(26%)/`032`(50%)/`037`(59%) 同一族，**这次最硬**：前几次是"假阳性多"，这次是"原理不成立" | `tools/probe_unit_declarations.py`；`docs/script-layer-units.md`；`_triage_unit_flags.py`（那 4 个的逐条形参/docstring 打印）|
"""
if "判据的原理就不成立" not in tk:
    K.write_text(tk.rstrip() + ADD, encoding="utf-8")
    print("  ok known-facts 已加 74")
else:
    print("  已有 74")
