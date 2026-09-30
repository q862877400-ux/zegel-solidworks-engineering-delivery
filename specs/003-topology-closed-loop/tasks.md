# Tasks: 拓扑优化闭环

**Input**: [spec.md](spec.md) · [plan.md](plan.md)

**格式**：`[ID] [P?] [Story] 描述` —— 每个任务带 `→ 验收:`

**状态**：**全部完成**（真机已验证）。本表同时是「这件事是怎么做成的」的可复核记录。

---

## Phase 1: Setup —— 先把判据与资源查清（**不写代码**）

- [x] **T-001** 查拓扑优化的官方硬约束与调用顺序
  **✅** 官方 CHM：**只能对单实体零件做**；`CreateNewStudy3(Name, 13, 0, &Err)`；
  目标用 `CreateGoal`，约束用 `CreateMassConstraint`/`CreateFactorOfSafetyConstraint`。
  `→ 验收:` `Select-String D:\AI\SW\_raw\cworksapi\Create_Topology_Study_Example_VBA.txt -Pattern 'CreateNewStudy3'`

- [x] **T-002** 查网格参数的**官方签名**（此前一直是猜的）
  **✅** 解包 **VB6 类型库 CHM**（`cworksapivb6.chm`，3000 页，**每方法一页含参数名**）⇒
  `CreateMesh(NUnits, DElementSize, DTolerance)`，后两参单位是**毫米**。
  `→ 验收:` `python tools\fetch_api_signature.py CreateMesh --book cosworksapi --iface ICWStudy`
  （期望输出含 `NUnits` / `DElementSize` / `DTolerance`）

- [x] **T-003** 查材料赋值的**正确库名与材料名**
  **✅** 官方 `SldWorks~PartDoc~SetMaterialPropertyName2` 给出三参 `(ConfigName, Database, Name)`；
  两家外部项目（MIT / Apache-2.0）用同一个库名 `"SOLIDWORKS Materials"` 交叉印证。
  `→ 验收:` `python tools\fetch_api_signature.py SetMaterialPropertyName2 --book sldworksapi --iface IPartDoc`

- [x] **T-004** 查清「屏幕上为什么看不到变化」（用户质疑）
  **✅** 探针设 `CommandInProgress = True`（铁律 2，抑制弹窗）⇒ UI 不刷新；
  且整链真的只要 2–3 秒。
  `→ 验收:` `Select-String C:\swprojects\sw-skill-fork\tools\capture_simulation_evidence.py -Pattern 'CommandInProgress'`

**Checkpoint**：判据与签名都拿到 ✅

---

## Phase 2: User Story 1 —— 闭环（P1）

- [x] **T-005** [US1] 建单实体板 + 赋材料
  **✅** 100×60×20 mm；`MaterialIdName` 回读 `'solidworks materials|AISI 1020|2'`
  `→ 验收:` 证据 JSON 的 `steps.material.ok == true`

- [x] **T-006** [US1] 建拓扑研究并确认类型
  **✅** 入口 `CreateNewStudy3`（**未走降级**），`AnalysisType == 13`
  `→ 验收:` 证据 JSON 的 `steps.topology_study`

- [x] **T-007** [US1] 设目标与约束（**复用**目标自带的质量约束）
  **✅** `goal_endedit_code == 0`（成功）、`mass_constraint_reused == true`
  `→ 验收:` 证据 JSON 的 `steps.goal_and_constraints`

- [x] **T-008** [US1] 施夹与加载（按**面坐标**选面）
  **✅** 两个面的选区计数都是 1；`LoadsAndRestraintsManager.Count == 2`
  `→ 验收:` 证据 JSON 的 `steps.fixtures_and_loads`

- [x] **T-009** [US1] 划网格（官方建议值 / 毫米）
  **✅** `CreateMesh = 0`、**85,748 个单元**、1.1 秒
  `→ 验收:` 证据 JSON 的 `steps.mesh`

- [x] **T-010** [US1] 求解并**专门断言 Material Mass 图存在**
  **✅** `RunAnalysis = 0`（187 秒）⇒ `Results` 非空、`GetPlotCount == 2`、
  `GetPlotNames == ('品质1', '材料质量1')` ⇒ **`material_mass_plot.ok == true`**
  `→ 验收:` 证据 JSON 的 `steps.material_mass_plot`

**Checkpoint**：闭环跑通 ✅

---

## Phase 3: User Story 2 —— 回读判据（P1）

- [x] **T-011** [US2] 每一步都改成回读值，不用返回码
  **✅** 选区计数 / `MaterialIdName` / `ElementCount` / `Results` 非空 + 图数
  `→ 验收:` 证据 JSON 里每一步都有非 `ok` 的回读字段

- [x] **T-012** [US2] 修掉**我自己写的**判据 bug（真假值当成功码）
  **✅** `set_topology_goal` 的 `goal` 是 `EndEdit` 返回码、**成功为 0**，
  而 `bool(0)` 为假 ⇒ 第一版把成功判成失败。真机复核：`D:\AI\SW\probe_bool_com.py`
  `→ 验收:` 证据 JSON 的 `goal_endedit_code == 0` 且 `ok == true`

- [x] **T-013** [US2] 无许可时**非零退出**并写明原因
  **✅** 脚本顶层 `except` 落进证据文件的 `error` 字段；`verdict != "pass"` ⇒ 退出码 1
  `→ 验收:` `Select-String tools\capture_topology_evidence.py -Pattern 'verdict.*pass.*else 1'`

---

## Phase 4: User Story 3 —— 节流与安全（P2）

- [x] **T-014** [US3] 内存守护放**旁路线程**（COM 留主线程）
  **✅** 早期把 COM 放后台线程 ⇒ `AttributeError: <unknown>.X`（STA 线程亲和）
  `→ 验收:` `Select-String tools\capture_topology_evidence.py -Pattern 'MEM_LIMIT_MB'`

- [x] **T-015** [US3] 单元数上限（挡「毫米当米」这类 1000× 误传）
  **✅** `ELEMENT_SANE_MAX = 2_000_000`（实测 85,748，留一个量级余量）
  `→ 验收:` `Select-String tools\capture_topology_evidence.py -Pattern 'ELEMENT_SANE_MAX'`

- [x] **T-016** [US3] 收尾不留垃圾
  **✅** `CommandInProgress = False` + `CloseDoc`（**不保存**）+ 杀残留求解器
  `→ 验收:` 跑完 `Get-Process cwbcbfmesh` 应为空

---

## Phase 5: Polish

- [x] **T-017** 清单升级：`topology_optimization` → `verified`
  **✅** `verified_versions: ["2026"]`；`evidence` 指向**两条可跑命令**；`limitations` 置顶六条
  `→ 验收:` `python -c "import json;d=json.load(open('capabilities.yaml',encoding='utf-8'));print([c['level'] for c in d['capabilities'] if c['id']=='topology_optimization'])"`
  ⇒ `['verified']`

- [x] **T-018** 给 `simulation_and_fea` 也补**可跑证据**（原来只有文字）
  **✅** 新增 `tools/capture_simulation_evidence.py`；`evidence` 指向它
  `→ 验收:` `python tools\capture_simulation_evidence.py` ⇒ `verdict: pass`

- [x] **T-019** 顺带建在线官方 API 签名查询
  **✅** `tools/fetch_api_signature.py`（在线优先，本地 VB6 CHM 兜底）
  `→ 验收:` 见 T-002 的命令

- [x] **T-020** 四项门禁 + 全量回归
  **✅** 门禁全 exit 0；回归 **6 failed / 758 passed / 15 skipped**（与基线逐条相同）
  `→ 验收:` 见 [plan.md](plan.md) §六

---

## 本特性**没做**的（如实记，与 spec 的边界一致）

| 项 | 为什么 |
|---|---|
| 多实体零件 / 装配体 | 官方硬约束：只能对单实体零件做 |
| 导出类结果（`Export Smoothed Mesh` / 收敛曲线） | **四源**（接口清单 / DLL / CHM / 运行期 `GetIDsOfNames`）均未查到公开方法 ⇒ 铁律 5：查不到就写查不到 |
| 在 `pytest` 里自动跑 | 单次约 3 分钟且需许可 ⇒ 由人按需跑 |

## 依赖（用户侧）

**拓扑优化需要 `SOLIDWORKS Simulation Professional/Premium` 许可。**
本机原先只有 `SimulationXpress`；2026-10-01 用户在 **SolidNetWork License Manager**
中调整并**重启 SolidWorks** 后解除。
⚠ **许可在 SolidWorks 启动时签出 ⇒ 改许可设置后必须重启**（不重启则仍报「拓扑算例未获许可」）。
