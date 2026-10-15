# Contract — 307-ec05-first-part-loop 的公开接口

**Feature**: `specs/307-ec05-first-part-loop/`

**来源**: ★ **AST 提取**（★ 真签名）

---

| ★ 函数 | ★ 说明 |
|---|---|
| `readback_verdict` | ★★★★ **五项回读判定**（★ 逐字承 EC05-T05）。 |
| `reference_plate_volume` | ★★ **独立参考体积**（★ 手写公式 —— ★ **不共享被测实现**）。 |
| `reference_hole_positions` | ★★ **独立参考孔位**（★ 手写 —— ★ 等距排布）。 |
| `check_disturbance_coverage` | ★★★★ **扰动覆盖检查**（★ 逐字承验收：「★ **至少三组不同类型**参数扰动」）。 |
| `load_case_allows_strength` | ★★★★ **缺载荷 ⇒ 不给强度结论**（★ 逐字承 EC05-T01： |
| `check_dof_plan` | ★ 对外入口（★ 与 `DofPlan.is_acceptable()` 同义 —— ★ 便于判据调用）。 |
| `config_switch_verdict` | ★★★ **配置切换判定**（★ 逐字承 EC05-T07：★「★ **保存重开/配置切换/导出比较**」）。 |
| `export_compare_verdict` | ★★★ **导出比较**（★ 逐字承 EC05-T07：★「★ ……**导出比较**」）。 |
