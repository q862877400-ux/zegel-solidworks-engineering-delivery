import sys
from pathlib import Path
S = Path(r"D:\AI\SW\specs\014-callability-census")
S.mkdir(parents=True, exist_ok=True)

spec = """# 014 · 可调用性普查：暴露候选里有几个「从没跑通过」

**Status**: Implemented（轮 94）

## 背景
轮 93 抽 4 个候选就撞上 1 个坏的（`get_mass_property_override_options`），
当时估了「**约 25%** 的孤立能力是坏的」。**那是个只有 4 个样本的估计** ⇒ 本轮扩大普查。
且 `013/converge.md` 把「先做一遍能不能跑的普查」列为下轮首选。

## 范围（**故意收窄，不铺开**）
只查 `012`/`013` 认定的「**签名兼容现有注入**」的那批（**17 个**）—— 那才是真正的暴露候选。
**不查全部 300 个**：每个都要备前置条件，成本失控。

## 判据
| ID | 判据 |
|---|---|
| SC-1001 | 普查工具可跑，输出四类分类（ok / raised / needs_doc / other）|
| SC-1002 | **不下"可用"结论** —— 工具自己声明 `ok ≠ 结果正确` |
| SC-1003 | 每个 `raised` **单独复验**才能定性（普查有假阳性）|
| SC-1004 | 真缺陷入库（`docs/orphan-functions-not-runnable.md`）|
| SC-1005 | 普查**不新建/不修改/不保存**文档；收尾关掉自己开的 |
| SC-1006 | 门禁 + 回归不退化 |

## 结果（见 `converge.md`）
```
ok 14 · raised 3 ⇒ 真缺陷 **2** · 普查假阳性 **1**
⇒ 真缺陷率 ≈ **12%**（更正轮 93 的 25% 估计）
```
"""

plan = """# 014 · Plan

**不重造**：复用 `probe_unexposed_functions.py` 的候选定义；只加一个真机普查工具。

## 步骤
1. 写 `tools/census_orphan_callability.py`（17 个候选，真机各调一次）
2. 跑 ⇒ 得到 ok/raised 分档
3. ★ **每个 raised 单独复验**（普查有状态相关假阳性）
4. 定性：真缺陷 / 输入不合适 / 假阳性
5. 更新缺陷档 + 更正轮 93 的估计
6. 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| **把普查结果当结论** | SC-1002/1003：工具自己声明 `ok ≠ 正确`；raised 逐个复验 |
| COM 调用挂起 | `CommandInProgress` 抑制 + 外层作业超时 |
| 在用户文档上留改动 | 只读调用；零件用完即关（按标题，只关自己建的）|
| 又一次"估计代替测量" | 本轮正为此而做 —— 并**更正**了上轮的估计 |
"""

tasks = """# 014 · Tasks（全部完成，轮 94）

- [x] T-1001 写 `tools/census_orphan_callability.py`
  `→ 验收:` `python tools/census_orphan_callability.py`
- [x] T-1002 跑普查 ⇒ 17 个候选：**ok 14 · raised 3**
- [x] T-1003 ★ 逐个复验 raised
  ⇒ `get_extension` **单独调用是好的**（假阳性）；`create_cut_list` **真缺陷**；
  `get_mass_property_override_options` **真缺陷**（轮 93 已知）
  `→ 验收:` 见 [converge.md](converge.md) §2
- [x] T-1004 更新缺陷档（追加 `create_cut_list` + 普查结果）
  `→ 验收:` `Select-String docs\\orphan-functions-not-runnable.md -Pattern 'create_cut_list'`
- [x] T-1005 更正轮 93 的 25% 估计 ⇒ **12%**
- [x] T-1006 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
"""

converge = """# 014 · Converge

**Converged**: 2026-10-01（轮 94）

## 一、普查结果
```
17 个暴露候选（签名兼容现有注入的那批），真机各调一次：
   ok        14
   raised     3  ⇒ 逐个复验后：
        ✓ 真缺陷 2：get_mass_property_override_options · create_cut_list
        ✗ 假阳性 1：get_extension（**单独调用是好的**，连调 17 个时才报错）
```
**⇒ 真缺陷率 ≈ 2/17 ≈ 12%**。

## 二、★ 更正轮 93 的估计
轮 93 说「抽 4 个撞上 1 个坏的 ⇒ **约 25%**」。本轮证明：
* 那次样本只有 **4** 个；
* 而且那 1 个「坏的」里**不含**假阳性（那次确实是真缺陷）；
* 扩大到 17 个后，比率降到 **12%**。
⇒ **4 个样本估不出比例** —— 这正是本轮做普查的理由。

## 三、⚠⚠ 普查**自己**有假阳性（这是本轮最该记住的）
`get_extension(model)` 在普查里报 `TypeError: This dispatch object does not define a Count method`，
**单独调用却完全正常** ⇒ 失败与**前面那 16 次调用造成的状态**有关。

★ **⇒ 普查只能用来「缩小范围」；每个 raised 必须单独复验才能定性。**
否则会把**好的函数冤枉成坏的** —— 那和"坏函数被放过去"一样有害。

## 四、两个真缺陷的共性与处置
| 函数 | 症状 | 处置 |
|---|---|---|
| `sw_export.get_mass_property_override_options` | `GetMassProperties` 任何参数数都失败；`GetMassProperties2` 返回数组而非接口 | **不暴露**（轮 93 已剔除）|
| `sw_weldment.create_cut_list` | `InsertWeldmentCutList2` 在迟到绑定下解析为 `None` ⇒ 调用即崩 | **不暴露**；记档 |

★ 共性：**都是孤立函数** ⇒ **孤立 = 从没跑过 = 缺陷可以长期潜伏**。

## 五、未查证
* **剩下 283 个孤立能力**（300 − 17）**没查** —— 本轮只查了"暴露候选"那批。
  若要普查全部，需为每个备前置条件，**成本需要单独立项**；
* `create_cut_list` 的**正确调用方式**未查（不知道 `InsertWeldmentCutList2` 该用什么替代）。
"""

for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)
