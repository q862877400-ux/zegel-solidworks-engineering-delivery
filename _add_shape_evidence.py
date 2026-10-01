import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

Q = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(Q.read_text(encoding="utf-8"))

EV = ("python tools/probe_sketch_getter_shapes.py + probe_spline_creation.py + "
      "probe_spline_redraw.py（**真机**，SW 2026 SP4.1 / 34.4.1）：**按类型取法全是数值数组** "
      "（line/arc/ellipse = **12 / 16 / 22** 个 `float` 每实体，画 1/2 个 ⇒ 12/24 · 16/32 · 22/44）；"
      "★★ 并查出 **`sketch_spline` 是静默空操作** —— `CreateSpline2` 返回 `None`、段数 **0**，"
      "**重绘后仍是 0**（排除了官方 Remark 的「必须重绘」解释）⇒ 已改成**失败即抛**")
L1 = ("★★ **2026-10-01（轮 141）查出：`get_*` 系列按类型取法全部返回「数值数组」而不是「对象列表」**"
      " —— 实测每个实体占 **line 12 / arc 16 / ellipse 22** 个 `float`，元素类型是 `float`"
      "（画 1/2 个 ⇒ 12/24 · 16/32 · 22/44）⇒ ★ **轮 140 在 `get_lines` 上发现的是通例，不是孤例**。"
      "⚠ 官方文档**没写**返回结构；⚠ 既有冒烟的判据只有「非空」⇒ 这个语义长期没被写下。"
      "⇒ 已把三个取法的 docstring 写明形状 + 契约测试 3 条钉住。")
L2 = ("★★★ **并查出 `sw_part.sketch_spline` 是「静默空操作」**：`CreateSpline2` 返回 **`None`**、"
      "`get_sketch_segments` = **0**，而**没有抛异常**；★ **重绘后仍是 0** ⇒ 排除了官方 Remarks 那句"
      "「always adds directly to the database / 必须重绘才看得见」；`CreateSpline`（1 参旧版）"
      "**在迟到绑定里没有这个成员**；对照组（同流程画直线）段数 **1** ⇒ 流程本身没问题。"
      "★ 根因：`CreateSpline2` 官方已 **Obsolete**，后继 `CreateSpline3(Object,Object,Object,Boolean,Object&)` "
      "末参是 **BYREF `Object&`** ⇒ 事实 47/68 的架构限制 ⇒ **这条后端上不达**。"
      "⇒ 处置照 `sw_surface._invoke` 的先例（事实 40）：**让失败可见** —— 返回 `None` 即抛 `RuntimeError`。")
L3 = ("⚠ **未查证**：那 12/16/22 个 `float` 的**具体含义**未逐位核；"
      "`get_splines` / `get_polylines` / `get_sketch_points` 等**其余取法的形状未测**"
      "（`get_splines` 量到 0 是**因为样条画不出来**，不是取法本身的问题）；"
      "`CreateSpline3` 的 BYREF 末参**没有再去试**（事实 47 已穷尽 20+ 形态）。")

for c in d["capabilities"]:
    if c.get("id") == "part_and_features":
        c["evidence"] = list(c.get("evidence") or []) + [EV]
        c["limitations"].insert(0, L1)
        c["limitations"].insert(1, L2)
        c["limitations"].insert(2, L3)
        print("  ok part_and_features 已更新")
    if c.get("id") == "sketch_query":
        c["evidence"] = list(c.get("evidence") or []) + [EV]
        c["limitations"].insert(0, L1)
        print("  ok sketch_query 已更新")
Q.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# 已知事实 82
FACT = ("| 82 | **`get_*` 按类型取法全部返回「数值数组」不是「对象列表」（通例）；"
        "且 `sketch_spline` 是「静默空操作」** —— 2026-10-01（轮 141）真机实测"
        "（`tools/probe_sketch_getter_shapes.py` / `probe_spline_creation.py` / `probe_spline_redraw.py`）："
        "① **形状是通例** —— 画 1/2 个实体 ⇒ `get_lines` **12/24** · `get_arcs` **16/32** · "
        "`get_ellipses` **22/44**，元素类型都是 `float` ⇒ 每个实体占 **line 12 / arc 16 / ellipse 22** 个；"
        "★ 轮 140 在 `get_lines` 上发现的是**通例**。② **`sketch_spline` 静默空操作** —— "
        "`CreateSpline2` 返回 **`None`** ⇒ `get_sketch_segments` = **0**，**不抛异常**；"
        "★★ **重绘后仍是 0** ⇒ **排除了**官方 Remarks 那句「always adds directly to the database / "
        "必须重绘才看得见」；`CreateSpline`（1 参）**迟到绑定里没有该成员**；对照直线 = **1** ⇒ 流程没问题。"
        "★ 根因：`CreateSpline2` 已 **Obsolete**，后继 `CreateSpline3(…, Object&)` 末参是 **BYREF** ⇒ "
        "事实 47/68 的架构限制。⇒ 处置照 `sw_surface._invoke`（事实 40）：**让失败可见**，返回 `None` 即抛。"
        "★ 这一条与事实 81 合起来是一次**同族追问**：「一个取了 0 或取了奇怪个数的取法，"
        "要拿**定量**判据去量，别只查非空」。 | `tools/probe_sketch_getter_shapes.py`（**12/16/22**）；"
        "`tools/probe_spline_creation.py`（返回 `None`）；`tools/probe_spline_redraw.py`"
        "（**重绘后仍 0**）；`tests/test_sw_sketch_contract.py`（**18 条**）；事实 40 / 47 / 68 / 81 |")

K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
if "get_*` 按类型取法全部返回" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + FACT + "\n", encoding="utf-8")
    print("  ok known-facts 已加 82")
else:
    print("  已有 82")
