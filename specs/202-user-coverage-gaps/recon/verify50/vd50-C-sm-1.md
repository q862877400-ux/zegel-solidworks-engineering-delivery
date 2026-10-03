# vd50-C-sm-1 · 钣金域（基体法兰 / 边线法兰 / 斜接法兰 / 闭合角）契约摘要与对账

> ★ 本文件只抄**亲手读到**的内容。五条纪律：查不到就说查不到 · 每条给「仓内那一段」+「官方/目标那一段」两段可搜索原文（**不给行号**）· 只判成立/不成立/存疑 · 宁少勿滥 · 只读 + 只写本文件一个。
>
> **格式模板**：`recon/api-pre/api-03-weldment.md`（源表 + 逐条 ① ② ③ + 前置/配方一句话）。
> **本片范围**：基体法兰（base flange）· 边线法兰（edge flange）· 斜接法兰（miter flange）· 闭合角（closed corner）。
>
> **读过的三套离线源（全部本机，未联网）**
>
> | 源 | 本文件简称 | 抄什么 |
> |---|---|---|
> | `C:\swapi\types\<接口>\<成员>.md` | **[md]** | 精确签名（`System.*` 口径）、`## Parameters`、`## Remarks` 逐字 |
> | `C:\swapi\enums\<枚举>.md` | **[en]** | 枚举成员与数值 |
> | `D:\AI\SW\AI Solidworks\官方文档\SWhelp\...` · `D:\AI\SW\_raw\reflect_sldworks\` | 反射 | 出厂类型库口径（**只用于交叉印证 `System.*` 与参数个数**） |
>
> **仓内读过**：`capabilities.yaml` · `scripts/sw_sheet_metal.py` · `scripts/sw_sheet_metal_weld_entry.py` · `mcp-server/tool_specs_batch3.py` · `mcp-server/tool_specs_batch74.py` · `mcp-server/register_capabilities.py` · `tests/test_sw_sheet_metal.py` · `tests/solidworks_sheet_metal_regression.py` · `recon/sheetmetal.md` · `recon/scan-S2a-tools-not-in-ledger.md`。

**核了 14 处，对不上 6 处。**

---

# 〇 · 名字与枚举的「查不到」（铁律 5：查不到就说查不到）

| 想找的 | 结果 | 证据 |
|---|---|---|
| `swFeatureNameID_e` 里的 **MiterFlange / Hem / ClosedCorner** 项 | **查不到** | `C:\swapi\enums\swFeatureNameID_e.md` 全文检索 `MiterFlange` / `Hem` / `ClosedCorner` **三个都是 0 命中**；同文件 `swFmBaseFlange` / `swFmEdgeFlange` / `swFmSweptFlange` / `swFmSMGusset` / `swFmSketchBend` 均命中 |
| `IFeatureManager` 下的 **MiterFlange 入口** | **存在** | `C:\swapi\types\IFeatureManager\InsertSheetMetalMiterFlange.md`（**14 参 · 回 `Feature`**，无 `Obsolete` 句） |
| `IModelDoc2` 下的 **MiterFlange 入口** | **存在，且 Obsolete** | `C:\swapi\types\IModelDoc2\InsertSheetMetalMiterFlange.md`：`Obsolete. Superseded by [[IFeatureManager::InsertSheetMetalMiterFlange]].`，**11 参 · 回 `void`** |
| `IModelDoc2` 下的 **ClosedCorner 入口** | **存在** | `C:\swapi\types\IModelDoc2\InsertSheetMetalClosedCorner.md`：**零参 · 回 `void`** |
| 斜接法兰 / 闭合角的官方 **`## Remarks`** | **查不到** | 两份 md 逐段看过：`InsertSheetMetalMiterFlange.md` 只有 `## Parameters` / `## Returns` / `## See Also`；`InsertSheetMetalClosedCorner.md` **全文只有标题 / Signature / See Also** |

---

# 一、基体法兰（base flange）

## 1.1 `IBaseFlangeFeatureData.Initialize` 九参与仓内调用逐位对齐 —— **成立（不成立）**

**官方那一段** —— [md] `C:\swapi\types\IBaseFlangeFeatureData\Initialize.md` 原文片段 `**Signature**:`：

> `void Initialize( System.bool UseMaterialSheetMetalParameters, System.bool OverrideDefaultBendAllowance, System.object CustomBendAllowance, System.bool OverrideDefaultBendRelief, System.int ReliefType, System.bool UseReliefRatio, System.double ReliefRatio, System.double ReliefWidth, System.double ReliefDepth )`

**仓内那一段** —— `scripts/sw_sheet_metal.py::create_base_flange` 的实参块（连续 9 行，逐位抄）：

> ```
>     data.Initialize(
>         False,
>         True,
>         bend_allowance,
>         True,
>         SW_SHEET_METAL_RELIEF_RECTANGULAR,
>         True,
>         float(spec.relief_ratio),
>         0.0,
>         0.0,
>     )
> ```

**判定：不成立**（仓内无问题）。
**一句话依据**：9 个实参与官方 9 个形参**逐位同序同型**（两个 `bool` 前置 → `object` 折弯补偿 → `bool` → `int ReliefType` → `bool` → 三个 `double`），且 `SW_SHEET_METAL_RELIEF_RECTANGULAR = 1` 与 [en] `swSheetMetalReliefTypes_e` 的 `swSheetMetalReliefRectangular | 1` 一致。

---

## 1.2 ★★ V-1 · 「开放折线能不能跑」在仓内**自相矛盾** —— **判定：成立**

**仓内那一段（甲）** —— `mcp-server/tool_specs_batch3.py` 里 `solidworks_sheet_metal_create_base_flange` 的 `doc=`（**这是用户直接读到的工具契约**）：

> `Create a native base flange (swFmBaseFlange) from an open or closed sketch. An open polyline path produces a profile flange; a closed contour produces a flat plate.`

**仓内那一段（乙）** —— `scripts/sw_sheet_metal.py::SHEET_METAL_RUNTIME_STATUS` 的 `create_base_flange` 条目（**标的是同一个 2026-10-01 真机**）：

> `"**闭轮廓**真机建成：特征树出现「钣金6 / 基体-法兰1 / 平展型式6」。"` … `"⚠ **开放折线（轮廓法兰）真机失败**：`CreateFeature(IBaseFlangeFeatureData) 创建失败`"` … `"⇒ **`True` 仅对闭轮廓成立**"`

**官方那一段（判据用，不用来裁决谁对）** —— [md] `C:\swapi\types\IFeatureManager\InsertSheetMetalBaseFlange.md` 首行：

> `Obsolete. Superseded by [[IFeatureManager::InsertSheetMetalBaseFlange2]].`

★ 即现行路线是 FeatureData 路线，官方**对「开放/闭合轮廓」没有任何一句前置说明** ⇒ 官方判不了谁对。

**判定：成立**（仓内两处对同一个入口、同一天的真机，给出**互斥**的可用性结论）。
**一句话依据**：工具契约对外承诺「开放折线走轮廓法兰」，而实现侧的运行期状态表逐字写「开放折线真机失败 · True 仅对闭轮廓成立」⇒ 用户按工具契约调用开放轮廓时必然撞上失败，而契约没说。
⚠ **不裁决谁更新**：`git log --oneline -- <两文件>` 只返回一次 `914bf5e merge: 把代码仓 sw-skill-fork 并进工作区，两仓合一` ⇒ **历史被压成单次提交，先后判不了**（按铁律 5，不猜）。
⚠ 第三方旁证（**只作背景，不作判据**）：`tests/solidworks_sheet_metal_regression.py` 的 `run_regression` 用的是**开放**轮廓（三段 `sketch_line` 拼的 U 型），注释逐字写「开放轮廓由 BaseFlange 生成两道真实折弯」；`capabilities.yaml` 的 `sheet_metal` limitations 也逐字写「已真机验证现代 BaseFlange FeatureData、**开放 U 型轮廓双折弯**」⇒ **仓内其实有三份文字说「开放能跑」，对上一份说「开放失败」。**

---

## 1.3 ★★ V-2 · `sheet_metal`（**`level: "verified"`**）的 evidence #1 **从不碰 COM、也不调 `create_base_flange`** —— **判定：成立**

**仓内那一段** —— `capabilities.yaml` 的 `sheet_metal` 条目：

> `"id": "sheet_metal",` … `"level": "verified",` … `"evidence": [` / `"pytest tests/test_sw_sheet_metal.py",`

**目标那一段** —— 该测试文件里与钣金有关的**全部** import 与 3 个用例名（逐字）：

> `from sw_export import (` … `)` / `from sw_sheet_metal import BaseFlangeSpec  # noqa: E402`
> `def test_flat_pattern_export_uses_alignment_array_and_option_bitmask(tmp_path):` / `def test_flat_pattern_export_requires_saved_model(tmp_path):` / `def test_base_flange_spec_rejects_invalid_manufacturing_values(spec, message):`

**判定：成立**。
**一句话依据**：该文件从 `sw_sheet_metal` 只导入 **`BaseFlangeSpec`（一个纯 dataclass）**，三个用例分别测 `export_flat_pattern_dxf` 对 **`FakePart` 替身**的入参与 `BaseFlangeSpec.validate()` 的抛错 ⇒ 全程**不碰 COM、不调 `create_base_flange`** ⇒ 拿它当 `verified` 的运行证据对「钣金建模」**零信息量**。
★ 对照（同仓同文件里真跑机器的写法）：`tests/solidworks_sheet_metal_regression.py` 才 `from sw_connect import connect_solidworks, …`。

---

## 1.4 ★★ V-3 · 同一 `verified` 条目的 evidence #2 **按字面写法跑不起来**（pytest 收 0 个用例）—— **判定：成立**

**仓内那一段** —— 同一条目的 `evidence` 第二项：

> `"pytest tests/solidworks_sheet_metal_regression.py（钣金）"`

**目标那一段** —— 该文件的模块骨架（逐字，**全文没有任何 `def test_`**）：

> `"""SolidWorks 2026 原生钣金样件、展开 DXF 与重开回归。"""` … `def _validate_evidence(evidence: dict, *, stage: str) -> None:` … `def run_regression(output_dir: Path, *, visible: bool = True, wait_seconds: int = 12) -> dict:` … `def main() -> int:` … `if __name__ == "__main__":` / `raise SystemExit(main())`

**判定：成立**。
**一句话依据**：按证据原文「pytest \<该文件\>」执行，该文件**只有 `_validate_evidence` / `run_regression` / `main` 三个函数、`def test_` 计数为 0** ⇒ pytest **收集不到任何用例**，实际入口是 `__main__` 命令行（默认输出到 `%TEMP%\solidworks_sheet_metal_regression`）。
⇒ ★ **两条 evidence 合起来**：`sheet_metal` 挂在 `verified` 上的两条，一条**证明不了建模**（1.3），另一条**按字面跑不起来**（1.4）⇒ 该 level 在本域没有可执行的 pytest 支撑。

---

# 二、边线法兰（edge flange）

## 2.1 仓内「`ReverseDirection` 不属本接口」的判断 —— **判定：不成立**（仓内正确）

**官方那一段** —— `C:\swapi\types\IEdgeFlangeFeatureData\` 的成员文件名表里**没有** `ReverseDirection.md`，但**有** `ReverseOffset.md` 与 `ReversePositionOffset.md`。

**仓内那一段** —— `scripts/sw_sheet_metal.py::create_edge_flange` 的 `_apply` 内注释（逐字）：

> `#    ⛔ 原代码在此设 `data.ReverseDirection` —— **该属性不属于本接口**。` … `#    ⚠ **不臆造替代**：最接近的 `ReverseOffset` / `ReversePositionOffset` 是**偏置**方向，语义不同 —— 边法兰没有「反向」这个开关。`

**判定：不成立**（这一处仓内是对的，不判为问题）。
**一句话依据**：官方成员表确实只有 `ReverseOffset` / `ReversePositionOffset` 两个「Reverse*」，没有 `ReverseDirection` ⇒ 仓内的判断与官方逐项吻合。

---

## 2.2 ★★ V-4 · MCP 工具契约把**已修掉的缺陷**当成当前失败原因 —— **判定：成立**

**仓内那一段（甲）** —— `mcp-server/tool_specs_batch4.py` 里 `solidworks_sheet_metal_create_edge_flange` 的 `doc=`（**用户直接读到的契约**）：

> `*** NOT USABLE ON THE TEST MACHINE *** run 2026-10-01 on SW 2026 SP4.1 and it FAILED with: setting `ReverseDirection` gave `Property ... can not be set`. The correct call shape has not been determined yet`

**仓内那一段（乙）** —— `capabilities.yaml` 的 `sheet_metal` 条目 `limitations` 第二项，在「**已修掉的缺陷**」标题下逐字列着它：

> `**已修掉的缺陷**：`create_one_bend` 的常量（`swFmOneBend(33)` → `swFmSketchBend(35)`，报错前推到 `CreateFeature(35)`）；`create_gusset` **整步缺失的官方步骤 3**（…）；`create_edge_flange` 的 `ReverseDirection` 跨接口泄漏。`

**目标那一段（第三方）** —— `scripts/sw_sheet_metal.py::SHEET_METAL_RUNTIME_STATUS` 的 `create_edge_flange` 条目写明报错已经**前推**：

> `⇒ 报错已从 `Property ... can not be set` 变为 `CreateFeature(37) 创建失败``

**判定：成立**。
**一句话依据**：工具契约对外陈述的失败原因是 `ReverseDirection` 跨接口属性，而仓内两处（`capabilities.yaml` 的「已修掉的缺陷」+ 运行期状态表的「报错已从 … 变为 …」）都记录该缺陷已修、真实失败点已前推到 `CreateFeature(37)` ⇒ **用户按契约排查会停在一个已经修好的原因上**。

---

## 2.3 边法蘭的边集合能否由程序传入 —— **判定：不成立**（仓内「到不了」的结论有官方依据）

**官方那一段** —— [md] `C:\swapi\types\IEdgeFlangeFeatureData\ISetEdges.md` 的 `EdgeArray` 逐字：

> `in-process, unmanaged C++: Pointer to an array of [[edges]] for this edge flange` / `VBA, VB.NET, C#, and C++/CLI: Not supported`

**仓内那一段** —— `scripts/sw_sheet_metal.py::create_edge_flange` 的来源块：

> `⚠ 边集合由调用方在创建前用 SelectByID2 选好；本函数不代为选边，`

**判定：不成立**（仓内只读形状与官方「非进程内语言 Not supported」一致）。
**一句话依据**：官方逐字写明 `ISetEdges` 在 **VBA / VB.NET / C# / C++CLI 全都 Not supported** ⇒ pywin32 这条后端确实传不了边数组，只能靠图形区预选。
★ 但**同族另一条路存在**且仓内未采用：[md] `C:\swapi\types\IFeatureManager\InsertSheetMetalEdgeFlange2.md` 的首行 `FlangeEdges`: Array of [[edges]] to which to apply a flange，形参类型是 `System.object`（**数组，非指针**）⇒ **可从 VBA 调用**；代价是该方法带 `Obsolete. Superseded by [[IFeatureManager::CreateDefinition]] and [[IFeatureManager::CreateFeature]].`。⇒ 本条**只记事实，不判该不该换路线**。

---

# 三、斜接法兰（miter flange）

## 3.1 参数个数 14 与废弃链 —— **判定：不成立**（仓内正确）

**官方那一段** —— [md] `C:\swapi\types\IFeatureManager\InsertSheetMetalMiterFlange.md` 的 `**Signature**:`（逐字全量）：

> `Feature InsertSheetMetalMiterFlange( System.bool UseDefaultRadius, System.double GlobalRadius, System.double RipGap, System.bool UseDefaultRelief, System.bool UseReliefRatio, System.double ReliefRatio, System.double ReliefWidth, System.double ReliefDepth, System.int ReliefType, System.bool TrimSideBends, System.int FlangePos, System.double OffsetDist1, System.double OffsetDist2, CustomBendAllowance PCBA )`

**目标那一段** —— 出厂类型库反射 `D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt` 同名条目（逐字）：

> `Feature InsertSheetMetalMiterFlange(Boolean, Double, Double, Boolean, Boolean, Double, Double, Double, Int32, Boolean, Int32, Double, Double, CustomBendAllowance)`

**仓内那一段** —— `scripts/sw_sheet_metal_weld_entry.py` 的调用块注释与返回字典：

> `"entry_point": "IFeatureManager.InsertSheetMetalMiterFlange（★ 14 参 · 非废弃）",` … `"obsolete_note": "★ 同名的 IModelDoc2.InsertSheetMetalMiterFlange（11 参 · 回 void）**已 Obsolete** ⇒ 本模块**不调**它",`

**判定：不成立**（14 参、非废弃那份、11 参 Obsolete 那份，三处口径与官方逐字一致）。
**一句话依据**：[md] 逐个数是 **14 个形参**，反射逐个数也是 **14 个类型**，仓内实参块亦**逐位同序**（末位第 14 位传 `null_dispatch` 作 `PCBA` 的 NULL 分支）⇒ 参数个数与顺序都对得上。

---

## 3.2 ★★ V-5 · `recon/sheetmetal.md` 把斜接法兰与闭合角记成「官方没写」 —— **判定：成立**

**仓内那一段** —— `recon/sheetmetal.md` 的表格前两行数据行（逐字）：

> `| 斜接法兰 | 官方没写 | 官方没写 | 无 | 无 | — |`
> `| 闭合角 | 官方没写 | 官方没写 | 无 | 无 | — |`

**官方那一段** —— 两份签名都实打实在：

> [md] `C:\swapi\types\IFeatureManager\InsertSheetMetalMiterFlange.md`：`# IFeatureManager.InsertSheetMetalMiterFlange` / `Inserts a meter flange in a sheet metal part.`
> [md] `C:\swapi\types\IModelDoc2\InsertSheetMetalClosedCorner.md`：`# IModelDoc2.InsertSheetMetalClosedCorner` / `Inserts a sheet metal closed corner into this model document.`

**仓内旁证（同仓已实现，且点名正确的入口）** —— `scripts/sw_sheet_metal_weld_entry.py` 的文件首行与映射表：

> `"""★ 钣金/焊件/曲面 5 项「直入法」入口（斜接法兰 / 闭合角 / 顶端盖 / 角撑板 / 中面）。"""`
> `"钣金/斜接法兰": "IFeatureManager.InsertSheetMetalMiterFlange（14 参）"`
> `"钣金/闭合角": "IModelDoc2.InsertSheetMetalClosedCorner（零参 · 回 void）",`

**判定：成立**。
**一句话依据**：该表把「官方成员 / 签名」两列都写成「官方没写」，而官方两份签名文件存在、**且本仓自己已在 `sw_sheet_metal_weld_entry.py` 里按这两个入口实现** ⇒ 这份核对产物是**过期残留**，会把后来人引到「官方没有、走不通」的错误结论上。

---

# 四、闭合角（closed corner）

## 4.1 零参、回 `void` 的判据设计 —— **判定：不成立**（仓内正确）

**官方那一段** —— [md] `C:\swapi\types\IModelDoc2\InsertSheetMetalClosedCorner.md` **全文只有三段**：

> `**Signature**: `void InsertSheetMetalClosedCorner()`` … `## See Also` / `- [[IClosedCornerFeatureData Interface]]`

**仓内那一段** —— `scripts/sw_sheet_metal_weld_entry.py::insert_sheet_metal_closed_corner`：

> `⚠⚠★ **这是本批判据最紧的一条**，★ 因为官方**同时**给了「**零参数**」与「「回 `void`**」：⇒ ★ **没有返回对象可读**`
> `get_com_member(model, "InsertSheetMetalClosedCorner")` … `"returned_is_none": None,          # ★ 官方回 void ⇒ ★ 这个字段**无意义**，如实置 None`

**判定：不成立**。
**一句话依据**：官方确实是零参且回 `void`，仓内据此把 `returned_is_none` 如实置 `None`、改用「树增量 + 面数增量 + 体积增量」三判据，**没有**去读一个不存在的返回值 ⇒ 判据设计与官方口径一致。
★ 同族接口 [md] `C:\swapi\types\IClosedCornerFeatureData\_overview.md` 的 `## See Also` 逐字 `- [[IModelDoc2::InsertSheetMetalClosedCorner Method]]`，与上条互为印证。

---

# 五、台账侧

## 5.1 ★★ V-6 · 斜接法兰 / 闭合角两个工具**已挂 MCP、台账零引用** —— **判定：成立**

**仓内那一段** —— `mcp-server/register_capabilities.py` 把整批挂进 `BATCH_MODULES`：

> `"""★ 覆盖面缺口批（第三批）：钣金斜接法兰 / 闭合角 · 焊件顶端盖 / 角撑板。"""` … `"tool_specs_batch74",`

**目标那一段** —— `mcp-server/tool_specs_batch74.py` 里两条工具名（逐字）：

> `name="solidworks_sheet_metal_insert_miter_flange",`
> `name="solidworks_sheet_metal_insert_closed_corner",`

**再一段（对不上的那一侧）** —— `capabilities.yaml` 全文检索 `solidworks_sheet_metal_insert_miter_flange` 与 `solidworks_sheet_metal_insert_closed_corner`：**两个都是 0 命中**（`miter_flange` / `closed_corner` / `sheet_metal_weld` / `weld_entry` 四个关键词亦全部 0 命中）⇒ 既不在任何条目的 `mcp_tools` 里，也没有任何条目收录它们。

**判定：成立**。
**一句话依据**：两个已注册的用户可见工具在能力台账里**完全不存在** ⇒ 台账的钣金覆盖面与工具层的钣金覆盖面不一致（本片 4 项里，基体/边线法兰在台账内，斜接/闭合角在台账外）。
⚠ **两点如实标注**：① 仓内**自己已经记过这件事** —— `recon/scan-S2a-tools-not-in-ledger.md` 的表里逐字列着两行：`| 257 | `solidworks_sheet_metal_insert_closed_corner` | `tool_specs_batch74.py` | 0 |` 与 `| 258 | `solidworks_sheet_metal_insert_miter_flange` | `tool_specs_batch74.py` | 0 |`，判语「已挂工具、台账 `mcp_tools` 未引用」⇒ **不是新发现，是已知未清项**；② `register_capabilities.py` 自己逐字写着「⚠⚠ **本批的 4 条工具尚未真机验证** … ★ **在那之前不许把它们的 level 写成 verified**」⇒ **它们本就不该标 verified**，本条只主张「台账应有条目（哪怕标 `stitched`）」，不主张它们已验证。

---

# 附 · 核过但**查不出问题**的 8 处（不判为问题，供对照）

| # | 核了什么 | 结论 |
|---|---|---|
| C-1 | `IFeatureManager.InsertSheetMetalMiterFlange` 存在性 | ✅ 存在 |
| C-3 | 斜接法兰废弃链（IModelDoc2 版 Obsolete → IFeatureManager 版） | ✅ 两份 md 逐字对上 |
| C-4 | `IModelDoc2.InsertSheetMetalClosedCorner` 存在性 | ✅ 存在 |
| C-5 | 闭合角「零参 · 回 void」 | ✅ 与官方逐字一致 |
| C-7 | `IBaseFlangeFeatureData.Initialize` 9 参逐位对齐 + `swSheetMetalReliefRectangular = 1` | ✅ 对齐 |
| C-9 | 边法兰 `ReverseDirection` 不属 `IEdgeFlangeFeatureData` | ✅ 仓内判断正确 |
| C-10 | 边法兰边集合能否程序传入 | ✅ 仓内「到不了」有官方依据 |
| C-14 | 「`swFeatureNameID_e` 里没有 MiterFlange / Hem ⇒ 不提供其 CreateDefinition 入口」 | ✅ 查了，确实没有（`sw_sheet_metal.py` 的「⚠ 查不到故不编」是**如实**的，不是漏查） |

★ 另附两条**做对了的诚实写法**（不判为问题）：
- `sw_sheet_metal_weld_entry.py` 对斜接/闭合角逐字标 `preconditions_held: None` 并写 `★★ **官方页无 `## Remarks` 段 ⇒ 前置查不到** ⇒ 本模块**不编前置**（铁律 5）` —— 我逐段翻过那两份 md，**确实没有 Remarks 段**，它没编前置是对的。
- 该模块对官方自相矛盾处（`ReliefWidth` 与 `ReliefDepth` 两行说明都写 "relief depth"）选择「原样透传、不替官方调和」—— 逐字核对 [md] 该文件，两行确实都写 `then specify relief depth`，**照实保留是对的**。

---

**计数**：核了 **14** 处（4 个特征的官方成员存在性 / 参数个数与顺序 / 废弃链 / 枚举取值，加上 `verified` 条目的 evidence 可执行性与仓内台账一致性），**对不上 6** 处：
V-1 基体法兰开放/闭合结论自相矛盾 · V-2 `verified` 的 evidence #1 不碰 COM · V-3 `verified` 的 evidence #2 按字面收 0 个用例 · V-4 边线法兰工具契约报的是已修掉的缺陷 · V-5 `recon/sheetmetal.md` 把有官方入口的斜接/闭合角记成「官方没写」 · V-6 两个已挂工具台账零引用（★ 仓内 `scan-S2a` 已自记，属未清项）。
**查不到、不顶替的**：斜接法兰与闭合角的官方 `## Remarks`（两份 md 均无该段 ⇒ 前置查不到，仓内的 `preconditions_held: None` 因此是对的）；`git log` 判定「开放轮廓」两条结论孰先孰后（历史压成单次合并提交 `914bf5e`）。