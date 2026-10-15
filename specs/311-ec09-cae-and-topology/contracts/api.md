# Contract — 311-ec09-cae-and-topology 的公开接口

**Feature**: `specs/311-ec09-cae-and-topology/`

**来源**: ★ **AST 提取**（★ 真签名）

---

| ★ 函数 | ★ 说明 |
|---|---|
| `beam_tip_deflection_reference` | ★★★ **悬臂梁端部挠度**（★ 材料力学闭式解 —— ★ **独立于求解器**）。 |
| `beam_bending_stress_reference` | ★★ **梁弯曲应力**（★ 闭式解）：★ `σ = M c / I`。 |
| `engineering_verdict` | ★★★★★ **工程结论**（★ EC09 的**总判据**）。 |
| `beam_stress_under_load` | ★ 供敏感性扫描用的**响应函数**（★ 闭式解 —— ★ 独立于求解器）。 |
