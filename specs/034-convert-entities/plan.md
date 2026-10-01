# 034 · Plan

## 步骤
1. 确认 `convert_entities` 确实没实现
2. ★ **先查废弃**：`SketchUseEdge2` 已 Obsolete ⇒ 在 `ConvertEntities()` 与
   `SketchUseEdge3` 之间选 ⇒ 取后者（两参都有官方说明）
3. **并进已有模块** `sw_sketch_edit.py`（不新开文件）
4. 写实现 + 6 条契约测试
5. ★ 扩 `sketch_edit_ops` 能力条目（**不新增条目**）
6. 重生成 + 门禁 + 回归 → 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| 用了已废弃的 `SketchUseEdge2` | ★ 测试断言实现段里**不出现**该名字；来源块记下原因 |
| 把返回 `False` 吞掉 | ★ 单列一条测试（`False` 是假值，最容易被 `if not got: pass` 吞）|
| 为一条功能新开一个模块 | ★ **并进同类模块**（`sw_sketch_edit.py`）—— 不重造 |
| 顺手改别的 | 本轮**只加这一个函数** |
