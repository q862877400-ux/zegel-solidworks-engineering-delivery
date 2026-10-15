"""落盘 AVI 导出的真机证据 + 修正 capabilities.yaml 的两处。

## 修正的根据
1. **`animation_export`**：我此前写「AVI 由哪个成员写出**尚未查证到**」⇒ **那是检索疏漏**
   （只搜了 `SaveAnimation`/`SaveMovie`，**没搜 `SaveToAVI`**）。真机已证明 API 链通。
   ⇒ `not_implemented` → `stitched`（**有实现、真机验证到"导不出空算例"为止**，
     但**没有**「用真实马达导出出非零文件」的证据 ⇒ 不升 `verified`）。
2. **`motion_study`**：它的 `verified` 证据是 `tests/test_sw_motion_audit.py`，而该测试
   **把两个入口函数整个 monkeypatch 掉了** ⇒ **入口零覆盖** ⇒ 里面的 `NameError`（`Path` 未 import）
   **永远测不出来**（本轮真机一跑就炸）。⇒ 证据换成**真机证据**，
   且 `verified_versions` 从 `['2024']` 改成 **`['2026']`**（本机 2026；
   **2024 从未在本机验过** ⇒ 那个值没有根据）。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
CAP = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")

ANIM_LIMITS = [
    "⚑ **护城河域之一**（`AGENTS.md §〇`：真正全网空白的三个域是拓扑优化、动画导出 AVI、Costing）。",
    "⚑ **2026-10-01（轮 63）真机验证：API 链已全部打通**（SW 2026 SP4.1）——",
    "   `ensure_motion_type_library()` ⇒ `D:\\Program Files\\SOLIDWORKS Corp\\SOLIDWORKS\\swmotionstudy.tlb`；",
    "   `GetMotionStudyManager` ⇒ 非 None；`CreateMotionStudy` ⇒ 非 None（`GetDuration` = 4.0）；",
    "   **`CreateAVIParameter()` ⇒ 非 None**，默认值可读（`FramePerSecond=7.5` · `ImageSize=1` · "
    "`OutputType=1` · `RendererType=0` · `SaveEntireAnimation=True`）；",
    "   **`configure_avi_parameter(FramePerSecond=12)` ⇒ 回读 12.0**（写入生效）。",
    "⚠ **导出需要真实动画**：在**空装配体**上 `SaveToAVI` 导不出东西 ——",
    "   不 `Calculate` 时它**返回 `True` 而文件 0 字节**（**「返回码撒谎」的又一例**）；",
    "   `Calculate` 之后**返回 `False`、文件不存在**。⇒ 空算例没有动画可导是**合理边界**。",
    "   ⇒ 因此本模块的判据**不看返回值**，只看「文件存在且大小 > 0」。",
    "⇒ **升 `verified` 需要**：一个**真有动画**的装配体（零件 + 马达 → `Calculate` → 导出出**非零** AVI）。"
    "**这是本域下一步。**",
    "⚠⚠ **本条修正了我此前写下的一个错误结论**：我曾在 `limitations` 里写"
    "「**「AVI 文件由哪个成员真正写出」尚未查证到** ⇒ 按铁律 5 写「查不到」」。"
    "**那是检索疏漏** —— 我只搜了 `SaveAnimation` / `SaveMovie` / `PlayAnimation`，**没搜 `SaveToAVI`**，"
    "而它一直在官方反射里（`IMotionStudy` 段）。"
    "★ **教训：把「没搜到的词」写成「官方没有这个成员」，是**铁律 5**最危险的误用** ——"
    "铁律 5 允许「查不到」，但**不允许「没查全就说查不到」**。",
    "⚠ 官方语义（`C:\\swapi\\types\\IMotionStudy\\SaveToAVI.md`）：「Saves the animation to a "
    "**`.avi`**, **`.bmp`**, or **`.tga`** file.」⇒ 同一成员也能出 bmp / tga。",
    "⚠ API 索引层（`scripts/sw_api_swmotionstudy.py`）**早就登记了** `'SaveToAVI': 2` 与 "
    "`'CreateAVIParameter': 0` —— 也就是说**答案一直躺在仓库里，只是没人去实现它**。",
]

MOTION_LIMITS_ADD = [
    "⚑ **2026-10-01（轮 63）真机跑通入口链**：`ensure_motion_type_library()` ⇒ "
    "`D:\\Program Files\\SOLIDWORKS Corp\\SOLIDWORKS\\swmotionstudy.tlb`；"
    "`get_motion_study_manager(装配体)` ⇒ 非 None；`create_motion_study()` ⇒ 非 None"
    "（`GetDuration()` = 4.0）。",
    "🔴 **同时修掉一个真 bug**：本模块 `import` 区**没有 `from pathlib import Path`**，"
    "而 `_motion_typelib_candidates()` 里用了 `Path(executable)` ⇒ **`NameError`** ⇒ "
    "**整条 Motion 路径在真机上根本走不通**。该 bug 能存活至今，是因为 "
    "`tests/test_sw_motion_audit.py` 把 `get_motion_study_manager` / `ensure_motion_type_library` "
    "**两个入口整个 monkeypatch 掉了** ⇒ **入口零覆盖**。"
    "⇒ 契约测试已补「入口可调用且不抛 NameError」的断言（不连真机）。",
    "⚠ `verified_versions` 由 `['2024']` 改为 **`['2026']`** —— 本机是 **2026 SP4.1**，"
    "而 **2024 从未在本机验过** ⇒ 原来的值**没有根据**。",
]


def main() -> int:
    RAW = CAP.read_text(encoding="utf-8")
    d = json.loads(RAW)
    assert json.dumps(d, ensure_ascii=False, indent=2) + "\n" == RAW, "往返不是逐字节相同 ⇒ 停"

    # ① animation_export：not_implemented → stitched
    a = next(x for x in d["capabilities"] if x["id"] == "animation_export")
    old_a = a["level"]
    a["level"] = "stitched"
    a["limitations"] = ANIM_LIMITS
    a["evidence"] = []          # ⚠ 没有「导出非零文件」的证据 ⇒ 留空，不编
    a["source"] = "original"
    a["source_evidence"] = (
        "实现模块 `scripts/sw_motion.py` 的 AVI 三函数（`create_avi_parameter` / "
        "`configure_avi_parameter` / `export_motion_study_avi`）**不在** `origin/main` ⇒ 我们新增；"
        "签名照 `swmotionstudy` 官方反射；**无** `provenance` ⇒ 与 `original` 自洽（R13）")

    # ② motion_study：改 verified_versions + 追加两条 limitations
    m = next(x for x in d["capabilities"] if x["id"] == "motion_study")
    old_vv = list(m["verified_versions"])
    m["verified_versions"] = ["2026"]
    m["limitations"] = list(m.get("limitations") or []) + MOTION_LIMITS_ADD

    CAP.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    after = json.loads(CAP.read_text(encoding="utf-8"))
    from collections import Counter
    aa = next(x for x in after["capabilities"] if x["id"] == "animation_export")
    mm = next(x for x in after["capabilities"] if x["id"] == "motion_study")
    print("  animation_export: %s → **%s**（evidence 留空：没有'导出非零文件'的证据）" % (old_a, aa["level"]))
    print("  motion_study.verified_versions: %s → %s" % (old_vv, mm["verified_versions"]))
    print("  level 分布: %s" % dict(Counter(x["level"] for x in after["capabilities"])))
    print("  护城河三域：")
    for mid in ("topology_optimization", "costing", "animation_export"):
        x = next(y for y in after["capabilities"] if y["id"] == mid)
        print("    %-24s %s / %s" % (mid, x["level"], x["source"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
