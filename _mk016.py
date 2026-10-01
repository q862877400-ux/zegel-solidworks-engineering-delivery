import sys
from pathlib import Path
S = Path(r"D:\AI\SW\specs\016-expose-pilot-3")
S.mkdir(parents=True, exist_ok=True)

spec = """# 016 · 暴露试点（第三步·收尾）：再暴露 3 个

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
"""

plan = """# 016 · Plan

**不重造**：形式与 batch1–6 一致（一个模块 + 一行注册 + 契约测试 + 真机冒烟）。

## 步骤
1. 从 7 个剩余候选里筛：剔掉 COM 辅助与生成器 ⇒ 剩 3
2. 写 `tool_specs_batch7.py` → 接入 `BATCH_MODULES`（批次钉子 28 → 31）
3. 契约测试（沿用 batch5/6 的判据集）
4. **真机冒烟**（`014` 的教训：普查不下"可用"结论，须隔离复跑）
5. 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| 把 COM 辅助当用户操作暴露 | 逐个看签名与返回类型，辅助类**一律不取** |
| 生成器返回被注册器误处理 | **本批不动生成器**（要物化需另设计）|
| 批次钉子测试红 | 按它的设计意图更新 |
| 「普查 ok」当成「可用」 | SC-1204 要求**隔离复跑**（普查有状态相关假阳性）|
"""

tasks = """# 016 · Tasks（全部完成，轮 96）

- [x] T-1201 从剩余 7 个候选里筛出 3 个
- [x] T-1202 写 `tool_specs_batch7.py`
- [x] T-1203 接入 `BATCH_MODULES` + 钉子 28→31
  `→ 验收:` `python -m pytest tests/test_server_wiring.py -q`
- [x] T-1204 契约测试 `tests/test_tool_specs_batch7.py`（**20 passed**）
- [x] T-1205 真机冒烟 `tools/verify_batch7_smoke.py`（**4/4**）
  `→ 验收:` `python tools/verify_batch7_smoke.py`
- [x] T-1206 重生成地图/审计/digest + 同步报告数字
- [x] T-1207 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
"""

converge = """# 016 · Converge

**Converged**: 2026-10-01（轮 96）

## 结果
| 判据 | 结论 |
|---|---|
| SC-1201/1202/1203 声明正确 | ✅ 契约测试 **20 passed** |
| SC-1204 真机冒烟 | ✅ **4/4**（3 个工具 + 连接）|
| SC-1205 暴露面 80 → **83** · 孤立 300 → **295** | ✅ |
| SC-1206 门禁 + 回归 | ✅ `release_check` exit 0 · 回归 **1015 passed** |

## 三批暴露的合计（`012`+`013`+`016`）
```
接了 **11** 个工具（batch5/6/7）· 暴露面 72 → **83** · 孤立 308 → **295**
```

## ⚠ 本批的工具**只读性不齐**
`activate_model_for_preview` / `clear_selection_for_preview` / `refresh_scene_graph`
**都改了文档状态**（激活、清选择、刷新图形）—— 声明里**没标 `read_only`**（正确）。
★ 但它们**改的是视图/选择状态，不碰几何** ⇒ 风险低；
⚠ **未验证**的是：它们**是否会弄脏文档**（让 `IsDirty` 变 true）⇒ 未查。

## 未查证
* **`reset` 类操作的可逆性**：清选择/刷新图形之后，用户原来的选择**回不来** —— 未评估这算不算副作用；
* **生成器那两个**（`iter_features_recursive` / `iter_feature_tree`）能否暴露 —— 需先定「生成器怎么过注册器」，未查；
* **剩 4 个候选**（2 个 COM 辅助 + 2 个生成器）**已明确不取**，但**生成器那两个可能很有用**
  （特征树遍历对 AI 有价值）⇒ 记为**待设计**，不是否决。
"""

for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)
