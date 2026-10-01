# 016 · 暴露试点（第三步·收尾）：再暴露 3 个

**Status**: Implemented（轮 96）

## 背景
候选来自「签名兼容现有注入」那批（17 个）。`012`（5 个）+ `013`（3 个）共接 8 个；
`014` 普查定性 **2 个坏了**（已记档 + 改成失败可见）。**剩 7 个**，本批取 3 个收尾。

## 本批取的 3 个
| 工具名 | 实现 |
|---|---|
| `solidworks_activate_model_for_preview` | `sw_review.activate_model_for_preview` |
| `solidworks_clear_selection_for_preview` | `sw_review.clear_selection_for_preview` |
| `solidworks_refresh_scene_graph` | `sw_render_material.refresh_scene_graph` |

## 明确**不取**的 4 个（各有理由，不是挑剩下的）
| 函数 | 理由 |
|---|---|
| `sw_render_material.get_extension` | **COM 辅助**（返回 `IModelDocExtension`），不是用户操作 |
| `sw_com_traps.byref_pair` | **COM 辅助**（构造 BYREF 对）|
| `sw_weldment.iter_features_recursive` | **生成器** —— 注册器按值传参/返回，需先物化；**本批不动** |
| `sw_assembly.iter_feature_tree` | 同上 |

## 判据
| ID | 判据 |
|---|---|
| SC-1201 | batch7 声明 3 条，全 `solidworks_` 前缀 |
| SC-1202 | 指向的函数真实存在、参数在签名里（契约测试 **20 passed**）|
| SC-1203 | 首参 `model` 的注入 `model`；无参的不注入 |
| SC-1204 | 3 条**真机冒烟**通过（**4/4**），且工具**不新建/不修改/不保存**文档 |
| SC-1205 | 暴露面 **80 → 83** · 孤立 **300 → 295** |
| SC-1206 | 门禁 + 回归不退化（回归 **1015 passed**）|
