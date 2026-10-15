# plan 230 · 施工方案

## 一 · 三源与冲突裁决

| 源 | 路径 | 本切片用到 |
|---|---|---|
| ① 官方 API 反射转储 | `C:/swapi`、`_raw/**/iface_*.txt` | **本切片不用**（只分类，不比签名） |
| ② CHM 解包 | `D:/AI/SW/AI Solidworks/**` | **不用** |
| ③ 仓库自身源码 | `scripts/**/*.py` | ★ **唯一源**（纯 AST） |

⇒ 本切片**没有三源冲突**（不裁决签名，只判「调用点能否静态解析出字面量」）。
★ 与 spec 227 的边界：227 是「表值 × 反射」，本切片**不碰**表值，因此
**不引入任何新约定**（FR-6 的由来）。

## 二 · 落点（**改既有门禁，不新开门禁**）

| 文件 | 改动 |
|---|---|
| `scripts/check_dispatch_entry_guard.py` | 新增 `_import_map` / `_entry_sites` / `_bind` / `_one_level_forward` / `resolution`；`_baseline()` 支持 3 或 5 值；`main()` 打印解析面 + 两条下界 + 假绿守卫 |
| `tests/test_dispatch_resolution.py` | 新增 **11 例**（真树读数 + 下界承重 + 合成树端到端） |
| `tests/test_dispatch_entry_guard.py` | **不改**（229 的 20 例回归必须继续绿） |

★ **为什么改既有门禁而不是新开**：解析面与声明面**共用同一批分发口清单**
（`scan()` 的 `entries`）。新开门禁会**第二次**计算同一批入口 ⇒ 两份清单必然漂移。
⇒ 「一个事实一个家」：分发口的定义只允许有**一处**。

## 三 · 顺序（先证能红）

1. **量**（`output/_probe230_*.py`，不进仓库代码）—— 先量清边界，再写门禁。
2. 写门禁的解析面（**先只打印**）⇒ 跑真树拿读数。
3. 写判据 ⇒ 用**合成树端到端负例**证「能红」（下界承重 + 假绿守卫）。
4. 接进 `release_check` —— ★ **不需要**：本切片改的是**既有已登记门禁**，
   `docs/gate-classification.json` 与 `release_check.py` **均不改**（门禁数不变）。

## 四 · 便携性

纯 AST + 仓内文件 ⇒ **无 SKIP 路径**。合成树开关沿用 229 的三个
（`DSH_DISPATCH_ROOT` / `DSH_DISPATCH_CLASSIFICATION` / `DSH_DISPATCH_BASELINE_MIN`）。

## 五 · 已知风险

| 风险 | 处置 |
|---|---|
| 裸名索引把同名 `def` 合并 | FR-1：按文件作用域；判据 `test_same_name_defs_are_not_merged` 钉死 |
| 二级数据流（`*局部变量`）被误判为可解析 | FR-3：严格一级判定；判据 `test_local_var_forwarding_is_not_one_level` 钉死 |
| 新下界把 229 的合成树判据判红 | `_baseline()` 3 值兼容 ⇒ 解析面下界取 0；判据 `test_old_three_value_baseline_keeps_synthetic_green` 钉死 |
| 把「解析不出」当成「没问题」 | FR-6 + §四 未过门 1：**明确写出还没接判据** |
