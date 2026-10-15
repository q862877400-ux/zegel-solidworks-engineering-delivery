"""把 `animation_export` 的真机边界如实记进 capabilities.yaml（**不升 verified**）。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
CAP = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")

LIMITS = [
    "⚑ **护城河域之一**（`AGENTS.md §〇`：真正全网空白的三个域是拓扑优化、动画导出 AVI、Costing）。",
    "⚑ **2026-10-01（轮 63/64）真机验证：API 链已全部打通**（SW 2026 SP4.1）——",
    "   `ensure_motion_type_library()` ⇒ `D:\\Program Files\\SOLIDWORKS Corp\\SOLIDWORKS\\swmotionstudy.tlb`；",
    "   `GetMotionStudyManager` / `CreateMotionStudy` ⇒ 非 None；`CreateAVIParameter()` ⇒ 非 None，",
    "   默认值可读（`FramePerSecond=7.5` · `ImageSize=1` · `OutputType=1` · `SaveEntireAnimation=True`）；",
    "   `configure_avi_parameter(FramePerSecond=10)` ⇒ **回读 10.0**（写入生效）。",
    "⚑ **马达也真机建成了**：`add_constant_speed_rotary_motor_by_cylinders` ⇒ `AEMRotationalMotor`（type_id 102），",
    "   且 `collect_motion_study_summary` 显示该算例 `motor_count=1` · `results_out_of_date=False`（**结果新鲜**）。",
    "🔴 **但 `SaveToAVI` 始终返回 `False` 且不产出文件** —— 已试 **5 种条件组合，全部排除**：",
    "   ① 空装配体（不 `Calculate`）⇒ 返回 `True` 但文件 **0 字节**（**「返回码撒谎」**）；",
    "   ② 空装配体 + `Calculate` ⇒ 返回 `False`、无文件；",
    "   ③ 有马达的装配体 + 挑出**含马达的那个算例** + `ActivateMotionStudy` ⇒ 返回 `False`、无文件；",
    "   ④ 再加「**保存装配体**（有磁盘路径）」⇒ 仍 `False`；",
    "   ⑤ 再加「**先 `Play` 一遍**」⇒ 仍 `False`。",
    "⚠ **未定位到根因**。剩下的候选**未验证**（按铁律 5 不猜）：",
    "   • 算例类型 —— 实测 `StudyType == 1`，但其**语义在 `C:\\swapi\\enums` 里查不到**（不臆断它是不是「基本运动」）；",
    "   • 两个组件**没有加 mates**（都浮动）⇒ 运动学可能无解；",
    "   • 是否需要 **SolidWorks Motion 加载项**（而非仅基本运动）；",
    "   • 是否需要 **UI 交互/特定许可**。",
    "⚠ **判据一律不看返回值**：本模块只看「文件存在且大小 > 0」（上面 ① 就是返回值撒谎的实证）。",
    "⇒ **升 `verified` 的条件**：一条 `python tools/verify_motion_avi_e2e.py` ⇒ `verdict: pass`。",
    "   该脚本**已就位、可复跑**，会在 `D:\\AI\\SW\\output\\motion-avi-evidence.json` 落证据。",
    "⇒ **本轮的价值**：把这一域从「**查不到**」推进到「**API 可用、条件未定位**」——",
    "   前者是**结论**（会让人放弃），后者是**待办**（有明确的下一步与已排除清单）。",
    "⚠⚠ **并修正了我此前写下的一个错误结论**：我曾写「**「AVI 由哪个成员真正写出」尚未查证到**」——",
    "   **那是检索疏漏**：只搜了 `SaveAnimation`/`SaveMovie`/`PlayAnimation`，**没搜 `SaveToAVI`**。",
    "★ **教训：把「没搜到的词」写成「官方没有这个成员」，是**铁律 5**最危险的误用** ——",
    "   铁律 5 允许「查不到」，但**不允许「没查全就说查不到」**。",
    "⚠ 官方语义（`C:\\swapi\\types\\IMotionStudy\\SaveToAVI.md`）：「Saves the animation to a .avi, .bmp, or .tga file.」",
]


def main() -> int:
    RAW = CAP.read_text(encoding="utf-8")
    d = json.loads(RAW)
    assert json.dumps(d, ensure_ascii=False, indent=2) + "\n" == RAW, "往返不是逐字节相同 ⇒ 停"
    a = next(x for x in d["capabilities"] if x["id"] == "animation_export")
    old = a["level"]
    a["level"] = "stitched"          # 不变：没有「导出非零文件」的证据
    a["limitations"] = LIMITS
    a["evidence"] = [
        "python tools/verify_motion_avi_e2e.py（本轮 verdict: fail —— 已排除 5 种条件组合；"
        "证据 D:\\AI\\SW\\output\\motion-avi-evidence.json）",
    ]
    CAP.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    after = json.loads(CAP.read_text(encoding="utf-8"))
    from collections import Counter
    aa = next(x for x in after["capabilities"] if x["id"] == "animation_export")
    print("  animation_export: %s → %s（**保持 stitched**）" % (old, aa["level"]))
    print("  limitations: %d 条（含 5 项已排除条件 + 4 项未验证候选）" % len(aa["limitations"]))
    print("  level 分布: %s" % dict(Counter(x["level"] for x in after["capabilities"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
