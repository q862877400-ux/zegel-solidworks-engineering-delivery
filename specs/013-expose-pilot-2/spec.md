# 013 · 暴露试点（第二步）：3 个孤立能力 + 一个缺陷发现

**Status**: Implemented（轮 93）

## 背景
`012` 从「签名兼容现有注入」的 22 个里接了 5 个，**还剩 17 个**。本轮接着挑。

## 跳过两类（不是随手挑剩下的）
* **COM 辅助/内部函数**（`get_extension` / `byref_pair` / `iter_features_recursive`）—— 不是用户操作；
* **需要新解析器的草图读回类**（17 个）：它们收 `ISketch`，而 `GetActiveSketch2`
  **要求草图处于编辑态** ⇒ 成本高，**本轮不做**（已记 `converge.md`）。

## 本轮接了 3 个
| 工具名 | 实现 | 为什么 |
|---|---|---|
| `solidworks_available_point_selectors` | `sw_geometry_selectors.available_point_selectors` | **无参纯读**：有哪些点选择器 |
| `solidworks_available_direction_selectors` | `sw_geometry_selectors.available_direction_selectors` | 同上，方向 |
| `solidworks_collect_assembly_bom` | `sw_delivery.collect_assembly_bom` | 装配 BOM 结构化行（**与既有 CSV 导出工具不同**）|

## ★★ 第 4 个候选被**剔除**：它从没跑通过
`sw_export.get_mass_property_override_options` **签名完全兼容**，但真机跑不通：
```
GetMassProperties(1.0) / (0) / ()            ⇒ 全部 (-2147352561, '非选择性的参数。')
GetMassProperties2(1.0, outStatus, False)    ⇒ 能跑，但**返回扁平浮点数组**（13+ 个 float）
```
⇒ 它要的 `IMassProperty2.GetOverrideOptions()` **两条路都拿不到** ⇒ **前提不成立**，
**不是"参数没调对"**。已记进 `docs/orphan-functions-not-runnable.md`。

## 判据
| ID | 判据 |
|---|---|
| SC-901 | batch6 声明 3 条，全 `solidworks_` 前缀 |
| SC-902 | 指向的函数真实存在、参数在签名里（契约测试 **20 passed**）|
| SC-903 | **无参函数不注入**（`inject=None` + `needs_model=False`）|
| SC-904 | 3 条**真机冒烟**通过（`tools/verify_batch6_smoke.py`，**4/4**）|
| SC-905 | 暴露面 **77 → 80** · 孤立 **303 → 300** |
| SC-906 | 缺陷已入库（`docs/orphan-functions-not-runnable.md`），且**未纳入本批** |
| SC-907 | 门禁 + 回归不退化（回归 **1000 passed**）|

## 明确不做
不修 `get_mass_property_override_options`（换路子要查官方 API，超出「暴露」范围）。
