# Tasks — **EC09 CAE 和拓扑优化可信纵切片**

**Feature**: `specs/311-ec09-cae-and-topology/`

**上游**: `output/ENGINEERING_CONSTRUCTION_PLAN.md`

---

## 五、★★★★★ 任务逐条（★ T01–T08）

| ★ 任务 | ★ 状态 | ★ 依据 |
|---|---|---|
| **EC09-T01** 简单梁/板静力基准 + 独立参考解 | ✅ **完成** | ★ `beam_tip_deflection_reference()` · `beam_bending_stress_reference()`（★ **闭式解**） |
| **EC09-T02** AnalysisIR（八项） | ✅ **完成** | ★ `AnalysisIR.completeness()`（★ 八项） |
| **EC09-T03** 几何/单位/刚体/约束与载荷平衡；★ **缺失不得默认求解后通过** | ✅ **完成** | ★ `ReactionBalance` · ★ `AnalysisIR`（★ **缺项 ⇒ 明写「不得以默认值求解后通过」**） |
| **EC09-T04** ≥3 档网格收敛；★ **奇异峰值不能追峰** | ✅ **完成** | ★ `MeshConvergence`（★ **`peak_chasing`** 独立结论） |
| **EC09-T05** 分开 verification/validation/不确定性 | ✅ **完成** | ★ `VerificationKind`（★ **三类分开**）· ★ `ValidationScope` |
| **EC09-T06** 设计敏感性与保守边界；优化输入/不可改域冻结 | ✅ **完成** | ★ SensitivityScan（★ **归一化敏感性排序** · ★ **不可改域必须冻结**）· ★ 判据 6 例 |
| **EC09-T07** 拓扑结果重构后**重新分析**；★ **不把云图直接交制造** | ✅ **完成** | ★ `engineering_verdict(reanalyzed_after_optimization=…)`（★ **没复分析 ⇒ 不通过**） |
| **EC09-T08** 未支持物理领域拒绝或升级 | ✅ **完成** | ★ `AnalysisIR.constitutive`/`applicability`（★ **必填** ⇒ 未支持领域**填不出来** ⇒ 拒） |

---
