import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

CORRECT = ("⚠⚠ **2026-10-01（轮 142）更正**：轮 141 曾写「`get_*` 系列**全都**返回数值数组」——"
           "**那是错的**。实测（`tools/probe_slot_and_point_shapes.py`，真机 SW 2026 SP4.1）："
           "① 返回**数值数组**的（**曲线类**）：`get_lines` **12** · `get_arcs` **16** · `get_ellipses` **22**；"
           "② 返回**对象列表**的（**点/实体类**）：`get_sketch_slots`（**1**/个，元素 `CDispatch`）·"
           "`get_sketch_points`（**2**/线 —— 一条直线的两个端点）。"
           "⇒ ★ **两种形状都有**，不能一概而论。"
           "★ 规律**候选**（⚠ n=5，**当假设不当定则**）：**曲线类 ⇒ 数值数组；点/实体类 ⇒ 对象列表**。")

# ── ① capabilities.yaml（两处）────────────────────────────────────
Q = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(Q.read_text(encoding="utf-8"))
n = 0
for c in d["capabilities"]:
    lim = c.get("limitations") or []
    for i, s in enumerate(lim):
        if "get_*` 系列按类型取法全部返回" in str(s):
            lim[i] = str(s) + " " + CORRECT
            n += 1
Q.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("  capabilities.yaml 更正 %d 处" % n)

# ── ② sw_sketch.py 的两段说明 ─────────────────────────────────────
P = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_sketch.py")
t = P.read_text(encoding="utf-8")
OLD = "    ⇒ ★ **这是通例，不是孤例**：`get_*` 系列都返回**数值数组**（元素类型是 `float`）。"
NEW = ("    ⇒ ★ 这三条**都是数值数组**（元素类型 `float`）。\n"
       "    ⚠⚠ **2026-10-01（轮 142）更正**：此处原写「`get_*` 系列**都**返回数值数组」——**那是错的**。\n"
       "    实测 `get_sketch_slots`（**1**/个）与 `get_sketch_points`（**2**/线）返回的是**对象列表**\n"
       "    （元素 `CDispatch`）⇒ ★ **两种形状都有**。★ 规律**候选**（⚠ n=5，当假设不当定则）：\n"
       "    **曲线类 ⇒ 数值数组；点/实体类 ⇒ 对象列表**。")
cnt = t.count(OLD)
t = t.replace(OLD, NEW)
P.write_text(t, encoding="utf-8")
print("  sw_sketch.py 更正 %d 处" % cnt)

# ── ③ 契约测试的注释 ──────────────────────────────────────────────
T = Path(r"C:\swprojects\sw-skill-fork\tests\test_sw_sketch_contract.py")
tt = T.read_text(encoding="utf-8")
OLD3 = "#   ⇒ ★ 三个**都是数值数组**（元素 `float`）⇒ 与轮 140 发现的 `get_lines` **同类**。"
NEW3 = ("#   ⇒ ★ 三个**都是数值数组**（元素 `float`）⇒ 与轮 140 发现的 `get_lines` **同类**。\n"
        "#   ⚠⚠ **轮 142 更正**：原写「`get_*` 系列**都是**数值数组」——**错的**。\n"
        "#   `get_sketch_slots`（1/个）与 `get_sketch_points`（**2**/线）返回的是**对象列表**（`CDispatch`）\n"
        "#   ⇒ ★ **两种形状都有**；规律**候选**（n=5，当假设）：曲线类 ⇒ 数值数组，点/实体类 ⇒ 对象列表。")
if OLD3 in tt:
    tt = tt.replace(OLD3, NEW3, 1)
TT = T
TT.write_text(tt, encoding="utf-8")
print("  契约测试注释已更正")

# ── ④ 已知事实 82：**就地更正**（不新开一条，因为它就是同一条）────
K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
OLDK = "**`get_*` 按类型取法全部返回「数值数组」不是「对象列表」（通例）"
NEWK = ("**`get_*` 按类型取法的返回形状**"
        "〔⚠⚠ **2026-10-01 轮 142 就地更正**：本条原写「**全部**返回数值数组」——**那是错的**。"
        "实测 `get_sketch_slots`（**1**/个）与 `get_sketch_points`（**2**/线，一条直线两个端点）"
        "返回的是**对象列表**（元素 `CDispatch`）⇒ ★ **两种形状都有**。"
        "★ 规律**候选**（⚠ n=5，**当假设不当定则**）：**曲线类 ⇒ 数值数组；点/实体类 ⇒ 对象列表**。"
        "证据：`tools/probe_slot_and_point_shapes.py`。原话保留在下〕"
        "（通例〔**已更正**〕）")
if OLDK in tk:
    tk = tk.replace(OLDK, NEWK, 1)
    K.write_text(tk, encoding="utf-8")
    print("  known-facts 82 已就地更正")
else:
    print("  ⚠ known-facts 锚点不符")

# ── ⑤ ROADMAP：日志不改写，**加一个更正标记**──────────────────────
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
tr = R.read_text(encoding="utf-8")
r"""
⚠ 游标行是**日志**（记录当时说了什么）⇒ **不重写**，改在**本轮游标**里更正。
   但当前那句会误导后来读者 ⇒ 在那行**加一个指向更正的短标记**。
"""
OLDR = "⇒ `get_*` 系列**全都返回数值数组**（元素 `float`）⇒ 已把三个 docstring 写明形状。"
NEWR = ("⇒ `get_*` 系列**全都返回数值数组**（元素 `float`）⇒ 已把三个 docstring 写明形状。\n"
        "               ⚠⚠ **轮 142 更正**：这句「**全都**」**是错的** —— 见游标 382。")
if OLDR in tr:
    R.write_text(tr.replace(OLDR, NEWR, 1), encoding="utf-8")
    print("  ROADMAP 已加更正标记（不重写日志）")
else:
    print("  ⚠ ROADMAP 锚点不符")
