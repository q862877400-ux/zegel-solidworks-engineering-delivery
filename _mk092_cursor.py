import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           526 🎯 **Spec Kit `092`：`mold_evidence` 从****错的接口****读 ⇒ 真机永远全 None；而假对象测试全绿**（轮 172）——
               动机：`mold_tools` 是 `stitched` 且 **evidence 为空**；它的第 3 条限度只说 headless-occt 无法复现，
               ★ 但同一条目第 1 条说「新增 `scripts/sw_mold.py`（… + `mold_evidence`）」——
               ★★ **那是我们自己的 COM 侧能力**，**可以真机验** ⇒ 本轮给它取证。
            527 ★★★ **真机结果**（`tools/probe_mold_evidence_readers.py`，新零件，**两种取法都试**）：
               ```
               IFeatureManager.GetPartingLinesCount / GetPartingSurfacesCount /
                 GetCavitySurfacesCount / GetCoreSurfacesCount   ⇒ **全 AttributeError: <unknown>.X**
               IModelDoc2.PartingType / CoreCavitySplit          ⇒ **同样不存在**
               （get_com_member 与 call_com_member **两种**取法结果一致 ⇒ 不是「取法」问题）
               ```
            528 ★★★ **根因：成员在****别的接口****上**（**事实 36** 那一族）：
               ```
               GetPartingLinesCount    ⇒ **IPartingLineFeatureData**（另有 IDraftFeatureData2 同名成员）
               GetPartingSurfacesCount ⇒ I*FeatureData（swapi 有独立说明页）
               PartingType             ⇒ **IPartingSurfaceFeatureData**
               CoreCavitySplit         ⇒ **IPartingLineFeatureData**
               ```
               ⇒ ★ 从 `FeatureManager` / `model` 上读**永远是 None** ⇒
                 **「全 None」不是「空件没有分型」，而是「读错了对象」**。
               ⚠ **要真读到**必须先拿到对应的 `I*FeatureData`（从**已存在的**分型线/分型面特征上取）
                 ⇒ ★ 前提是零件上**已经有那些特征**；空零件上**本来就取不到**（**两者表象相同，别混**）。
            529 ★★ **这是「假对象测试看不见真契约」的第 4 次**：
               ```
               99  干涉检查：三个**不存在的成员名**          ⇒ 一直绿而真机永远坏
               101 sketch_relations：**无 sw_ 前缀**被整体漏扫
               106 AddIndicator：TolType **取值不在官方清单**
               112 mold_evidence：成员**在错的接口上**      ⇒ 假对象恰好**有**它们
               ⇒ ★★ 收敛成一句：**假对象能测「逻辑」，
                 测不出「成员名 / 接口归属 / 取值 / 实参形态」** —— 这四样**只有真机能证**。
               ```
            530 ★ **处置三条**：① **如实更正** `mold_evidence` 的 docstring（写明它**在真机上只会全 None**、
               **不假装能读** —— 铁律 5）· ② 补一条**能开火**的负例测试（用**没有那些成员**的假对象 ⇒
               断言**必须是 None、不许变成 0**）⇒ 契约 **11 passed** ·
               ③ 修法（从 FeatureData 取）**需要**有分型特征的零件才能验证 ⇒ **未做**，记进限度。
               ★ **一次「判据先错」的自我更正**：我第一版判据以为 `mold_evidence` 的键是**扁平的**（报 2/6），
                 读实现才知是**嵌套的**（计数在 `counts` 里）⇒ ★ **是判据错，不是函数坏**（事实 51 那一族）。
               门禁 + `release_check` exit 0 · 回归 **1247 passed**。
               ⚑ **未查证**：⚠ **功能未修** —— `mold_evidence` **仍从旧位置读** ⇒ 真机上**仍只会全 None**；
                 ⚠ 从 `I*FeatureData` 取**需要有分型特征的零件** ⇒ 本轮**没有那样的件**，**未验证**；
                 ⚠ 「成员不在 `IFeatureManager` 上」是**真机**证实的；「它们在 `I*FeatureData` 上」
                 来自**官方源**（**未经真机调用**）；⚠ `mold_tools` **仍 `stitched`**（读取侧是空壳、
                 写入侧在未准备件上会弹框 ⇒ **没有升它**）。
               下轮候选：① 造一个有分型线/分型面特征的零件，把 `mold_evidence` **真修好**并升条目；
               ② 回到在上下文链（`SketchUseEdge3` 静默无效）；③ 扫其它 `*_evidence` 类函数**是否有同样的"读错接口"**。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+526 ", before, re.M):
    print("  游标 526 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+530 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 530 行已存在 ✓")
