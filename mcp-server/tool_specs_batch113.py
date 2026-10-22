"""★ EC00 T017 批 113 —— 把 `sw_sketch_relations.apply_sketch_relations` **正式注册**成 MCP 工具。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植）
# 文件:   `scripts/sw_sketch_relations.py`（★ 实现 · ★ 151 行 · ★ 判据 = `GetRelationsCount` 真 +1）
#         `tests/test_sw_sketch_relations_safety.py`（★ spec 221 的 **12 例**安全判据）
#         `specs/221-sketch-relation-dispatch-safety/`（★ 离线安全切片 · ★ runtime/product=not_run）
#         `specs/302-ec00-trustworthy-tool-base/research/T006-official-signature.md`（★ 官方签名核验）
#         `C:\swapi\types\ISketchRelationManager\AddRelation.md`（★ 官方逐字 · 2 参）
# 定位:   ★★ **EC00 T017**（★ 逐字：「完成草图关系正式注册、参数注入/包装和类型/数量/
#           上下文预检」）。
#         ★★★ **实测缺口**（2026-10-10）：★ `sw_sketch_relations.py` **有实现但 0 个 ToolSpec**
#         ⇒ ★★ 它**不可被 MCP 调用**（★ 从「用户可发现、可调用」口径看**等于不存在**）。
#         ★ 本批**只做注册**（★ 不改业务逻辑 —— ★ 实现已由 spec 221 验过 12 例）。
# 官方依据: `AddRelation( System.object Entities, System.int RelationType )`（★ 2 参 · ★
#            已核）+ `## Remarks`「A sketch must be active for this method to have any e
#           ffect.」+ `ISketchSegment::GetRelationsCount`（★ 回读判据）
# 许可:   本仓库 MIT。★ 无第三方代码引入（★ 引用的四家仅作对照）。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH113"]

#: ★★★ 关系类型（★ 官方枚举 `swConstraintType_e` · ★ 86 个成员）——
#:   ★★ 本工具收**关系名**（★ 字符串），★ 由实现映射到枚举**数值**（★ 见 `RELATION_TYPES`）。
#:   ★ 逐字依据：`C:\swapi\enums\swConstraintType_e.md`。
RELATION_HELP = (
    "★ 关系名（★ 实现内部映射到官方 `swConstraintType_e` **数值**；"
    "★ 不是 `sg*` 字符串 —— ★ 那是另一入口 `SketchAddConstraints` 的口径）。"
    "★ 合法值见 `scripts/sw_sketch_relations.py` 的 `RELATION_TYPES`。"
    "★★ 非法名 ⇒ **调用前拒绝**（★ 官方 `SketchAddConstraints` 会**静默回 True** 而不加任何关系）。"
)

#: ★★ 关系清单的格式：★ **分号分隔的多项**、★ 每项 `"<关系名>:<段序号>,<段序号>"`（★ 声明式 · ★ 规则 3）。
#:   ★★★ **为什么用 `str` 而不用 `list`** —— ★ 依据 `mcp-server/tool_specs_batch15.py:21-25` 逐字：
#:     「因为它们是 **`list` 型**，而实测：`tool_specs_batch*.py` 里**没有任何 `list` 型 `Param` 的先例**
#:      ⇒ 记进队列 A10：若要暴露，先决定"list 怎么过 MCP 边界"（逗号串？JSON 串？），**并留下先例**」。
#:   ★★ **本仓既有约定**（★ 多处先例）：★ **`str` + 分隔符**（★ 如 `tool_specs_batch81.py:118` 的
#:     「逗号分隔且**顺序即语义**」· ★ `tool_specs_batch93.py:36` 的「逗号分隔」）
#:     ⇒ ★ **本批遵守既有约定**：★ 外层用 **`;`** 分隔多项、★ 内层用 `,` 分隔段序号
#:     （★ 因为**关系名本身不含** `;`/`,` ⇒ ★ 无歧义）。
RELATIONS_HELP = (
    "★ 关系清单（★ **分号 `;` 分隔**的多项）。每项形如 `horizontal:0` / `coincident:0,1` —— "
    "★ 冒号前是**关系名**、★ 冒号后是**段序号**（★ 多个段用逗号 `,` 分隔）。"
    "★ 段序号是 `index:N` 口径（★ **声明式** ⇒ ★ 不传裸坐标 ⇒ ★ 规则 3 合规）。"
    "★ 例：`\"horizontal:0;coincident:0,1\"`（★ 加两条关系）。"
    "★★ 判据不看返回码：★ 每条关系 ⇒ **该段 `ISketchSegment::GetRelationsCount` 真的 +1** ✓"
)


def _relations_list(params) -> dict:
    """★ 把 `;` 分隔的字符串**拆成清单**（★ 实现收 `list[str]`，★ 每项 `"<关系名>:<段序号>,…"`）。

    ★★ **为什么在这里拆**（★ 而不是在实现里）：
      · ★ 实现 `apply_sketch_relations(model, *, relations, verify=True)` 收的是 **`list`**；
      · ★★ MCP 边界**只过标量**（★ 无 `list` 型 `Param` 先例 —— ★ `tool_specs_batch15.py:21-25`）；
      · ★★★ **⇒ 拆分发生在 `derived_args`**（★ 与全仓既有的「`str` + 分隔符」约定一致）。
    ★ 空串 ⇒ **空清单**（★ 实现会回 `total=0`，★ **不是**错误）。
    """
    raw = str(getattr(params, "relations", "") or "")
    items = [x.strip() for x in raw.split(";") if x.strip()]
    return {"relations": items}


SPECS_BATCH113: list[ToolSpec] = [
    ToolSpec(
        name="solidworks_sketch_apply_relations",
        title="Apply a Batch of Sketch Relations (read-back verified)",
        module="sw_sketch_relations", function="apply_sketch_relations",
        inject="model",
        params=[
            Param("relations", str, description=RELATIONS_HELP),
            Param("verify", bool, default=True,
                  description="★ 是否取前/后态关系数（★ **默认 True**）。"
                              "⚠ 设 `False` **不绕过状态门**（★ 实现仍查活动草图与约束状态）"
                              "—— ★ 它只是省掉一次回读 ⇒ ★ 那样 `effect_status` 只能是 `unknown`。"),
        ],
        derived_args=_relations_list,
        doc=("★ **一次把一整张几何关系清单加全**（★ 与画圆/画线同级）。"
             "★★ **官方入口**：`ISketchRelationManager::AddRelation`"
             "（★ 官方签名逐字：`SketchRelation AddRelation( System.object Entities, "
             "System.int RelationType )` —— ★ **2 参**；"
             "⚠ **不要**与指针变体 `IAddRelation(Int32, Object&, Int32)`（**3 参**）混用 ⇒ "
             "传错个数报 `0x8002000E`）。"
             "★★ **官方 `## Remarks` 逐字**：「A sketch must be active for this method to have "
             "any effect.」⇒ ★ **必须有活动草图**（★ 实现已查：`_active(model)` 为 None 即拒绝）。"
             "★★★ **判据（规则 6 · 全回读）**：★ **不看返回码**（★ 事实 8）—— "
             "★ 每条关系 ⇒ 该段 `GetRelationsCount` **真的 +1** ✓；"
             "★ 前态读不到 ⇒ `rejected`（★ **不做任何修改**）；"
             "★ 调用抛异常 ⇒ `uncertain`（★ **不重放**，★ 批内后续项 `not_started`）。"
             "★★ **防过定义**：★ 草图已完全定义 ⇒ **整批拒加**。"
             "★★ **选段**：`index:N` + `IEntity::Select4`（★ 事实 32：实体**不能按名字选**）。"
             "⚠ **验证等级**：★ 本工具的实现由 `tests/test_sw_sketch_relations_safety.py`（**12 例**）"
             "在**假宿主**上验过（★ **离线**）；★★ **真机未在本特性内验证** ⇒ "
             "★ `runtime` = **`not_run`**（★ 依据 `specs/221-*/acceptance.md`："
             "「限定离线行为回归通过；runtime/product=not_run」）。"
             "★ 见 `specs/302-ec00-trustworthy-tool-base/`（EC00 T017/T018）。"),
    ),
]
