# 工具栏缺口的「后端到不了」清单（X1 · X2）

> ★ **本文件是 `specs/201-toolbar-gaps` 的 X 段的交付物**（对应 `tasks.md` 的 **TX01** 与 **TX02**）。
> ★ 2026-10-03（轮 482）写。
> ★★ **它的核心结论与最初的假设相反** —— 见 §一。

---

## 一、★★ 先说结论：三条被点名的「结构性到不了」，**两条不成立**

`specs/201-toolbar-gaps/spec.md` 与目标原话里，把这三族列为「**pywin32 后端结构性到不了**」：

| 被点名的族 | ★ 核实后的结论 | 依据 |
|---|---|---|
| **线性阵列族** | ❌ **不成立** —— ★ **不是后端到不了**，★ 是**旧入口废弃了** | 见 §二 |
| **`IAccessSelections` 指针族** | ✅ **成立** | 见 §三 |
| **结构系统** | ❌ **不成立** | 见 §四 |

★ **为什么最初的归因会错**（★ 值得记下来，因为它是**方法问题**）：

> 那个归因看的是**「台账里那几条是"不能"」**，★ 而**台账的核实器只核「API 名在不在
> `C:\swapi\` 里」** —— ★★ **它没核「本仓有没有实现」** ⚠

⇒ ★ 于是"旧 API 名废弃了、新架构走 `CreateDefinition`"这一类，在台账里**一律显示成"不能"**，
  而它**其实早已实现**。

---

## 二、线性阵列族 —— ★ **不是后端到不了，本仓早已攻克**

### 2.1 官方现状（三源：`C:\swapi\types\IFeatureManager\`）

★ 台账「特征」「特征下拉」两栏里判「不能」的这几条，**官方全都是 `Obsolete`**，
而**继任者统一指向新架构**：

| 工具栏 | 台账给的 API | 官方状态 | ★ 继任者（官方逐字） |
|---|---|---|---|
| 线性阵列 | `FeatureLinearPattern4` | **Obsolete** | `FeatureLinearPattern5` |
| 线性阵列 | `FeatureLinearPattern5` | **Obsolete** | ★ **`IFeatureManager::CreateFeature`** + `ILinearPatternFeatureData` |
| 曲线驱动的阵列 | `FeatureCurvePattern` | **Obsolete** | `CreateFeature` + `ICurveDrivenPatternFeatureData` |
| 草图驱动的阵列 | `FeatureSketchDrivenPattern` | **Obsolete** | `CreateFeature` + `ISketchPatternFeatureData` |
| 填充阵列 | `FeatureFillPattern` | **Obsolete** | `CreateFeature` + `IFillPatternFeatureData` |
| 表格驱动的阵列 | `InsertTableDrivenPattern` | **Obsolete** | `InsertTableDrivenPattern2` |
| （圆周阵列） | `FeatureCircularPattern4` | **Obsolete** | `FeatureCircularPattern5` |

★★ `FeatureLinearPattern5` 的 `Obsolete` 行**逐字**是：

> Obsolete. See [[IFeatureManager::CreateFeature]] and the Remarks in
> [[ILinearPatternFeatureData]] and [[ILocalLinearPatternFeatureData]].

★★★ 而 `ILinearPatternFeatureData` **确实在**（`C:\swapi\types\ILinearPatternFeatureData\_overview.md`：
`property_count: 37 · method_count: 23`）。

### 2.2 ★★ 本仓早已按新架构实现，并有真机证据

```
scripts/sw_pattern.py            428 行
   configure_linear_pattern           ← ★ CreateDefinition(swFmLinearPattern) → 设属性 → CreateFeature
   configure_curve_driven_pattern     ← ★ CreateDefinition(swFmCurveDrivenPattern)
   edit_selection · read_pattern_element · collect_pattern_evidence
```

★ **真机证据 11 份**（`output/`）：

```
linear-pattern-generations-evidence.json     ← ★ 两代对比
linear-pattern-geometry-evidence.json
pattern-direction-marks-evidence.json  ·  pattern-direction-marks2-evidence.json
pattern-axis-evidence.json  ·  pattern-members-evidence.json  ·  pattern-dimension-units-evidence.json
dimension-pattern-evidence.json  ·  dimension-pattern-retry-evidence.json
hole-pattern-evidence.json  ·  flat-pattern-dxf-evidence.json
```

★ **探针 6 个**（`tools/prove_pattern_members.py` · `prove_linear_pattern_generations.py` ·
`prove_linear_pattern_geometry.py` · `probe_pattern_direction_marks{,2}.py` ·
`probe_pattern_dimension_units.py`）· **契约测试 2 个**
（`tests/test_sw_pattern_contract.py` · `tests/test_sw_hole_pattern_contract.py`）。

⇒ ★★ **结论：线性阵列族不能记成「后端到不了」** —— ★ 它属于**"旧入口废弃、新架构已做"**那一类。
  ★ 台账那 5 条**应改判**（★ 而改判要**按本仓的 W2 判据**：凡「能」必有真机证据 —— ★ 证据就在上面）。

---

## 三、`IAccessSelections` 指针族 —— ✅ **这一族是真的到不了**

### 3.1 官方的语义（★ 为什么它天然到不了）

★ 本仓 `capabilities.yaml` 的 `backend_catalog` 对 `solidworks-com-pywin32` 记着：

> **不能调用官方标记为仅进程内非托管 C++ 的指针接口**

★ 而反射里那对 **`IAccessSelections` / `IAccessSelections2`** 正是那种 **`I` 前缀的指针变体**
（★ `IAccessSelections` 在 `_raw/reflect_sldworks/iface_sldworks.txt` 里出现 **70 次** ——
  ★ 存在、★ 但**没有 dispinterface**）。

### 3.2 真机证据（★ 这不是猜的）

★ **事实 47**（两轮 **20+ 种形态**实测）：

> `ISketchedBendFeatureData` 的 `AccessSelections` / `SetFixedFace` 在 pywin32 迟到绑定下**不可调用**
> —— 这是**架构性限制**，不是参数没找对：
> · `SetFixedFace(X,Y,Z,EdgeArray)` 的**七种数组包装 × 两个重载**全部报 `类型不匹配`（位置 1 或 4）；
> · `AccessSelections(model, None)` 报 `类型不匹配`（位置 2）；
> · 改传 `VARIANT(VT_DISPATCH, None)` 则报 **`服务器出现意外情况`（`0x80010105`）**。
> **⇒ 不要再用「换个参数试试」的方式继续试 —— 20+ 种已穷尽。**

★ **事实 67**：`ISketchManager.CreateChamfer` **同族**（`0x80010105`）。
★ **事实 126**：`ISafeArrayUtility` **是给 C++ 的，pywin32 到不了**（**21/21 不可达、无 dispinterface**）
  —— ★ 一条外部评审把它列为「高杠杆缺口」，**实测否定**。
★ **能力条目 `topology_iteration_options_backend_limited`** 给了**可复用的判据**：

> ★★★ **同一个错误码 = 同一类后端限制** —— 见到 **`0x80010105`** 不必重新穷举形态。

### 3.3 ★ 因此受影响的工具栏项（★ 单列）

★ 这些**包装写了、真机到不了**（★ 保留包装当**可复算的证据**，★ 不删）：

| 工具栏 | 官方成员 | 到不了的位置 |
|---|---|---|
| 折弯（钣金） | `ISketchedBendFeatureData.SetFixedFace` | `0x80010105` |
| 边线法兰 | `ISketchedBendFeatureData.AccessSelections` | 同族 |
| 角撑板 | `ISMGussetFeatureData.AccessSelections` | 同族 |
| 草图倒角 | `ISketchManager.CreateChamfer` | `0x80010105`（★ **绕法**：改成回读线段数判定，★ 建成时回 `None`） |
| 拓扑迭代选项 | （Options 接口） | 同族 |

★ ⚠ **一句话的诚实边界**：★ 「到不了」说的是**pywin32 迟到绑定这条后端**；
  ★ **换 `comtypes` 早绑定或进程内 C++ 后端未在本机实测** ——
  ★ 而 known-facts 的 `ISafeArrayUtility` 那条更正说明「早绑定**看得到**某些成员」
  ⇒ ★ **不能断言「永远不行」** ✓

---

## 四、结构系统（焊件）—— ❌ **也不成立**

### 4.1 官方现状

| 官方成员 | 状态 | 继任者 |
|---|---|---|
| `IFeatureManager.InsertStructuralWeldment` | **Obsolete** | `InsertStructuralWeldment2` |
| `IFeatureManager.InsertStructuralWeldment2` | ★ **也 Obsolete** | ★ **`InsertStructuralWeldment3`** |

### 4.2 本仓现状

```
scripts/sw_weldment.py
output/weldment-evidence.json · output/weldment-profile-evidence.json · output/_weldment_smoke.csv
```

⇒ ★ **有实现、有真机证据** ⇒ ★ **同样不能记成「后端到不了」**。

★ 另：本机**装了焊件轮廓库**（`C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\weldment profiles\`
下 **111 个 `.sldlfp`**）⇒ ★ 结构构件那条路**是通的**。

---

## 五、X2 · ★ **官方源里查不到的**（★ 铁律 5：查不到就说查不到）

| 工具栏 | 台账给的 API | ★ 核实结果 |
|---|---|---|
| **螺柱向导** | `InsertStudWizard` | ★★ **`C:\swapi\types\` 里没有这个名字**（★ 在 `IModelDoc2` 与 `IFeatureManager` 两处**都查不到**） |

★ 按**铁律 5**：

> 两套源都查不到 → **写「查不到」并停下换思路**，不要用相似名字蒙混。
> **名字缺席 = 官方 API 里没有这个成员**，不是「没写文档」。

⇒ ★ **螺柱向导（`InsertStudWizard`）记「查不到」** —— ★ 台账给的名字**在官方源里不存在**；
  ★ **不拿相似名字（如 `InsertReferencePoint` 之类）冒充它** ⚠
  ★ 若要用它，**下一步该做的是**：★ 查 CHM 的 SolidWorks Help 里「Stud Wizard」那一节，
    ★ 看它是不是**纯 UI 功能**（★ 那样就没有 API 入口，★ 与"名字没写文档"是两回事）。

---

## 六、★ 本文件**不做**什么

- ★ **不改** `docs/toolbar-ledger.json` 里的判定 —— ★ 那是**核实器的产物**；
  ★ 本文件只**指出**它的归因错在哪、证据在哪（★ 改判要连同核实器的判据一起改，★ 否则下次重生成又回去）。
- ★ **不把「换后端能不能行」写成结论** —— ★ 那**没有本机实测**（★ 见 §3.3 的诚实边界）。
- ★ **不删**任何"到不了"的包装 —— ★ 它们**是可复算的证据**（★ 也是换后端时的起点）。
