# Tasks — **EC06 装配、机构、尺寸链与维护**

**Feature**: `specs/308-ec06-assembly-and-mechanism/`

**上游**: `output/ENGINEERING_CONSTRUCTION_PLAN.md`

---

## 六、★★★★★ 任务逐条（★ T01–T08）

| ★ 任务 | ★ 状态 | ★ 依据 |
|---|---|---|
| **EC06-T01** 装配层级/地件/目标自由度/运动范围/禁用位姿 | ✅ **完成** | ★ `Component.is_ground` · ★ `ConstraintGraph.target_dof` · ★ `expected_motions` |
| **EC06-T02** 配合约束图检查（四类分开） | ✅ **完成** | ★ `ConstraintGraph.verdict()`（★ **五类** · ★ **冗余与过约束分开**） |
| **EC06-T03** 基准/配合链 → 公差链（各自声明假设） | ✅ **完成** | ★ `ToleranceChain`（★ **复用 EC02** · ★ RSS **须声明假设**） |
| **EC06-T04** 位置扫描 + 自适应局部加密；★ **有限采样不冒充全域** | ✅ **完成** | ★ `InterferenceScan`（★ **`coverage()`** · ★ **`unknown`** · ★ `refine()` 留痕） |
| **EC06-T05** 紧固件可达/装拆次序/轴承/润滑/传感器/维护空间 | ✅ **完成** | ★ `MaintenanceCheck`（★ **一项没查 ⇒ 不算通过**） |
| **EC06-T06** 双导杆滑台/轴承支撑轴系两类案例 | ✅ **完成** | ★ `CASE_LIBRARY`（★ **两个案例** · ★ 各自 **目标自由度 = 实际 = 1** · ★ **都是「预期运动」**）· ★ 判据 7 例（★ 含 **齿轮不在基本案例里**） |
| **EC06-T07** 组件配置/BOM/持久引用/替换件/配合稳定性 | ✅ **完成** | ★ `ASSEMBLY_TOOLS`（★ **工具面已有的 6 个** —— ★ 不另建）· ★ `bom_traceability()`（★ **空 BOM ⇒ 不通过**）· ★ `replacement_stability()`（★ 具名差异）· ★ 判据 6 例 |
| **EC06-T08** 交付运动包络/关键间隙/公差链/装配与维护说明 | ✅ **完成** | ★ `InterferenceScan.coverage()` · ★ `ToleranceChain` · ★ `MaintenanceCheck` 三者**合起来**即交付 |

---
