# 任务 A · 核「每个工具的证据与 level」——证据 vs 清单 对账

> 只读核账：只读 `capabilities.yaml` / `mcp-server/tool_specs_batch*.py` / `output/*.json`，
> ★ **未跑 SolidWorks**、★ **未跑 pytest**、★ **未改仓内任何文件**（本文件是本次唯一写入）。
> ★ 全部结论给**可搜索的原文位置**（文件 + 片段，★ 不写行号）。

---

## 〇 · 口径与核法

| 项 | 值 |
|---|---|
| 核的能力条目 | **97 条** —— `capabilities.yaml` 的 `capabilities`（110 条）里 `level: verified` 的全部 |
| 这 97 条带 `evidence` 的比例 | **97 / 97**（`verified` 无一条缺 `evidence`） |
| `level` 分布（全 110 条） | `verified` 97 · `stitched` 12 · `not_implemented` 1 |
| `evidence` 里引用的**文件路径** | **266 处**（`output/ scripts/ tools/ tests/ docs/ mcp-server/ apps/ …`） |
| 其中 **`output/*.json` 证据文件** | **116 个不同文件**（113 个存在、3 个不存在） |
| 另有**裸文件名**引用（无目录前缀） | 5 处 —— 2 处拼不出来、3 处落在 `output/` 下能对上 |
| 结论一致性 | 逐个读回 JSON 的**顶层 `verdict` / `passed` / `of`** 与条目文字对撞 |

**核法（可复算）**：`re.sub` 从 97 条的 `evidence` 字符串里抽路径 → `path.exists()`；
再把抽到的现存 JSON 逐个 `json.load`，取顶层 `verdict/passed/of/…` 与条目文字比。
对「声称建成但引的文件记否」的一类，回原文把**两段**并排放。

---

## 一 · 对不上的那几条（★ 只报 7 条）

### ★★★ 第 1 类：**引的证据文件自己记的是「失败」，条目写成「建成」**

| 能力名 | level | evidence 路径 | 文件在不在 | 结论一致否 |
|---|---|---|---|---|
| `surface_delete_hole` | verified | `output/delete-hole-for-surface-evidence.json`<br>`output/delete-hole-inner-loop-evidence.json`<br>`output/delete-hole-on-surface-evidence.json` | **三份都在** | **❌ 不一致（三份全记否）** |

**不一致的两段原文 —— ① 清单条目的断言**（`capabilities.yaml`，`surface_delete_hole` 的 `evidence` 第 1 条）：

> 「★★ 2026-10-03（轮 564）**真机建成**（零弹窗）：在**一张真正的带孔平面**（面 1 / 环 2）上选**孔那圈边** ⇒ `InsertDeleteHoleForSurface()` ⇒ **名 `删除孔1`**·**型 `DelHole`**·★ **环Δ = −1**（孔被填上）✓」

同条目的 `label` 也写着「★ **真机建成**」。

**② 三份被引证据文件的结论（全部记否）**：

- `output/delete-hole-for-surface-evidence.json`：`"passed": 0, "total": 3, "verdict": "successor_also_fails"`；
  三个 case（继任者+选孔的边 / 继任者+只选面 / 对照第一代）逐个 `"ok": false` · `"returned": "None"` · `"new": []` · `"delta": {"faces": 0, "loops": 0}`
- `output/delete-hole-inner-loop-evidence.json`：`"verdict": "inner_loop_still_fails"`（只选内环 / 只选外环 / 全部边 —— `"picked": 0` 或 18，`"new": []`）
- `output/delete-hole-on-surface-evidence.json`：`"passed": 0, "total": 4, "verdict": "delete_hole_still_noop_on_surface"`（四格的 `area_delta` 全是 `0.0`）

**★ 为什么是「引用链错」而不是「能力是假的」**（这一层必须如实说，否则就是另一种蒙混）：
真正支持「建成」的那次真机跑**存在，但在另一个没被引用的文件里** ——
`output/planar-region-and-delete-hole-evidence.json`：
`"del_name": "删除孔1"` · `"del_type": "DelHole"` · `"geom_after_planar": {"faces": 1, "loops": 2, "edges": 5}` · `"loop_delta": -1` · `"verdict": "planar_region_and_delete_hole_work"`。
★ 其中 `faces:1 / loops:2` **逐字对得上**条目说的「面 1 / 环 2」⇒ 那一次才是条目描述的那次跑。
而**被引的那三份恰好是同目录下唯一三份记「不成」的**（且它们的夹具是拉伸体 5 面/6 环，正是本条 `limitations` 自己写的「★ 拉伸得到的是 5 面 / 6 环、不行」那一组）。
⇒ ★ **结论**：`level: verified` 本身有实据，但**条目把结论挂在了三份否证文件上**。
★ 这一条正是任务点名的最严重那一类（证据文件里有否定结果、条目写成肯定）——只是真因是**指错文件**，不是编造。

---

### ★★ 第 2 类：**证据文件不存在，却把它的具体数字写进条目**

| 能力名 | level | evidence 路径 | 文件在不在 | 结论一致否 |
|---|---|---|---|---|
| `simulation_and_fea` | verified | `output/simulation-evidence.json` | **❌ 不存在** | **无法核** |
| `mesh_size_sanity_gate` | verified | `output/simulation-evidence.json`（第 2 条 evidence，称其为「权威参照」） | **❌ 不存在** | **无法核** |
| `topology_optimization` | verified | `output/topology-evidence.json`（由 `tools/capture_topology_evidence.py` 产出） | **❌ 不存在** | **无法核** |

**不一致的两段原文 —— ① 条目把数字写死了**（`simulation_and_fea` 的 `evidence` 第 3 条）：

> 「…`CreateMesh`（**7,310 个单元**）→ `RunAnalysis`（1 秒）→ **`study.Results` 非空、`GetPlotCount == 4`、`GetPlotNames == ('品质1','应力1','位移1','应变1')`**。**已复现两次。**」

`mesh_size_sanity_gate` 的 `evidence` 第 2 条把同一组数字挂在那份不存在的文件上：

> 「★ **对照证据**：tools/capture_simulation_evidence.py 的 `output/simulation-evidence.json`（`suggested_size_mm: 4.933908705960544` · `element_count: 7310` · `plot_count: 4`）—— ★ 那是「参数生效」的**权威参照**」

**② 该路径在仓里的实际状态**：`output/` 下 `*simulation*` 只有
`simulation-addin-by-clsid.json` · `simulation-addin-status.json` · `simulation-loadaddin-by-path.json` · `simulation-loads-evidence.json` · `simulation-study-evidence.json` · `simulation-study-shapes.json`
—— ★ **`simulation-evidence.json` 不在其中**；`*topolog*` 只有 `topology-readback-evidence.json`。
★ 产出脚本 `tools/capture_simulation_evidence.py`、`tools/capture_topology_evidence.py` **都在**，
⇒ ★ 是**产物没落盘 / 被清掉**，不是脚本不存在。

★ 按铁律 5：这三处的数字（7,310 / 4.93 / 4）**回原文核不到**，只能写「查不到」。
★ 注：`simulation_and_fea` 的第 1 条 evidence（`pytest tests/test_fea_analysis.py`）与 `topology_optimization` 的第 2 条（`pytest tests/test_sw_topology_contract.py`）指向的测试文件**都在**（★ 本次未跑，不核其内容）。

---

### ★★ 第 3 类：**条目声称的「PASS」在被引文件里找不到，而那份文件记的是别的**

| 能力名 | level | evidence 路径 | 文件在不在 | 结论一致否 |
|---|---|---|---|---|
| `simulation_solver_options` | verified | `output/batch37-evidence.json` | 在 | **❌ 不一致** |

**不一致的两段原文 —— ① 条目的断言**（该条目 `evidence` 的最后一条）：

> 「python 真机（轮 273）★ `list_setter_summary`（零参）**ok=True**（9 个族 / 202 个 setter 名）· 证据 output/batch37-evidence.json」

**② 该文件的实际内容**：`output/batch37-evidence.json` 的 `steps` 只有四步 ——
`create_study`（`"ok": true`）· `set_option_ComputeFreeBodyForce`（`"ok": false`）·
`set_option_ContactPenaltyStiffnessScaleFactor`（`"ok": false`）· `set_options`（`"ok": false`）；
顶层 `"passed": 1, "of": 4, "verdict": "partial"`。
★ 该文件里 **搜不到 `list_setter_summary`、搜不到 `setter`**（`grep` 全文 `setter` = 0 命中），
★ 也搜不到「9 个族 / 202」这两个数（`202` 的唯一命中是时间戳里的 `2026-…`）。
⇒ ★ 条目挂的那条断言**不在被引文件里**；而这份文件本身是 **1/4、三项 `ok:false`**，
★ 条目其余 evidence 未提及这三个失败。
（★ 工具本身在：`mcp-server/tool_specs_batch36.py` 里的 `solidworks_simulation_list_setter_summary`。）

---

### ★ 第 4 类：**引用的文件名拼不出来（仓内实际存在的是另一个名字）**

| 能力名 | level | evidence 里写的 | 仓内实际存在的 | 文件在不在 |
|---|---|---|---|---|
| `loft_and_sweep` | verified | `loom-type-evidence.json` | `output/loft-type-evidence.json`（`l-o-f-t`，**loft**） | **❌ 写的那个不存在** |
| `weldment_cut_list` | verified | `out-cut-list-property-names-evidence.json` | `output/cut-list-property-names-evidence.json` | **❌ 写的那个不存在** |

**不一致的两段原文 —— ① 条目**（`loft_and_sweep` 的 `evidence` 第 2 条末尾）：

> 「…**类型名 = `Blend`**（★ 对照拉伸 = `Extrusion`）· 未选中 ⇒ 显式拒绝 · 证据 output/loft-evidence.json · **loom-type-evidence.json**」

`weldment_cut_list` 的 `evidence` 第 1 条里：

> 「…而**中文名（`说明`/`材料`）写入并回读得到**（**out-cut-list-property-names-evidence.json** PASS）」

**② 目录实况**：`output/` 下 loft 族只有
`loft-cut-evidence.json` · `loft-evidence.json` · `loft-fixed-e2e-evidence.json` · `loft-probe.json` · **`loft-type-evidence.json`** · `loft-volume-probe.json` —— ★ **没有 `loom-*`**；
cut-list 族只有 `cut-list-chain-evidence.json` · `cut-list-chain.csv` · **`cut-list-property-names-evidence.json`** · `weldment-cut-list-evidence.json` —— ★ **没有 `out-*`**。
⇒ ★ 属**笔误级**引用错（指向的意图文件都在），但按判据 ①「逐个 `path.exists`」它们**是死链**。

---

## 二 · 核过但**对得上**的（抽样几处，证明不是只挑刺）

| 能力名 | evidence 文件 | 文件自报结论 | 条目写法 | 判定 |
|---|---|---|---|---|
| `absolute-criteria-evidence` → `geometry_measurement` | `output/absolute-criteria-evidence.json` | `"verdict": "pass"` | 「PASS · 三条判据各带正例与负例」 | ✅ 一致（文中的 `"ok": false` 是**负例**，非失败） |
| `hole-units-fixed-evidence` → `declarative_hole_creation` | `output/hole-units-fixed-evidence.json` | `"passed": 5, "verdict": "pass"` | 「PASS 5/5」 | ✅ 一致 |
| `costing-evidence.json` → `costing_readback` | `output/costing-evidence.json` | `"passed": 5, "of": 6, "verdict": "partial"` | 「**5/6**」 | ✅ 一致（条目如实写了 5/6） |
| `drawing-view-evidence.json` → `drawing_view_operations` | `output/drawing-view-evidence.json` | `"passed": 2, "of": 3, "verdict": "partial"` | 「list/collect ok count=3 · get_view_scale ok scale=0.002」，且**另一条 evidence 明写** `set_view_scale_verified 如实报 ok=false` | ✅ 一致（第三个失败项被条目自己写出） |
| `split-line-*` → `curve_and_split` | `output/split-line-silhouette-marks-evidence.json` | `"passed": 1, "total": 7` | 「S5：树新增 `分割线1`…」，并在 limitations 里明写「S6/S7 不成」 | ✅ 一致 |
| `b3-sketch-edit-evidence.json` → `sketch_edit_ops_b3` | `output/b3-sketch-edit-evidence.json` | `"can": 6, "total": 7, "verdict": "partial"`，含一项 `"verdict": "不能", "built": false` | `limitations` 里明写「**6/7 真机建成**」「⚠ **交叉曲线未验成**」 | ✅ 一致（否定项已被条目自曝，不算对不上） |
| `equations` / `export_delivery` / `mold_analysis` 等 | — | `"verdict": "pass"` | 「PASS 5/5 / 8/8 / 4/4」 | ✅ 一致 |

⇒ ★ 97 条里，被**引的证据文件里含 `"ok": false`** 的有 **50 个文件**，
但 ★ 绝大多数是**条目自己写明的负例/对照**（探针故意试的失败路径）⇒ **不计入对不上**。
★ 只把「条目顶层断言与被引文件的顶层 `verdict` 对撞不上」的挑出来 —— 也就是上面那几条。

---

## 三 · 末尾交代

- **核了几处**：**97 条 `verified` 能力**（= `capabilities.yaml` 里带 `evidence` 的 `verified` 全集），
  逐条核了三件事 —— ① 路径 `path.exists`（266 处路径引用 + 5 处裸文件名）；② 证据文件的结论与条目文字是否一致（116 个 `output/*.json` 全读）；③ 有无「证据记否、条目写肯」。
- **对不上几条**：**7 条**（占 97 条的 **7.2%**）——
  `surface_delete_hole` · `simulation_and_fea` · `mesh_size_sanity_gate` · `topology_optimization` · `simulation_solver_options` · `loft_and_sweep` · `weldment_cut_list`。
  ★ 其中**等级判错 0 条**（没有任何一条是「证据全无却被写成 verified」），
  ★ 全部是**引用链 / 引用内容**的问题。

### 最严重的 3 条

1. **`surface_delete_hole`** —— ★ 唯一一条「**引的三份证据全部记否，条目写成「真机建成 ✓」**」。
   被引的 `delete-hole-for-surface` / `-inner-loop` / `-on-surface` 三份都是 `"passed": 0` + `"new": []` + `verdict` 里带 `fails` / `noop`；
   而支持「建成」的那次跑在**未被引用的** `output/planar-region-and-delete-hole-evidence.json`（`loop_delta: -1` · `del_type: "DelHole"` · `faces:1/loops:2` 与条目逐字对上）。
   ⇒ 能力大概是真的，**证据指针是反的**。
2. **`simulation_and_fea`** —— `output/simulation-evidence.json` **不存在**，条目却把它的结论写成**具体数字**（`7,310 个单元` / `GetPlotCount == 4` / `已复现两次`）⇒ 这串数字**在仓内回不到原文**。
   （`mesh_size_sanity_gate` 是同一份死文件的第二次引用，且自称「权威参照」，一并记。）
3. **`simulation_solver_options`** —— 条目写「`list_setter_summary` ok=True（9 个族 / 202 个 setter 名）· 证据 output/batch37-evidence.json」，
   而那份文件**通篇没有 `list_setter_summary`**（`setter` 零命中），`steps` 是 `1 ok / 3 fail`、`"verdict": "partial"` ⇒ **断言与证据不是同一件事**。

### ★ 查不到就说查不到（三处，别当它们已核过）

- `output/simulation-evidence.json` —— **查不到**（产出脚本在，产物不在）⇒ `simulation_and_fea` 的「7,310 单元 / 4 个 plot / 已复现两次」**无法回原文核**。
- `output/topology-evidence.json` —— **查不到**（`tools/capture_topology_evidence.py` 在，产物不在）⇒ `topology_optimization` 的「真机闭环」**无法回原文核**。
- `simulation_and_fea` / `topology_optimization` 各自的 `pytest …` 证据 —— ★ **本次按指令未跑 pytest**，故**只核了「测试文件在不在」**（`tests/test_fea_analysis.py` 在 · `tests/test_sw_topology_contract.py` 在），**未核其结果**。

### ★ 边界声明

- ★ 本次**没有**跑 SolidWorks、**没有**跑 pytest、**没有**改仓内任何文件 —— 全部结论来自静态读取。
- ★ 工具表 `mcp-server/tool_specs_batch*.py` 只做了**旁证**：确认被挑出的能力确实有工具落地（`solidworks_simulation_list_setter_summary` 在 `tool_specs_batch36.py`；`surface_delete_hole` **无对应 MCP 工具**，与该条目 `limitations`「⚠ 本包装未接进 MCP 工具层」一致 ⇒ ★ 不构成额外矛盾）。
- ★ 「结论一致否」只对**条目顶层断言**与**被引文件的顶层结论**下判断；条目自曝的负例（探针故意试的失败路径）**不算对不上**。