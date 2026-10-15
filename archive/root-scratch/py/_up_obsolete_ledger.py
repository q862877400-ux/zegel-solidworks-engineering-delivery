import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\docs\obsolete-member-candidates.md")
t = P.read_text(encoding="utf-8")
old_head = "## 二、★ 已核实**为真**（我们确实在调官方已废弃的入口）"
add = """## 〇、⚑ 已处置（2026-10-01 轮 111）
**`sw_sketch.py` 的 6 个 `ISketch` 取法已改用后继**：
```
GetLines         → GetLines2(swCrossHatchFilter_e)   ⚠ 唯一带参的后继
GetArcs          → GetArcs2()
GetEllipses      → GetEllipses3()
GetParabolas     → GetParabolas2()
GetSketchPoints  → GetSketchPoints2()
GetUserPoints    → GetUserPoints2()
```
⚠ **换完仍未在真机上验过**（等级仍是 `stitched`）—— 换的是**入口名**，不是"测过了"。
★ 复跑 `tools/probe_obsolete_members.py`：**这 6 个已不再出现在候选里**。

## 二、★ 已核实**为真**（我们确实在调官方已废弃的入口）
"""
if "已处置（2026-10-01 轮 111）" not in t:
    assert old_head in t, "锚点不符"
    t = t.replace(old_head, add.rstrip() + "\n", 1)
    # 表格里给这 6 行加「已改」标记
    t = t.replace("| `GetLines` | `ISketch` | `ISketch::GetLines2` | `sw_sketch.py` |",
                  "| ~~`GetLines`~~ **已改** | `ISketch` | `ISketch::GetLines2` | `sw_sketch.py` |")
    t = t.replace("| `GetArcs` | `ISketch` | `ISketch::GetArcs2` | `sw_sketch.py` |",
                  "| ~~`GetArcs`~~ **已改** | `ISketch` | `ISketch::GetArcs2` | `sw_sketch.py` |")
    t = t.replace("| `GetEllipses` | `ISketch` | `ISketch::GetEllipses3` | `sw_sketch.py` |",
                  "| ~~`GetEllipses`~~ **已改** | `ISketch` | `ISketch::GetEllipses3` | `sw_sketch.py` |")
    t = t.replace("| `GetParabolas` | `ISketch` | `ISketch::GetParabolas2` | `sw_sketch.py` |",
                  "| ~~`GetParabolas`~~ **已改** | `ISketch` | `ISketch::GetParabolas2` | `sw_sketch.py` |")
    t = t.replace("| `GetSketchPoints` | `ISketch` | `ISketch::GetSketchPoints2` | `sw_sketch.py` |",
                  "| ~~`GetSketchPoints`~~ **已改** | `ISketch` | `ISketch::GetSketchPoints2` | `sw_sketch.py` |")
    t = t.replace("| `GetUserPoints` | `ISketch` | `ISketch::GetUserPoints2` | `sw_sketch.py` |",
                  "| ~~`GetUserPoints`~~ **已改** | `ISketch` | `ISketch::GetUserPoints2` | `sw_sketch.py` |")
    t = t.replace("⇒ **8 条确认为真**", "⇒ **8 条确认为真**（其中 **6 条已在轮 111 改用后继**，剩 `AddMate5` 与 `GetBodies2` **未改**）")
    P.write_text(t, encoding="utf-8")
    print("  ok 台账已更新（6 条标为已改）")
else:
    print("  已有")
