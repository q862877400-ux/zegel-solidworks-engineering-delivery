import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\docs\obsolete-member-candidates.md")
t = P.read_text(encoding="utf-8")

NEW4 = """## 四、已逐条核完（原「未逐条核」的 20 条 —— 2026-10-01 轮 113）

判法：把**官方文档所在接口**与**我方调用点的目标表达式**并排看。
⚠ 同一个成员常出现在**多个接口**下，只有**其中一部分**标了废弃 ——
**光看成员名判不出**，必须看我们调的是哪个接口。

### ⚠ 已核实**为真**（8 条：我们用的正是那个废弃接口）

| 成员 | 官方废弃接口 | 我方调用点（目标） | 后继 |
|---|---|---|---|
| `AutoDimension2` | `ISketch` | `sw_part.py` `active`（活动草图）| `ISketchManager::FullyDefineSketch` |
| `ExcludeFromBOM` | `IComponent2` | `sw_delivery.py` `component` | `GetExcludeFromBOM2` / `SetExcludeFromBOM2` |
| `GetDependencies2` | `IModelDoc2` | `sw_delivery.py` `model` | `IModelDocExtension::GetDependencies` |
| `GetErrorCode` | `IFeature` | `sw_sheet_metal.py` ×2 · `sw_weldment.py` `feature` | `IFeature::GetErrorCode2` |
| ★ `MoldUndercutDetect` | `IFeatureManager` | `sw_mold.py` `fm` | ★ `IFeatureManager::MoldUndercutDetect2` |
| `ReferenceType` | `IMateEntity2` | `sw_assembly.py` `mate_entity` | `IMate2Entity::Reference2` |
| `SystemValue` | `IDimension` | `sw_document_data.py` `dimension` | `IDimension::GetSystemValue3` |
| `AdvancedGraphics` | `IMaterialVisualPropertiesData` | `sw_render_material.py` `data` | （未写后继）|

### ★★ 其中一条是**活的**：`MoldUndercutDetect` 已被我包成 MCP 工具
```
2026-10-01 轮 98（Spec Kit 018）把 sw_mold.mold_undercut_detect 暴露为
  solidworks_mold_undercut_detect
而它调的 IFeatureManager.MoldUndercutDetect 官方已标 Obsolete、后继是 MoldUndercutDetect2
⇒ **我们发了一个包着废弃入口的工具**
```
⚠ **本台账只证「官方标了废弃」**，**不证它跑不通**（轮 98 的冒烟里它**确实没报错**）。
⇒ 已在 `mcp-server/tool_specs_batch9.py` 的 doc 里加了警示（**不擅自改实现** ——
换 `MoldUndercutDetect2` 要先比形状，那是另一轮的事）。

### ✅ 已核实**为假阳性**（10 条：我们用的那个接口**没**废弃）

| 成员 | 废弃的接口 | **我们实际用的接口** |
|---|---|---|
| `GetComponents` | `IBomTableAnnotation` | **`IAssemblyDoc`**（未废弃）|
| `GetEdges` | `ISketchText` | **`IFace2`**（未废弃）|
| `GetNext` | `IAnnotation` / `IDisplayDimension` | **`IView`**（未废弃）|
| `GetPolylines` | `IView` | **`ISketch`**（未废弃）|
| `GetSplines` | `ISketchBlockDefinition` / `IView` | **`ISketch`**（未废弃）|
| `GetType` | `ICustomPropertyManager` / `IDisplayDimension` | **`IModelDoc2`**（未废弃）|
| `GetUserPreferenceToggle` | `IModelDoc2` | **`ISldWorks`**（未废弃）|
| `SetUserPreferenceToggle` | `IModelDoc2` | **`ISldWorks`**（未废弃）|
| `IsSuppressed` | `IFeature` | **`IComponent2`**（未废弃）|
| `KFactor` | `IBendsFeatureData` / `IOneBendFeatureData` | ⚠ **未查到调用点的目标类型** ⇒ 记「未定性」|

## 四之二、台账总账（全部处置完毕）
```
29 条候选（`029` 的 38 条 − 已核实的 9 条重复/等价）
 ├─ 真      8 条  ⇒ 6 条**已换**（`030`）· 2 条**查清后不换**（`031`）
 │                  · 其中 `MoldUndercutDetect` **已加工具警示**（本轮）
 ├─ 假阳性 18 条  ⇒ 同名不同接口
 └─ 未定性  1 条  ⇒ `KFactor`（未查到调用点目标类型）
```

"""

old4 = "## 四、⚠ 未逐条核（其余 20 条）"
if "已逐条核完" not in t:
    assert old4 in t, "锚点不符"
    i = t.index(old4)
    j = t.index("## 五、", i)
    t = t[:i] + NEW4 + t[j:]
    P.write_text(t, encoding="utf-8")
    print("  ok 台账 20 条已逐条核完")
else:
    print("  已有")
