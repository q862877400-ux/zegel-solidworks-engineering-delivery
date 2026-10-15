# 计划 227 · `*_ARITY` 表 × 出厂反射门禁

## 一、三源与冲突裁决顺序

| 源 | 位置 | 本规格里的角色 |
|---|---|---|
| ① 官方文档 | `C:\swapi\types\<接口>\<成员>.md` | **第 0 源**。本轮用它核出 `IModelView.ShowMagnifyingGlass` 的 6 个形参 |
| ② CHM 解包 | `_raw/chm_*/` | 本例未用到（该成员在官方 md 里已给全签名） |
| ③ `_raw` 反射转储 | `_raw/**/iface_*.txt` | **门禁的机器数据源**（本门禁**只**读它做逐条比对） |

**裁决顺序**（与 `AGENTS.md` 铁律 4 一致）：① 官方 md ＞ ③ 反射转储 ＞ ② CHM；
两源冲突时**取反射**并**显式列出冲突**（既有 `check_enum_values_vs_reflection.py` 的 `CONFLICT` 段就是这一形态）。

⚠ 本规格的**约定**（by-ref 含/不含）**不是**从三源读出来的，而是从**本仓既有散文注释 + 第 4 轮量测**读出来的：
两种约定**并存**是**本仓的历史事实**，因此只能**显式声明**，不能自动推断（FR-003）。

## 二、实现

| 文件 | 动作 |
|---|---|
| `scripts/check_arity_tables_vs_reflection.py` | **新增**（门禁本体，~230 行） |
| `scripts/release_check.py` | 新增 `_run_arity_tables_gate()` + `_gate_results` 登记 + `raise` 判据（硬门禁形态） |
| `docs/gate-classification.json` | 登记 `kind: hard` / `runner: _run_arity_tables_gate` / `reason` |
| 14 张 `*_ARITY` 表的模块 | 各插 **1 行** `#: arity-reflect: byref=…`（**纯插入零删除**，由 `output/_apply_227_declarations.py` 按**表名**定位） |
| `scripts/sw_view.py` | ① 同上插 1 行；② `VIEW_ARITY['ShowMagnifyingGlass']` **5 → 6**（真缺陷，见 §四）；③ `VIEW_ARITY` 补 `#: enum-gate: not-enum arity` |

## 三、环境开关（便携性 / 可测性）

| 变量 | 作用 |
|---|---|
| `DSH_ARITY_GATE_ROOT` | 把**扫描根**指向别处 ⇒ 负例可在**合成树**上端到端跑（同 `DSH_ENUM_GATE_ROOT` 风格） |
| `DSH_ARITY_DUMPS` | 覆盖反射转储路径（多个用 `;` 分隔）⇒ 合成夹具用 |

★ 拿不到任何转储 ⇒ `[SKIP]` 且 **exit 0**（与 `check_enum_values_vs_reflection.py` 同口径：
**缺数据源 ≠ 检查失败**）。

## 四、施工中发现的两件事（★ 都必须记下来）

### 4.1 真缺陷：`VIEW_ARITY['ShowMagnifyingGlass']` 登记 5，实为 6

- 官方：`C:\swapi\types\IModelView\ShowMagnifyingGlass.md`
  `void ShowMagnifyingGlass(double Ptx, double Pty, double Ptz, double ZoomFactor, bool HideOnClick, bool FollowMouse)` = **6**，**无 by-ref**。
- 反射：`_raw/reflect_sldworks/iface_sldworks.txt:11458` = **6**。
- 本仓另一处（`scripts/sw_api_sldworks.py:6926`）也登记 **6**。
- ⇒ **三处一致对一处**，`sw_view.py` 的 5 是**孤立错值**（且在**两种约定下都不符** ⇒ 与约定无关的真错）。
  **已订正为 6**，并在表内留下出处注释。

### 4.2 ★ 踩到 225 的同一个坑（但**方向相反**）

给 `VIEW_ARITY` 插 `#: arity-reflect:` 行**本身没出事**；出事的是我在**表体内**加的那段
出处注释（含「官方」与 `C:\swapi\...`）—— `check_enum_values_vs_reflection.py` 的盲区窗口是
`lines[lo-15 : hi]`，**包含表体** ⇒ 该表**新被算作「自称官方」** ⇒ 变成**未表态盲区** ⇒ 枚举门禁**红**。
**修法**：给 `VIEW_ARITY` 补 `#: enum-gate: not-enum arity`（它**本来就是**反射派生的实参个数表，
表态是**正确**的，不是为了让门禁闭嘴）。
⇒ ★ **可复用纪律**：**表体内部**的注释也在盲区窗口里 —— 「补出处注释」这件事会**同时**影响两道门禁。
