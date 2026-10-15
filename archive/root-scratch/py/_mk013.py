import sys
from pathlib import Path
S = Path(r"D:\AI\SW\specs\013-expose-pilot-2")
S.mkdir(parents=True, exist_ok=True)

spec = """# 013 · 暴露试点（第二步）：3 个孤立能力 + 一个缺陷发现

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
"""

plan = """# 013 · Plan

**不重造**：形式与 batch1–5 一致，只加一个模块 + 一行注册 + 一个契约测试 + 一个冒烟。

## 步骤
1. 列出剩下 17 个签名兼容的孤立能力
2. 跳过「COM 辅助」与「需新解析器」两类
3. 写 `tool_specs_batch6.py`（3 条）→ 接入 `BATCH_MODULES`
4. 契约测试（含**无参函数不许注入**这条特有判据）
5. **真机冒烟** —— 这一步抓出了第 4 个候选是坏的
6. 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| **只凭签名兼容就暴露** | ★ 强制真机冒烟（`012` 的教训），本轮因此抓出 1 个坏函数 |
| 无参函数错标 `inject="model"` | 契约测试专设一条判据（SC-903）|
| 批次钉子测试红 | 已按它的设计意图更新（28）|
| 新文件漏来源块 | `check_provenance` 会抓（本轮被抓一次，已补）|
"""

tasks = """# 013 · Tasks（全部完成，轮 93）

- [x] T-901 列出剩下 17 个 → `→ 验收:` `python tools/probe_unexposed_functions.py`
- [x] T-902 跳过 COM 辅助与需新解析器两类
- [x] T-903 写 `tool_specs_batch6.py`（3 条）
- [x] T-904 接入 `BATCH_MODULES` + 批次钉子 25→28 → `→ 验收:` `python -m pytest tests/test_server_wiring.py -q`
- [x] T-905 契约测试 `tests/test_tool_specs_batch6.py`（**20 passed**）
- [x] T-906 ★ **真机冒烟** ⇒ **抓出第 4 个候选从没跑通过** ⇒ 剔除 + 立档
- [x] T-907 补 `verify_batch6_smoke.py` 的来源块（`check_provenance` 抓的）
- [x] T-908 门禁 + 回归 → `→ 验收:` `python scripts/release_check.py`（exit 0）
"""

converge = """# 013 · Converge

**Converged**: 2026-10-01（轮 93）

## 结果
| 判据 | 结论 |
|---|---|
| SC-901/902 声明 3 条、指向真实函数 | ✅ 契约测试 **20 passed** |
| SC-903 无参函数不注入 | ✅（专设判据）|
| SC-904 真机冒烟 | ✅ **4/4** |
| SC-905 暴露面 77 → **80** · 孤立 303 → **300** | ✅ |
| SC-906 缺陷入库且未纳入本批 | ✅ `docs/orphan-functions-not-runnable.md` |
| SC-907 门禁 + 回归 | ✅ `release_check` exit 0 · 回归 **1000 passed** |

## ★★ 最重要的产出：**签名兼容 ≠ 能用**
`get_mass_property_override_options` 的签名**完全兼容**、参数**完全对得上**，
但真机跑不通，**而且不是参数问题**（两条 API 路都拿不到它要的接口对象）。

★ **它是孤立函数** —— 没调用者、没测试、没人跑 ⇒ **孤立同时意味着"便宜的机会"和"从未被验证"**。
**两者必须分开处理**：暴露前**必须真机冒烟**。

⚠ **更正 `012` 的说法**：`012` 说孤立能力是「最便宜的待办（只要接出去）」——
本轮证明那句话**过于乐观**：**便宜的只是接线，可用性得单独验**。

## 不符合项 / 实测记录
1. **`check_provenance` 抓我一次**：`verify_batch6_smoke.py` 漏了来源块 ⇒ 已补。
2. **批次钉子测试红**（设计意图）⇒ 已更新到 28。

## 未查证
* **草图读回那 17 个未做**：需 `ISketch`，而 `GetActiveSketch2` 要求**编辑态** ——
  **未查证**「能不能在不进入编辑态的情况下拿到 `ISketch`」；
* **剩余 300 个孤立能力里还有多少是坏的** —— 本轮只抽了 4 个，就撞上 1 个坏的（**25%**）
  ⇒ ⚠ **这个比例如果成立，暴露工作必须先做一遍"能不能跑"的普查**。
"""

for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)
