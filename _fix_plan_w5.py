import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
p = Path(r"D:\AI\SW\docs\plan-10h.md")
t = p.read_text(encoding="utf-8")
MARK = "★★ W5 范围更正（轮 232 实测后）"
if MARK in t:
    print("  已在，跳过")
else:
    NEW = """### W5 · 检查 / 测量 / 反馈族（`specs/138`）· 约 80 分钟 · ★★ **2026-10-01 轮 232 实测后改范围（见下）**

```
★★★ **改范围的理由（实测）**：⑫inspect 那 16 个缺口名逐个核过 ——
   ① **已有**：`bbox`（= `solidworks_part_bounding_box`，名字不同）·
      `view_orientation` / `zoom_to_fit`（视图那批已有）
   ② **不是只读**：`display_mode`（改视图）· `analyze_draft`（分析，但要选中面）
   ③ ★★ **真缺且是高频只读需求**：**读质量属性**（`calculate_mass_properties` / `mass_props`）
      ⇒ ★ 本仓库有 `sw_export.set_mass_property_override`（**改**覆盖值），却**读不出实际值**
      ⇒ ★ **与 W3 的"能写不能读"同型**（见 `specs/133`）。
      ⇒ 官方入口在：`IModelDocExtension.CreateMassProperty` → `IMassProperty` / `IMassProperty2`
        （反射表里都有；`GetMassProperties` 也在）
      ⇒ 一个零件"多重 / 体积多少 / 重心在哪"是**最常被问的问题之一**，而**答不出来**。
   ④ 其余（`measure_distance` / `sensors` / `status` / `check_errors` / `reference_geometry` /
      `analyze_geometry` / `capture_screenshot`）⇒ 留后续批次。

★ **所以 W5 改为**：挂**质量属性读数**（质量 / 体积 / 表面积 / 重心 / 惯性矩）。
   ★ 照 W1/W3 的教训：**先写真机探针**答两件事 ——
     ① 从 `model` 怎么拿到 `IMassProperty`；
     ② ★ **哪些读成员带 by-ref out**（那是 pywin32 的死穴，见事实 8/33/161）。
★ 验证：★ **数字断言** —— 建一个已知实体（W4 的 `extrude_boss` 已能做）
  ⇒ 40×20×10 的盒 ⇒ ★ **期望体积 8000 mm³** ⇒ 与读回来的值对；质量随密度而定（要记密度的来源）。
   ★ 而且这次能**给 W4 续 c 的断言补一个更强的读数**。

来源 / license：本项目自身（MIT）；官方依据 `IMassProperty` / `IMassProperty2` /
  `IModelDocExtension.CreateMassProperty`（反射与 `C:\\swapi` 两源）
验收①：工具数 + 门禁；②：`python tools/capture_mass_property_evidence.py` ⇒ `verdict: pass`
```

"""
    anchor = "### W6 · 装配族"
    i = t.find(anchor)
    assert i > 0, "锚点不符: W6"
    j = t.find("### W5 · 检查 / 测量 / 反馈族")
    assert j > 0, "锚点不符: W5"
    t = t[:j] + NEW + t[i:]
    #: W6/W7 的编号顺移（139/140）
    t = t.replace("W6 · 装配族（`specs/137`）", "W6 · 装配族（`specs/139`）", 1)
    t = t.replace("W7 · 仿真载荷包装层（`specs/138`）", "W7 · 仿真载荷包装层（`specs/140`）", 1)
    #: 编号说明加一句：本次是第三次顺移 ⇒ 说明"编号不写死"的必要
    t = t.replace(
        "> ⚠ 这正是「编号必须现场核、不能照计划抄」的一个实例。",
        "> ⚠ 这正是「编号必须现场核、不能照计划抄」的一个实例。\n"
        "> ★★ **2026-10-01 轮 232 第三次顺移**：W4 后来拆成 **三个特性**（135 建草图 / 136 拉伸 /\n"
        "> 137 倒角圆角）⇒ W5–W7 再顺移一号：**W5=138 · W6=139 · W7=140**。\n"
        "> ⇒ ★ 教训：**计划里不要写死编号**，写「用当时的下一个空闲号」；\n"
        ">   因为**一个 W 可能拆成多个特性**，编号必然漂移（三次顺移都是这个原因）。", 1)
    p.write_text(t, encoding="utf-8")
    print("  ✓ W5 段已替换 + W6/W7 顺移 + 编号说明补充")
u = p.read_text(encoding="utf-8")
for k in ("W5 范围更正", "specs/138", "specs/139", "specs/140", "第三次顺移", "不要写死编号"):
    print("  含「%s」: %s" % (k, k in u))
