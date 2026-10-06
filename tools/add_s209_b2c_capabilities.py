"""★ 规格 209 · B2-3（idx 52）：把 `drawing_center_lines` 能力写进 capabilities.yaml。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具/一次性施工脚本）
# 文件:   `tools/add_s209_b2c_capabilities.py`
# 定位:   ★ 追加 **1 条**能力 `drawing_center_lines`（★ level = **`stitched`**：
#   真机**没建出来**，且**官方前置只复现了一半**）✓
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
from pathlib import Path

CAPS = Path(r"D:\AI\SW\capabilities.yaml")

ENTRY = {
    "id": "drawing_center_lines",
    "label": "工程图中心线（`IDrawingDoc::InsertCenterLine2`，零参）—— ★ 真机**定案**："
             "选中了也没产出（如实标 `stitched`）",
    "level": "stitched",
    "verified_versions": ["2026"],
    "backends": ["solidworks-com-pywin32"],
    "dependencies": ["solidworks"],
    "evidence": [
        "★★★ 真机（2026-10-06 · 规格 209 的 **B2-3** · idx **52**）："
        "`python tools/sw_guard.py --timeout 900 -- python tools/probe_spec209_b2_centerline.py` ⇒ "
        "圆柱零件的工程图视图：`IView::GetVisibleEntities2` 回 **edge=1 · face=1**"
        "（`silhouette_edge`/`vertex` 回 **0**）；用 `Select4` **按对象**选上后"
        "**选区回读 = 1**（★ 事实 8：回读值可信）；而 `InsertCenterLine2` **回 `None`**、"
        "`IView::GetCenterLineCount()` **0 → 0（Δ=0）** ⇒ ★★ **「选中了也没产出」** ✓ "
        "★ 证据 `output/spec209-centerline.json`",
        "★★★ **两家外部项目「互相矛盾」的定案（各对一半）**：★ 说「**静默无效**」的那家"
        "**不准确** —— ★ 它**并不静默**（返回值就是 `None`，`bool(None)` 为假）；"
        "★ 而说 `bool(result)` 的那家**在本例里恰好是对的** —— "
        "★★ **但那条判据不能通用**（另有「返回非 None 而几何没变」的情形，"
        "★ 只有 `GetCenterLineCount` 的**增量**抓得住）⇒ ★ 本仓的判据是**回读增量** ✓",
        "★ 官方依据逐页读过：`C:\\swapi\\types\\IDrawingDoc\\InsertCenterLine2.md`"
        "（`Centerline InsertCenterLine2()`；摘要逐字「Inserts a centerline on the **selected "
        "entities**.」；★ **既无 `## Remarks` 也无 `Parameters`** ⇒ 「要选什么」**只能从示例读**）· "
        "★★ `examples\\Get_Centerlines_in_Drawing_Example_VB.md`（**调用序**：先 "
        "`SelectByID2(…, \"COMPONENT\", …)`、**再**按**点**选 `FACE`、然后才调）· "
        "`IView\\GetVisibleEntities2.md`（★ **无 out 参** ⇒ pywin32 可直接用）· "
        "`IView\\GetCenterLineCount.md`（**判据来源**）· `enums\\swViewEntityType_e.md`（四值）",
    ],
    "limitations": [
        "★★★ **官方前置只复现了一半**（★ 这是标 `stitched` 的**主要**原因）：官方示例的调用序是"
        "**先选 `COMPONENT`、再按点选 `FACE`**，★ 而**它的视图来自装配**"
        "（示例里的选择串是 `cylinder20-9@Drawing View1`）⇒ ★ 本轮只复现了「**选实体**」那一半，"
        "**没走「先选组件」**、且夹具是**零件**视图 ⇒ ★★ **结论必须限定在这条路径上** ✓ "
        "★ **下一步（写清楚）**：① 用**装配**工程图；② **先选组件**"
        "（`SelectByID2(\"<组件名>@<视图名>\", \"COMPONENT\", …)`）**再选面**；③ 重跑本探针 ✓",
        "★★ **判据纪律（本条的要点）**：**「选不上」与「选了也没用」必须分开** —— "
        "★ 选区回读为 0 时本函数**在调 `InsertCenterLine2` 之前就报错**"
        "（★ 那种情形**不构成**「能力无效」的证据）；★ 只有**选到了**（回读 1）仍 Δ=0，"
        "才是「选了也没用」⇒ ★ 两者在返回值里分成 `selection_count` 与 `centerline_delta` 两个字段 ✓",
        "★★ **我踩了本仓已知事实 33 的同一形态**：`IView::GetVisibleEntities2` 的 "
        "`LpViewComponent` **不能传 Python `None`** —— ★ 传 `None` ⇒ `com_error` **-2147352571"
        "（类型不匹配）**；★ 第一次四种实体类型**全部**报这个错，★ 看着像「读不到」，"
        "**实际是我传错了** ⇒ 现在包 `sw_connect.create_empty_dispatch_variant()` ✓ "
        "（★ 与事实 33 记的 `SelectByID2`/`Select4` 的 `Callout` 坑**一模一样**）",
        "★ 判据用的是 **`GetCenterLineCount()`**（**零参回 int**）—— ⚠ **不用** "
        "`GetCenterLineCount` 之外的带 out 参的兄弟成员（本仓已知 pywin32 下 out 参不保证回写）✓",
        "⚠ **未验**：★ 装配视图 + 先选组件那条路（见上）· ★ 多实体 / 多视图 / 多配置 · "
        "★ 官方示例里 `SelectByID2` 的坐标是**图纸坐标**还是**模型坐标**（★ 本模块**不猜坐标**，"
        "改走按对象选 ⇒ 这个问题在**本路径上不出现**，★ 但在「按点选」那条路上**仍未查**）✓",
        "★★ **裁决书建议「与 idx 30 `auto_center_marks` 合并成一条工具两种模式」—— 我没照做**，"
        "理由可核：两条入口的**入参形状不同**（本条形参可全做成标量；`auto_center_marks` 收的是"
        "**结构化 requirements 列表** `[{\"id\",\"view\",\"targets\",\"count\"}]`）⇒ `Param` 表达不了 "
        "⇒ ★ 硬合并会造出「一半参数对一半模式无意义」的工具 ⇒ ★ 偏离已记进 `tasks.md` ✓ "
        "⚠ 另：裁决书 §一 第 2 条点名的缺口（**批量路 `AutoInsertCenterMarks2` 从未单独真机验证**）"
        "**本轮仍未补**，★ 已列为下一步 ✓",
    ],
    "source_evidence": "★ 本仓自建（按官方签名 + 官方示例的**调用序**立）："
                       "`C:\\swapi\\types\\IDrawingDoc\\InsertCenterLine2.md` · "
                       "`IView\\GetVisibleEntities2.md` · `IView\\GetCenterLineCount.md` · "
                       "`enums\\swViewEntityType_e.md` · "
                       "官方示例 `Get_Centerlines_in_Drawing_Example_VB.md` —— ★ **逐页读过** ✓ "
                       "★ 落点 `scripts/sw_drawing_create_missing.py`（已有模块，★ 裁决书指定）· "
                       "★ **不来自任何外部项目**（★ 而本条的定案**正是去判两家外部项目**）✓",
    "source": "original",
    "allowed_modes": ["interactive", "reviewed", "unattended"],
    "mcp_tools": ["solidworks_drawing_insert_center_lines"],
}


def main() -> int:
    data = json.loads(CAPS.read_text(encoding="utf-8"))
    caps = data["capabilities"]
    if any(c.get("id") == ENTRY["id"] for c in caps):
        print("★ 已存在 ⇒ 跳过")
    else:
        caps.append(ENTRY)
        print("★ 追加 drawing_center_lines（stitched）")
    out = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    json.loads(out)
    CAPS.write_text(out, encoding="utf-8")
    print("★ capabilities 共 %d 条" % len(caps))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
