# vd50-B · misc 域「置信度为高」条目复核

**范围**：域 `10-misc`，只核 `audit-vs-official/` 下三份 misc 核对表里**置信度标「高」**的条目。
**来源**：`audit-10-misc-A.md`（1 条）· `audit-10-misc-B.md`（3 条：#1 #2 #3；#4 #5 #6 是「中」，不碰）·
`audit-10-misc-C.md`（10 条，#1–#10 全为「高」）。
**共核 14 条。**

**两条铁律的做法**：① 官方侧一律去 `C:/swapi/` 逐字搜；② 仓内侧一律去 `D:/AI/SW/` 逐字搜。
**两段原文缺一段的一律不写进表** ⇒ 下方每条都带「仓内那一段」+「官方那一段」两个可搜索片段。
**全文不写行号**（会漂移），一律写片段。

---

## 总账

| 判定 | 条数 | 条目 |
|---|---|---|
| **成立** | **13** | A#1 · B#1 · B#2 · B#3 · C#1 · C#2 · C#3 · C#4 · C#5 · C#7 · C#8 · C#9 · C#10 |
| **不成立** | **1** | **C#6** |
| **存疑** | 0 | — |

**核了 14 处 · 对不上 1 处（C#6：官方原文在，★「我们的原文」不在那个文件里）。**

---

## A#1 · `audit-10-misc-A.md` 第 1 条 · 判定：**成立**

- **官方原文（在）** — `C:\swapi\types\IModelDocExtension\GetMassProperties.md` 逐字：
  `**Signature**: `System.object GetMassProperties( System.int Accuracy, out System.int Status )``
  旁证两条也都核到：出厂反射 `D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt` 在 **`## IModelDocExtension`** 段内逐字 `Object GetMassProperties(Int32, Int32&)`；
  `scripts/sw_connect.py` 的 `get_com_member` 里逐字 `return member(*args)`（证明 `*args` 原样透传、不补位）。
- **我们的原文（在）** — `scripts/sw_export.py` 的 `get_mass_property_override_options` 里逐字：
  `mass_property = get_com_member(extension, "GetMassProperties", float(accuracy))`
- **依据**：官方两个源一致给 **2 个形参**（`System.int Accuracy` + `out System.int Status`），我方只给 **1 个**实参且是 `float(...)`，个数与首参类型双双不符。

---

## B#1 · `audit-10-misc-B.md` 第 1 条 · 判定：**成立**

- **官方原文（在）** — `C:\swapi\types\IFeatureManager\InsertRefPlane.md` 的 Remarks 逐字：
  `Before calling this method, you must have selected the reference entities using these marks with [[IModelDocExtension::SelectByID2]]:`
  且紧接着**给了取值表** `- 0 = First reference entity` / `- 1 = Second reference entity` / `- 2 = Third reference entity`。
- **我们的原文（在）** — `scripts/sw_ref_geometry.py` 的 `insert_ref_plane` 里逐字：
  `"selection_mark": "★ 官方 Remarks 只说「these marks」、**未给取值表** ⇒ 不假定"},`
  同函数调用点逐字 `obj = get_com_member(fm, "InsertRefPlane",` 与 `int(first_constraint), float(first_angle_or_dist),`；
  ★ 从取 `FeatureManager` 到该调用之间**只有 `before = _tree_names(model)`，无任何选择动作**（全文件搜 `SelectByID2` / `Select4` / `ClearSelection2` / `SelectByRay` 命中 0 处代码，仅注释里出现）。
- **依据**：官方**明确给了 mark 取值表 0/1/2**，而我们的返回值逐字断言「未给取值表 ⇒ 不假定」，且调用前不做选择 —— 官方写死的前置两步都没做。

---

## B#2 · `audit-10-misc-B.md` 第 2 条 · 判定：**成立**

- **官方原文（在）** — 两个入口逐字相同：
  `C:\swapi\types\IFeatureManager\InsertProtrusionBlend2.md` 与 `C:\swapi\types\IFeatureManager\InsertCutBlend.md` 各有
  `When UseAutoSelect is false, the user must select the bodies that the feature will affect.`
- **我们的原文（在）** — `scripts/sw_loft.py` 两处元组各逐字一行 `False,                   # UseAutoSelect`
  （`InsertProtrusionBlend2` 的 18 元组与 `InsertCutBlend` 的 12 元组各一处）；★ 全文件无 `SelectByID2` / `Select4` / `GetBodies` 等任何 body 选择动作，
  只有 `GetSelectedObjectCount2` 读 mark=1 的**轮廓**数；`UseAutoSelect` 未暴露成可配参数。
- **依据**：官方写明该值为 false 时**必须由用户选中受影响的 body**，我方硬编码 `False` 且全程不选 body。

---

## B#3 · `audit-10-misc-B.md` 第 3 条 · 判定：**成立**

- **官方原文（在）** —
  `InsertProtrusionBlend2.md`：`You can use any number of profiles; however, if you select only one profile, then any selected guide curves must be closed curves.`
  `InsertCutBlend.md`：`You can use any number of profiles; however, if you selected only one profile, then any selected guide curves must be closed curves.`
- **我们的原文（在）** — `scripts/sw_loft.py` 逐字：
  `if use_selected_profiles and sel_n < 2:` ＋ `"error": "放样至少要选 **2 个轮廓**（★ mark=1 —— 官方 Remarks）；"`
  `if sel_n < 2:` ＋ `"error": "放样切除至少要选 **2 个轮廓**（★ mark=1 —— 官方 Remarks）；"`
- **依据**：官方写「轮廓数量任意」，只在**只有 1 个**时附加引导线须闭合的条件；我方两处 `< 2` 门禁把官方允许的 1 轮廓情形一并挡掉。

---

## C#1 · `audit-10-misc-C.md` 第 1 条 · 判定：**成立**

- **官方原文（在）** — `C:\swapi\types\IModelDocExtension\SaveAs.md` 正文首行逐字：
  `Obsolete. Superseded by [[IModelDocExtension::SaveAs2]].`
- **我们的原文（在）** — `scripts/sw_export.py` 两处：`export_to_pdf` 里逐字
  `success = model.Extension.SaveAs(str(output_path), 0, 1, pdf_data, errors, warnings)`；
  `_export_generic` 里逐字 `success = model.Extension.SaveAs(`
- **依据**：两条导出路径都调官方标 `Obsolete` 的 `IModelDocExtension.SaveAs`，后继是 `SaveAs2`。

---

## C#2 · `audit-10-misc-C.md` 第 2 条 · 判定：**成立**

- **官方原文（在）** — `C:\swapi\types\IModelDoc2\SetUserPreferenceIntegerValue.md` 正文首行逐字：
  `Obsolete. Superseded by [[IModelDocExtension::SetUserPreferenceInteger]].`
- **我们的原文（在）** — `scripts/sw_export.py` 的 `export_to_stl` 里逐字：
  `model.SetUserPreferenceIntegerValue(78, quality_map[quality])  # swSTLQuality`
- **依据**：我们调的是 `IModelDoc2` 上那个整数首选项设置成员，官方标 `Obsolete`、后继改在 `IModelDocExtension` 上。

---

## C#3 · `audit-10-misc-C.md` 第 3 条 · 判定：**成立**

- **官方原文（在）** — `C:\swapi\types\IModelDocExtension\GetMassProperties.md` 正文首行逐字：
  `Obsolete. Superseded by [[IModelDocExtension::GetMassProperties2]].`
- **我们的原文（在）** — `scripts/sw_export.py` 的 `get_mass_property_override_options` 里逐字：
  `mass_property = get_com_member(extension, "GetMassProperties", float(accuracy))`
- **依据**：`IMassProperty2` 对象取自官方标 `Obsolete` 的 `GetMassProperties`，调用仍走旧成员而非后继 `GetMassProperties2`。

---

## C#4 · `audit-10-misc-C.md` 第 4 条 · 判定：**成立**

- **官方原文（在）** — `C:\swapi\types\ISldWorks\ActivateDoc2.md` 正文首行逐字：
  `Obsolete. Superseded by [[ISldWorks::ActivateDoc3]].`
- **我们的原文（在）** — `scripts/sw_export.py` 的 `_activate_source_document` 两个降级分支里逐字：
  `sw.ActivateDoc2(title, False, errors)` 与 `dynamic_sw.ActivateDoc2(title, False, errors)`
- **依据**：降级分支调官方标 `Obsolete` 的 `ISldWorks.ActivateDoc2`，而同函数第一分支已经在用后继 `ActivateDoc3`。

---

## C#5 · `audit-10-misc-C.md` 第 5 条 · 判定：**成立**

- **官方原文（在）** — `C:\swapi\enums\swSTLQuality_e.md` 成员表逐字三行：
  `| swSTLQuality_Coarse | 1 |` · `| swSTLQuality_Custom | 3 |` · `| swSTLQuality_Fine | 2 |`
  ⇒ 合法成员只有 **1 / 2 / 3**（`enum_member_count: 3`）。
- **我们的原文（在）** — `scripts/sw_export.py` 的 `export_to_stl` 里逐字：
  `quality_map = {"coarse": 1, "fine": 0}`
- **依据**：`"fine"` 映射的字面量 **0 不是该枚举的任何成员**（`"coarse": 1` 与官方一致）。
  ⚠ 该行里另一个字面量 `78` 的出处两套离线源都查不到（与原表一致，**不判定**）。

---

## C#6 · `audit-10-misc-C.md` 第 6 条 · 判定：**★ 不成立**（只有一段原文）

- **官方原文（在）** — `C:\swapi\types\IModelDoc2\GraphicsRedraw2.md` 正文首行逐字：
  `Obsolete. Superseded by [[IModelView::GraphicsRedraw]] and [[IModelView::IGraphicsRedraw]].`
- **★ 我们的原文（★ 不在）** — 该条声称 `scripts/sw_review.py` 有两处逐字 `get_com_member(model, "GraphicsRedraw2")`
  （`zoom_to_fit` 一处、`clear_selection_for_preview` 收尾一处）。**全文搜 `GraphicsRedraw2` 在 `scripts/sw_review.py` 只命中 docstring 一处**，且那段 docstring 是**引用官方 Obsolete 横幅作为「已换后继」的依据**：
  `★ 官方 `types/IModelDoc2/GraphicsRedraw2.md` 逐字：` /  `「**Obsolete. Superseded by [[IModelView::GraphicsRedraw]] and [[IModelView::IGraphicsRedraw]].**」`
  ★ 该文件**实际调用的是后继**，逐字为
  `view = get_com_member(model, "ActiveView")` → `get_com_member(view, "GraphicsRedraw", None)`；
  两个函数都调用同一个 `_graphics_redraw(model)` 辅助函数，**没有任何 `GraphicsRedraw2` 调用**。
- **依据**：官方原文确实存在，但**「我们的原文」不存在于该文件** —— 代码早已迁到后继 `IModelView.GraphicsRedraw`，
  这条是把 docstring 里**引用的官方横幅**误当成了调用点（旁证：同仓 `scripts/sw_part.py`、`scripts/sw_import_mesh_reference.py`
  的注释也都逐字写着「★ 2026-10-03 接手轮 **换成后继入口** —— 原来是 `model.GraphicsRedraw2()`」）。

---

## C#7 · `audit-10-misc-C.md` 第 7 条 · 判定：**成立**

- **官方原文（在）** — `C:\swapi\types\ISldWorks\ActivateDoc2.md` 正文首行逐字：
  `Obsolete. Superseded by [[ISldWorks::ActivateDoc3]].`
- **我们的原文（在）** — `scripts/sw_review.py` 的 `activate_model_for_preview` except 分支里逐字：
  `sw.ActivateDoc2(title, False, errors)`
- **依据**：与 C#4 同一成员、换到 `sw_review.py` 的降级分支，官方标 `Obsolete`、后继 `ActivateDoc3` 就在同函数的 try 分支里被使用。

---

## C#8 · `audit-10-misc-C.md` 第 8 条 · 判定：**成立**

- **官方原文（在）** — `C:\swapi\types\IDimension\GetSystemValue2.md` 正文首行逐字：
  `Obsolete. See [[IDimension::GetSystemValue3]] and [[IDimension::IGetSystemValue3]].`
- **我们的原文（在）** — `scripts/sw_document_data.py` 的 `_dimension_value_mm` 里逐字：
  `return float(dimension.GetSystemValue2(configuration_name)) * 1000.0`
- **依据**：取指定配置下的系统值走官方标 `Obsolete` 的 `GetSystemValue2`，官方指向 `GetSystemValue3`。

---

## C#9 · `audit-10-misc-C.md` 第 9 条 · 判定：**成立**

- **官方原文（在）** — `C:\swapi\types\IDimension\SystemValue.md` 正文首行逐字：
  `Obsolete. Superseded by [[IDimension::GetSystemValue3]], [[IDimension::IGetSystemValue3]], [[IDimension::SetSystemValue3]], and [[IDimension::ISetSystemValue3]].`
- **我们的原文（在）** — `scripts/sw_document_data.py` 的 `_dimension_value_mm` 里逐字：
  `return float(get_com_member(dimension, "SystemValue")) * 1000.0`
- **依据**：读「当前配置」系统值走官方标 `Obsolete` 的 `IDimension.SystemValue` 属性，后继是 `GetSystemValue3` 一族。

---

## C#10 · `audit-10-misc-C.md` 第 10 条 · 判定：**成立**

- **官方原文（在）** — `C:\swapi\types\IFeatureManager\InsertWrapFeature2.md` 的 `## Parameters` 逐字：
  `- **MeshFactor**: Accuracy of flattened triangle mesh; 1 (lowest) - 10 (highest)`
- **我们的原文（在）** — `scripts/sw_wrap.py` 里逐字 `WRAP_MESH_FACTOR_DEFAULT = 0`，
  且作为**第 5 个实参**传入：`obj = get_com_member(fm, "InsertWrapFeature2", WRAP_TYPES[key], thickness_m, bool(reverse),`
  与 `WRAP_METHOD_DEFAULT, WRAP_MESH_FACTOR_DEFAULT)`
- **依据**：官方把 `MeshFactor` 合法取值写死为 **1–10**，我们传的 **0 落在该范围之下**。

---

## 复核方法与自限（供审计者复查）

- **只读 + 只写一个文件**：本轮只新建本文件，未改仓内任何文件、未运行 SolidWorks / pytest。
- **官方侧**：`C:\swapi\types\<接口>\<成员>.md` 与 `C:\swapi\enums\swSTLQuality_e.md` 逐字读；
  另用出厂反射 `D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt` 定位 A#1 的 `## IModelDocExtension` 段。
- **仓内侧**：对 7 份 `scripts/*.py` 逐字搜（`sw_export.py` · `sw_review.py` · `sw_document_data.py` ·
  `sw_ref_geometry.py` · `sw_loft.py` · `sw_wrap.py` · `sw_connect.py`）。
- **未核**（按铁律 3「只核置信度为高的」）：`audit-10-misc-B.md` 的 #4 #5 #6（置信度**中**）、
  `audit-10-misc-A.md` 的「查不到」段与「接口归属」备注段、`audit-10-misc-C.md` 的「查不到」表与「判定为一致」留痕段。
- **口径提醒**：本表判的是「**核对表所引的两段原文是否名实相符**」，不是替核对表裁定代码对错；
  C#6 即属「引用失实」而非「代码有 bug」—— 那处代码恰恰**已经**用了官方后继。