"""★ 规格 209 · B4-5（idx 205）：把 `drawing_model_annotations` 能力写进 capabilities.yaml。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具/一次性施工脚本）
# 文件:   `tools/add_s209_b4e_capabilities.py`
# 定位:   ★ 追加 **1 条**能力 `drawing_model_annotations`（★ level = **`stitched`**，
#   因为真机只验到「可达 + 回读可用」，★ **没能产出非空插入**）✓
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
from pathlib import Path

CAPS = Path(r"D:\AI\SW\capabilities.yaml")

ENTRY = {
    "id": "drawing_model_annotations",
    "label": "把模型标注插进工程图视图（`IDrawingDoc::InsertModelAnnotations4`，**8 参**）—— "
             "★★ **本机未产出非空插入**（如实标 `stitched`）",
    "level": "stitched",
    "verified_versions": ["2026"],
    "backends": ["solidworks-com-pywin32"],
    "dependencies": ["solidworks"],
    "evidence": [
        "★★ 真机（2026-10-06 · 规格 209 的 **B4-5** · idx **205**）："
        "`python tools/sw_guard.py --timeout 900 -- python tools/probe_spec209_b4_model_annotations.py` ⇒ "
        "新建零件（存盘）+ 工程图 + 一个投影视图（`工程图视图1`）⇒ "
        "① **调用可达**：`InsertModelAnnotations4` **不抛异常**、回的是数组（★ 数组长度 **0**）；"
        "② **回读可用**：`IView::GetAnnotationCount()` 的前后回读 **0 → 0**；"
        "③ 负例都**大声报**：空图纸（一个视图都没有）与「两个 `insert_all_*` 都 False 且 `types` 空」"
        "✓ ★ 证据 `output/spec209-model-annotations.json`",
        "★★★ **为什么标 `stitched` 而不是 `verified`（原因已查明，如实记）**：我们的零件是"
        "**纯坐标画出来的**（`sketch_corner_rectangle` + `extrude_boss`）⇒ ★ **一个尺寸都没有**；"
        "★ 而本仓的 `sw_sketch_dimensions.add_horizontal_dimension` / `add_vertical_dimension` "
        "**都回了 `None`**（★ 官方 `AddDimension2` 摘要逐字「Creates a display dimension … "
        "for **selected entities**」⇒ 它**要先选中实体**）⇒ ★★ **那份夹具里根本没有可插的东西** ✓ "
        "⇒ ★ 这是**数据相关**的失败，**不是**后端到不了（★ 两者必须分开记账）✓",
        "★ 官方依据逐页读过：`C:\\swapi\\types\\IDrawingDoc\\InsertModelAnnotations4.md`"
        "（**8 参**；`## Returns` 逐字「Array of inserted `IAnnotation` objects」；摘要逐字"
        "「into this drawing document's **currently selected drawing view**」）· "
        "`C:\\swapi\\enums\\swImportModelItemsSource_e.md`（四值）· "
        "`C:\\swapi\\enums\\swInsertAnnotation_e.md`（★ **26 个成员的位掩码**）· "
        "`C:\\swapi\\types\\IView\\GetAnnotationCount.md` · "
        "★★ `examples\\Insert_Model_Annotations_Example_VB.md`（**调用序**：选中视图 → "
        "**`ActivateView`** → 清选区 → 调它）✓",
    ],
    "limitations": [
        "★★★ **没能产出非空插入**（★ 因此 `level` = `stitched`，**不是** `verified`）："
        "夹具里的零件**没有尺寸/标注可插**。★ **下一步（写清楚）**：① 先**选中一条草图段**再调"
        "`AddHorizontalDimension2`（★ 它要 selected entities）把尺寸**真建出来**；"
        "或 ② 直接用**已有的、带尺寸的**零件（★ 磁盘上 `AI Solidworks\\模型\\` 那批）当夹具；"
        "再重跑本探针 ✓",
        "★★ **调用序里有一处签名看不出来的东西**：官方示例先 `SelectByID2(<视图>, \"DRAWINGVIEW\", …)`、"
        "**再 `ActivateView(<视图>)`** ⇒ ★ 少了 `ActivateView` 那一步（或视图没被激活）都可能静默失空 ✓",
        "★★ **`AllViews` 决定「选区去留」**：官方示例走 `AllViews=True` 所以它**清选区**；"
        "而 `AllViews=False` 时官方摘要要的是「**currently selected drawing view**」⇒ "
        "★★ **必须把视图留在选区里** —— ★ 我第一版**无脑清掉** ⇒ 回空数组"
        "（★ 一个**指不出真因**的现象）✓ 已加静态断言钉住 `if all_views:` ✓",
        "★ **判据不能用返回值**：它回的是 **COM 标注对象数组** ⇒ ★ **过不了 MCP 的 JSON 边界** ⇒ "
        "★ 本能力用 **`IView::GetAnnotationCount()` 的前后回读**（`_sum_over_views` + `_delta`）✓",
        "★ 本工具**不设** `require_verified` 式硬闸 —— 因为这里的「插不进去」是**数据相关**的"
        "（模型里有没有标注），★ **不是**后端到不了 ⇒ ★ 硬闸会**误杀**（★ 与 `create_hem` 那类"
        "「后端到不了」的处置**故意不同**）✓",
        "⚠ **未验**：★ `AllViews=True` 走**全部视图**那条路的效果（★ 本轮只验到它**不抛**、"
        "回空数组）· ★ 装配体的标注（`assembly_only` / `selected_component`）· "
        "★ `duplicate_dims`/`hidden_feature_dims`/`use_placement_in_sketch` 三个开关**均未验** ✓",
    ],
    "source_evidence": "★ 本仓自建（按官方签名 + 官方示例的**调用序**立）："
                       "`C:\\swapi\\types\\IDrawingDoc\\InsertModelAnnotations4.md` · "
                       "`C:\\swapi\\enums\\{swImportModelItemsSource_e,swInsertAnnotation_e}.md` · "
                       "`C:\\swapi\\types\\IView\\GetAnnotationCount.md` · "
                       "官方示例 `Insert_Model_Annotations_Example_VB.md` —— ★ **逐页读过** ✓ "
                       "★★ **落点偏离裁决书建议**（它说 `scripts/sw_drawing.py`）：★ 那只有 **29 行**、"
                       "是**桥接壳**（`exec_module` 加载 subskill 再 `globals().update`）⇒ 往里加会被覆盖；"
                       "★ 实际落 `scripts/sw_drawing_create_missing.py` —— ★ **裁决书自己要求"
                       "「复用该文件已有的读侧助手，别新造」**，那就只能落那里 ✓ "
                       "★ **不来自任何外部项目** ✓",
    "source": "original",
    "allowed_modes": ["interactive", "reviewed", "unattended"],
    "mcp_tools": ["solidworks_drawing_insert_model_items"],
}


def main() -> int:
    data = json.loads(CAPS.read_text(encoding="utf-8"))
    caps = data["capabilities"]
    if any(c.get("id") == ENTRY["id"] for c in caps):
        print("★ 已存在 ⇒ 跳过")
    else:
        caps.append(ENTRY)
        print("★ 追加 drawing_model_annotations（stitched）")
    out = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    json.loads(out)
    CAPS.write_text(out, encoding="utf-8")
    print("★ capabilities 共 %d 条" % len(caps))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
