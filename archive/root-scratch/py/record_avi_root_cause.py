"""把 AVI 域的边界从「条件未定位」升级为「**已定位为环境约束**」。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
CAP = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")

LIMITS = [
    "⚑ **护城河域之一**（`AGENTS.md §〇`：真正全网空白的三个域是拓扑优化、动画导出 AVI、Costing）。",
    "⚑ **2026-10-01（轮 63-66）真机验证：API 链已全部打通**（SW 2026 SP4.1）——",
    "   `ensure_motion_type_library()` ⇒ `…\\SOLIDWORKS\\swmotionstudy.tlb`；`GetMotionStudyManager` /",
    "   `CreateMotionStudy` ⇒ 非 None；`CreateAVIParameter()` ⇒ 非 None（默认值可读）；",
    "   `configure_avi_parameter(FramePerSecond=10)` ⇒ **回读 10.0**（写入生效）；",
    "   匀速旋转马达建成（`AEMRotationalMotor`，type_id 102），算完 `motor_count=1` · 结果新鲜。",
    "🔴 **边界已定位：`SaveToAVI` 需要 `CosmosMotion` 系列算例，而本机拿不到那种算例。**",
    "   **真机实测的可行性矩阵**（`D:\\AI\\SW\\probe_motion_addin.py`，逐值 set 再回读）：",
    "   ```",
    "   set StudyType=1  (swMotionStudyTypeAssembly)           ⇒ 回读 1 ✅ 生效  → 导出失败",
    "   set StudyType=2  (swMotionStudyTypePhysicalSimulation) ⇒ 回读 2 ✅ 生效  → 导出失败",
    "   set StudyType=4  (swMotionStudyTypeCosmosMotion)       ⇒ 回读 2 ❌ **静默失败**",
    "   set StudyType=8  (swMotionStudyTypeLegacyCosmosMotion)  ⇒ 回读 2 ❌ **静默失败**",
    "   set StudyType=16 (swMotionStudyTypeNewCosmosMotion)     ⇒ 回读 2 ❌ **静默失败**",
    "   ```",
    "   **且 Motion 加载项的 4 个 ProgID 全返 `None`**：`CMotionswapi.CMOTIONSWAddin` /",
    "   `SldWorks.Motion` / `SolidWorks.Motion` / `SWMotionStudy.SWMotionStudyAddin`。",
    "   ⇒ **本机只能建 Assembly(1) 与 PhysicalSimulation(2)；CosmosMotion 家族设不上**",
    "     ⇒ **AVI 导出需要真正的 Motion 分析算例，本机没有那个加载项/许可**。",
    "⚑ **这是一条**环境约束**，不是代码缺陷**（同上：`SldWorks.Motion` 没有 ⇒ 见 `§九.4`）。",
    "   ⚠ **`AGENTS.md §九.4`：需要用户提供的东西 ⇒ 停下报告，不自行拍板。**",
    "   **需要用户提供**：**SolidWorks Motion 加载项**（或其许可）⇒ 装上后本域可直接升 `verified`。",
    "⚠ **判据一律不看返回值**：本模块只看「文件存在且大小 > 0」。",
    "   **实证**：空装配体**不 `Calculate`** ⇒ `SaveToAVI` **返回 `True` 而文件 0 字节**（**「返回码撒谎」**）。",
    "⇒ **升 `verified` 的条件**（一条命令）：`python tools/verify_motion_avi_e2e.py` ⇒ `verdict: pass`。",
    "   该脚本**已就位、可复跑**，会在 `D:\\AI\\SW\\output\\motion-avi-evidence.json` 落证据。",
    "⚠⚠ **并修正了我此前写下的一个错误结论**：我曾写「**「AVI 由哪个成员真正写出」尚未查证到**」——",
    "   **那是检索疏漏**：只搜了 `SaveAnimation`/`SaveMovie`/`PlayAnimation`，**没搜 `SaveToAVI`**。",
    "★ **教训：把「没搜到的词」写成「官方没有这个成员」，是**铁律 5**最危险的误用** ——",
    "   铁律 5 允许「查不到」，但**不允许「没查全就说查不到」**。",
    "⚠ 官方语义（`C:\\swapi\\types\\IMotionStudy\\SaveToAVI.md`）：「Saves the animation to a .avi, .bmp, or .tga file.」",
    "⚠ `swMotionStudyType_e` 的取值来自**反射**（`D:\\AI\\SW\\_raw\\reflect\\enum_swmotionstudy.txt`）：",
    "   Assembly=1 · PhysicalSimulation=2 · CosmosMotion=4 · LegacyCosmosMotion=8 · NewCosmosMotion=16；",
    "   官方 CHM 示例（`Create_3D_Contact_Feature_Example_*`）用的是 `swMotionStudyTypePhysicalSimulation`",
    "   ⇒ 证明 `StudyType` **是可用于设定的属性**（不是只读）。",
]


def main() -> int:
    RAW = CAP.read_text(encoding="utf-8")
    d = json.loads(RAW)
    assert json.dumps(d, ensure_ascii=False, indent=2) + "\n" == RAW, "往返不是逐字节相同 ⇒ 停"
    a = next(x for x in d["capabilities"] if x["id"] == "animation_export")
    a["limitations"] = LIMITS
    a["evidence"] = [
        "python tools/verify_motion_avi_e2e.py（verdict: fail —— 已排除 6 种条件；"
        "**根因已定位为「缺 SolidWorks Motion 加载项」**；证据 D:\\AI\\SW\\output\\motion-avi-evidence.json）",
        "python probe_motion_addin.py（算例类型可行性矩阵 + Motion 加载项 ProgID 探测）",
    ]
    CAP.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    after = json.loads(CAP.read_text(encoding="utf-8"))
    aa = next(x for x in after["capabilities"] if x["id"] == "animation_export")
    print("  animation_export: level=%s（保持）· limitations=%d 条 · evidence=%d 条"
          % (aa["level"], len(aa["limitations"]), len(aa["evidence"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
