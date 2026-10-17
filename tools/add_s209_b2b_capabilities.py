"""★ 规格 209 · B2-2（idx 34）：把 `drawing_bom_balloons` 能力写进 capabilities.yaml。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具/一次性施工脚本）
# 文件:   `tools/add_s209_b2b_capabilities.py`
# 定位:   ★ 追加 **1 条**能力 `drawing_bom_balloons`（★ level = `verified`：
#   两格独立真机对照都 **Δ=1**）· ★ 同一批还**收紧了原函数的 `ok`**（改成纯回读）✓
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
from pathlib import Path

CAPS = Path(Path(__file__).resolve().parents[1] / "capabilities.yaml")

ENTRY = {
    "id": "drawing_bom_balloons",
    "label": "BOM 气泡（`IDrawingDoc::AutoBalloon5`）—— ★ 真机**定案**了外部两家互相矛盾的结论",
    "level": "verified",
    "verified_versions": ["2026"],
    "backends": ["solidworks-com-pywin32"],
    "dependencies": ["solidworks"],
    "evidence": [
        "★★★ 真机（2026-10-06 · 规格 209 的 **B2-2** · idx **34**）："
        "`python tools/sw_guard.py --timeout 900 -- python tools/probe_spec209_b2_balloon.py` ⇒ "
        "自建 **装配**（2 个组件，存盘）+ **两张独立的**装配工程图，**两格对照**："
        "① **没有 BOM 表** ⇒ **`ok=True`** · `sum(IView::GetNoteCount)` **0 → 1（Δ=1）**、"
        "`AutoBalloon5` 返回的数组长度 **1**；"
        "② **先插一张 BOM 表**（`IView::InsertBomTable6`）⇒ **`ok=True`** · **Δ=1**、返回长度 **1** ✓ "
        "★ 证据 `output/spec209-balloon.json`",
        "★★★ **这一条是裁决书点名要「真机定案」的那件**（§一 逐字：「★★ 两家结论**互相矛盾**"
        "（Slacker-LLC 说静默无效、Eduardof0nt 直接调并回 `bool(result)`）⇒ **不许照抄任何一家**」）"
        "⇒ ★★ **定案**：装配工程图上**有没有 BOM 表都插得进去**（两格各 Δ=1）⇒ "
        "★ **Slacker-LLC 的「静默无效」在本机不成立**；★ 而 **Eduardof0nt 的 `bool(result)` 也不能当判据**"
        "（★ 它只是「返回数组非空」，与\"真的插进去了\"不是一回事）⇒ "
        "★★ **判据只能是 `sum(IView::GetNoteCount)` 的增量 > 0** ✓",
        "★★ **我自己的假设也被这一轮推翻（如实记）**：我原先按官方示例的 `Preconditions` 逐字"
        "（「Open a drawing **with a bill of materials (BOM) table**」）假设「**没有 BOM 表 ⇒ 静默无效**」"
        "⇒ ★★ **真机否证了它**（没有 BOM 表那格 **Δ=1**）⇒ ★ **官方示例的 `Preconditions` 是"
        "「例子的环境」，不是「方法的硬前置」** —— ★ 这已记进 `spec.md` §五 ✓",
        "★★ **探针自身的一处设计缺陷（也如实记）**：第一版把第二格跑在**同一张图、同一个视图**上"
        "⇒ 那时气泡**已经存在**，`IgnoreMultiple=True` 很可能只是**没重复插** ⇒ "
        "★ 那一格的 Δ=0 **不能**当证据 ⇒ ★ 改成**两张独立图纸**重做，才得到上面那两格 ✓",
        "★ 官方依据逐页读过：`C:\\swapi\\types\\IDrawingDoc\\AutoBalloon5.md`（Returns 逐字 "
        "「Array of **INotes**」；`## Remarks` 给**四步前置** —— ① 先选中一个或多个**视图或图纸** "
        "（★ 选**图纸**时会插到该图纸的**所有**视图上）② `CreateAutoBalloonOptions()` ③ 设属性 "
        "④ 调它）· `C:\\swapi\\types\\IView\\GetNoteCount.md`（**判据来源**）· "
        "`C:\\swapi\\types\\IModelDocExtension\\InsertBOMBalloon2.md`（单发气泡："
        "`Note InsertBOMBalloon2(BalloonOptions)`，**同样是四步前置**）· "
        "`C:\\swapi\\types\\IView\\InsertBomTable6.md`（★ 用来造「有 BOM 表」那格的夹具）· "
        "`enums\\{swBomType_e,swBomConfigurationAnchorType_e}.md` · "
        "★★ `examples\\Add_Autoballoon_to_Face_Example_VB.md`（**调用序** + 默认值来源）✓",
    ],
    "limitations": [
        "★★★ **判据已收紧**（★ 本批改的）：原 `auto_insert_balloons` 的 `ok` 是 "
        "`bool(AutoBalloon5 返回的数组) and (delta >= 0)` —— 两处都不合规格："
        "① 依赖**返回值**；② `delta >= 0` **太松**（★ **差 0 = 什么都没插，却会通过**）⇒ "
        "★ 现在 `ok = (delta is not None and delta > 0)`，★ 返回的数组长度**照旧回报、不当判据** ✓ "
        "★ 已加静态断言钉住（含「旧判据不许留在**代码**里」，注释里引用它是防它的证据）✓",
        "★★ **原函数自述「不建 ToolSpec」的理由已过期**：它写「`AutoBalloon5` 的形参是 "
        "`AutoBalloonOptions` **COM 对象** ⇒ `Param` 表达不了」—— ★ 那句说的是**底层成员**；"
        "★ 而**包装函数的形参全是标量**（`layout`/`style`/`size`/…）⇒ ★ **本批把它挂成了工具** "
        "`solidworks_drawing_insert_balloons` ✓（★ 与裁决书 §九「建议挂在 `auto_insert_balloons` 之上」一致）",
        "★ **`InsertBOMBalloon2`（单发气泡）本轮未单独验**：它**不是** `AutoBalloon5` 的替代品"
        "（一个是「给整个视图自动插」，一个是「给选中的那一项插一个」）⇒ ★ 本条目**只覆盖批量那一路** ✓ "
        "⚠ 要用单发那条，① 得**先选中一个项**、② 得先 `CreateBalloonOptions()`（★ 与 "
        "`CreateAutoBalloonOptions` **不是同一个**）",
        "⚠ **未验**：★ 只在本机 **SW 2026 SP4.1**、**2 个组件**的装配工程图上验过；"
        "★ 多视图 / 选**图纸**（`## Remarks` 说那样会插到该图纸所有视图）/ 多配置 / "
        "组件被压缩 等组合**均未验** · ★ `layout`/`style`/`size` 等选项**只用了官方示例的默认值**，"
        "★ **逐个选项的效果未验** ✓",
        "★ 默认值**逐条照官方示例**（`Add_Autoballoon_to_Face_Example_VB.md`）—— ★ **不声称**"
        "它们是 SolidWorks 的出厂默认（★ 官方页没给默认值表）✓",
    ],
    "source_evidence": "★ 本仓自建（按官方签名 + 官方示例的**调用序**立）· "
                       "★ 能力层**早已实现**于 `scripts/sw_drawing_create_missing.py::auto_insert_balloons`"
                       "（本批只做「收紧判据 + 挂工具 + 真机定案」）· "
                       "官方依据：`C:\\swapi\\types\\IDrawingDoc\\AutoBalloon5.md` · "
                       "`C:\\swapi\\types\\IView\\GetNoteCount.md` · "
                       "`C:\\swapi\\types\\IModelDocExtension\\InsertBOMBalloon2.md` · "
                       "官方示例 `Add_Autoballoon_to_Face_Example_VB.md` —— ★ **逐页读过** ✓ "
                       "★ **不来自任何外部项目**（★ 而本条恰恰是**去否证**两家外部项目的论断）✓",
    "source": "original",
    "allowed_modes": ["interactive", "reviewed", "unattended"],
    "mcp_tools": ["solidworks_drawing_insert_balloons"],
}


def main() -> int:
    data = json.loads(CAPS.read_text(encoding="utf-8"))
    caps = data["capabilities"]
    if any(c.get("id") == ENTRY["id"] for c in caps):
        print("★ 已存在 ⇒ 跳过")
    else:
        caps.append(ENTRY)
        print("★ 追加 drawing_bom_balloons（verified）")
    out = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    json.loads(out)
    CAPS.write_text(out, encoding="utf-8")
    print("★ capabilities 共 %d 条" % len(caps))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
