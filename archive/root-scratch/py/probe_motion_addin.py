r"""@brief 只读探针：本机 **SolidWorks Motion 加载项**与**算例类型支持**。

## 为什么探这一条（2026-10-01 轮 66）
`animation_export` 的真机验收卡在 `SaveToAVI` 返 `False`（已排除 5 种条件）。
轮 66 从**反射**查到 `swMotionStudyType_e` 的官方取值：
```
swMotionStudyTypeAssembly           = 1   ← 实测拿到的默认值
swMotionStudyTypePhysicalSimulation = 2
swMotionStudyTypeCosmosMotion       = 4   ← **真正的 Motion 分析（COSMOS Motion）**
swMotionStudyTypeLegacyCosmosMotion = 8 · swMotionStudyTypeNewCosmosMotion = 16
```
而**把 `StudyType` 设成 4 之后回读仍是 1** ⇒ **赋值静默失败**。
⇒ 本探针查「是不是因为 **Motion 加载项不可用**」——**只读，不改任何设置**。

# ── 来源 ──
# 仓库:   本项目自身（真机判定 · 只读诊断）
# 文件:   D:\AI\SW\probe_motion_addin.py
# 定位:   给 `animation_export` 的边界定性：是**代码问题**还是**环境约束**。
# 官方签名依据: `IMotionStudyManager::GetMotionStudyManager` ·
#         `IMotionStudy::get_StudyType` / `set_StudyType` ·
#         `IMotionStudy::GetSupportedStudyTypes(Int32&)`（`iface_swmotionstudy.txt`）
#         · `swMotionStudyType_e`（`enum_swmotionstudy.txt`）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 连真机；**只读**；只用自己新建的文档；收尾恢复 CommandInProgress。
# ─────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

_REPO = Path(r"C:\swprojects\sw-skill-fork")
for _p in (str(_REPO), str(_REPO / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.stdout.reconfigure(encoding="utf-8")

from scripts.sw_connect import connect_solidworks, get_com_member, new_document  # noqa: E402
from scripts import sw_motion as M  # noqa: E402

#: 已知的 Motion 相关 ProgID（注册表实测：只有 `CMotionswapi.CMOTIONSWAddin[.18]`）
PROGIDS = (
    "CMotionswapi.CMOTIONSWAddin",
    "SldWorks.Motion",
    "SolidWorks.Motion",
    "SWMotionStudy.SWMotionStudyAddin",
)

TYPES = {1: "Assembly", 2: "PhysicalSimulation", 4: "CosmosMotion",
         8: "LegacyCosmosMotion", 16: "NewCosmosMotion"}


def step(label, fn):
    try:
        v = fn()
        print("   %-46s ⇒ %r" % (label, v))
        return v
    except Exception as exc:  # noqa: BLE001
        print("   %-46s ⇒ ✗ %s: %s" % (label, type(exc).__name__, str(exc)[:110]))
        return None


def main() -> int:
    sw, _m, _meta = connect_solidworks(wait_seconds=20, return_metadata=True)
    sw.CommandInProgress = True
    title = None
    try:
        print("=== ① Motion 加载项 ProgID 试探 ===")
        for pid in PROGIDS:
            step("GetAddInObject(%r)" % pid, lambda p=pid: sw.GetAddInObject(p))

        print()
        print("=== ② 建装配体 + 算例，查「支持的算例类型」 ===")
        asm = new_document(sw, doc_type="assembly")
        title = get_com_member(asm, "GetTitle")
        print("   文档: %r" % title)
        mgr = step("get_motion_study_manager(asm)", lambda: M.get_motion_study_manager(asm))
        if mgr is None:
            print("   ⚠ 拿不到 manager ⇒ 停")
            return 2
        study = step("create_motion_study(asm)", lambda: M.create_motion_study(asm))
        if study is None:
            return 2

        print()
        print("=== ③ get_StudyType（当前）===")
        cur = step("study.StudyType", lambda: M.motion_member(study, "StudyType"))
        print("   ⇒ %r = %s" % (cur, TYPES.get(cur, "（未知）")))

        print()
        print("=== ④ GetSupportedStudyTypes（**by-ref，可能不可用**）===")
        step("GetSupportedStudyTypes()", lambda: M.motion_member(study, "GetSupportedStudyTypes"))

        print()
        print("=== ⑤ 逐个试探 set_StudyType（**只读目的：看能不能设上**）===")
        for t, name in sorted(TYPES.items()):
            ok = step("set StudyType=%d（%s）" % (t, name),
                      lambda tt=t: setattr(study, "StudyType", tt) or True)
            if ok:
                back = step("   回读", lambda: M.motion_member(study, "StudyType"))
                print("        ⇒ 设 %d（%s）回读 %r %s"
                      % (t, name, back,
                         "**生效**" if back == t else "**未生效（静默失败）**"))
        # 还原成 1（Assembly），别留副作用
        try:
            study.StudyType = 1
        except Exception:  # noqa: BLE001
            pass
        return 0
    finally:
        try:
            if title:
                sw.CloseDoc(title)
        except Exception:  # noqa: BLE001
            pass
        try:
            sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass
        print()
        print("收尾完成（文档未保存；CommandInProgress 已恢复）")


if __name__ == "__main__":
    raise SystemExit(main())
