import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

# ① 能力条目
Q = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(Q.read_text(encoding="utf-8"))
for c in d["capabilities"]:
    if c.get("id") != "part_and_features":
        continue
    c["evidence"] = list(c.get("evidence") or []) + [
        "python tools/verify_centerline_smoke.py（**真机**，SW 2026 SP4.1 / 34.4.1："
        "`sketch_centerline` 建成 → `get_sketch_segments` **读回 1 段**；"
        "**再测单位**：半径 25 的圆 ⇒ 边界框 **50 mm** ⇒ **官方文档的「in meters」是错的**；"
        "**8/8 通过**，证据落 output/centerline-smoke-evidence.json）",
        "python tools/probe_getlines_count.py（**真机**：画 **1/2/3** 条直线 ⇒ "
        "`get_lines` 读回 **12/24/36** 个 `float` ⇒ **每条 12 个**，元素类型是 `float`）",
    ]
    c["limitations"].insert(0, "⚑ 2026-10-01（轮 140）**补 `centerline`**（`sketch_centerline`，真缺档）。"
                              "★ 走**现行入口** `ISketchManager.CreateCenterLine` —— 官方有**两级废弃链**："
                              "`IModelDoc2.CreateCenterLine(Object,Object)` ⇒ "
                              "`CreateCenterLineVB`（**Void** 返回的 VB 变体）⇒ "
                              "**`ISketchManager.CreateCenterLine`**。")
    c["limitations"].insert(1, "★★ **同一轮量出一件要紧的事**：`sw_sketch.get_lines` **返回的是"
                              "「数值数组」不是「线对象列表」** —— 实测每条直线占 **12 个 `float`**
                              "（画 1/2/3 条 ⇒ 12/24/36，元素类型是 `float`）。"
                              "⚠ **官方文档没写这个返回结构**；⚠ 而此前**冒烟只查「非空」**"
                              "⇒ **12 对 1 也照样绿** ⇒ 这个语义**一直没人写下来**。"
                              "⇒ 已改写 docstring + 冒烟加**定量**判据（18/18）+ "
                              "契约测试加 3 条（含「**不许**把结果当对象用」）。")
    c["limitations"].insert(2, "⚠ **未查证**：那 12 个 `float` 的**具体含义**（哪几个是哪个端点/是否含额外字段）"
                              "**未逐位核**；中心线的**构造几何标记**是否自动置上**未测**；"
                              "`get_arcs` / `get_ellipses` 是否也是「数值数组」**未测**。")
    print("  ok part_and_features 已更新")
    break
Q.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("  能力数 %d" % len(d["capabilities"]))

# ② 已知事实 81
K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
ADD = """

| # | 事实 | 依据 |
|---|---|---|
| 81 | **`ISketch.GetLines2` 返回的是「数值数组」不是「线对象列表」—— 每条直线占 12 个 `float`** —— 2026-10-01（轮 140）真机实测（`tools/probe_getlines_count.py`）：画 **1 / 2 / 3** 条直线 ⇒ `get_sketch_segments` = **1 / 2 / 3**（对）而 `get_lines` = **12 / 24 / 36**，且 `get_lines(...)[0]` 的类型是 **`float`**（不是 `Dispatch`）⇒ **完全线性：每条 12 个**。⚠ **官方文档没写这个返回结构**；⚠⚠ 而此前 `tools/verify_sketch_getters_smoke.py` 的判据只是「**非空**」⇒ **12 对 1 也照样绿** ⇒ 这个语义**一直没人写下来**（这正是"**判据太弱 ⇒ 真问题藏在绿里**"的一个实例）。★ 处置：改写 `sw_sketch.get_lines` 的 docstring（写明「数值数组」+「每条 12 个 float」+ 给出「要几条线用 `get_sketch_segments`」的替代）· 冒烟**加定量判据**（18/18）· `tests/test_sw_sketch_contract.py` 加 3 条（含「**仓库里不许有人把结果当对象用**」）。⚠ 同轮还**再测**了长度单位：半径 25 的圆 ⇒ 边界框 **50**（毫米）⇒ **官方文档 `ISketchManager.CreateCenterLine` 那句「in meters」是错的**（事实 73 的第二次印证）。 | `tools/probe_getlines_count.py`（12/24/36 三例）；`tools/verify_centerline_smoke.py`（**8/8**，含单位再测）；`tools/verify_sketch_getters_smoke.py`（**18/18**，含新的定量判据）；`tests/test_sw_sketch_contract.py`（15 条）；事实 73 |
"""
if "数值数组」不是「线对象列表」" not in tk:
    K.write_text(tk.rstrip() + ADD, encoding="utf-8")
    print("  ok known-facts 已加 81")
else:
    print("  已有 81")
