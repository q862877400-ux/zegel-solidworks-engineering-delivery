"""★ spec 293：**换路由可行性逐站点拍板** —— ★ 5 处真命中里 **2 处可换、3 处不可换**（★ 官方依据）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   D:/AI/SW
# 文件:   C:\swapi\types\IFeatureManager\FeatureLinearPattern5.md:12（★ 「Obsolete. See `CreateFeature` and the
#           Remarks in `ILinearPatternFeatureData` and `ILocalLinearPatternFeatureData`.」）
#         C:\swapi\types\IFeatureManager\FeatureLocalCurveDrivenPattern.md:12（★ 同形 ⇒ `CreateFeature`）
#         C:\swapi\types\IFeatureManager\InsertFormToolFeature.md:12（★ 「Superseded by `CreateDefinition` and `CreateFeature`」）
#         C:\swapi\docs\Programming with the SOLIDWORKS API\Pattern Features and their Feature Data Objects.md:20,32
#           （★ 「Before calling `CreateDefinition`, you must **pre-select** the entities」+ 四步流程）
#         C:\swapi\types\ILinearPatternFeatureData\_overview.md:20（★ 同句 · ★ mark 表 1/2/4/256）
#         C:\swapi\examples\Create_Bidir_Linear_Pattern_Example_CSharp.md:50-67（★ 官方**迁移示例**：先选 mark 4/1/2 ⇒ CreateDefinition ⇒ CreateFeature）
#         C:\swapi\examples\Create_and_Access_Curve-driven_Pattern_Feature_Example_VB.md:65-74（★ 同形）
#         scripts/sw_part.py::linear_pattern（★ 「后继空」**是错的** ⇒ 订正）· scripts/sw_pattern.py::insert_local_curve_driven_pattern_report（★ **已预选** mark 1/2）
#         scripts/sw_sheet_metal.py::insert_form_tool_report（★ **已预选** 一个面）
#         scripts/sw_render_material.py::delete_render_material · output/render-material-family-evidence.json
#         specs/292-evidence-table-line-free/acceptance.md（★ 292 量出 5 处站点）
# 定位:   ★★★ 250 的「换路由 + 真机验」**从未逐站点拍板** ⇒ ★ 本轮**先量**：★ 每处**能不能换**。
# 判据:   ★★★ 逐站点表态（★ 未表态即红）：★ 官方后继**都要预选** ⇒ ★ 站点**已经预选**才**可换**；
#         ★★ 且 `sw_part.py` 的记档**不得**再写「后继空」（★ 官方逐字给的是 `CreateFeature`）。
# 官方依据: 见上「文件」段（★ 逐条逐行）。
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   只读（★ 官方页 + 真树源码 + 既有证据 json）；★ 本文件不写任何文件。
# ────────────────────────────────────────────────────────────────────
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
OFF = Path(r"C:\swapi")

#: ★★★ **250 的 5 处真命中**（★ 292 用 AST 量出；★ `tools/` 里的 8 处是**探针**，★ 不算）。
#: 值 = (★ **真机前置已满足**, ★ **可换？**) —— ★★★ **2026-10-10（spec 294）真机订正**：
#:   ★★ 原先第一项写的是「**代码里**有选择调用」—— ★ **那是弱判据**：★ 真机实测
#:   `FeatureLocalCurveDrivenPattern` 的 **mark2（方向曲线）选不上**（★ `output/spec211-b5-curvedriven.json`）
#:   ⇒ ★★★ **「代码里写了 `mark=2`」≠「真机上真的选上了」** ⇒ ★ **全部改为「真机前置已满足」**。
SITES = {
    ("sw_part.py", "linear_pattern"): (False, False),
    ("sw_part.py", "linear_pattern_report"): (False, False),
    ("sw_pattern.py", "insert_local_curve_driven_pattern_report"): (False, False),
    ("sw_sheet_metal.py", "insert_form_tool_report"): (False, False),
    ("sw_render_material.py", "delete_render_material"): (False, False),
}
#: ★★ **官方后继**（★ 逐字）。
SUCCESSORS = {
    "FeatureLinearPattern5": "IFeatureManager::CreateFeature",
    "FeatureLocalCurveDrivenPattern": "IFeatureManager::CreateFeature",
    "InsertFormToolFeature": "IFeatureManager::CreateFeature",
}
#: ★★★ **官方「必须预选」逐字**（★ 两处独立页面同句）。
PRESELECT = ("Before calling [[IFeatureManager::CreateDefinition]], you must pre-select",
             "you must pre-select the entities needed to create the linear pattern feature")


def _enclosing_sites() -> dict:
    """★ 现场 AST：`scripts/` 里三个成员的调用点 → `{(文件, 包围函数): 成员名}`。"""
    targets = {"FeatureLinearPattern5", "FeatureLocalCurveDrivenPattern",
               "InsertFormToolFeature", "DeleteRenderMaterial"}
    out: dict = {}
    for p in sorted(SCRIPTS.glob("*.py")):
        src = p.read_text(encoding="utf-8", errors="replace")
        if not any(t in src for t in targets):
            continue
        tree = ast.parse(src)
        enc: dict = {}
        for n in ast.walk(tree):
            if isinstance(n, ast.FunctionDef):
                for c in ast.walk(n):
                    enc.setdefault(getattr(c, "lineno", 0), n.name)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            f = node.func
            name = f.attr if isinstance(f, ast.Attribute) else (
                f.id if isinstance(f, ast.Name) else None)
            if name in ("get_com_member", "call_com_member"):
                if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant):
                    name = node.args[1].value
            if name in targets:
                out[(p.name, enc.get(node.lineno, "<module>"))] = name
    return out


def _failures(sites: dict, asm_doc: str, successors: dict, preselect: tuple) -> list:
    """★ 纯函数（★ 判据必须能在合成输入上红）：返回问题清单（★ 空 = 通过）。"""
    bad: list = []
    if len(sites) != 5:
        bad.append("★ 应 5 处真命中（★ `scripts/`），实测 %d ⇒ 读取器或真树变了" % len(sites))
    for key, (preselected, switchable) in sites.items():
        if switchable and not preselected:
            bad.append("★ %s 判「可换」却**没预选** ⇒ 表态与事实矛盾" % (key,))
        if (not switchable) and preselected:
            bad.append("★ %s 判「不可换」却**已预选** ⇒ 请复核" % (key,))
    for member, succ in successors.items():
        if succ != "IFeatureManager::CreateFeature":
            bad.append("★ %s 的后继记成了 %r ⇒ 与官方逐字不符" % (member, succ))
    for phrase in preselect:
        if not phrase:
            bad.append("★ 「必须预选」的官方逐字丢了")
    if asm_doc is None:
        bad.append("★ 取不到 `sw_part.py` 的源码")
    else:
        #: ★★★ **「后继空」这句错话必须**整文件**绝迹** —— ★ 实测它曾出现在**两处函数**里
        #:   （★ 1456 的官方链 + 2547 的换代记档）⇒ ★ 只查一个函数会**漏**。
        if "后继空" in asm_doc:
            bad.append("★★★ `sw_part.py` 仍写「后继空」⇒ 与官方逐字矛盾（★ 官方给的是 `CreateFeature`）")
        if "CreateFeature" not in asm_doc:
            bad.append("★★ `sw_part.py` 没写出官方后继 `CreateFeature`")
        if "pre-select" not in asm_doc and "预选" not in asm_doc:
            bad.append("★★ `sw_part.py` 没写出「后继**要求预选**」这条**不能换的真因**")
    return bad


def _asm_docstring() -> str:
    """★ 取 `sw_part.py` 的**全文**（★ 不是 `get_docstring` —— ★★ 本仓的记档写在 `#:` **注释块**里、
    ★ 位于 docstring **之外** ⇒ ★ 用源码才收得到；★ 且「后继空」这句错话在**两处函数**里都出现过
    ⇒ ★ **整文件**检查，★ 不只看一个函数）。"""
    return (SCRIPTS / "sw_part.py").read_text(encoding="utf-8", errors="replace")


# ── ① ★★ **锚点**：官方三页 + 指南的逐字（★ 铁律 6：锚回原文） ────────
def test_official_pages_give_successor_and_preselect():
    """★★★ **前提断言**：★ 官方**确实**给了后继、**且**后继**要求预选**。

    ★★ 若官方页变了 ⇒ ★ 本判据的期望值失效 ⇒ **先红**（★ 那正是它该做的）。
    """
    pages = {
        "FeatureLinearPattern5.md": ("CreateFeature", "Obsolete"),
        "FeatureLocalCurveDrivenPattern.md": ("CreateFeature", "Obsolete"),
        "InsertFormToolFeature.md": ("CreateFeature", "Obsolete"),
    }
    for fn, toks in pages.items():
        p = OFF / "types" / "IFeatureManager" / fn
        if not p.is_file():
            return                                            # ★ 官方源不在本机 ⇒ 跳过
        t = p.read_text(encoding="utf-8", errors="replace")
        for tok in toks:
            assert tok in t, "★ `%s` 里没有 `%s` ⇒ 判据要重看" % (fn, tok)
    guide = OFF / "docs" / "Programming with the SOLIDWORKS API" / \
        "Pattern Features and their Feature Data Objects.md"
    if guide.is_file():
        g = guide.read_text(encoding="utf-8", errors="replace")
        #: ★★ 指南给的是**四步流程** + 「Pre-selection of entities **may be supported**」（★ 弱句）
        assert "Pre-selection" in g and "CreateFeature" in g, \
            "★ 指南里「Pre-selection / CreateFeature」不见了 ⇒ 判据要重看"
    ov = OFF / "types" / "ILinearPatternFeatureData" / "_overview.md"
    if ov.is_file():
        o = ov.read_text(encoding="utf-8", errors="replace")
        #: ★★★ **强句**（★ 「you must pre-select」）—— 这才是「不能换」的依据
        assert PRESELECT[1] in o, "★ `ILinearPatternFeatureData` 页里「必须预选」不见了"


# ── ② ★★★ **现场**：`scripts/` 里**只有 5 处**真命中 ────────────────
def test_exactly_five_real_sites_in_scripts():
    """★★★ 现场 AST：★ `scripts/` 里三个成员的调用点 **= 5 处**（★ `tools/` 里的是**探针**，★ 不算）。"""
    got = _enclosing_sites()
    assert len(got) == 5, "★ 应 5 处，实测 %d：%s" % (len(got), sorted(got))
    assert set(got) == set(SITES), "★ 站点集合变了：%s" % sorted(set(got) ^ set(SITES))


# ── ③b ★★★ **已被真机推翻的旧判据**（★ 保留为墓碑 · 不再断言） ────────
#: ★★★ **墓碑（★ spec 294 · 2026-10-10）**：这里原有 `test_switchable_sites_already_preselect`，
#:   ★ 它断言「`sw_pattern.py` 里有 `mark=1`/`mark=2`」「`sw_sheet_metal.py` 里有 `select_entity_by_index`」
#:   ⇒ ★★ **据此判那两处「可换」** —— ★★★ **而真机一跑就推翻了**：
#:     ★ `output/spec211-b5-curvedriven.json` 逐字 `mark2_direction1_curve: **false**`
#:     ⇒ ★★ **「代码里写了 `mark=2`」≠「真机上真的选上了」** ⇒ ★ **那是个**弱判据****（★ 只查代码）。
#:   ★★★ **⇒ 删掉它、换成 `test_machine_says_the_direction_curve_never_selects`**（★ 查**真机读数**）。
#:   ★★ **教训**：★ **凡「前置已满足」的判据，必须问：它查的是**代码**还是**真机****。**


# ── ③ ★★★ **真机证据**：曲线阵列的 mark2 **选不上** ⇒ 换路由**无效** ──
def test_machine_says_the_direction_curve_never_selects():
    """★★★ **真机读数**（★ SW rev **34.4.1** · `tools/probe_spec211_curvedriven.py` · **2026-10-10** ·
    ★ 走 `tools/sw_guard.py --timeout 600` · ★ 证据 `output/spec211-b5-curvedriven.json`）：

    ★ `mark1(要阵列的特征)=True` · ★★ **`mark2(方向曲线)=False`** · ★ `selection_count=1`
    ⇒ ★★★ **调用后 `new_features=[]` · `returned_is_none=true` ⇒ **不建****
    ⇒ ★★ **真因是**前置没上****（★ 定则：「**读到静默**」≠「**判定试死**」）。

    ★★★ **⇒ 这条判据的意义**：★ 它把「**代码里写了 `mark=2`**」与「**真机上真的选上了**」**分开** ——
      ★★ 293 的 FR-003 只查**代码**（★ 弱判据）⇒ ★ **真机一跑就把它推翻了**。
      ★★★ **⇒ 「换路由」在 `sw_pattern.py` 上**无效****：★ 后继 `CreateDefinition` + `CreateFeature`
      **同样要 mark2** ⇒ ★ **换了照样不建** ⇒ ★★ **该做的是**修前置**，★ 不是换路由**。
    """
    p = ROOT / "output" / "spec211-b5-curvedriven.json"
    if not p.is_file():
        return                                                # ★ 缺数据源 ≠ 检查失败
    ev = json.loads(p.read_text(encoding="utf-8"))
    assert ev["select"]["mark2_direction1_curve"] is False, \
        "★ mark2 居然选上了 ⇒ 前置已修 ⇒ 请重跑真机并**重新拍板**（★ 那才是「可换」）"
    assert ev["select"]["selection_count"] == 1, \
        "★ 选区计数变了（%r）⇒ 读数要重看" % ev["select"]["selection_count"]
    assert ev["new_features"] == [] and ev["returned_is_none"] is True, \
        "★ 居然建成了 ⇒ 结论要翻（★ 请重跑真机并更新本判据）"


# ── ④ ★★★ **不可换的记档必须写清真因**（★ 且「后继空」必须消失） ────
def test_unspportable_site_records_the_real_reason():
    """★★★ `sw_part.py::linear_pattern` 的记档：★ 官方后继 = `CreateFeature` · ★ 真因 = **后继要求预选**
    ⇒ ★★★ **「后继空」不得再出现**（★ 那是**错的** · ★ spec 293 订正）。
    """
    bad = _failures(SITES, _asm_docstring(), SUCCESSORS, PRESELECT)
    assert not bad, "逐站点拍板不合格：\n" + "\n".join("  " + b for b in bad)


# ── ⑤ ★★ **第三处不可换**：后继在**本机不可调**（★ 既有真机证据） ──
def test_render_material_successor_is_unreachable_per_evidence():
    """★★ `DeleteRenderMaterial` 的后继 `DeleteDisplayStateSpecificRenderMaterial` ——
    ★ **既有真机证据**说它**取回来不可调**（★ `新入口能调数 3/4`）⇒ ★ 该处**不可换**。
    """
    p = ROOT / "output" / "render-material-family-evidence.json"
    if not p.is_file():
        return                                                # ★ 缺数据源 ≠ 检查失败
    ev = json.loads(p.read_text(encoding="utf-8"))
    assert ev.get("★_新入口能调数") == "3/4", \
        "★ 证据读数变了（%r）⇒ 该处「不可换」的依据要重看" % ev.get("★_新入口能调数")
    assert ev["新_DeleteDisplayStateSpecificRenderMaterial"]["ok"] is False, \
        "★ 后继居然能调了 ⇒ 该处可以换 ⇒ 请复核拍板"


# ── ⑥ ★★ 判据必须能红 ───────────────────────────────────────────────
def test_pure_function_is_red_able():
    """★ 五组负例：① 站点数不对；② 判「可换」却没预选；③ 后继记错；④ 仍写「后继空」；⑤ 没写预选。"""
    good_doc = "官方后继 `CreateFeature`；★ 真因：后继**要求预选**（pre-select）"
    assert not _failures(SITES, good_doc, SUCCESSORS, PRESELECT), "正常读数被判红 ⇒ 判据过严"
    assert _failures({k: v for k, v in list(SITES.items())[:4]}, good_doc, SUCCESSORS, PRESELECT), \
        "站点数不对却未判出"
    assert _failures({**SITES, ("x.py", "f"): (False, True)}, good_doc, SUCCESSORS, PRESELECT), \
        "判「可换」却没预选却未判出"
    assert _failures(SITES, good_doc, {"FeatureLinearPattern5": "FeatureLinearPattern6"}, PRESELECT), \
        "后继记错却未判出"
    assert _failures(SITES, "★ 5 也废弃、★ 后继空", SUCCESSORS, PRESELECT), "仍写「后继空」却未判出"
    assert _failures(SITES, "★ 官方后继 `CreateFeature`", SUCCESSORS, PRESELECT), \
        "没写「要求预选」却未判出"
