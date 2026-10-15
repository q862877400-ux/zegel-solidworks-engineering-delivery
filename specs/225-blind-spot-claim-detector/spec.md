# Spec — 门禁盲区探测器的漏网：`sws[A-Z]` 名族与「反射/转储/CHM」自称

**Feature**: `specs/225-blind-spot-claim-detector/`
**日期**: 2026-10-09
**上游**: `specs/223-enum-fabrication-and-gate-boundaries/`（造出「盲区探测器」）
→ `specs/224-enum-table-disposition/`（把 44 张盲区表**逐张表态**、未表态判红）
**本轮只做一件事**：修**探测器自己**的漏网 —— 它认不出 `sws[A-Z]` 名族与「反射/转储/CHM」自称，
⇒ 有 10 张表**自称官方/反射**却**从没进过盲区清单**，因而 224 的「未表态即红」对它们**完全无效**。

---

## 一、问题（实测，不是推测）

### 1.1 探测器现状

`scripts/check_enum_values_vs_reflection.py` 的盲区探测器：

```python
CLAIM = re.compile(r"官方|swapi|sw[A-Z]\w+")     # ← 用于 find_uncovered_claimed_tables()
```

判据是「该表**未被 `# swXxx` 标注覆盖**」**且**「表起始行上方 15 行窗口里 `CLAIM` 命中」。

### 1.2 漏网之一：`sw[A-Z]` 要求 `sw` 后**紧跟大写**，`sws*` 全族不命中

```
CLAIM.search('swSolverType_e')                 → True     （sw + S）
CLAIM.search('swsSolverType_e')                → False    ✗  （sw + s）
CLAIM.search('swsTopologyDemoldDirectionOption_e') → False ✗
```

★ **`sws*` 是 Simulation/Cosworks 程序集的**整族**枚举名**（转储里 `sws*` 枚举 **300+ 个**），
而 `sw[A-Z]\w+` 把它们**一律**漏掉 —— 与 223 判过的「边界外的表静默不报」**同族**：
这次漏在**探测器的正则**里。

**放宽到 `sws?[A-Z]\w+` 后实测**：盲区 44 → **47**，新暴露 3 张，**全部未表态**：

| 文件:行 | 表 | 项 | 表上方注释自称 |
|---|---|---|---|
| `sw_simulation.py:1565` | `SWS_SOLVER_TYPES` | 7 | `swsSolverType_e`（★ 出处：本仓 `_raw` 的 cosworks 枚举页） |
| `sw_topology.py:185` | `SWS_TOPOLOGY_DEMOLD_DIRECTIONS` | 3 | `反射：swsTopologyDemoldDirectionOption_e` |
| `sw_topology.py:193` | `SWS_TOPOLOGY_ACTIVATION` | 2 | `反射：swsTopologyActivationOption_e` |

★★ **这不是「没人想过要表态」**：同文件紧邻的 `SWS_TOPOLOGY_ITERATION_OPTIONS`（`sw_topology.py:177`）
**有** `#: enum-gate: enum swsTopologyIterationOption_e` —— 它当年是被**人**顺手补的，
**不是被探测器逼出来的**（它同样不在盲区里）。⇒ 漏的是**机制**，不是**人**。

### 1.3 漏网之二：探测器只认「官方 / swapi / `swXxx`」，不认「反射 / 转储 / CHM / `_raw`」

本仓的出处自称**不止**「官方」一种写法。实测：窗口里出现「反射」「转储」「CHM」「`_raw`」的表
同样**自称有出处**，但探测器看不见。再加上 `sws` 那一条，**共 10 张**：

| 文件:行 | 表 | 项 | 拟表态 |
|---|---|---|---|
| `sw_simulation.py:1565` | `SWS_SOLVER_TYPES` | 7 | `enum swsSolverType_e` |
| `sw_topology.py:185` | `SWS_TOPOLOGY_DEMOLD_DIRECTIONS` | 3 | `enum swsTopologyDemoldDirectionOption_e` |
| `sw_topology.py:193` | `SWS_TOPOLOGY_ACTIVATION` | 2 | `enum swsTopologyActivationOption_e` |
| `sw_costing.py:75` | `COSTING_ARITY` | 25 | `not-enum arity` |
| `sw_featureworks.py:75` | `FEATUREWORKS_ARITY` | 5 | `not-enum arity` |
| `sw_pdm.py:94` | `DOCUMENT_ARITY` | 10 | `not-enum arity` |
| `sw_pdm.py:107` | `TABLE_ARITY` | 7 | `not-enum arity` |
| `sw_routing.py:84` | `ROUTING_ARITY` | 31 | `not-enum arity` |
| `sw_selection.py:99` | `SELECTION_ARITY` | 40 | `not-enum arity` |
| `sw_simulation_loads.py:304` | `_REFGEOM_POSITIONS` | 6 | `not-enum index` |

### 1.4 顺带订正上一轮的误读（★ 记录在案，防下一轮再走一遍）

224 交接单 §④ 与 ROADMAP「下一 WIP」都写着「D 类余下 **42 张**可溯源整数表的逐张表态」。
**这是误读**。实测：

```
总表 101 · 已覆盖 33 · 未覆盖 68
未覆盖 68 = 盲区 44（★ 已全部表态）+ 非盲区 24（★ 不自称官方，探测器**有意**不看）
```

那个 **42 = 44 − 2**（2 张键即官方成员名：`ANNOTATION_TYPE_BITS`、`DIALOG_SUPPRESSORS`）——
它出现在 **224 的代码注释**里（解释「为什么不能逐行补 `# swXxx`」），**不是待办数量**。
⇒ **枚举表表态线在 224 已经走完**，没有 42 张余量。本轮据此改从**真缺陷**接。

---

## 二、需求（每条带来源与许可）

### FR-001 探测器必须认得出 `sws[A-Z]` 名族

`CLAIM` 的正则从 `sw[A-Z]\w+` 改为 **`sws?[A-Z]\w+`**。

- **来源**：本仓库自身门禁 `scripts/check_enum_values_vs_reflection.py`（本仓 MIT，自研）。
- **官方依据（判据侧）**：出厂反射转储 `_raw/reflect/enum_cosworks.txt`（`sws*` 枚举节）。
- **许可**：本仓库 MIT。无第三方代码引入。
- **实测依据**：`CLAIM.search('swsTopologyDemoldDirectionOption_e')` 现为 `False`（见 §1.2）。

### FR-002 探测器必须认得出「反射 / 转储 / CHM / `_raw`」这类出处自称

`CLAIM` 追加 **`反射|转储|CHM|_raw`**。

- **来源**：同上。
- **官方依据**：`_raw/reflect/*.txt`（反射转储）· `_raw/chm_cosworks/`（CHM 解包）—— 本仓三种出处源里的两种。
- **许可**：本仓库 MIT。
- **实测依据**：追加后盲区 47 → **54**，新暴露 7 张（见 §1.3 表下半）。
- ★ **诚实边界**：`CLAIM` **仍是启发式**（窗口里出现这些词就算「自称」）。它**不**证明该表真有出处，
  只证明**该表旁边的人声称有** ⇒ 于是要求**表态**（把声称变成可核的一句话）。
  用**散文**（不含上述词）声称出处的表**仍看不见** —— 这条**登记为未过门**，不在本轮范围。

### FR-003 新暴露的 10 张表必须逐张表态

按 §1.3 表逐张在其**表起始行正上方**补一行 `#: enum-gate: <code> <arg>`（形态沿用 224 FR-002）。

- `enum <swsXxx_e>`：值集 ⊆ 该枚举取值集（`check_dispositions()` 校验）。
- `not-enum arity`：值是**实参个数**。
- `not-enum index`：值是**实参位置索引**。

- **来源**：`specs/224-.../spec.md` FR-002（声明形态）+ 本轮的实测清单。
- **官方依据**：三张 `enum` 表的枚举名与取值集**逐条核过出厂反射转储**：
  ```
  ## swsSolverType_e
    swsSolverTypeAutomatic = 0 · swsSolverTypeDirectSparse = 1 · swsSolverTypeFFEPlus = 2
    swsSolverTypeCASI = 5 · swsSolverTypeAbaqus = 6 · swsSolverTypeINTEL = 7 · swsSolverTypeINTELCluster = 8
  ## swsTopologyDemoldDirectionOption_e
    TwoDirectionMidPlane = 0 · PullDirectionOnly = 1 · Stamping = 2
  ## swsTopologyActivationOption_e
    ActivationOption_Deactivate = 0 · ActivationOption_Activate = 1
  ```
  三张表的值集分别为 `{0,1,2,5,6,7,8}` · `{0,1,2}` · `{0,1}` ⇒ **全部 ⊆ 对应枚举取值集**。
- **许可**：本仓库 MIT。
- ★ **不做**：**不逐行补 `# swXxx`** —— 这 10 张表的键是**本地语义键**（`"intel": 8`、`"Close": 0`），
  官方成员名**不在键里**；硬补只能靠人一一对表，成本高且易写错（★ 223 抓的「冒官方名」正是这类）。
  224 已经判过这个结论，本轮沿用。

### FR-004 端到端负例：自称 `sws*` 官方却未表态 ⇒ 门禁必须红

合成一棵树，里面放一张注释自称 `swsFakeEnum_e` 的整数表、**不给** `#: enum-gate:` ⇒
`check_enum_values_vs_reflection.py` 必须 **exit 1** 且**点名该表**、理由含「未表态」。

- **来源**：`specs/224-.../tests` 的同类负例（`test_undeclared_claimed_table_makes_the_gate_red`）的**镜像**。
- **为什么必须有**：★ 否则「改宽正则」这件事**没有可红的判据** —— 改前改后都能 exit 0，
  正是 223 判过的「空判据」形态。
- **官方依据**：不适用（本项目自身门禁的契约）。
- **许可**：本仓库 MIT。

### FR-005 表态可核性沿用 224 机制，不新造

`enum` 声明必须能在出厂反射里解析到 + 值集包含；`not-enum` 子类必须在封闭词表内。
**不新增** code、**不新增**子类、**不改**退出码语义（未覆盖仍**不**判罪，只判「未表态」）。

- **来源**：`specs/224-.../spec.md` FR-002/FR-005。
- **许可**：本仓库 MIT。

---

## 三、不做（明确划界）

| 不做 | 原因 |
|---|---|
| 逐行补 `# swXxx` 标注 | 键是本地语义键，硬补要靠人工对表，易写错（224 已判） |
| 把「未覆盖」也判红 | 未覆盖的表**未必**是枚举（68 张里 24 张不自称官方）⇒ 判红是**噪音**（223 已判） |
| 改 `#: enum-gate:` 的 code 词表 / `not-enum` 子类 | FR-005；改了就要重核 224 的 54 条声明 |
| 修 223 登记的 8 条 `HEAD` 即红既有失败 | 权属落在他人未提交改动内，**先确认权属** |
| `HEM_POSITIONS` 真机复核 | 需业主另行授权 COM |
| 用散文（不含 `反射/转储/CHM/_raw`）自称出处的表 | **登记为未过门**，见 §二 FR-002 诚实边界 |
| 提交 / 部署 / 打 tag / 调 COM | 硬约束 |

---

## 四、验收（可跑的命令）

```bash
# 1) 判据（受管 3.13.12）
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B tests/test_gate_blind_spot_claim.py
# 2) 门禁本体
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B scripts/check_enum_values_vs_reflection.py
# 3) 回归（223 / 224）
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B tests/test_enum_table_disposition.py
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B tests/test_gate_boundary_transparency.py
# 4) 门禁全套（★ 必须 3.14.7）
C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe scripts/release_check.py
```

期望读数：① 全绿（改动前**至少 4 例红**）；② `未表态 = 0` · `exit 0`；
③ `test_enum_table_disposition.py` 8/8 仍绿（`BASELINE_BLIND=44` 是**下界**断言，54 ≥ 44 ✓）；
④ `release_check` exit 0。
