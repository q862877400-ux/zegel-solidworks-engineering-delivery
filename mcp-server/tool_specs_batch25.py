"""第二十五批 MCP 工具声明：**装配只读** 3 个（砌墙 W6 / Spec Kit `139`）。

## ★★★ 本批补的是装配域里**只读的"看装配里有什么 / 撞不撞"**
```
★ 已有工具：`add_component` · `add_*_mate` · `collect_assembly_bom` · `pack_and_go` ·
  `set_component_fixed`（都是"建/改/导出"）
★ 而**已实现、首参可注入、却没挂**的只读函数有三个（见 fact 169）：
    `sw_assembly.get_components(asm_model, top_level_only=True)`
    `sw_assembly.collect_mate_feature_summary(model)`
    `sw_assembly.get_interference_detection(asm_model)`      ← ★★ **干涉检查**
```

## ★★★★ 干涉检查那个函数：**修过三处成员名，却**没有真机证据****
```
`sw_assembly.get_interference_detection` 的实现里记着（轮 159）：
   ① 入口属性是 `InterferenceDetectionManager`（**带 `Manager`**）
   ② 取结果用 `GetInterferences()`（**复数**），没有 `GetInterference(index)`
   ③ `IInterference` 上**没有 `Name`** ⇒ 改用官方有的 `Volume` 与 `GetComponentCount()`
★ 而注释明写：「**两处都在 `try:` 里 ⇒ 此前静默降级**（不炸，但**永远拿不到数据**）」
⇒ ★★ **"修过"不等于"验过"** —— 本批的真机验证就是它的**第一次验证**。
   ★ 验证设计**必须有正反两个场景**，否则证明不了"它真的在看几何"：
     · 两个组件**重叠** ⇒ 应 `status: warn` · `interference_count >= 1`
     · 两个组件**分开** ⇒ 应 `status: pass` · `interference_count == 0`
   ★ 若两个场景**都回 0** ⇒ 它**仍是静默降级**（不炸但没数据）；
     若**都回 warn** ⇒ 判据不对。⇒ ★ 只有一正一反才说明它在看几何。
```

## ★ 注入名：本批第一次用 `asm_model`（见 fact 169）
```
★ 三个函数里有两个首参叫 **`asm_model`**（不是 `model`），而**注入名只能是 `RESOLVERS` 的键**
  ⇒ ★ 解法：给 `register_capabilities.RESOLVERS` **加一行** `"asm_model": resolve_model`
    （装配文档同样是 `model`，同一个解析器）
  ★ 那是**那张表的设计用途**（其注释写着「注入名 → 解析器。`tool_registry` **不硬编码宿主 API**，
    全从这里供给」）⇒ ★ **不动核心**。
```

## ★ 返回结构（已核，可 JSON 化 ⇒ 能直接挂）
```
`get_components`               ⇒ `[{name, path, suppressed, visible}, …]`
`collect_mate_feature_summary` ⇒ `[{name, type, depth}, …]`
`get_interference_detection`   ⇒ `{status, interference_count, items[], manual_review_required}`
```

## ⚠ 一个写操作，以及它为什么允许
```
★ 真机验证需要一个**真实的装配文档**，而装配要引用**已存的零件文件**
  ⇒ 证据脚本会**写一个零件到临时目录**（`D:\\AI\\SW\\output\\_fixtures\\`）。
★ **这不是"改用户数据"**：只在**临时目录**里造**自己的测试夹具**（与既有的
  `pack_and_go`（写文件）同性质）⇒ ★ **允许**，且**在证据里写明**。
★ 收尾：关件**不保存**；临时零件文件留在 `_fixtures/`（可复跑时复用）。
```

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装的函数各自的来源块在其源码里）
# 文件:   mcp-server/tool_specs_batch25.py
# 定位:   「孤立能力暴露」第二十五批 / 砌墙 W6（Spec Kit `139`）。
# 官方签名依据: 不适用（只做参数搬运）；干涉检查的官方依据见 `sw_assembly` 的来源块
#          （`IInterferenceDetectionMgr` / `IInterference`，族覆盖 19/19 与 7/7）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH25"]


SPECS_BATCH25 = [
    ToolSpec(
        name="solidworks_assembly_list_components",
        title="List Assembly Components",
        module="sw_assembly", function="get_components",
        inject="asm_model",
        params=[
            Param("top_level_only", bool, default=True,
                  description="True = only top-level components; False = also descend into "
                              "sub-assemblies."),
        ],
        doc="List the components of the ACTIVE assembly: for each one its name, file path, "
            "whether it is suppressed and whether it is visible. ★ Reading only. ★ 别名: batch, list, operation, operations",
    ),
    ToolSpec(
        name="solidworks_assembly_list_mates",
        title="List Assembly Mates",
        module="sw_assembly", function="collect_mate_feature_summary",
        inject="model",
        params=[],
        doc="List the MateGroup and mate features of the active assembly (name, type, tree depth). "
            "★ Use it to check that real mates were actually written into the feature tree — "
            "it does NOT report degrees of freedom.",
    ),
    ToolSpec(
        name="solidworks_assembly_check_interference",
        title="Check Assembly Interference",
        module="sw_assembly", function="get_interference_detection",
        inject="asm_model",
        params=[],
        doc="Run interference detection on the ACTIVE assembly and return an auditable report: `status` (pass when nothing interferes / warn when something does / blocked when the check itself failed), `interference_count`, and per-interference `volume` + `component_count`. ⚠ `blocked` means the CHECK failed — do not read it as 'no interference'. ★ Reading only (it runs the detector, it does not change the model).",
    ),
]
