"""★ 批次 89：C 类**最后两组语义无歧义**的解锁 —— Costing 写侧 3 个 + 运动算例 2 个（★ 含护城河域 AVI）。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装函数的来源块在其 `scripts/` 源码里）
# 文件:   `scripts/sw_costing.py`（`include_body` / `set_costing_method` / `update_cost_
# for_all_bodies`）·
#         `scripts/sw_motion.py`（`calculate_and_play` / `export_motion_study_avi`）
# 定位:   ★ 规格 `specs/205-tool-ramp/` §8 的**批 89** —— ★ 走的是「**加解析器换工具**
#           」那条路：
#         C 类里**最后两组语义无歧义**的组（`cost_part` / `motion_study`），
#         ★ 两个新注入键 `"cost_part"` / `"motion_study"` 已在本笔同一提交里加进 `RESOLVERS` ✓
# 官方依据: **两组分别不同，如实分开写**：
#   · ★ **motion 那两个有官方页**（逐字抄）：
#       `C:\swapi\types\IMotionStudy\Calculate.md`  ⇒ `System.bool Calculate()`
#       `C:\swapi\types\IMotionStudy\Play.md`       ⇒ `System.bool Play()`
#       `C:\swapi\types\IMotionStudy\SaveToAVI.md`  ⇒
#         `System.bool SaveToAVI( System.string FileName, AVIParameter Parameter )`
#     ★ 解析器用的三个成员也都有页：
# `IMotionStudyManager\GetMotionStudy.md`      ⇒ `MotionStudy GetMotionStudy( System.str
# ing MotionStudyName )`
#       `IMotionStudyManager\GetMotionStudyCount.md` ⇒ `System.int GetMotionStudyCount()`
#       `IMotionStudyManager\GetMotionStudyNames.md`（同名清单）
#   · ★★ **Costing 那三个`C:\swapi\types` 下没有官方页**（那套源不含 `sldcostingapi` 册；
# `IncludeBody` / `SetCostingMethod` / `UpdateCostForAllBodies` 三页 `glob` **均 0 命中*
# *）⇒
#     ★ 真源是**本仓** `scripts/sw_costing.py`（它的来源块逐字写着依据是
#     「**反射确认的实参个数** `COSTING_ARITY`」，成员名如 `ICostManager` / `ICostModel`）
#     ⇒ ★ **不编官方签名**（铁律 5），doc 里如实说明真源 ✓
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 规模:   **5 个工具** ⇒ 工具数 414 → **419**
# ★★ 本批**不做**的（FR-002/D-5 要求记"不做 + 原因"）：
#     · `sw_costing.get_body_count` / `get_bodies` / `get_costing_method` /
#       `get_cost_analysis` / `collect_costing_evidence` —— ★ **各自的 `*_report` 包装
#       （`get_body_count_report` 等）已挂成工具**（`solidworks_costing_body_count` /
# `…_list_bodies` / `…_method_value` / `…_read_analysis` / `…_evidence`）⇒ **FR-006 去重
# ** ✓
#     · `sw_motion.add_constant_speed_rotary_motor` / `…_by_cylinders` —— ★ 上游遗留工具
#       `solidworks_add_rotary_motor` 就是这两个的封装 ⇒ **已覆盖** ✓
#     · `sw_costing.get_costing_model` 本身 —— ★ 它是**解析器用的路径**，不是给用户的动作 ✓
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH89"]

SPECS_BATCH89 = [
    # ── ① Costing 写侧（3）—— ★ 无官方页 ⇒ 真源 = 本仓 `scripts/sw_costing.py` ────────
    # ──
    ToolSpec(
        name="solidworks_costing_include_body",
        title="Include/Exclude a Body from the Cost Calculation",
        module="sw_costing",
        function="include_body",
        inject="cost_part",
        params=[
            Param(
                "body_name",
                str,
                description=(
                    "Name of the body as listed by solidworks_costing_list_bodies; it is a name, not a coordinate."
                ),
            ),
            Param(
                "include",
                bool,
                default=True,
                description=(
                    "Whether the body counts in the cost calculation, where true includes it and false excludes it. Def"
                    "aults to true."
                ),
            ),
        ],
        evidence=(
            "把某个实体纳入（或排除出）**成本计算**。★ 官方依据：`C:\\swapi\\types` **无该成员的页**（那套源不含 `sldco"
            "stingapi` 册）⇒ ★ 真源是**本仓** `scripts/sw_costing.py:240-242`（`_checked(cost_part, \"IncludeBody\", bo"
            "dy_name, include)`），而该模块的来源块写明依据是「反射确认的实参个数」。★ 注入键 `cost_part` 给的是 Costin"
            "g 的**成本模型对象**（其依据在仓里：`get_body_count_report` 逐字把 `_costing_chain(cost_manager)` 取出的对"
            "象喂给 `get_body_count(cost_part)`）✓ ⚠ **未在本机实测**（铁律 2）。"
        ),
        doc=(
            "Set whether one body counts in the cost calculation, addressed by name. Writes the inclusion flag on the c"
            "osting body and does not save; it is not yet verified on a real machine, so list the body names first with"
            " solidworks_costing_list_bodies."
        ),
    ),
    ToolSpec(
        name="solidworks_costing_set_method",
        title="Set a Costing Method on the Cost Model",
        module="sw_costing",
        function="set_costing_method",
        inject="cost_part",
        params=[
            Param("method_name", str, description="Costing method name to set."),
            Param(
                "method",
                int,
                description=(
                    "Integer method value; the allowed values are undocumented, so the tool passes it through without i"
                    "nterpreting it."
                ),
            ),
        ],
        evidence=(
            "设某个成本方法的取值。★ 同族：只读的 `solidworks_costing_method_value`（读当前值）——本工具是它的**写侧配对"
            "** ✓ ★ 官方依据：`C:\\swapi\\types` **无该成员的页** ⇒ ★ 真源是**本仓** `scripts/sw_costing.py:245-247`；⚠"
            " **未在本机实测**（铁律 2）。"
        ),
        doc=(
            "Set the value of one costing method by name. Writes to the costing model and is not yet verified on a real"
            " machine; the integer value has no published meaning, so it is passed through unchanged."
        ),
    ),
    ToolSpec(
        name="solidworks_costing_update_cost_for_all_bodies",
        title="Recompute the Cost for All Bodies",
        module="sw_costing",
        function="update_cost_for_all_bodies",
        inject="cost_part",
        params=[],
        evidence=(
            "对**全部实体**重算成本。零参。★ 官方依据：`C:\\swapi\\types` **无该成员的页** ⇒ ★ 真源是**本仓** `scripts/"
            "sw_costing.py:265-267`；⚠ **未在本机实测**（铁律 2）。★ 典型调用序：改完材料/模板（`solidworks_costing_set"
            "_default_*`）或纳入实体（`solidworks_costing_include_body`）之后，用本工具让成本刷新 ✓"
        ),
        doc=(
            "Update the cost of every body in the active part after a material, template or inclusion change. Writes th"
            "e refreshed cost figures and is not yet verified on a real machine; it takes no arguments, so call it once"
            " those earlier settings are in place."
        ),
    ),
    # ── ② 运动算例（2）—— ★ 有官方页，逐字引自 `C:\swapi\types\IMotionStudy\` ─────────
    # ────
    ToolSpec(
        name="solidworks_motion_calculate_and_play",
        title="Calculate the Motion Study (and Optionally Play It)",
        module="sw_motion",
        function="calculate_and_play",
        inject="motion_study",
        #: ★★ `param_alias` 里给 **None** = 「**由解析器消费、不进目标函数**」——
        #:   ★ 这是 `tool_registry.py:511-513` 逐字写明的机制：
        #:   「`param_alias` 里 None = 由解析器消费，不进目标函数」✓
        #:   ★ 而 `resolve_motion_study` 正是**读**这个参数来决定注哪个算例的 ✓
        param_alias={"motion_study_name": None},
        params=[
            Param(
                "play",
                bool,
                default=True,
                description=(
                    "Whether to play the animation after a successful calculation; false only calculates. Defaults to t"
                    "rue."
                ),
            ),
            Param(
                "motion_study_name",
                str,
                default="",
                description=(
                    "Motion study name; when empty a single study is used, none raises an error and more than one raise"
                    "s asking you to name it. Defaults to empty."
                ),
            ),
        ],
        evidence=(
            "两步：`IMotionStudy::Calculate()` 再（可选）`IMotionStudy::Play()`。★ 官方签名逐字：`C:\\swapi\\types\\IMo"
            "tionStudy\\Calculate.md` ⇒ `System.bool Calculate()`；`…\\Play.md` ⇒ `System.bool Play()`。★ 返回值是两步"
            "里 **`Calculate` 的 bool** ✓ ⚠ 本仓累计多处「返回码撒谎」⇒ ★ 别只看返回值，配套用 `solidworks_motion_colle"
            "ct_summary` 复核结果是否真的出现 ✓"
        ),
        doc=(
            "Compute one motion study, then optionally play the animation back. Writes the computed results into the st"
            "udy and does not save; the returned value is Calculate's boolean, which has lied before, so check the outc"
            "ome with solidworks_motion_collect_summary as well."
        ),
    ),
    ToolSpec(
        name="solidworks_motion_export_avi",
        title="Export the Motion Study to AVI (one of this repo's moat domains)",
        module="sw_motion",
        function="export_motion_study_avi",
        inject="motion_study",
        #: ★★ 同 `calculate_and_play`：`motion_study_name` 由**解析器消费**（`None` = 不
        #: 进目标函数）✓
        param_alias={"motion_study_name": None},
        params=[
            Param(
                "file_path",
                str,
                description=(
                    "Output file path including the extension; .bmp and .tga are also accepted by the same member, and "
                    "the parent directory must already exist."
                ),
            ),
            Param(
                "motion_study_name",
                str,
                default="",
                description=(
                    "Motion study name; an empty value follows the same single-study rule as solidworks_motion_calculat"
                    "e_and_play. Defaults to empty."
                ),
            ),
        ],
        evidence=(
            "把运动算例导出成 **AVI** —— ★★ **AVI 导出是本仓三个「业界空白域护城河」之一** ✓ ★ 官方签名逐字：`C:\\swapi"
            "\\types\\IMotionStudy\\SaveToAVI.md` ⇒ `System.bool SaveToAVI( System.string FileName, AVIParameter Parame"
            "ter )`。★★ **判据不看返回值**：本仓累计多处「返回码撒谎」⇒ 该函数**以「文件真的出现且大小 > 0」为准**（返"
            "回 `{ok, returned, exists, size_bytes, path}`）✓ ⚠ `AVIParameter` 是 **COM 对象**、**过不了 MCP 的 JSON 边"
            "界** ⇒ ★ 本工具**不收它**（函数默认 `None`）⇒ ★ 时长/帧率走 SolidWorks 默认值（★ 本仓**不猜**默认值）✓"
        ),
        doc=(
            "Export one motion study animation to a file and report whether the file really appeared with a non-zero si"
            "ze. Writes the file, whose parent directory must already exist; duration and frame rate come from the Soli"
            "dWorks defaults because the parameter object cannot cross this boundary."
        ),
    ),
]
