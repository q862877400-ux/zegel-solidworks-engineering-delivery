# Implementation Plan: 拓扑优化闭环

**Feature**: `003-topology-closed-loop` · **Spec**: [spec.md](spec.md)

**Created**: 2026-10-01 · **Status**: Implemented

---

## 一、与既有实现的关系（**不重造**）

本特性**不新增能力实现** —— 拓扑与仿真的函数**早已存在**：

| 已有模块 | 提供 |
|---|---|
| `scripts/sw_topology.py`（617 行 / 26 导出项） | `create_topology_study` / `set_topology_goal` / 各类约束与控制 / `run_topology_study` / `collect_topology_evidence` |
| `scripts/sw_simulation.py` | `set_material` / `select_face_at` / `apply_fixed_restraint` / `apply_normal_force` / `create_mesh` / `default_element_size_and_tolerance` / `run_analysis` |
| `scripts/sw_part.py` | 草图 / 拉伸 等建模 |
| `scripts/sw_connect.py` | `get_com_member` / `set_com_member` / `out_i4` |
| `tests/test_sw_topology_contract.py` | 8 条契约测试（无 COM） |

**⇒ 本特性新增的只有两样**：
1. `tools/capture_topology_evidence.py` —— **串起闭环**并把结果变成可复核的 JSON
2. `docs/A9-solve-attempts.md` §二之四/五 —— 真因与排除过程的记录

**⇒ 判据：能复用的一律复用；本特性不引入任何新的 COM 成员**（已在来源块写明）。

---

## 二、技术路径（每个判断都有出处）

### 2.1 材料赋值
```
model.SetMaterialPropertyName2("", "SOLIDWORKS Materials", "AISI 1020")
                                        ↑ 库的【显示名】   ↑ 库里真实存在的材料名
```
- **依据**：官方 VB6 类型库 CHM 的 `SldWorks~PartDoc~SetMaterialPropertyName2`
  （`(ConfigName, Database, Name)`）；两家外部项目（`Eduardof0nt` MIT /
  `Slacker-LLC` Apache-2.0）**用同一个库名**（交叉印证）。
- **坑**：库名不是 `.sldmat` **文件名**；`"Plain Carbon Steel"` **不在该库**。
- **判据**：**回读 `MaterialIdName`**（该函数返回 `Void`）。

### 2.2 选面
```
model.Extension.SelectByID2("", "FACE", x, y, z, …)   ← (x,y,z) 是【面上一点】
```
- **坑**：既有 `sw_part._select_by_id(ext, "", "FACE", …)` 硬编码 `(0,0,0)`；
  原点在实体**内部** ⇒ 一个面都没选中 ⇒ `DispArray` 为空 ⇒ 弹
  「未定义载荷或规定的位移」。
- **判据**：**回读 `GetSelectedObjectCount2(-1)`**。

### 2.3 网格
```
study.CreateMesh(NUnits, DElementSize, DTolerance)     ← 第 1 参是【单位】不是网格类型
```
- **依据**：官方 VB6 类型库 CHM 的 `CosmosWorksLib~CWStudy~CreateMesh`；单位是**毫米**。
- **坑**：早期按 `(meshType, tolerance, size)` 传 ⇒ 后两参颠倒 ⇒ 1950 万单元 / 20–25 GB。
- **判据**：返回 0 **且** 单元数在合理区间。

### 2.4 目标与约束
```
set_topology_goal(...)  →  goal = EndEdit 的返回码，**0 = 成功**
```
- **坑**：`CreateGoal(0/1)` **自带**一个质量约束；再建一个 ⇒ `EndEdit` 返回 **7**
  （`swsTopoErrCode_OnlyOneMassConstraintCanBeDefined`）⇒ **复用**目标自带的那个。
- **坑**：**不要用真假值判成功码**（`bool(0)` 为假）—— 本特性第一版踩到，
  把成功判成了失败。

### 2.5 求解与结果
- **官方签名**：`RunAnalysis()` **零参**。
- **坑**：**返回 0 不代表成功**（夹具缺失、许可缺失时都返回 0）。
- **判据**：`study.Results` 非空 + `GetPlotCount > 0` + **`GetPlotNames` 含 Material Mass**。

### 2.6 单元数上限的由来
100×60×20 mm 的板，官方建议尺寸 ≈4.93 mm ⇒ 实测 **85,748** 个单元。
合理上限取 `2_000_000`（比实测大一个量级，仍能挡住「毫米当米」这类 1000× 误传）。
**这是启发式阈值，不是官方常数**（证据里同时记 `element_count` 与 `seconds` 供人判）。

---

## 三、证据形态

`output/topology-evidence.json`（`output/` 已 gitignore）：

```json
{
  "captured_at": "...",            // UTC，脚本自己写
  "capability": "topology_optimization",
  "revision": "34.4.1",            // SolidWorks 版本，从 COM 读
  "steps": {
    "part":                {"ok": true, "size_mm": [100,60,20], "bodies": 1},
    "material":            {"ok": true, "MaterialIdName": "solidworks materials|AISI 1020|2"},
    "topology_study":      {"ok": true, "entry": "CreateNewStudy3", "AnalysisType": 13},
    "goal_and_constraints":{"ok": true, "goal_endedit_code": 0, "mass_constraint_reused": true},
    "fixtures_and_loads":  {"ok": true, "selection_count_fixture_face": 1, "...Count": 2},
    "mesh":                {"ok": true, "element_count": 85748, "seconds": 1.1},
    "solve":               {"ok": true, "results_present": true, "plot_count": 2,
                            "plot_names": ["品质1", "材料质量1"], "seconds": 187.1},
    "material_mass_plot":  {"ok": true, "matched_plots": ["材料质量1"]}
  },
  "verdict": "pass"
}
```

**每一步都带回读值**（FR-002）⇒ 失败时能定位到**具体哪一步**。

---

## 四、节流与安全

| 措施 | 做法 |
|---|---|
| 内存守护 | **旁路线程**只读 `cwbcbfmesh` 内存，超 6 GB 杀之 |
| **COM 在主线程** | ⚠ 早期把 COM 放进后台线程 ⇒ `AttributeError: <unknown>.X`（**STA 线程亲和**）。守护线程**不碰 COM**。 |
| 单元数上限 | `ELEMENT_SANE_MAX = 2_000_000` |
| 收尾 | `CommandInProgress = False` + `CloseDoc`（**不保存**）+ 杀残留求解器 |
| 不进 pytest | 单次约 3 分钟且需许可 ⇒ 由人按需跑（FR-007） |

---

## 五、本特性**不做**什么（如实划界）

| 不做 | 为什么 |
|---|---|
| 多实体零件 / 装配体 | 官方硬约束：「只能对单实体零件做拓扑优化」 |
| **导出**类结果（`Export Smoothed Mesh` / 收敛曲线） | **四源**均未查到可调用的公开方法（接口清单 / DLL 二进制 / CHM / 运行期 `GetIDsOfNames`）；官方只在界面流程里有说明 ⇒ 按铁律 5 记为查不到，不猜 |
| 在 `pytest` 里跑 | 慢且需许可 |
| 新增 COM 成员 | 复用既有；`check_member_names` 保证不引入反射里没有的名字 |

---

## 六、验收

```powershell
cd C:\swprojects\sw-skill-fork
python -W error::SyntaxWarning -m compileall -q scripts tools
python scripts\check_member_names.py         # 成员名全在官方反射里
python scripts\check_provenance.py           # 新增行均可追溯
python scripts\check_diff_markers.py
python scripts\check_union_conventions.py    # 五统一
python -m pytest tests -q --no-header -p no:cacheprovider

# 真机（需含拓扑优化的 Simulation 许可；单次约 3 分钟）
python tools\capture_topology_evidence.py    # 期望 verdict: pass
```
