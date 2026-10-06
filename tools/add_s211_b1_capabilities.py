"""★ 规格 211 · B1-1：把「截面属性」登记进 `capabilities.yaml`（★ 照仓里既有 adder 的做法）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（规格 211 · B1-1 的能力登记）
# 文件:   tools/add_s211_b1_capabilities.py
# 定位:   ★ 规格 `specs/211-user-feature-gaps` 的 **B1-1**。★ 按规格的验收流水线，★ 落地之后必须
#   ★ **登记 `level` + 非空 `evidence` + `limitations`** ✓
# 判据:   ★★ `level` 取 **`stitched`**（★ 不是 `verified`）—— ★ 理由**必须写清**：
#   ★ 真机**读到了**（`status=0` · `area` 有值 · 与 `IFace2.GetArea()` **12/12 完全相同**）✓
#   ★★ **但面积单位未确证**（★ 正方体实验里侧面读 0.4、应为 400、差 1000 倍，★ 而那**不是**面积换算）
#     ⇒ ★ 按本仓口径：★ **不完整就不许标 `verified`**（★ 铁律 2 的精神：★ 有证据才算）✓
#   ★★ `limitations` 必须含三条：★ ① 单位未确证 · ② **只支持"当前选择集"**（★ 属性形态吃不到
#     `Sections` 形参）· ③ **有副作用**（★ 清空并重写选择集 ⇒ ★ 不许标 `read_only`）✓
# 官方依据: `C:\swapi\types\IModelDocExtension\GetSectionProperties2.md`（24 元 + status 取值）
# 许可:   本仓库 MIT。无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(r"D:\AI\SW")
CAPS = ROOT / "capabilities.yaml"

ENTRY = {
    "id": "section_properties",
    "label": "截面属性（当前选择集的截面面积 / 形心 / 惯性矩族）",
    #: ★★ `stitched`（不是 `verified`）—— ★ 单位未确证 ⇒ ★ 不完整就不许标 verified ✓
    "level": "stitched",
    "source": "official",
    "source_evidence": [
        "官方 `C:\\swapi\\types\\IModelDocExtension\\GetSectionProperties2.md`："
        "`System.object GetSectionProperties2(System.object Sections)`；"
        "`## Remarks` 给出**24 元返回**的下标定义与 `retval[0]` 的四个 status 取值",
        "官方 `C:\\swapi\\types\\IFace2\\GetArea.md`：`System.double GetArea()`，"
        "`## Returns` 写「Face area in square meters」（★ 而真机读数与该 Remark **不符**，见 limitations）",
    ],
    "evidence": [
        "★ 建状态 + 正例：`python tools/sw_guard.py --timeout 900 -- "
        "python tools/probe_spec211_section_properties.py`（★ 100×60×20 板）",
        "★★ 形态判定：`python tools/sw_guard.py --timeout 900 -- "
        "python tools/probe_spec211_section_props_forms.py` ⇒ ★ **入口是「当属性取」**："
        "`type` = `tuple` · `callable` = `False` · ★ **求值即返回结果**；"
        "★ 对照 `InsertChainDimensions`（事实 386 的样本）回的是 **`None`** ⇒ ★★ **两者不同命** ✓",
        "★★ 单位实验：`python tools/sw_guard.py --timeout 900 -- "
        "python tools/probe_spec211_section_units_cube.py`（★ 20×20×20 正方体）⇒ "
        "**两个端面读 400**（= 20×20 的真值）· **四个侧面读 0.4**（应为 400，差 1000 倍）",
        "★★ 交叉验证读数（**12/12 次**）：`retval[1]` 与 `IFace2.GetArea()` **逐面完全相同** ⇒ "
        "证据文件 `output/spec211-b1-section-area-units.json` · "
        "`output/spec211-b1-section-units-cube.json` · `output/spec211-b1-section-props-forms.json`",
        "★ 契约/负例：`python -m pytest tests/test_spec211_section_properties.py -q` ⇒ **6 passed**"
        "（★ 含两条必然失败：★ 工程图先拒 · ★ 入口不存在）",
    ],
    "limitations": [
        "★★ **面积单位未确证**：正方体实验里**端面**读 400（= 20×20 的真值 mm²），而**侧面**读 0.4"
        "（应为 400，差 **1000** 倍）；★ **1000 不是任何面积换算**（1 cm² = 100 mm²）⇒ "
        "★ 所以**不是「单位差」、而是那类面读的不是同一个东西** ✗ ⇒ ★ 返回值带 "
        "`units_verified: False` + `unit_caveat`，★ **不许假装知道**（铁律 5）。"
        "★ 另记：官方 `IFace2.GetArea` 的 `## Returns` 写「square meters」，★ 与真机读数**不符** ⇒ "
        "★ 这是一条「官方 Remarks 与真机不一致」，归 `specs/211/spec.md §五`",
        "★★ **只支持「当前选择集」**：★ 该成员的可用形态是**属性**（无参），"
        "★ **吃不到 `Sections` 形参** ⇒ ★ 本包装**不支持显式传 `Sections`**（★ 如实记，不假装支持）；"
        "★ 故**调用方必须先选好对象** ✓",
        "★★ **有副作用**：★ 官方写「**This method clears the selection set**」+「objects in the "
        "`Sections` parameter **are added to** the current selection set」⇒ "
        "★★ **它清空并重写选择集** ⇒ ★ 按**规格 210** 的效应声明体系，★ **它不许被标 `read_only`** ✓",
        "⚠ ★ 只对**零件/装配**有效（★ 工程图**先拒** —— ★ 与 `mass_property_object` 那条教训同判据）✓",
    ],
    "backends": ["pywin32"],
    "allowed_modes": ["part", "assembly"],
    "dependencies": [],
    "verified_versions": {"solidworks": ["2026"]},
}


def main() -> int:
    d = json.loads(CAPS.read_text(encoding="utf-8"))
    caps = d["capabilities"]
    if any(c.get("id") == ENTRY["id"] for c in caps):
        print("★ 已有 `%s` ⇒ 不重复添加" % ENTRY["id"])
        return 0
    caps.append(ENTRY)
    CAPS.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    import collections
    c = collections.Counter(x.get("level") for x in caps)
    print("★ 已登记 `%s` ⇒ 共 %d 条 · level 分布 = %s" % (ENTRY["id"], len(caps), dict(c)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
