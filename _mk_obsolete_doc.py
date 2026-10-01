import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

DOC = """# 「官方已废弃但我方仍在调」的成员 —— 复核台账

> 来源：`tools/probe_obsolete_members.py`（2026-10-01 轮 110，Spec Kit `029`）
> ⚠⚠ **这不是门禁的判据，是人工复核清单** —— 理由见文末「为什么不能做成门禁」。

## 一、怎么产生的
```
1. 抽代码里 `get_com_member(<目标>, "<成员>")` 的**成员名** —— 共 429 个；
2. 去 `C:\\swapi\\types\\**\\<成员>.md` 找同名官方文档；
3. 文档正文带 `Obsolete` 的 ⇒ 列出，并把 `Superseded by` 指向谁一起打出来。
⇒ 命中 **38** 个候选。
```

## 二、★ 已核实**为真**（我们确实在调官方已废弃的入口）

| 成员 | 官方文档所在接口 | 后继 | 我们在哪用 | 依据 |
|---|---|---|---|---|
| `GetLines` | `ISketch` | `ISketch::GetLines2` | `sw_sketch.py` | 该模块 docstring 明写「**ISketch 完整封装**」，来源块也引 `ISketch 段` |
| `GetArcs` | `ISketch` | `ISketch::GetArcs2` | `sw_sketch.py` | 同上 |
| `GetEllipses` | `ISketch` | `ISketch::GetEllipses3` | `sw_sketch.py` | 同上 |
| `GetParabolas` | `ISketch` | `ISketch::GetParabolas2` | `sw_sketch.py` | 同上 |
| `GetSketchPoints` | `ISketch` | `ISketch::GetSketchPoints2` | `sw_sketch.py` | 同上 |
| `GetUserPoints` | `ISketch` | `ISketch::GetUserPoints2` | `sw_sketch.py` | 同上 |
| `AddMate5` | `IAssemblyDoc` | `IAssemblyDoc::CreateMate` | `sw_assembly_doc.py` | 模块名即 `assembly_doc` |
| `GetBodies2` | `IComponent2` | `IComponent2::GetBodies3` | `sw_assembly.py` / `sw_geometry_selectors.py` / `sw_hole_features.py` / `sw_review.py` | 调用目标是**装配体零部件** |

```
⇒ **8 条确认为真**（其中最集中的一簇是 `sw_sketch.py` 的 **6 个 ISketch 取法**）
```

⚠ **它们能不能用，未知**：本台账只证「**官方标了废弃**」，**不证「跑不通」**。
`sw_sketch.py` 有测试、这些取法很可能**当前仍工作**（与已知事实 40 的情形类似：
废弃 ≠ 立刻失效）。**但在未来版本上有被移除的风险。**

## 三、已核实**为假阳性** —— 同名但**不同接口**

| 成员 | 文档在 | 我们实际用的 | 为什么误报 |
|---|---|---|---|
| `Add2` | `ICustomPropertyManager` | **`IEquationMgr.Add2`** | 同名不同接口；`IEquationMgr.Add2` **未**废弃 |
| `Delete` | `ICustomPropertyManager` | **`IEquationMgr.Delete`** | 同上 |
| `GetMassProperties` | `IModelDoc2` | **`IModelDocExtension.GetMassProperties`** | 文档的「后继」正是我们用的那个 |
| `GetRenderMaterials` / `…Count` | `IComponent2` | **`IModelDocExtension.*`** | 同上（`list_render_materials` 实测可跑，见 `012`）|
| `GetModelDoc` | `IComponent2` | 我们也调 `GetModelDoc2` | 后继已在用 |
| `GraphicsRedraw` / `GraphicsRedraw2` | `IModelDoc2` | 两个都调了 | 互为后继，**无法据此判** |
| `Name` | `IComponent2` | 我们也调 `Name2` | 后继已在用 |
| `ResumeSelectionList` | `ISelectionMgr` | 我们也调 `ResumeSelectionList2` | 后继已在用 |
| `Scale` | `IFaceHatch` | 我们也调 `Scale2` | 后继已在用 |
| `MaterialIdName` | `IModelDoc2` | 我们也调 `SetMaterialPropertyName2` | 后继已在用 |

```
⇒ **10 条已核实为假阳性**（同名不同接口 / 后继已在用）
```

## 四、⚠ 未逐条核（其余 20 条）
`AdvancedGraphics` · `AutoDimension2` · `ExcludeFromBOM` · `GetComponents` ·
`GetDependencies2` · `GetEdges` · `GetErrorCode` · `GetNext` · `GetPolylines` ·
`GetSplines` · `GetType` · `GetUserPreferenceToggle` · `IsSuppressed` · `KFactor` ·
`MoldUndercutDetect` · `ReferenceType` · `SetUserPreferenceToggle` · `SystemValue` 等

**⇒ 未逐条核。**

## 五、⚠⚠ 为什么**不能**做成门禁
```
38 条候选里：
  · 已核实为真   8 条
  · 已核实假阳性 10 条
  · 未逐条核     20 条
⇒ **假阳性率 ≥ 26%**（10/38），且**剩余大半里还会有一批**
```
★ 这与本项目**反复出现的同一个教训**一致：
**按名字做的自动检查，假阳性太多，不能当判据。**
⇒ 所以本台账**只出清单，不拦发布**。

⚠ 真正的困难是**同名不同接口**：`GetMassProperties` 在 `IModelDoc2` 上废弃、
在 `IModelDocExtension` 上**没废弃**；光有成员名**判不出**我们调的是哪个。
（这与已知事实 36「同名接口分属不同族」是同一类问题。）

## 六、未查证
* 这 8 条**能不能跑** —— 未测（本台账只管「官方标了废弃」）；
* 剩余 **20 条未逐条核**；
* 探针只扫 `get_com_member(...)` 这一种调用形态；**其它调用形态未扫**。
"""

P = Path(r"C:\swprojects\sw-skill-fork\docs\obsolete-member-candidates.md")
P.write_text(DOC, encoding="utf-8")
print("  ok 已写 docs/obsolete-member-candidates.md")
