"""第二十七批 MCP 工具声明：**仿真研究族** 3 个（24h 计划 · 段 1.1 / Spec Kit `141`）。

## ★★★ 本批补的是 **W7 的硬前置**
```
★ W7（`specs/140`）把仿真**载荷**挂上了柜台，但它的 `limitations` 第一条就是：
    「★ **没有**「建研究」的工具 ⇒ `study_name` 只能引用**已存在**的研究」
⇒ ★★ 也就是说：**用户必须先手动在 SolidWorks 里建一个研究**，我们的工具才有东西可用。
⇒ 本批把那一步补上 ⇒ ★ **仿真链从"能用"变成"闭环"**。
```

## ★★ §5.0 先找后搓（**强制第一步**）的结果
```
① 四家 live 测试 ⇒ **没有**建研究的判据（andrewbartels1 0 处，其余三家无）
② ★ **自己的仓库** ⇒ ★★ **有**：`tools/capture_simulation_loads_evidence.py:109`
   **已在用** `create_static_study(sw, "DSH-W7")` 且**真机跑通**
⇒ ★ 所以**没有搓新判据** —— 沿用 W7 那条链并**加强**（建完回读 + 看入口名）。
```

## ★★★ 为什么本批要**新写三个薄函数**（而不是直接挂既有四个）
```
★ 真机探针（`tools/probe_simulation_study_shapes.py`）实测三个真形状：
   · `create_static_study` ⇒ **tuple(3)** = `(CDispatch, str, int)`
     ⇒ ★ `study` 是 **COM 对象**（MCP 回不了对象）；★ 而 `entry_name` 是
       「**是否走了降级入口**」的**唯一证据**（其 docstring 明写「CreateNewStudy3/2/1」）
   · `iter_studies` ⇒ yield **`(index, study)` 元组** ⇒ 同样含对象
   · `get_study_by_name` ⇒ 回对象或 **`None`**（★ 实测「找不到**返回 None，不抛错**」）
⇒ ★★ 三个**都不可直接挂** ⇒ 各包一层，只回**可 JSON 化**的东西。
★ 三个薄函数返回**形状一致**（只含 str/int/bool 的字典）⇒ ★ 调用方好处理。
★ **既有四个函数一行未改**（本批只**加**）。
```

## ★ 真机实测到的两条关键读数（写进工具说明，免得调用方猜）
```
· `entry_name` 实测 = **`"CreateNewStudy3"`**（★ 最高版本入口，**不是降级**）· `error_code = 0`
· `get_study_by_name("NoSuchStudy_XYZ")` ⇒ **回 `None`**（★ **不抛错**）
  ⇒ ★ 所以对外用**显式的 `found` 字段**，避免把"没有"当成"有"。
```

## ⚠ 只支持静力学研究（硬约束③：未验的必须明确标注）
```
★ `SWS_ANALYSIS_STUDY_TYPES` 有多个值，但**只有 static 被真机验过**
⇒ ★ 本批**不暴露** `study_type` / `mesh_type` 参数，说明里写明「目前只支持静力学研究」。
★ 这比"暴露一个我没验过的开关"诚实，也避免调用方以为支持其它类型。
```

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植）
# 文件:   mcp-server/tool_specs_batch27.py
# 定位:   「孤立能力暴露」第二十七批 / 24h 计划 段 1.1（Spec Kit `141`）。
# 官方签名依据: 不适用（只做参数搬运）；被搬运函数的官方依据见 `scripts/sw_simulation.py`
#          的来源块（`ICWModelDoc.StudyManager` / `ICWStudyManager.CreateNewStudy3/2/1`）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH27"]

_NAME = ("Name of the study to create. ⚠ The capability layer does NOT check duplicates — "
         "if a study with this name already exists, SolidWorks decides what happens (that "
         "behaviour is not verified here, so re-read with solidworks_simulation_list_studies).")


SPECS_BATCH27 = [
    ToolSpec(
        name="solidworks_simulation_create_study",
        title="Create a Static Simulation Study",
        module="sw_simulation", function="create_study_report",
        inject="sw_app",
        #: ★★ `study_name` → `name`：能力层形参叫 `name`（不带前缀），对外名带域前缀
        #:   ⇒ **必须靠 `param_alias` 改名**。
        #:   ⚠ 第一版**漏了**，被"走工具路径"的证据脚本当场抓住
        #:   （`TypeError: create_study_report() got an unexpected keyword argument 'study_name'`）
        #:   —— ★ 这与 W7 的 `magnitude_n` 是**同一个 bug 家族**，★ 于是本批加了门禁 `check_param_binding`
        #:   （见 `scripts/check_union_conventions.py`）**让这一类不再可能发生**。
        param_alias={"study_name": "name"},
        params=[
            Param("study_name", str, description=_NAME),
        ],
        doc="Create a STATIC simulation study and return a JSON-able report: "
            "`{ok, requested_name, study_name, entry_name, error_code}`. "
            "★★ Read `entry_name`: it names the entry point that actually succeeded "
            "(CreateNewStudy3 / 2 / 1), so an EMPTY value means the study was NOT created — "
            "this is the only evidence of whether a fallback path was used. "
            "⚠ Only static studies are supported (other study types are not verified). "
            "⚠ Requires the Simulation add-in; it is loaded automatically on first use.",
    ),
    ToolSpec(
        name="solidworks_simulation_list_studies",
        title="List Simulation Studies",
        module="sw_simulation", function="list_studies",
        inject="sw_app",
        params=[],
        doc="List every simulation study in the active document as "
            "`[{index, name}, …]`. ★ Returns names only, never COM objects. "
            "★ A study whose name cannot be read is still listed with an empty name — "
            "it is not skipped, so an empty list really means 'no studies'.",
    ),
    ToolSpec(
        name="solidworks_simulation_find_study",
        title="Find a Simulation Study by Name",
        module="sw_simulation", function="find_study",
        inject="sw_app",
        #: ★★ 同上的改名（能力层形参是 `name`）—— ★ 门禁 `check_param_binding` 现在会盯住这一类。
        param_alias={"study_name": "name"},
        params=[
            Param("study_name", str, description="Exact study name to look for."),
        ],
        doc="Look up a simulation study by name and return `{found, requested_name, study_name}`. "
            "★★ The capability layer returns None when the name does not exist (it does not "
            "raise), so this tool exposes an explicit `found` flag instead — never read a "
            "missing study as present.",
    ),
]
