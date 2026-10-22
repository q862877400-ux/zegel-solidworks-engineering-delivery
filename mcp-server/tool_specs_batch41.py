"""第四十一批 MCP 工具声明：**齿轮 2 + Toolbox 索引 4 + 草图编辑 3**（24h 段 5/6 续 / Spec Kit `158`）。

## ★★★★ 为什么这一批是**填真缺口**（★ 事实 210/213 的处置）
```
★ 轮 280 后仍剩 **9 条「`verified` 却 0 工具」** ⇒ ★★ 逐条查「它的下游在哪」⇒ ★ 三条找到了：
   · `external_spur_gear_geometry`（★ `verified` · 0 工具）⇒ ★ `sw_gear` 有 **4 个公开函数**；
   · `standard_parts_toolbox`（★ 同上）⇒ ★ `sw_toolbox_index` 有 **4 个**（★★ **全是纯数据、无 COM**）；
   · `sketch_chamfer`（★ 同上）⇒ ★ `sw_sketch_edit` 有 **3 个**（★ 而 `sketch_edit_ops` 那条也在等同族）。
⇒ ★★★ **所以本批 = "把已验过的能力接上工具"**（★ 与轮 277 同一处置）
   ⇒ ★ `all_specs()` **164 → 173**，★ 且**三条空条目被填实**。
```

## ★ 参数命名（规则 2 / 3）
```
★ `distance_mm` 带 `_mm`（★ 规则 2）
· `module_mm` / `face_width_mm` / `pitch_diameter_mm` 在 **spec** 里（★ 同样带 `_mm`）
★ `chamfer_type` / `teeth` 是**枚举与计数**（★ 不是长度、不是角度）⇒ 不带后缀
★ `plane_name` 是**基准面名**（★ 随 UI 语言变 —— 沿用 `sw_part` 的候选名机制）· **无裸坐标** ✓
```

## 判据
```
★ `create_external_spur_gear` ⇒ ★ 判"**特征树有变化**"（★ 规则 6：不静默成功）；
★ `calculate_external_spur_gear` ⇒ ★ **纯几何计算** ⇒ 判"回几何对象且**数值与解析式对得上**"
  （★ §5.0：★ 期望值优先用**几何推出的公式**，不用"看着像对"）；
★ `sw_toolbox_index` 的 4 个 ⇒ ★ **纯数据**（★ 读本地索引）⇒ 判"回 dict/list 非空"；
★ 草图编辑 3 个 ⇒ ★ 判"**选区/草图实体计数变化**"（★ 规则 6）。
```

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装的函数各自的来源块在其源码里）
# 文件:   mcp-server/tool_specs_batch41.py
# 定位:   24h 计划 段 5/6 续（Spec Kit `158`）—— 填三条空条目（齿轮 / Toolbox / 草图倒
#           角）。
# 官方依据: 渐开线直齿轮几何（★ 见 `scripts/sw_gear.py` 的来源块）·
#          Toolbox 索引（★ `sw_toolbox_index` 读本地索引文件）·
#          `ISketchManager` 族（★ 见 `scripts/sw_sketch_edit.py`）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 本批**不保存文档**（红线）。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
"""

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH41"]

_STD = "Toolbox standard name (★ see solidworks_toolbox_list_standards)."
_SPEC = (
    "A SpurGearSpec as a dict: module_mm / teeth / face_width_mm / bore_diameter_mm / "
    "pressure_angle_deg / helix_angle_deg (★ lengths carry _mm, angles carry _deg)."
)


SPECS_BATCH41 = [
    #: ★★★ 2026-10-10 **齿轮两个工具已移除**（★ 业主架构指令）：
    #:   ★ 业主原话：「★ **我想让你继承上游的是工具，只是单纯的工具。**
    #:     ★ **而像齿轮这种东西，在我认知里属于方法 —— 方法错了，工具再多也没有用。**
    #:     ★ **你要从你继承的东西里面把方法筛选出来，把工具留下来，方法全部都删掉。**」✓
    #:   ★★ **判据**：★ 「**那个数字错了，回读能不能查出来**」——
    #:     ★ 齿轮是**渐开线齿形公式**（★ 模数/齿数/压力角 → 齿廓点）⇒
    #:     ★★ **齿形错了，回读几何查不出来**（★ 它看起来"就是个齿轮"）⇒ ★ **它是方法** ✗
    #:   ★ 已移出：★ `scripts/sw_gear.py` → `archive/inherited-methods/scripts/` ✓
    #: ★★ 移出的两个工具：★ `solidworks_gear_calculate_spur` · `solidworks_gear_create_s
    #: pur`
    #:   ⚠ **留在这里的 Toolbox 四个是工具**（★ 索引查询 ⇒ ★ 判据是数据，回读可查）✓
    #: ── Toolbox 索引（★ 空条目 `standard_parts_toolbox` 的填实）──────────
    ToolSpec(
        name="solidworks_toolbox_list_standards",
        title="List the Toolbox Standards",
        module="sw_toolbox_index",
        function="list_standards",
        inject=None,
        params=[
            Param(
                "index",
                dict,
                default=None,
                description="A pre-loaded index (omit to load the local one).",
            )
        ],
        doc="List the Toolbox standards available in the local index. ★ Pure data — no "
        "SolidWorks call.",
    ),
    ToolSpec(
        name="solidworks_toolbox_load_index",
        title="Load the Toolbox Index",
        module="sw_toolbox_index",
        function="load_index",
        inject=None,
        params=[
            Param(
                "path",
                str,
                default=None,
                description="Index path (omit for the default local index).",
            )
        ],
        doc="Load the Toolbox index as a JSON-able dict. ★ Pure data — no SolidWorks call.",
    ),
    ToolSpec(
        name="solidworks_toolbox_search",
        title="Search the Toolbox Index",
        module="sw_toolbox_index",
        function="search",
        inject=None,
        params=[
            Param("keyword", str, description="Search keyword."),
            Param("standard", str, default="", description=_STD),
            Param("category", str, default="", description="Optional category filter."),
        ],
        doc="Search the Toolbox index by keyword. ★ Pure data — no SolidWorks call.",
    ),
    ToolSpec(
        name="solidworks_toolbox_part_path",
        title="Get a Toolbox Part's File Path",
        module="sw_toolbox_index",
        function="part_path",
        inject=None,
        params=[
            Param("standard", str, description=_STD),
            Param(
                "part_name",
                str,
                description="Part name inside that standard (★ see the search tool).",
            ),
            Param(
                "index",
                dict,
                default=None,
                description="A pre-loaded index (optional).",
            ),
        ],
        doc="Resolve a Toolbox part name to its file path. ★ Pure data — no SolidWorks call. "
        "★ An unknown name fails with what is available instead of returning nothing.",
    ),
    #: ── 草图编辑（★ 空条目 `sketch_chamfer` / `sketch_edit_ops` 的填实）──
    ToolSpec(
        name="solidworks_sketch_create_chamfer",
        title="Create a Sketch Chamfer",
        module="sw_sketch_edit",
        function="create_sketch_chamfer",
        inject="model",
        params=[
            Param(
                "chamfer_type", int, default=0, description="Chamfer type enum value."
            ),
            Param("distance_mm", float, description="Chamfer distance in MILLIMETRES."),
        ],
        doc="Create a chamfer on the selected sketch entities. ★ Needs entities selected first "
        "(★ rule 3: select declaratively, do not pass coordinates). "
        "⚠ The backend limit in known-facts 47 applies to the *feature* chamfer; this is the "
        "sketch one — the layer reports what actually happened.",
    ),
    ToolSpec(
        name="solidworks_sketch_mirror",
        title="Mirror the Selected Sketch Entities",
        module="sw_sketch_edit",
        function="sketch_mirror",
        inject="model",
        params=[],
        doc="Mirror the selected sketch entities about the selected centerline. "
        "★ The criterion is that the sketch entity count changes.",
    ),
    ToolSpec(
        name="solidworks_sketch_convert_entities",
        title="Convert Entities into the Active Sketch",
        module="sw_sketch_edit",
        function="convert_entities",
        inject="model",
        params=[
            Param("chain", bool, default=True, description="Select the whole chain."),
            Param(
                "inner_loops", bool, default=False, description="Include inner loops."
            ),
        ],
        doc="Convert the selected model edges into the active sketch. ★ The criterion is that the "
        "sketch entity count changes.",
    ),
]
