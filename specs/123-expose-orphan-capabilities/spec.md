# 123 · 挂柜台（第一批）：把孤立能力从「看得到 30 个」变成「可复现的全量清单」并暴露

**Status**: Implemented（轮 204）

## 一、要什么（specify）
把 `scripts/sw_*.py` 里「谁都不调用、也没暴露」的**孤立能力**挂成 MCP 工具，让"柜台"变宽。
★ 但**第一步不是登记工具** —— 而是先解决一个**判据问题**（见第二节）。

## 二、★★★ 先撞到的病：候选清单**87% 看不见**（clarify）
```
`tools/probe_unexposed_functions.py`（既有工具）印到「孤立能力（前 30）」就停，
后面写「…（还有 %d 个）」。
⇒ ★★ 实测共 **302** 个 ⇒ **272 个（87%）读者看不到** ⇒ "选哪一批暴露"只能靠感觉。
★ 而本项目**明令禁止**靠感觉（事实 53：不为启发式硬凑）。
⇒ 所以本轮**先做的是**：给它加**结构化全量输出**（`D:/AI/SW/output/orphan-capabilities.json`），
  连**签名**一起落盘 ⇒ 于是"选哪批"**可从数据复现**。
```

## 三、★★ 全量清单给出的数（**这一步才是"选批"的依据**）
```
302 个孤立能力
  其中 **首参可注入**（`model` / `sw_app` / `study`）: **51**
  其中 **含裸坐标形参**（`x`/`y`/`z` —— 规则 3 会拒注册）: **4**
⇒ 本批从这 51 里取**拓扑的「目标 / 约束 / 控制」**那一族。
```

## 四、为什么先做拓扑这一族（四条理由，逐条可核）
1. `topology_optimization` 是 **`verified`**，且 **轮 203 真机复验 `verdict: pass`**
   （85,748 单元 / 图数 2 / `材料质量1` / 228.9 s）；
2. `sw_topology` 是**可注入孤立能力最集中的模块**（12 个）；
3. ★ **先例已存在**：`solidworks_topology_create_study` / `_evidence` / `_run` 三个工具**已经在挂**，
   本批沿用**同一个** `inject="study"` + `param_alias={"study_name": None}` 模板（不另立一套）；
4. 内聚：本批全部是**同一条真机链**上「目标 / 约束 / 控制」那一环的构造器。

## 五、本批取的 4 个（**签名照实取，不发明**）
| 工具 | 函数（真实签名）|
|---|---|
| `solidworks_topology_create_mass_constraint` | `create_mass_constraint(study, *, reduce_percent: float)` |
| `solidworks_topology_create_factor_of_safety_constraint` | `create_factor_of_safety_constraint(study, *, specified_factor: float)` |
| `solidworks_topology_create_preserved_region` | `create_preserved_region(study, *, option: int \| None = None)` |
| `solidworks_topology_create_thickness_control` | `create_thickness_control(study, *, min_thickness: float \| None = None, max_thickness: float \| None = None)` |

**明确不取**（附理由，见 `tool_specs_batch11.py` 的表）：
`create_symmetry_control` / `create_demold_control`（**枚举值未核**，铁律 5 不猜）·
`create_stress_constraint`（与本批两约束重叠，留批）·
`sw_surface.create_*`（已知事实 40：返回值跨次会变）·
`sw_part` 那 14 个（含 `angle_rad` ⇒ **与规则 2 冲突**，要先定换算边界）。

## 六、★★★★ 而实测给出了**一处必须诚实修正的地方**
```
我原以为"这批都真机跑过" —— **实测不是**：
`tools/capture_topology_evidence.py` **直接调用过**的拓扑函数**只有 4 个**
  （create_topology_study · set_topology_goal · set_material · run_analysis）
⇒ ★ 而本批这 4 个**不在其中** ⇒ **它们没有直接的真机证据**。
★ 所以本批**只做"暴露"**，**不声称真机验证**：
  `topology_optimization` 的真机证据仍以那条**已验证的整链**为准 ——
  **不因为"挂上了"就给它们任何 `verified` 身份。**
```

## 七、判据（★ 三处独立口径必须**一致地**动 4）
| 口径 | 之前 | 现在 |
|---|---|---|
| 被工具引用的公开函数（探针）| 93 | **97** |
| 孤立能力（探针）| 302 | **298** |
| 首参可注入（探针）| 51 | **47** |
| 地图「本仓库(MCP)」| 86 | **90** |
| 地图「本仓库独家」| 75 | **79** |
⇒ ★★ **五个数在同一次改动上一致地动 4** —— 这不是凑的，是同一件事在五个独立口径上的投影。

## 八、判据表
| ID | 判据 |
|---|---|
| SC-12301 | ★★★ **先解决"候选看不见"**（87% 不可见 ⇒ 加结构化全量输出），再做选择 |
| SC-12302 | ★★ 选择**从数据来**（51 可注入 / 4 含裸坐标）而不是凭感觉 |
| SC-12303 | ★★ 本批 4 个**签名照实取**（`inspect.signature`），模板**照既有先例** |
| SC-12304 | ★★★ **如实说**：这 4 个**没有直接真机证据**，只暴露、不给 `verified` |
| SC-12305 | ★★ **五处独立口径一致地动 4**（互相印证）|
| SC-12306 | 规则 1/2/3 门禁通过（`all_specs()` 的 `check_spec`）· 两处硬编码计数**同步更新** |
| SC-12307 | 门禁 + 回归不退化 |

## ⚠ 明确记下的限度
* ⚠ **只做了 4 个**（302 / 51 的极小一部分）—— 这是第一刀，**不是"挂完了"**；
* ⚠ 这 4 个**没有直接真机证据**（见第六节）；
* ⚠ `sw_surface` / `sw_part` / `sw_simulation_loads` 那几族**都有已知障碍**（事实 40 / 规则 2 / 规则 3），
  **不是"以后随手就能挂"**；
* ⚠ 本批**没跑真机**（暴露 ≠ 验证）。
