# 扫描 S2-b · 台账 → 工具（反向差集 + level 对账）

**性质**：只读扫描。**未改动任何既有文件**；**未运行 SolidWorks**；**未运行 pytest**。
**唯一新建文件**：本文件。

**快照（可复算）**：`2026-10-03 21:03` 本机 · `git HEAD = f41268b` · `capabilities.yaml` = **421 108 B** · `sha256[:12] = 62e477ce42e3` · mtime `2026-10-03 18:57:41`。

> ⚠⚠ **工作树在本扫描期间被并发改动**（实测：`git rev-parse --short HEAD` 在 20:59 读到 `b5a3f9b`、21:01 读到 `c17df43`、21:03 读到 `f41268b`；`git status` 期间出现过 `M scripts/sw_sheet_metal_weld_entry.py`、`M specs/202-user-coverage-gaps/recon/scan-S2a-tools-not-in-ledger.md`）。
> ⇒ **本表所有数字只对上面那个快照成立**；重跑时请先核对 `capabilities.yaml` 的 `sha256[:12]` 是否仍为 `62e477ce42e3`。

---

## 〇 · 两侧各自的取法（口径是我定的，不是抄来的）

| 侧 | 取法 | 命中数 |
|---|---|---|
| **① 台账条目** | `capabilities.yaml` 的 `capabilities[]`。⚠ 该文件**内容是 JSON**（首字符 `{`，`schema_version = "2.0"`），扩展名 `.yaml` 是历史遗留 ⇒ 按 JSON 解析 | **110** 条 |
| **② 工具名** | 见下 §〇·②，共**三条注册路**，全部**并集**记账 | **313** 个 |

### 〇·② 工具名的三条路（**AST 静态抽名，不 import 任何模块 ⇒ 不碰 COM**）

| 路 | 位置 | 抽名判据 | 命中 |
|---|---|---|---|
| **L1 ToolSpec 路** | `mcp-server/tool_specs_batch*.py`（**74** 个文件）+ `register_capabilities.py` 的 `BATCH_MODULES` | `ast.Call` 的 ①`name=` 关键字字符串 **或** ②**第一个位置实参**且整串匹配 `^(solidworks\|cadstudio)_[a-z0-9_]+$`；再与 `BATCH_MODULES` 求交（只有被注册的批次才算数） | **268**（唯一名 268，重名 0） |
| **L2 装饰器路** | `mcp-server/server.py` | `@mcp.tool(name=…)`，且 `name` 值整串匹配上述正则 | **45** |
| **L3 声明了但未注册** | `tool_specs_batch*.py` − `BATCH_MODULES` | 同 L1 判据，再取差集 | **0** |
| **合计（L1 ∪ L2）** | | | **313** |

**为什么要拆三条路**：本仓有两条注册路，且 **`all_specs()` 只能看见 L1** —— `docs/known-facts.md` 事实 364 记的就是这件事（L1 + L2 才是真实暴露面）。**只数一条会少算近一半。**

**⚠ 一处必须写明的坑（否则本表会假报 19 个"工具不存在"）**：
部分批次（实测 `tool_specs_batch29.py:116/129/140/150`、`tool_specs_batch30.py:82` …）**不走字面量 `ToolSpec(name=…)`，而是走本文件内的工厂函数 `_spec("工具名", …)`**。
⇒ ★ **只按 `ToolSpec(...)` 抽名，会把 `solidworks_simulation_apply_pressure` / `…_gravity` / `…_torque` / `…_centrifugal_force` / `solidworks_topology_collect_numbers` / `…_list_constraints` / `…_manager_report` / `…_options_report` / `solidworks_topology_set_goal` / `solidworks_topology_set_iteration_options` / `solidworks_simulation_apply_{elastic_connector,convection,heat_flux,heat_power,radiation,distributed_mass,force,temperature,remote_load}` 全部漏掉**（实测第一版就是 **19 个假阳性**，加上「首个位置实参」判据后归零）。**本表采用后者。**

**⚠ 一处必须剔除的假阳性**：`server.py:136` 有字符串 `"solidworks_mcp"`（是**模块名**、不是工具名）。它会被宽判据命中 ⇒ **L2 严格取 `@mcp.tool(name=)` 得 45；若用宽判据会得 46。多出的那 1 个就是它。**

---

## 一 · 表 C —— `level` 分布计数

| `level` | 条数 | 占比 |
|---|---|---|
| `verified` | **97** | 88.2 % |
| `stitched` | **12** | 10.9 % |
| `not_implemented` | **1** | 0.9 % |
| `source_verified` | **0** | — |
| **合计** | **110** | 100 % |

- ★ **本清单实际只出现 3 个取值**（实测 `sorted({c["level"] for c in caps})` = `['not_implemented','stitched','verified']`）。
- ★ `source_verified` 为 **0** ⇒ 这与 `AGENTS.md` A2 验收判据里写的「现 `source_verified` 条目数为 0，故②空满足」**一致**（本次独立复核通过）。
- ⚠ 五级枚举的**全集**是 `verified / source_verified / stitched / indexed / not_implemented`（`scripts/capabilities.py:22` 的 `VALID_LEVELS`）—— ★ **`indexed` 本清单一条都没有**（清单里查不到该取值）。
- 按侧交叉：**挂工具的 69 条**与**没挂工具的 41 条**的 level 分布见 §二 A 表末与 §三 B 表。

---

## 二 · 表 A —— **台账有、但 `mcp_tools` 无挂**的条目 —— **41 条**

> ★ 这是"**已实现但没暴露**"的候选池。判据：`not (cap.get("mcp_tools") or [])` ⇒ **字段缺失（40 条）** 与 **字段存在但为空列表（1 条：`render_material_library`，`level: verified`）** 都算。
> ⇒ ⚠ 这两种形态**不是一回事**（缺字段 = 没填；空列表 = 填了"无"），但**对"有没有工具挂"这个问题上等价**，故合并计数并单列标注。

### ⚠ 分组口径声明（**不是官方域标签**）

★ **`capabilities.yaml` 里没有 `domain` 字段** —— 实测 110 条的键集合只有
`{allowed_modes, backends, dependencies, evidence, id, label, level, limitations, mcp_tools, provenance, skills, source, source_evidence, title, verified_versions}`，**无 `domain` / `category` / `tags`** ⇒ 按铁律 5，**"能力域"在本清单里查不到**。
★ 全仓也**没有** `capability id → 域` 的映射表（实测：`scripts/capabilities.py`、`tools/build_toolbar_ledger.py`、`tools/build_union_map.py` 里都没有这张表；`docs/user-feature-coverage.md` §四 的 11 个域只作用在**另一张 145 项功能表**上，与 `capabilities.yaml` 的 id **对不上**）。
⇒ **本表按 `id.split("_")[0]`（首个下划线分段）分组** —— 这是**字符串分段、可机器复算**的规则，★ **不是域的权威判定**；每行同时带出 `backends[0]`，便于换口径重排。

### A 表（按 `id` 首段分组，组内按 id 升序）

| 组 | 条数 | 条目 |
|---|---|---|
| **sketch** | **12** | `sketch_primitives_b1`¹ `sketch_edit_ops_b3`¹ `sketch_modify_ops` `sketch_dimension_horizontal` `sketch_dimension_vertical` `sketch_slot_types` `sketch_line2` `sketch_spline` `sketch_spline3_2d` `sketch_rotate_or_copy_3d` `sketch_equation_curve` `sketch_offset_on_surface` |
| **surface** | **10** | `surface_modeling`² `surface_edit_ops` `surface_ref_ops` `surface_thicken_silent_noop`² `surface_offset` `surface_planar_region` `surface_revolve` `surface_flatten` `surface_untrim` `surface_delete_hole` |
| **feature** | **5** | `feature_readback_criterion` `feature_revolve_cut` `feature_loft_cut` `feature_cosmetic_thread` `feature_hole_wizard5` |
| **autocad** | **3** | `autocad_basic_drafting`³ `autocad_script_backend` `autocad_dotnet_backend` |
| **curve** | **2** | `curve_and_split` `curve_through_xyz` |
| **animation** | 1 | `animation_export`² |
| **coverage** | 1 | `coverage_gap_batch1` |
| **drawing** | 1 | `drawing_dimension_insertion` |
| **geometric** | 1 | `geometric_tolerance`² |
| **ref** | 1 | `ref_geometry` |
| **render** | 1 | `render_material_library`⁴ |
| **replace** | 1 | `replace_face` |
| **requirements** | 1 | `requirements_planning`⁵ |
| **select** | 1 | `select_by_ray` |
| **合计** | **41** | |

¹ `mcp_tools` 字段**缺失**（40 条中的一条）· ² `level: stitched`（共 4 条）· ³ `level: not_implemented`（全清单唯一 1 条）· ⁴ `mcp_tools: []`（**空列表**，不是缺字段）· ⁵ 见下方★注。

**A 表按 level：** `verified` **36** · `stitched` **4** · `not_implemented` **1** ⇒ **合计 41**。

> ★ **`requirements_planning` 不该算进"已实现但没暴露"**：它自己的 `limitations[0]` 逐字写着「**本条不挂工具 —— 理由写明**：★ 它是需求分析与工程规划（★ 一个**流程能力**，不是 COM 操作）⇒ ★ 它的实现在**编排层**…… ⇒ ★★ 所以**没有"工具"这种形态可挂**」。
> ⇒ ★ 这是**台账自己写明的豁免**，不是缺口。扣除它后，"候选"实为 **40 条**。

---

## 三 · 表 B —— **两边都有的**：核 `level: verified` 的条目，工具是否真存在

| 项 | 数 |
|---|---|
| 台账**挂了工具**的条目 | **69** |
| 这些条目引用的工具名（去重） | **226** |
| ★ **其中在 L1 ∪ L2 里查不到的** | **0** |
| `level: verified` 条目总数 | **97** |
| ├─ 其中**挂了工具** | **61** |
| └─ 其中**没挂工具**（= 表 A 里的 verified） | **36** |
| ★ **`verified` 条目引用了不存在的工具**的条数 | **0** |

**★ 结论**：`level: verified` 的条目所声明的工具，**226 个引用全部命中真实工具名，0 悬空**。
⇒ ★ 但要说清这个"0"**证明不了什么更强的事**：它只说明**台账写的工具名与工具面一致**，**不代表工具能建成**（那要看 `evidence`，不在本表口径内）。

### B 附：反向一个数（与 S2-a 同源，此处只作交叉引用，不重复其表）

- **被台账引用过的工具：226**；**工具面 313** ⇒ **87 个工具没有被任何能力条目认领**。
- ⚠ 这一侧由 `specs/202-user-coverage-gaps/recon/scan-S2a-tools-not-in-ledger.md` 负责，**本表不重复其结论**。
- ★ 交叉校验：226 + 87 = 313 ✔ 与 §〇·② 的工具面总数自洽。
- ⚠ 仓库内已有 `tools/check_tool_capability_coverage.py` 做同一件事，但它**只看 L1**（`rc.all_specs()`，实测 268 个）⇒ ★ **用它跑出来的"未被认领"会多算 L2 的 45 个**，且其 docstring 里的 `117 个工具` / `58 条能力` 是**轮 265 的旧快照、已过期**（当前 268 / 110）。

---

## 四 · 本扫描明确**查不到**的（铁律 5）

| # | 查不到的东西 | 实测依据 |
|---|---|---|
| 1 | **能力 id → 能力域的权威映射** | `capabilities.yaml` 无 `domain`/`category`/`tags` 字段；全仓无该映射表（§二 口径声明） |
| 2 | `level: indexed` 的条目 | 清单里该取值 **0** 条（`VALID_LEVELS` 里有它，清单里没有） |
| 3 | 挂在这些条目上的工具 | 表 A 的 41 条**没有** `mcp_tools` ⇒ ★ **不是"查不到工具存在"，而是"台账从未声明过要哪个工具"** —— 本表**不替它猜**（按名字相近去匹配 = 铁律 5 明令禁止） |
| 4 | 工具**能否建成 / 有无运行证据** | 本表只做**名字层**对账；`evidence` 字段与真机状态不在口径内 |

---

## 五 · 复算方法（本表每一行都可独立重算）

```
① 台账：json.loads(capabilities.yaml)["capabilities"]            → 110 条 / level 分布 / mcp_tools 存在性
② 工具：ast.parse(mcp-server/server.py)          → @mcp.tool(name=…)            → 45
       ast.parse(mcp-server/tool_specs_batch*.py) → name= 或 首个位置实参匹配正则    → 每批一份
       ast.parse(mcp-server/register_capabilities.py) → BATCH_MODULES（74 项）     → 只保留在册批次
③ 对账：TOOLS = L1 ∪ L2；A = {c : not c.get("mcp_tools")}；B = {c 的每个 mcp_tools 项 ∈ TOOLS}
```
⚠ **全程不 `import` 任何项目模块** —— 这是刻意的：`import` 批次模块会把 `scripts.sw_connect` 拉进来，与"不许跑 SolidWorks"的约束擦边；且 `batch17` 顶层就有 `from scripts.sw_connect import deg`。**AST 抽名对"名字层"对账是完备的**（工具名在两类声明里都是字面量字符串）。

---

## 六 · 与本轮其它扫描的分工

| 文件 | 方向 |
|---|---|
| **本文件（S2-b）** | **台账 → 工具**（差集 A）· 名字层对账（B）· level 分布（C） |
| `scan-S2a-tools-not-in-ledger.md` | **工具 → 台账**（87 个未被认领的工具） |

---

## 七 · 一句话结论

> **台账 110 条、工具面 313 个。**
> ① **表 A（台账有、工具无挂）= 41 条**，其中 **`verified` 36 条**是"已实现但没暴露"的候选池（扣掉台账自己声明豁免的 `requirements_planning` 后为 **40**）—— ★ 按 `id` 首段分组：**草图 12 · 曲面 10 · 特征 5 · AutoCAD 3 · 曲线 2 · 其余 9 组各 1**。
> ② **表 B**：挂工具的 69 条引用 **226** 个工具名，**悬空 0 个** —— 但其中 `verified` 的 **36** 条根本没挂工具，挂在 `verified` 上的只有 **61** 条。
> ③ **表 C**：`verified` **97** · `stitched` **12** · `not_implemented` **1** · `source_verified` **0**（· `indexed` **0**），合计 **110**。
> ⚠ **零风险提示（可复算的）**：结论 ①②③ 的关键前提是"工具名能被静态抽全"——**只有走 `ToolSpec(name=)` 字面量那条路时会假报 19 个"工具不存在"**（见 §〇·② 的坑）。
