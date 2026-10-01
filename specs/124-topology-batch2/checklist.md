# Checklist: 拓扑族第二批

- [x] **规则 1**：三个工具名都是 `solidworks_topology_create_*`（`solidworks_` 前缀，不与 `cadstudio_*` 混用）
- [x] **规则 2**：长度参数带 `_mm`（本批无长度参数）· 角度无
- [x] **规则 3**：无裸坐标（本批全是 `study` + 枚举/数值入参）
- [x] **参数名与目标函数真名一致**（`reduce_percent` / `specified_factor` / `option` / `direction` / `value` / `comparator` / `symmetry_type`）
- [x] ★ **每个枚举参数在描述里列出取值与含义**
- [x] ★ **查不到的**（对称枚举名）**如实标注**，不发明
- [x] 计数类测试**同步更新**（两处）
- [x] **不声称真机验证**（暴露 ≠ 验证；真机排 `135`）
- [x] 特性目录写完**不再改**（Flow-forward）
