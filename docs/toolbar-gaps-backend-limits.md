# 工具栏缺口的「后端到不了」清单（X1 · X2）

> ★ **本文件是 `specs/201-toolbar-gaps` 的 X 段的交付物**（对应 `tasks.md` 的 **TX01** 与 **TX02**）。
> ★ 2026-10-03（轮 482）写。
> ★★ **它的核心结论与最初的假设相反** —— 见 §一。

---

## 一、★★ 结论：三条被点名的「结构性到不了」**都成立**

> ★★★ **2026-10-03（轮 485）收口：**本节原题是「**两条不成立**」。
> 而经**三轮逐条真机核实**，结论**全部翻过来了**：三条**都成立**，
> ★ 而**理由各不相同**。★ 这也是本文件最值得读的一点：
> **一个看着对的归因，理由可能完全是错的** —— 而只有**逐条真机**才能分开它们。

`specs/201-toolbar-gaps/spec.md` 与目标原话里，把这三族列为「**pywin32 后端结构性到不了**」：

| 被点名的族 | ★ 核实后的结论 | 依据 |
|---|---|---|
| **线性阵列族** | ✅ **成立** —— ★★ **而理由与最初的猜测不同**：不是“旧入口废弃”，而是 **新旧两条路都要 `AccessSelections`** | 见 §二 |
| **`IAccessSelections` 指针族** | ✅ **成立** | 见 §三 |
| **结构系统（焊件）** | ✅ **成立** —— ★★ **而理由又不同**：`InsertWeldmentCutList2` **取不到** | 见 §四 |

★ **为什么最初的归因会错**（★ 值得记下来，因为它是**方法问题**）：

> ★ **我一度以为它们不成立**，★★ 而**错法只有一个**：**看到本仓有对应模块与证据文件就下结论**（★ 而没读它们的**内容**）。
> ★★ 三次都是这个错法：★ 一次看到 `sw_pattern.py`、一次看到 `linear-pattern-*-evidence.json` 存在、一次看到 `sw_weldment.py` 与证据。
> ⇒ ★★ **定则**：**证据要读 `verdict` 字段**，★ 不是读文件名。
> （★ 另：台账核实器的盲点也是真的（事实 379/380），★ 而**它与本节的归因对错无关** —— 两件事该分开说。）
>
> 原文（保留，它记录了我当时的真实推理）：那个归因看的是**「台账里那几条是"不能"」**，★ 而**台账的核实器只核「API 名在不在
> `C:\swapi\` 里」** —— ★★ **它没核「本仓有没有实现」** ⚠

⇒ ★ 于是"旧 API 名废弃了、新架构走 `CreateDefinition`"这一类，在台账里**一律显示成"不能"**，
  而它**其实早已实现**。

---

## 二、线性阵列族 —— ✅ **确实到不了，而理由是「指针族」（★ 本节已在轮 484 更正）**

> ★★★ **2026-10-03（轮 484）更正** —— ★ 本节**原文**判它「不成立」。★ 而**真机试过之后**，
> 结论**反过来了**，只是**理由与最初的目标原话不同**：
>
> | 路径 | 真机结果 |
> |---|---|
> | **旧入口** `FeatureLinearPattern3/4/5` | ★ **fail** —— 3 代逐个试，★ 3/4 回 `None`、★ 5 报 `非选择性的参数`；三判据（树名增量 / 特征数 / **几何：体数+包围盒**）**全没变**（`output/linear-pattern-*-evidence.json`，`verdict: fail`） |
> | **新架构** `CreateDefinition(swFmLPattern=6)` + `ILinearPatternFeatureData` | ★ `CreateDefinition` **成功**（拿到 `data`）；★★ 而 **`AccessSelections` 到不了** ⚠ |
>
> ★★ `AccessSelections` 的**三种传法**（真机，`output/linear-pattern-newarch-evidence.json`）：
> ```
> (model, None)        ⇒ com_error 类型不匹配，位置 2      ← 与事实 47 逐字一致
> (model, 空Dispatch)  ⇒ com_error 0x80010105（服务器出现意外情况）  ← 指针族的签名错误码
> (None, None)         ⇒ com_error 类型不匹配，位置 1
> ```
> ⇒ ★★★ **故**：★ 新旧两条路**都**要 `AccessSelections`，★ 而它在 **pywin32 迟到绑定**下到不了
> ⇒ ★ **归因成立，理由改写成「指针族」** ✓
>
> ★★ **另外更正两处小的**：
> · `scripts/sw_pattern.py` 的模块头引用的常量名 **`swFmLinearPattern` / `swFmCurveDrivenPattern`
>   在反射转储里都不存在** ⚠ —— ★ 真名是 **`swFmLPattern = 6`** / **`swFmCurvePattern = 103`**
>   （`_raw/enum_values_sldworks.txt`）。
> · ★ 故「本仓早已实现」这个说法要**降级**为「**本仓写了新架构的装配层，而它的入口到不了**」。

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

### 2.2.1 ⚠⚠ **2026-10-03（轮 598）撤销本节上面那句结论**

★ **上面那句「新架构已做」是**过度解读**的** —— ★ 而**撤销它的正是本节自己引的那些证据** ⚠

```
`output/linear-pattern-geometry-evidence.json`（★ 本节上面引的"真机证据"之一）逐字：
   trial               = pattern_named_feature
   ★ raw_none          = True        ← ★ 它回的是 None
   ★ raw_type          = NoneType    ← ★ 而不是一个 Feature
   ★ tree_before_after = [7, 7]      ← ★ 特征树**没长**
   ★ geom_changed      = False       ← ★ 几何**也没变**
```
  ⇒ ★★★ **故那些证据记的是「调了、而什么都没发生」** —— ★ **不是"已实现"** ⚠
    ★★ 而那是**第五种形态（静默 no-op）**的形态（★ 事实 439 那族）。

★ **而本轮还把那套"新架构"的**机理**读了、并真机测了**（事实 473 / 474）：

```
`scripts/sw_pattern.py::_SelectionAccess.__enter__` ⇒ `data.AccessSelections(model, None)`
★ 真机四种第 2 参形态（`tools/probe_access_selections_param2.py`，零弹窗，
  ★ 在一个真的 `CreateDefinition(swFmFillPattern=105)` 产物上试）：
     None                 ⇒ **`类型不匹配。`**（★ 位置 **2**）
     空 Dispatch           ⇒ **`服务器出现意外情况`**（`0x80010105`）
     空变体                ⇒ `类型不匹配`（位置 2）
     byref 空 Dispatch     ⇒ `远程过程调用失败`
  ⇒ ★★ **四种全到不了** ⚠
```

  ⇒ ★★ **故正确的说法是**：
    · ★ **事实 47 的判定是对的**，★ 而**理由可以更精确** —— ★ 不只"空 Dispatch 不行"，
      ★ **`None` 也不行**（★ 四种形态全试过）；
    · ★★ **`sw_pattern.py` 那套"新架构"的选区事务**本身**调不通** ⚠

  ★ **故本节的正确定论**（★ 取代上面那句）：
    ★★ **线性阵列族在 pywin32 这条后端上**目前到不了** —— ★ 而**依据比原先更硬**：
      ★ **四种第 2 参形态的真机错误码**（★ 上表）**+** ★ **那 11 份证据记的是 no-op**。
    ★ 而**"换后端能不能行"仍不写结论**（★ 那没有本机实测 —— 见 §3.3 的诚实边界）。

  ★ 证据：`tools/probe_access_selections_param2.py` · `output/access-selections-param2-evidence.json` ·
    `output/linear-pattern-geometry-evidence.json` · 事实 47 / 473 / 474。

---

### 2.3 ★★★ 2026-10-03（轮 600）**该族的另三个成员** —— ★ 四个阵列同一条边界

★ 台账「特征下拉」里有**四个阵列**：★ **曲线驱动的阵列** · **草图驱动的阵列** · **填充阵列** ·
  **表格驱动的阵列**。★ 本轮把它们的 `*FeatureData` 一起查了 —— ★ 而结论是**同一条边界**：

| 接口 | 成员数 | `AccessSelections` | 判定 |
|---|---|---|---|
| `ILinearPatternFeatureData` | 60 | ★ **有** | ★ 见 §2.2.1 |
| `ITablePatternFeatureData` | 35 | ★ **有** | ★ **同一条边界** |
| `ICurveDrivenPatternFeatureData` | 44 | ★ **有** | ★ **同一条边界** |
| `IFillPatternFeatureData` | 35 | ★ **有** | ★ **同一条边界** |
| `ISketchDrivenPatternFeatureData` | — | — | ★★ **接口根本不存在**（★ 台账那个 api 名是手填的 —— 铁律 5） |

★ **而它们的创建入口也指向同一条路**：★ 官方的 md 逐字写着
  「**Obsolete. See `IFeatureManager::CreateFeature`** and the Remarks in `I*PatternFeatureData`」
  —— ★ **即：`CreateFeature` + 那个 FeatureData** ⇒ ★ **而后者正是带 `AccessSelections` 的那个** ⚠

★ **而 `AccessSelections` 的第 2 参四种形态**（★ §2.2.1 那张表：`None` / 空 Dispatch / 空变体 /
  byref 空 Dispatch）**全到不了** —— ★ 故这四个阵列在 pywin32 这条后端上**目前到不了**。

★ 证据：`C:\swapi\types\<接口>\` 的成员表（★ 静态、可复核）·
  `tools/probe_access_selections_param2.py` · 事实 47 / 474。

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

### 3.4 ★★★ 2026-10-03（轮 546）**修正：这一族的边界**比 §三 说的窄****

> ★★ **本节是加法，不改 §三 的原文证据** —— ★ 而**把它的结论收窄**。
> ★ 触发：**事实 425/426** 的批量真机实验。

★ **§三 讲的是** `IAccessSelections` / `IAccessSelections2` **那对接口本身**
  （★ I 前缀、无 dispinterface）—— ★ 那条**成立**，★ 本节不推翻它。

★★ **而本轮的实验测的是**另一件事**：★ `*FeatureData.AccessSelections`（★ 即**数据接口上那个方法**）。

| 载体（★ 全是本仓**真机验过建成**的） | 类型名 | `GetDefinition` | `AccessSelections` |
|---|---|---|---|
| 等距曲面 | `OffsetRefSurface` | `CDispatch` | ★ **过** ✓ |
| 延伸曲面 | `ExtendRefSurface` | `CDispatch` | ★ **过** ✓ |
| 旋转曲面 | `RevolvRefSurf` | `CDispatch` | ★ **过** ✓ |
| 缝合曲面 | `ExtruRefSurface` | `CDispatch` | ★ **过** ✓ |
| 替换面 | `Extrusion` | `CDispatch` | ★ **过** ✓ |
| 曲面切除（★ 轮 545） | `SurfCut` | `CDispatch` | ★ **过** ✓ |

⇒ ★★★ **故：拿到**真特征对象**的**全部过**（**6/6**）** —— ★ 而**不是 1 个样本**。
  ★★ **⇒ 「`AccessSelections` 到不了」这条**只对 §3.3 表里那几个成员成立****，
    ★ **不能推广成"这一族都到不了"** ⚠

★★★ **2026-10-03（轮 547）再补一层 —— ★ 边界要写成**「哪个接口」****：

★ 本节（§3.4）刚立时，与**§二**（线性阵列族）看上去**冲突**：★ 那边记
  `(model, 空Dispatch)` ⇒ **`0x80010105`**。★ 故本轮**把 §二 那三种传法在同一脚本里重跑**
  （`tools/probe_linear_pattern_access_recheck.py`）—— ★ 结果**逐行复现**：
  ```
  ① `(model, None)`       ⇒ 类型不匹配（位置 2）      ✓ 一致
  ② `(model, 空Dispatch)` ⇒ **0x80010105**            ✓ 一致
  ③ `(None, None)`        ⇒ 类型不匹配（位置 1）      ✓ 一致
  ★ 而 `CreateDefinition(6)` 三组**都**拿到 `CDispatch` ⇒ 不是"没拿到 data"
  ```

⇒ ★★ **故两边**不矛盾**，原因就是**接口不同****：

| 接口 | `AccessSelections(doc, 空Dispatch)` |
|---|---|
| `ISurfaceCutFeatureData` · `IOffsetSurfaceFeatureData` · `IRevolvedRefSurfaceFeatureData` 等 | ★ **过**（**6/6**） |
| **`ILinearPatternFeatureData`**（★ 线性阵列新架构那个） | ★ **`0x80010105`** |

⇒ ★★ **故本节的标题那种写法还不够** —— ★ 边界要写成
  **「**哪个接口**的 `AccessSelections` 通」**，★ 而**不是「`AccessSelections` 通不通」** ⚠
  ★ 这与**事实 128**（可达性结论必须带**绑定层次**）**同族**：★ 可达性结论也**必须带接口**。

★ 证据：`tools/probe_linear_pattern_access_recheck.py` ·
  `output/linear-pattern-access-recheck-evidence.json` · 事实 **427**。

★★ **而 §二 的结论因此**不变****（★ 线性阵列族**仍到不了**）—— ★ 只是它的**理由现在更精确**：
  ★ **不是"指针族"，而是"`ILinearPatternFeatureData` 这个接口"**。

★★ **而 `Component` 参数有个坑**（★ 事实 425）：★ **必须传空 Dispatch 变体**（`create_empty_dispatch_variant()`），★ **传 `None` 会报 `类型不匹配（位置 2）`** —— ★ 而那个错**看不出是它的错**（★ 事实 12/33 的第三次应验）。

★ 证据：`tools/probe_access_selections_matrix.py` ·
  `output/access-selections-matrix-evidence.json` · 事实 **425 / 426**。

### 3.5 ★★★ 2026-10-03（轮 567）**该族的新实例** —— 投影曲线的 FeatureData 也在里面

★ 上一条说「`*FeatureData.AccessSelections` **6/6 通**」—— ★ **而本节补一条边界**：
  ★ **那 6 个里不包含「投影曲线」这个接口** ⚠

```
IProjectionCurveFeatureData.AccessSelections(doc, 空Dispatch)
  ⇒ com_error(-2147417851) = **0x80010105**（★ 与事实 47 同一个错误码）
★ 而同一接口的 ReleaseSelectionAccess() **是通的**
```

★ 怎么到这儿的：★ 事实 445 把**投影曲线**的链推到第 4 步（★ `CreateDefinition(swFmRefCurve=14)`
  **回 `CDispatch`** · 三个非实体属性**均设成**）⇒ ★ 而 `CreateFeature` 回 `None`
  ⇒ ★ 本轮把 `AccessSelections` **插进去验证「它是不是缺的那一步」** ⇒ ★ **结果给出了一条边界**。

⇒ ★★ **故正确说法是**：★ **那一族的可达性要**逐接口看****（★ 与**事实 128**同族：
  「可达性结论必须带**绑定层次**」）—— ★ **不能拿"6/6 通"推广到整个族** ⚠

★ 证据：`tools/prove_projection_curve.py` · `output/projection-curve-evidence.json` · 事实 **446**。

---


### 3.6 ★★★ 2026-10-03（轮 578）**新实例：`IMathUtility` 整族**（★ 而两类错码有规律）

★ 上一节说“那一族的可达性要**逐接口看**”—— ★ 而本节给出**整族**的一个例子**：

```
ISldWorks.GetMathUtility              ⇒ **ok**（★ 对象**拿得到**）✓
CreatePoint / CreateVector / CreateTransform（**不带 I**）
                                      ⇒ **`找不到成员`**（`0x80020003`）
ICreatePoint / ICreateVector（**带 I**）
                                      ⇒ **`无法读只写属性`**（`61836`）
```

⇒ ★★ **规律很整齐**：★ **不带 `I` 的名字取不到；带 `I` 的名字取得到、而**形态不对****。
★ **而它与事实 36 / 47 同一族**：★ **`I` 前缀是“进程内 C++ 指针变体”**（★ 事实 47 逐字），
★ 而迟到绑定下它**被当成属性** ⚠

★ **上下文**：它是为了办**曲面上的样条**（★ 需 `IMathVector` 数组作方向）而查的
  —— ★ **故那一条的思路在这里断了**。

★ 证据：`tools/probe_imathutility_family.py` · `output/imathutility-family-evidence.json` · 事实 **456**。

---

---

### 3.7 ★★★ 2026-10-03（接手轮）**该族的新实例：草图「样条曲线」**（★ 而它纠正了一次"有实现"的误读）

**项**：草图绘制 · **样条曲线**（`docs/user-feature-coverage.md` §八 的缺口项之一）。

**官方现状**（`C:\swapi\types\ISketchManager\`）：

| 成员 | 签名（逐字） | 备注 |
|---|---|---|
| `CreateSpline2` | `SketchSegment CreateSpline2( System.object PointData, System.bool SimulateNaturalEnds )` | ★ 官方标 **Obsolete** |
| `CreateSpline` | `SketchSegment CreateSpline( System.object PointData )` | 旧版（1 参） |
| `CreateSpline3` | `SketchSegment CreateSpline3( Object, Object, Object, Boolean, **Object&** )` | ★ 后继；★ **末参是 BYREF 引用** |

**真机证据**（2026-10-01 轮 141，`tools/probe_spline_creation.py` / `probe_spline_redraw.py`）：

```
① CreateSpline2(arr, False)            ⇒ 返回 None ⇒ 草图段数 = 0
② 重绘后（IModelView::GraphicsRedraw）  ⇒ 段数仍 = 0
   ⇒ ★ 排除了官方 Remarks 那句"必须重绘才看得见"的解释
③ CreateSpline（1 参旧版）              ⇒ ★ 迟到绑定里**没有这个成员**
④ 对照·同样流程画直线                    ⇒ 段数 = 1 ⇒ ★ **流程本身没问题**
```

**归因**：★ `CreateSpline2` 已废弃，★ **后继 `CreateSpline3` 的末参是 BYREF `Object&`**
⇒ ★ 与 §3.1 同一个机理（**引用参数在 pywin32 迟到绑定下到不了**，事实 47 / 68）。

**★ 本条另有一个方法论价值（★ 它纠正了一次"有实现"的误读）**：
`tools/audit_gap_implementations.py`（**AST**：本仓有没有**真调用**该成员）报本项「**有实现**」——
★ 因为 `scripts/sw_part.py::sketch_spline` **确实调了** `CreateSpline2`。
★★ 而**读那个函数自己的文档串**才发现：它**早在本轮之前就被真机判为不达**，并已改成**抛异常**（不再静默）。
⇒ ★★★ **故「有实现」≠「能用」** —— 中间**必须**再过两关：**① 读它自己的文档串；② 真机**。
★ 这正是本轮**故意不把样条接成工具**的原因（★ 不假装做到）。

★ **与 §3.4 的关系**：★ 本条**不扩大** §3.4 已经收窄过的边界 ——
★ 判据仍是**"参数里有 BYREF / 指针"**，★ **不是**"存在 `*FeatureData`"。
★★ 反例就在本会话：分割线也有 `ISplitLineFeatureData`，★ 而它的**直入法真机建成了**（事实 484）。

**证据**：`tools/probe_spline_creation.py` · `tools/probe_spline_redraw.py` · `scripts/sw_part.py::sketch_spline`
（★ 连带登记：`docs/backend-limited-items.json` 第 13 条）。

---

## 四、结构系统（焊件）—— ✅ **成立**（★ 本节已在轮 485 更正）

> ★★★ **2026-10-03（轮 485）更正** —— ★ 本节**原文**判它「不成立」，★ 而**理由是"本仓有 `sw_weldment.py` 与证据"**
> —— ★★ 那**又是"看文件存在"得出的结论**（★ 与轮 482 那次的错法**同一个**）⚠
>
> ★★ **实际证据**（`output/weldment-evidence.json`，`verdict: partial` · **1/3**）逐字：
> ```
> create_cut_list           ok:false  RuntimeError: IFeatureManager.InsertWeldmentCutList2
>                                     在当前后端（pywin32 迟到绑定）上**取不到**
>                                     （权威类型库里有该成员，但 CO…）
> set_cut_list_properties   ok:false  没有可写入切割清单的结构构件实体
> export_cut_list_csv       ok:true   path=…\_weldment_smoke.csv  size=26
> ```
> ⇒ ★★★ **故**：★ **导出能跑（那只是写 CSV，不依赖 COM 建模）**、
> ★★ 而 **`InsertWeldmentCutList2` 取不到** —— ★ 那与**事实 28**
> （「反射里有」≠「运行期调用得到」）**同族**，★ 属于**另一个后端限制** ✓
>
> ★ 另外 `output/weldment-profile-evidence.json` 是 **pass · 3/3**（★ 那验的是**轮廓库**可用性，
>  ★ 本机装了 111 个 `.sldlfp`）⇒ ★ **两者说的是不同的事，不该混谈** ✓
>
> ⇒ ★ **归因成立**（★ 结构系统到不了），★ **而"理由"是「切割清单那条入口取不到」**，
>   ★ **不是"整族不行"** —— ★ 准确说法是 **partial**：**轮廓库与导出可用、切割清单不可用** ✓

### 4.1 ★★★ 2026-10-03（轮 548）补两点证据 —— 「取不到」的形态 + **焊件特征真能建**（事实 428）

> ★★ **本节是加法** —— ★ 上面 §四 的归因**已经是对的**（★ 包含「不是"整族不行"」那句），
> ★ 本节只补**两条它没写到的证据**。

★ **第一点：「取不到」的**精确形态**（★ 一个**第四类失败****）

★ 真机（`tools/probe_weldment_cutlist_recheck.py`，★ 两体件、零弹窗）：
  ```
  ① `InsertWeldmentCutList2([])`   ⇒ **`getattr` 回 `NoneType`**（成员**不可调用**）
     ★ 即：**它在权威类型库里有（arity=2 · 1 in `Bodies`）、而在**实际对象上取不到**
  ② `InsertWeldmentCutList()`（旧版）⇒ **`silent_none`**（回 `None` · 树不动）
  ③ **`InsertWeldmentFeature()`**      ⇒ **`CDispatch` · 名 = `焊接件` · 型 = `WeldmentFeature`**
     ★ 而 `new = ['焊接件']` ⇒ ★★★ **它真机建成了！** ✓
  ```
  ★ 而静态先查过：★ **两源都有 `InsertWeldmentCutList2`**（swapi md + CHM）
  ⇒ ★ **故"取不到"不是"官方没有它"** ✓

⇒ ★★ **故失败形态至此有**四类****（★ 事实 420 那三类 + 本轮这一类）：

| 类 | 表现 | 例 |
|---|---|---|
| ① 回**对象** | 建了但在树外 | `InsertCutSurface` |
| ② 回**`None`** | 真的没建 | 加厚 · 直纹 · 剪裁 · 扫描曲面 · 分割线 |
| ③ **报错** | 抛异常 | `ILinearPatternFeatureData.AccessSelections`（`0x80010105`） |
| ④ ★★ **成员不在对象上** | `getattr` 回 `NoneType` | **`InsertWeldmentCutList2`** |

★★ **第二点（★ 这是最该记的）：`InsertWeldmentFeature` **真机建成「焊接件」** ✓**
  ⇒ ★★ **故到不了的是「切割清单」这一条能力**，
  ★ 而**「焊件特征本身」是**能建的**** ⚠ —— ★ 与 §四 那句"不是整族不行"一致，★ 而**本轮给了正面证据**。

★ 证据：`tools/probe_weldment_cutlist_recheck.py` ·
  `output/weldment-cutlist-recheck-evidence.json` · 事实 **428**。

### 4.2 官方现状

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

## 五之二、★ **第五种形态：静默 no-op**（★ 调用不报错、也不改变任何东西）

> ⚠⚠ **2026-10-03（轮 562）★ 更正**：★ 本节原先拿「**删除孔**」当**唯一实证** ——
> ★ 而轮 562 查出**那个入口是废弃的第一代**（md 逐字：*Obsolete. Supserseded by
> `IFeatureManager::InsertDeleteHoleForSurface`*）⇒ ★ **故本节的那个实证不成立**（★ 见 §5.2.3）。
> ★ **而「第五种形态」这个**分类本身仍然有用**** —— ★ 它描述的是**判据盲区**；
> ★ **只是本文件目前还没有一个站得住的实例** ⚠ ★ 故它暂时是**待补的分类**、不是已证的形态。

★ 事实 420 / 428 记了**四种**失败形态（① 回对象 · ② 回 `None` · ③ 报错 · ④ 成员不在对象上）。
★ **本节补第五种**，★ 而它是**最容易被误记成"做成了"**的一种 —— ★ 因为**它不报错** ⚠

| # | 形态 | 判据怎么才看得见 |
|---|---|---|
① | 回**对象**（而对象在树外） | 只有**几何量**看得见（★ 事实 406/407） |
② | 回 **`None`** | 显然 |
③ | **报错** | 显然 |
④ | **成员不在对象上**（`getattr` 回 `NoneType`） | 显然 |
★⑤ | **静默 no-op**（★ 不报错 · 树不动 · **几何量也不动**） | ★ **只有"前后都测几何量"才看得见** ⚠ |

### 5.2.1 实证：`IModelDoc2.InsertDeleteHole()`

★ 台账曲面栏的「**删除孔**」→ `IModelDoc2.InsertDeleteHole()`（★ 全接口查确认在 `IModelDoc2` 下 ·
**0 参** · 回 **`void`**）。

★ **两轮、六种前置，全部零效果**（★ 都走 `sw_guard`、零弹窗）：

| 轮 | 前置 | 选什么 | 结果 |
|---|---|---|---|
| 559 | **原生实体**（带一个拉伸切除的孔） | — | 面 7→7 · 体积无变化 · 树不动 |
| 559 | 对照：**原生实体无孔** | — | 面 6→6 · 同上 |
| 560 | **带内环（缺口）的曲面**（5 面 / 6 环 / 14 边） | 只选**面** | 面 5→5 · 环 6→6 · **面积 Δ = 0** |
| 560 | 同上 | 选**孔的那圈边** | 同上 |
| 560 | 同上 | **面 + 边都选** | 同上 |
| 560 | 同上 | **什么都不选** | 同上 |

★ 证据：`output/delete-hole-evidence.json` · `output/delete-hole-on-surface-evidence.json`；
★ 探针：`tools/prove_delete_hole.py` · `tools/prove_delete_hole_on_surface.py`。

### 5.2.2 ★ 归因（★ 按铁律 5，不猜「换后端能不能行」）

★ **可确证的**：★ 在上述**六种前置**下，该成员**不产生任何可观测变化**（★ 而它**不报错**）。

★ **最可能的解释**（★ 标为**解释**、不是结论）：★ SolidWorks 界面的「删除孔」是
  **曲面 / 导入体的修补**命令 —— ★ 它处理的是**导入几何里的缺口**，
  ★ 而**不是"删掉某个钻孔特征"** ⚠ ⇒ ★ 故在**原生体**上 no-op 是**应然的**（★ **名字误导**）。

★ **下一步该做什么**（★ 若要用它）：★ 在**导入的**（★ 而非原生的）带缺口模型上试 ——
  ★ 那需要先造一个**导入体**，★ 而本仓**尚无**"导入 STEP/IGES 再修补"的链路。

★ **按事实 53 停手**：★ 两轮 / 六种前置零效果 ⇒ ★ **不再换参数试**；
  ★ 台账该条**留在「可攻关」**，★ 而**不假装做到**。

★ ★ **配套的可复用定则**：★ **凡"成员是 0 参且回 `void`"的，判据必须是几何量的前后差** ——
  ★ 因为**返回值里没有任何东西能证明它做过什么**，★ 而**树增量也常常看不见**（★ 事实 436）。

---

### 5.2.3 ⚠ **撤销本节原本的实证**（★ 事实 441 · 轮 562）

★ 本节 §5.2.1 那六格，用的入口是 **`IModelDoc2.InsertDeleteHole()`** ——
  ★ 而它的 md **逐字**写着：

> "**Obsolete. Supserseded by `IFeatureManager::InsertDeleteHoleForSurface`.**"

⇒ ★★ **故「六格零效果」的真因是**入口错**（★ 我打的是废弃的第一代），
  ★ **而不是"那个成员本身是 no-op"** ⚠ ⇒ ★ **本节的实证不成立**。

★ **而继任者的文档把前置说得很清楚**：

```
Feature InsertDeleteHoleForSurface()      ← **0 参**、★ **回 `IFeature`**（不是 void）
Remarks: call SelectByID2 to select the **hole edges to remove** from the surface
```

★ 真机（`tools/prove_delete_hole_for_surface.py`）：
```
继任者 + 选"孔的边" ⇒ 回 `None` · 面 5→5 · ★ **而 `picked = 12`**（★ 那是**整个体的所有边**，不是孔的）⚠
对照：废弃的第一代（建在 `IFeatureManager` 上）⇒ **`AttributeError: <unknown>.InsertDeleteHole`**
```

⇒ ★★ **故**：★ ① 本节原本的实证**撤销**；② ★ **"选孔的边"这个前置我还没真搭对**
  （★ 我选了整个体的 12 条边）；★ **下一步**：★ **只选内环（孔）那一圈边**。

★ ★★ **可复用的方法论**：★ 用「零效果」去立一条边界**之前**，
  ★ 必须先确认自己打的**不是废弃的那个入口** —— ★ 而**查废弃只需读 md 头顶一行** ⚠

---

## 五之三、★ **「尚未证实」≠「到不了」** —— 复合曲线（★ 三停手，★ 而**不写成边界**）

★ 事实 53（连续 ≥3 次同一处就该停下）在本条上触发了 ⇒ ★ **而它停下来时，状态是"尚未证实"、不是"到不了"** ⚠

| 轮 | 试的实体形态 | 结果 |
|---|---|---|
| 570 | **体的两条边**（mark=1） | 回 `False` |
| 572 | **同一草图的两段** / 体的两边 / 不选 | ★ **三格全 `False`** |
| 573 | 照**官方例子**：两个**样条草图** + `SelectByID2` | ★ **卡在"造样条"那一步**（`草图=None`），**未跑到目标调用** |
| 573 | 对照：两个**直线草图** + `SelectByID2` | `sel=2`（选上了）· ★ **而仍 `False`** |
| **575** | 照**官方例子**（★ **样条现在造得出来了** —— 事实 452） | ★ **`sel=2`、两个样条草图都选中了 · 而仍 `False`** ⚠ |

★ **故状态在轮 575 升级了**：★ 从「**尚未证实**」（★ 卡在造样条）
  ⇒ ★★ **「已按官方例子试过（两个样条草图 + `SelectByID2` mark=1），仍回 `False`」** ⚠
  ★ 而★ 这**仍不等于「到不了」** —— ★ **原因尚未查明**。

★ **故如实分两句**：
- ★ **已试过的四种实体形态全失败**（体的边 · 同草图两段 · 不选 · 直线草图）；
- ★★ **而例子里那个形态（样条草图）**还没真试到** ⇒ ★ **不能写"到不了"** ⚠

★ **卡住的那一步很具体**：`ISketchManager.CreateSpline(pts)` 报
  `com_error(-2147352561, '非选择性的参数。')` ⇒ ★ **即点数组的传法不对**
  （★ 官方 Remarks 说过它要**至少两个 X,Y,Z**）。

★ **留给下一步**：★ 先把 **`CreateSpline` 的点数组传对**（★ 那本身是一条**草图图元**能力），
  ★ **再回来试复合曲线**。

> ★★ **2026-10-03（轮 575）★ 那个前置完成了**（★ 事实 452：`CreateSpline2` + `VARIANT(VT_ARRAY|VT_R8)` + `False`）
> ⇒ ★ **而复合曲线仍回 `False`** ⚠
> ★ **故剩下的假设**（★ 皆未验证）：★
> ① 那两个草图要**同类型**（★ 例子说 "two sketches of **splines**"，★ 我造的是两条 **3 点样条**，
>    也许要**真样条**的特定状态）；★ ② 也许要**跨两个平面**的特定相对位置；
> ③ 也许**创建**也要走 `ICompositeCurveFeatureData`（★ 例子只把它用于**读回** `GetEntitiesToJoinCount`）。
> ★ **按事实 53 停手**（★ 已四轮）—— ★ **而状态是「未证实原因」、不是「到不了」** ⚠

★ ★★ **可复用的方法论**：★ **「我试过了」与「我试到了那一步了」不是一回事** ——
  ★ 一组因为**前置没搭成**而没跑到目标调用的，★ **不能计入"试过了"** ⚠
★ ★★ **而反过来也有一条**：★ **前置搭成之后再试一次，状态就升级了** ——
  ★ 从「尚未证实」变成「**已按官方例子试过**」，★ **那是更值钱的一句话** ✓

---

## 六、★ 本文件**不做**什么

- ★ **不改** `docs/toolbar-ledger.json` 里的判定 —— ★ 那是**核实器的产物**；
  ★ 本文件只**指出**它的归因错在哪、证据在哪（★ 改判要连同核实器的判据一起改，★ 否则下次重生成又回去）。
- ★ **不把「换后端能不能行」写成结论** —— ★ 那**没有本机实测**（★ 见 §3.3 的诚实边界）。
- ★ **不删**任何"到不了"的包装 —— ★ 它们**是可复算的证据**（★ 也是换后端时的起点）。
