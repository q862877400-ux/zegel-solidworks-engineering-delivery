            65 🎯🎯 **AVI 边界**定位到根因：缺 SolidWorks Motion 加载项**（轮 66）——
               轮 64 结束时我说「边界未定位」，轮 66 把剩下最可疑的两个候选**逐个查证**：
               ★ **① 从**反射**查到 `swMotionStudyType_e` 的官方取值表**
                 （`D:\AI\SW\_raw\reflect\enum_swmotionstudy.txt`）：
                 ```
                 swMotionStudyTypeAssembly           = 1 ← 实测拿到的默认值
                 swMotionStudyTypePhysicalSimulation = 2
                 swMotionStudyTypeCosmosMotion       = **4** ← **真正的 Motion 分析**
                 swMotionStudyTypeLegacyCosmosMotion = 8 · swMotionStudyTypeNewCosmosMotion = 16
                 ```
                 并找到官方 CHM 示例（`Create_3D_Contact_Feature_Example_*`）用
                 `swMotionStudy1.StudyType = swMotionStudyType_e.swMotionStudyTypePhysicalSimulation`
                 ⇒ **证明 `StudyType` 是可用于设定的属性**（不是只读）。
               ★ **② 新增只读探针 `D:\AI\SW\probe_motion_addin.py`，做「逐值可行性矩阵」**：
                 ```
                 set StudyType=1  (Assembly)           ⇒ 回读 1 ✅ **生效** → 导出失败
                 set StudyType=2  (PhysicalSimulation) ⇒ 回读 2 ✅ **生效** → 导出**仍失败**
                 set StudyType=4  (CosmosMotion)       ⇒ 回读 2 ❌ **静默失败**
                 set StudyType=8  (LegacyCosmosMotion) ⇒ 回读 2 ❌ **静默失败**
                 set StudyType=16 (NewCosmosMotion)    ⇒ 回读 2 ❌ **静默失败**
                 GetSupportedStudyTypes()              ⇒ com_error（by-ref 在 pywin32 下不可用，事实 47 家族）
                 Motion 加载项 4 个 ProgID（CMotionswapi.CMOTIONSWAddin / SldWorks.Motion /
                   SolidWorks.Motion / SWMotionStudy.SWMotionStudyAddin）⇒ **全返 None**
                 ```
               🔴 **根因**：**AVI 导出需要 `CosmosMotion` 系列的算例（真正的 Motion 分析），
                 而本机没有那个加载项/许可** ⇒ **环境约束，不是代码缺陷**。
               ⚠ **按 `AGENTS.md §九.4`「需要用户提供的东西 ⇒ 停下报告，不自行拍板」。**
               **需要用户提供**：**SolidWorks Motion 加载项**（装上后本域**可直接升 `verified`**）。
               **升 verified 的条件**（一条命令）：`python tools/verify_motion_avi_e2e.py` ⇒ `verdict: pass`。
               ⇒ `animation_export` **保持 `stitched`**；`limitations` 29 → **35 条**（含可行性矩阵、
                 ProgID 探测、加载项缺失、升 verified 条件）；`evidence` 1 → **2 条**（验收脚本 + 探针）。
               ★ **本轮的纪律**：**先查证据再试参数** —— 本轮没有「换个值再试」，
                 而是**先查反射拿到取值表 + 做可行性矩阵**，才发现「1 与 2 能生效、4/8/16 设不上」。
                 ⇒ 这比再瞎试 5 次有用得多。
            66 ⚠ **本轮又踩已知坑一次（已被既有门禁拦住）**：`check_provenance` 的来源块**按定义单元**覆盖 ——
               我给 `verify_motion_avi_e2e.py` 的 `main()` 前**又加了一个重复块**。
               ⚠ 而**上一轮我刚用 `GROUP_MARK` 把这些重复块合并掉** ⇒ 本轮加回来是**倒退**
               ⇒ **下次改这个文件时不要再加重复块**（已有的块带 `覆盖: 后续同级定义`）。
