"""第三十二批 MCP 工具声明：**建模闭环补全（建特征 + 回读确认）** 4 个（24h 段 3 / Spec Kit `146`）。

## ★★★ 本批的两条主线
```
① **补建模能力**：抽壳 / 筋 / 圆顶 / 复合曲线 —— ★ 四个都是**真特征**（不是辅助函数）。
② ★★★ **落实规则 6**：「**建特征之后查 `EditRebuild3` + `GetWhatsWrong2`，不静默成功**」
   ⇒ ★ 四个工具**统一回"回读报告"**，判据三条：**特征在树里 + 重建成功 + 查错数 0**。
```

## ★★ 一个**规则文本的失真**（本批查清，已在能力层记明）
```
⚠ `docs/union-conventions.md` **规则 6** 写的成员名是 **`GetWhatsWrong2`** ——
  ★ 而它在**本机两套官方源里都不存在**（`C:\\swapi\\types` 与反射 dump 都查不到）。
★ 真正的成员是：**`IModelDocExtension.GetWhatsWrongCount()`**（★ 零参、直接回个数）
  与 `IModelDocExtension.GetWhatsWrong(out, out, out)`（★ 三参 by-ref）。
⚠ 而且它**挂在 `IModelDocExtension` 上**（不是 `IModelDoc2`）⇒ ★ 必须从 `model.Extension` 取。
⇒ ★ 已在 `scripts/sw_feature_readback.py` 的 docstring 里逐条写清（★ 连同"初版直接对 model 调
  ⇒ 取不到 ⇒ 判据按设计报「不算通过」、**没有静默成 0**"这一段）。
```

## ★★ 判据助手是**经过三次真机打磨**的（`scripts/sw_feature_readback.py`）
```
· 初版：直接对 `model` 调 `GetWhatsWrong2` ⇒ 取不到
· 二版：改用 `Extension.GetWhatsWrongCount` ⇒ ✓ 取到（'草图1' ⇒ 0 条错）
· ★ 三版：`feature_names` 的过滤从"**枚举中文容器名**"改成**结构性判据**
         （只收 `GetTypeName2` 非空的节点）—— ★★ 因为枚举名字**在英文界面下会全部失效**。
真机复验（轮 249）：特征名清单只剩 `['前视基准面','上视基准面','右视基准面','原点','Tables','草图1','凸台-拉伸1']`；
`'草图1'` ⇒ **ok=True · present=True · wrong=0**；不存在的名字 / 容器名 ⇒ **全 False**（★ 有判别力）。
```

## ★ 为什么这四个能挂（而草图图元那批不能）
```
★ 本批四个的形参**都不含裸坐标**（规则 3）：
    `shell(model, thickness)` · `rib(model, sketch_name, thickness, direction)`
    `insert_dome(model, height, reverse, elliptic)` · `insert_composite_curve(model)`
⚠ 而 `linear_pattern`（`d1_x, d1_y, d1_z`）与 `hole_wizard`（`x, y, z`）**有裸坐标**
  ⇒ ★ **本批不挂它们** —— ★ **不为了凑数量挂违反规则 3 的工具**；
    它们的正路是**先做声明式包装**（★ 属"修地基"级别）。
```

## ★ 参数命名（规则 2）
```
★ `thickness_mm` / `height_mm` —— ★ **长度参数带 `_mm`**（通过 `param_alias` 对上能力层的
  `thickness` / `height`）。
★ `feature_name` —— ★ 期望的特征名（中文 UI 下如「抽壳1」/「筋1」/「圆顶1」）；
  ★ 留空则用默认名（★ 能力层按中文 UI 取默认）。
```

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装的函数各自的来源块在其源码里）
# 文件:   mcp-server/tool_specs_batch32.py
# 定位:   24h 计划 段 3（Spec Kit `146`）—— 建模闭环补全 4 个工具。
# 官方依据: `IFeatureManager.InsertFeatureShell` / `InsertRib` / `InsertDome` ·
#          `IModelDoc2.InsertCompositeCurve` · `IModelDoc2.EditRebuild3` ·
#          `IModelDocExtension.GetWhatsWrongCount`（见 `scripts/sw_part.py` 与
#          `scripts/sw_feature_readback.py` 的来源块）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 本批**不做保存**（红线：不碰高风险写操作）。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
"""

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH32"]

_FEAT = (
    "Expected feature name as it appears in the FeatureManager tree "
    "(Chinese UI: 「抽壳1」/「筋1」/「圆顶1」/「复合曲线1」). ★ Leave empty to use the "
    "default name. ⚠ The read-back uses this name, so a wrong name reports "
    "`present: false` rather than silently succeeding."
)
_THICK = (
    "Wall thickness in MILLIMETRES (the capability layer's unit follows the document)."
)
_HEIGHT = "Dome height in MILLIMETRES."
_SKETCH = (
    "Name of an EXISTING sketch to use as the rib profile (e.g. 「草图2」). "
    "★ The sketch must already be in the tree."
)


SPECS_BATCH32 = [
    ToolSpec(
        name="solidworks_part_shell",
        title="Shell the Part (read-back confirmed)",
        module="sw_part",
        function="shell_report",
        inject="model",
        param_alias={"thickness_mm": "thickness_mm"},
        params=[
            Param("thickness_mm", float, description=_THICK),
            Param("feature_name", str, default="", description=_FEAT),
        ],
        evidence=(
            "Hollow the part with a wall thickness and return a READ-BACK report: whether the feature is in the tree, w"
            "hether EditRebuild3 succeeded, and the What's Wrong item count (★ rule 6 — feature creation must not succe"
            "ed silently). ⚠ Does NOT save the document."
        ),
        doc="Hollow the part with a wall thickness and return a READ-BACK report: whether the "
        "feature is in the tree, whether EditRebuild3 succeeded, and the What's Wrong item "
        "count (★ rule 6 — feature creation must not succeed silently). "
        "⚠ Does NOT save the document.",
    ),
    ToolSpec(
        name="solidworks_part_rib",
        title="Create a Rib from a Sketch (read-back confirmed)",
        module="sw_part",
        function="rib_report",
        inject="model",
        param_alias={"thickness_mm": "thickness_mm"},
        params=[
            Param("sketch_name", str, description=_SKETCH),
            Param("thickness_mm", float, description=_THICK),
            Param("feature_name", str, default="", description=_FEAT),
            Param(
                "direction",
                bool,
                default=True,
                description="Rib direction flag (official InsertRib arg 4).",
            ),
        ],
        evidence=(
            "Create a rib from an existing sketch and return a READ-BACK report (feature in tree + rebuild + What's Wro"
            "ng count). ★ Rule 6. ⚠ Does NOT save the document."
        ),
        doc="Create a rib from an existing sketch and return a READ-BACK report (feature in "
        "tree + rebuild + What's Wrong count). ★ Rule 6. ⚠ Does NOT save the document.",
    ),
    ToolSpec(
        name="solidworks_part_insert_dome",
        title="Add a Dome to the Selected Face (read-back confirmed)",
        module="sw_part",
        function="insert_dome_report",
        inject="model",
        param_alias={"height_mm": "height_mm"},
        params=[
            Param("height_mm", float, description=_HEIGHT),
            Param("feature_name", str, default="", description=_FEAT),
            Param(
                "reverse",
                bool,
                default=False,
                description="Reverse the dome direction.",
            ),
            Param(
                "elliptic", bool, default=False, description="Make the dome elliptical."
            ),
            #: ★★ 2026-10-07（接手轮 · 规格 216 T-216-06b）**新增 `face_index`** ——
            #: ★ 起因：★ 官方 Remarks 要求"先选一个面 + **mark=1**"，★ 而注入解析器**会
            #: 清空选区**
            #:     （**事实 503**）⇒ ★ 模型**没有任何办法**在调工具前把面选好 ✗
            #:   ★ 规则 3 **不许收裸坐标** ⇒ ★ 故用**声明式序号**，★ 由函数内自己选
            #: （`sw_part.select_face_by_index_mark1`，★ 形态由既有冒烟 9/9 证明、★ 已真
            #: 机复验）✓
            Param(
                "face_index",
                int,
                default=0,
                description="★ 第几个面（从 0 起）。★ 声明式序号 —— 不信坐标（规则 3）。"
                "越界或选不中会**响亮报错**，不会静默变成「圆顶建不出来」。",
            ),
        ],
        evidence=(
            "★ Add a dome on the face at `face_index` (0-based) and return a READ-BACK report. ★★ The tool selects that"
            " face itself with **selection mark 1** (the official Remarks require it) — so the caller does NOT need to "
            "pre-select anything, and a pre-selection would be cleared anyway. ★ Read-back confirmed (rule 6); does NOT"
            " save the document."
        ),
        doc="★ Add a dome on the face at `face_index` (0-based) and return a READ-BACK report. "
        "★★ The tool selects that face itself with **selection mark 1** (the official Remarks "
        "require it) — so the caller does NOT need to pre-select anything, and a pre-selection "
        "would be cleared anyway. ★ Read-back confirmed (rule 6); does NOT save the document.",
    ),
    ToolSpec(
        name="solidworks_part_insert_composite_curve",
        title="Insert a Composite Curve from the Selection (read-back confirmed)",
        module="sw_part",
        function="insert_composite_curve_report",
        inject="model",
        params=[
            Param("feature_name", str, default="", description=_FEAT),
        ],
        evidence=(
            "Join the selected entities into a composite curve and return a READ-BACK report (★ rule 6). The capability"
            " layer already raises when the official call returns False — this adds the tree/rebuild/What's Wrong read-"
            "back on top. ⚠ The official Remarks require the entities to be selected with mark = 1 first. ⚠ Does NOT sa"
            "ve the document."
        ),
        doc="Join the selected entities into a composite curve and return a READ-BACK report "
        "(★ rule 6). The capability layer already raises when the official call returns "
        "False — this adds the tree/rebuild/What's Wrong read-back on top. "
        "⚠ The official Remarks require the entities to be selected with mark = 1 first. "
        "⚠ Does NOT save the document.",
    ),
]
