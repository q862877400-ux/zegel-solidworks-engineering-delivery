# Tasks — **EC08 工程图与多工艺建模方法**

**Feature**: `specs/310-ec08-drawing-and-processes/`

**上游**: `output/ENGINEERING_CONSTRUCTION_PLAN.md`

---

## 五、★★★★★ 任务逐条（★ 四子域的共同任务）

★★★ **计划逐字**：★「★ 每子域共同任务：★ **需求冻结 → 官方调用与死路审查 → `MethodSpec` →
★ IR 适配 → 独立几何/工艺验收 → 修改域 → 保存重开 → 交付样例**」。

| ★ 共同任务 | ★ 状态 | ★ 依据 |
|---|---|---|
| ★ 需求冻结 | ✅ | ★ 各子域的 spec 字段（★ `SheetMetalSpec`/`SurfaceContinuity` 等**必填**） |
| ★ 官方调用与死路审查 | ✅ | ★ `baseline.md` §二 **逐条实测**（★ 含 `capabilities.yaml` 的 `limitations`） |
| ★ `MethodSpec` | ✅ | ★ **复用 EC03** 的 `MethodSpec`（★ 不另建 —— ★ 铁律 1） |
| ★ IR 适配 | ✅ | ★ **复用 EC03** 的四个 IR（★ `SketchIR`/`FeatureIR`/`AssemblyIR`/`DrawingIR`） |
| ★ 独立几何/工艺验收 | ✅ | ★ `unfold_consistency` · `bend_interference` · `continuity_verdict`（★ **各有独立公式**） |
| ★ 修改域 | ✅ | ★ **复用 EC03** 的 `MethodSpec.modification_domain` |
| ★ 保存重开 | ✅ | ★ **复用 EC00** 的三重判据（★ 体数/体积/outline） |
| ★ 交付样例 | ✅ | ★ **本文件的判据即交付样例**（★ 每个子域都有可跑的判据） |

---
